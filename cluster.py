import numpy as np
from sklearn.neighbors import BallTree

from copy import copy

def words_contains(words, f):
    for w in words:
        for l in w:
            if l == f:
                return True
    return False

def cluster_letters_to_words(rects, order_words_topleft_tobottomright=True, alpha=1.0, max_separation=2.5):
    rectangles = copy(rects)
    # decorate rectangles with an ID
    rectangles.sort(key=lambda x: (x[0] + x[2] / 2, x[1] + x[3] / 2))
    # also make mapping from id to rectangle
    id_to_rect = { r[4] : r[0:4] for r in rectangles }

    pts = np.array(rectangles, dtype=np.float)
    cx = pts[..., 0] + pts[..., 2]/2.0
    cy = pts[..., 1] + pts[..., 3]/2.0
    area = pts[...,2] * pts[...,3]
    boundingboxes = np.column_stack([cx, cy, area])

    words = []
    forbidden = []

    while boundingboxes.shape[0]:
        tree = BallTree(boundingboxes, metric='pyfunc', func=lambda x, y:
            alpha*np.linalg.norm(x[0:2]-y[0:2]) + (1-alpha)*np.linalg.norm(x-y))
        el = boundingboxes[0]
        distance, indices = tree.query([el], k=min(boundingboxes.shape[0], 2))
        nearest_elements = boundingboxes[indices]
        nearest_rectangles = pts[indices]
        candidate_neighbours = []
        for idx,n in enumerate(nearest_elements[0]):
            if idx != 0:
                ref_rect = nearest_rectangles[0][0]
                neighb_rect = nearest_rectangles[0][idx]
                ref_cx = el[0]
                ref_cy = el[1]
                ref_center = el[0:2]
                neighb_cx = nearest_elements[0][idx][0]
                neighb_cy = nearest_elements[0][idx][1]
                neigh_center = nearest_elements[0][idx][0:2]
                expected_distance = ref_rect[2] / 2 + neighb_rect[2] / 2 # half width of reference + half width of candidate
                diff = neigh_center - ref_center
                eucldist = np.linalg.norm(diff)
                angle = np.angle(diff[0] + 1j*diff[1])
                candidate_neighbours.append((neighb_rect, expected_distance, eucldist, angle))

        if (len(candidate_neighbours) != 0):
            c = sorted(candidate_neighbours, key=lambda e: np.pi*2-abs(e[3])) # choose the most horizontal nearest neighbour
            if (c[0][2]/c[0][1] > max_separation):
                forbidden.append([ref_rect[4], c[0][0][4]])
                pass
            else:
                found = False
                for existing in words:
                    if existing[-1] == ref_rect[4]:
                        found = True
                        existing.append(c[0][0][4])
                        break
                    if existing[0] == c[0][0][4]:
                        found = True
                        l = [ref_rect[4]]
                        l.extend(existing)
                        existing = l
                        break
                if not found:
                    words.append([ref_rect[4], c[0][0][4]])

            boundingboxes = np.delete(boundingboxes, (0), axis=0) # remove reference bbox so as to not reuse it
            pts = np.delete(pts, (0), axis=0)
        else:
            break

    # find out if forbidden contains entries not in words (special edge case where first recognized word is single letter)
    for fo in forbidden:
        for f in fo:
            if not words_contains(words, f):
                words.append([f])

    ordering = []
    if order_words_topleft_tobottomright:
        summary = []
        for idx, w in enumerate(words):
            wordcenters = []
            for r in w:
                rectangle = id_to_rect[r]
                cx = rectangle[0]+rectangle[2]/2
                cy = rectangle[1]+rectangle[3]/2
                wordcenters.append((cx,cy))
            avgx = sum(x[0] for x in wordcenters)/len(wordcenters)
            avgy = sum(x[1] for x in wordcenters)/len(wordcenters)
            summary.append((avgy, avgx, idx))
        for w in sorted(summary):
            ordering.append(w[2])
    else:
        for idx, w in enumerate(words):
            ordering.append(idx)

    return words, id_to_rect, forbidden, ordering