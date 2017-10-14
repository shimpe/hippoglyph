import pickle

import cv2
import numpy as np
from keras.models import model_from_yaml
import hunspell

def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype="float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect


def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # return the warped image
    return warped


# print(cv2.__version__)

def unwarp(image):
    img_scale = cv2.resize(image, None, fx=1 / 3.0, fy=1 / 3.0, interpolation=cv2.INTER_CUBIC)
    img = cv2.cvtColor(img_scale, cv2.COLOR_BGR2GRAY);
    gray = cv2.bilateralFilter(img, 11, 21, 21)
    edged = cv2.Canny(gray, 0, 70)
    image2, contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    # loop over our contours
    screenCnt = []
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            break

    warped = four_point_transform(img_scale, screenCnt.reshape(4, 2))
    height = warped.shape[0]
    width = warped.shape[1]
    # print ("width: {0}, height: {1}".format(width, height))
    xmargin = 2
    ymargin = 10
    crop_img = warped[ymargin:(height - 2 * ymargin), xmargin:(width - 2 * xmargin)]  # img[y: y + h, x: x + w]
    warped_copy = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY);
    return warped_copy


# Malisiewicz et al.
def non_max_suppression_fast(boxes, overlapThresh):
    # if there are no boxes, return an empty list
    if len(boxes) == 0:
        return []

    # if the bounding boxes integers, convert them to floats --
    # this is important since we'll be doing a bunch of divisions
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    # initialize the list of picked indexes
    pick = []

    # grab the coordinates of the bounding boxes
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)

    # keep looping while some indexes still remain in the indexes
    # list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the
        # index value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        # find the largest (x, y) coordinates for the start of
        # the bounding box and the smallest (x, y) coordinates
        # for the end of the bounding box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        # compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        # compute the ratio of overlap
        overlap = (w * h) / area[idxs[:last]]

        # delete all indexes from the index list that have
        idxs = np.delete(idxs, np.concatenate(([last],
                                               np.where(overlap > overlapThresh)[0])))

    # return only the bounding boxes that were picked using the
    # integer data type
    return boxes[pick].astype("int")


def rect_in_rect(enclosed_rect, enclosing_rect):
    r1x1 = enclosed_rect[0]
    r1y1 = enclosed_rect[1]
    r1x2 = enclosed_rect[0] + enclosed_rect[2]
    r1y2 = enclosed_rect[1] + enclosed_rect[3]
    r2x1 = enclosing_rect[0]
    r2y1 = enclosing_rect[1]
    r2x2 = enclosing_rect[0] + enclosing_rect[2]
    r2y2 = enclosing_rect[1] + enclosing_rect[3]
    return (r2x1 <= r1x1 <= r2x2 and \
            r2x1 <= r1x2 <= r2x2 and \
            r2y1 <= r1y1 <= r2y2 and \
            r2y1 <= r1y2 <= r2y2)


def rect_area(r1):
    return r1[2] * r1[3]


def find_letters(image):
    cnts = find_contours(image)
    letters = contours_to_boundingboxes(cnts)
    final_letters, unwarped_image = remove_doubles_and_overlaps(image, letters)
    return final_letters, unwarped_image


def remove_doubles_and_overlaps(image, letters):
    numpy_letters = np.array(letters)
    # print (numpy_letters)
    numpy_letters = non_max_suppression_fast(numpy_letters, 0.2)
    # print(len(numpy_letters))
    remove_idx = set([])
    for i in range(len(numpy_letters)):
        if rect_area(numpy_letters[i]) < 100:
            remove_idx.add(i)
        else:
            for j in range(len(numpy_letters)):
                if i != j:
                    if rect_in_rect(numpy_letters[i], numpy_letters[j]):
                        remove_idx.add(i)

    # print (remove_idx)
    final_letters = [letter for (i, letter) in enumerate(numpy_letters) if i not in remove_idx]
    unwarped_image = image.copy()
    for i, l in enumerate(final_letters):
        x = l[0]
        y = l[1]
        x2 = x + l[2]
        y2 = y + l[3]
        cv2.rectangle(unwarped_image, (x, y), (x2, y2), 3)
    return final_letters, unwarped_image


def contours_to_boundingboxes(cnts):
    letters = []
    for i, c in enumerate(cnts):
        contour = c[2]
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.2 * peri, True)
        x, y, w, h = cv2.boundingRect(contour)
        letters.append((x, y, w, h))
        # print(x, y, w, h)
    return letters


def find_contours(image):
    gray = cv2.bilateralFilter(image, 5, 51, 51)
    edged = cv2.Canny(gray, 0, 100)
    image3, contours3, hierarchy3 = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = []
    found = set({})
    for c in contours3:
        M = cv2.moments(c)
        cx = int(int(M['m10'] / M['m00']))
        cy = int(int(M['m01'] / M['m00']))
        if (cx, cy) not in found:
            found.add((cx, cy))
            cnts.append((cy, cx, c))
    return cnts

def dist(x1, y1, x2, y2):
    return np.sqrt((x2-x1)**2 + (y2-y1)**2)

def cutout_letters(unwarped_image, letters, xmargin=3, ymargin=3, desired_width=28, desired_height=28):
    result = []
    prevX = None
    prevY = None
    distance = 0
    for i, l in enumerate(sorted(letters, key=lambda x: (int(x[1] / 100), x[0]))):
        new_word = False
        x = l[0]
        y = l[1]
        w = l[2]
        h = l[3]
        if prevX is None:
            distance = 0
            prevX = x
            prevY = y
        else:
            distance = dist(prevX, prevY, x, y)
            prevX = x
            prevY = y

        if distance > w*3:
            new_word = True

        cropped_letter = unwarped_image[y:y + h, x:x + w]
        scaled_cropped_letter = cv2.resize(cropped_letter, None, fx=(desired_width - 2 * xmargin) / w,
                                           fy=(desired_height - 2 * ymargin) / h,
                                           interpolation=cv2.INTER_CUBIC)
        blur = cv2.GaussianBlur(scaled_cropped_letter, (5, 5), 0)
        ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        if (xmargin > 0) or (ymargin > 0):
            bordered = cv2.copyMakeBorder(th3, top=ymargin, bottom=ymargin, left=xmargin, right=xmargin,
                                          borderType=cv2.BORDER_CONSTANT, value=[255, 255, 255])
        else:
            bordered = th3

        # th3_blur = cv2.GaussianBlur(255-th3, (5, 5), 0)
        th3_inv_blur = 255 - bordered
        #cv2.imshow("{0}".format(i + 1), th3_inv_blur)
        # cv2.waitKey(0)
        if new_word:
            result.append(None)
        result.append(th3_inv_blur.copy())
    return result


def load_model(bin_dir):
    ''' Load model from .yaml and the weights from .h5

        Arguments:
            bin_dir: The directory of the bin (normally bin/)

        Returns:
            Loaded model from file
    '''

    # load YAML and create model
    yaml_file = open('%s/model.yaml' % bin_dir, 'r')
    loaded_model_yaml = yaml_file.read()
    yaml_file.close()
    model = model_from_yaml(loaded_model_yaml)

    # load weights into new model
    model.load_weights('%s/model.h5' % bin_dir)
    return model


def predict(model, mapping, img):
    #print(img.shape)
    x = img.reshape(1, 28, 28, 1)

    # Convert type to float32
    x = x.astype('float32')

    # Normalize to prevent issues with model
    x /= 255

    # Predict from model
    out = model.predict(x)

    # Generate response
    response = chr(mapping[(int(np.argmax(out, axis=1)[0]))])
    return response

def cleanup_word(word, use_spellcheck=True):
    word = word.replace("0","O").lower()
    if use_spellcheck:
        hobj = hunspell.HunSpell('/usr/share/hunspell/nl_NL.dic', '/usr/share/hunspell/nl_NL.aff')
        if hobj.spell(word):
            print(word)
            return word
        else:
            suggestions = hobj.suggest(word)
            if suggestions:
                print(word, " cleaned up to: ",suggestions[0]," from possible: ", suggestions)
                return suggestions[0].lower()
            else:
                print("unrecognized word: ", word)
                return word
    else:
        print(word)
        return word

def main():
    bindir = "/home/shimpe/development/python/ocr/EMNIST/bin"
    image = cv2.imread("/home/shimpe/development/python/ocr/img.jpg")
    model = load_model(bindir)
    mapping = pickle.load(open('%s/mapping.p' % bindir, 'rb'))

    unwarped_image = unwarp(image)
    letters, letter_image = find_letters(unwarped_image)
    cut_letters = cutout_letters(unwarped_image, letters)

    words = []
    current_word = ""
    for l in cut_letters:
        if l is None:
            words.append(cleanup_word(current_word))
            current_word = ""
        else:
            current_word += predict(model, mapping, l)
    if current_word:
        words.append(cleanup_word(current_word))

    print(" ".join(words))
    #cv2.imshow("letters", letter_image)

    #cv2.waitKey(0)
    #cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
