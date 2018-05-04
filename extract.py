import pickle
import difflib

import cv2
import numpy as np
from keras.models import model_from_yaml
from globals import GLOBAL_hobj, GLOBAL_fuzzylist

Y_SQUASH = 40.0

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
    #img_scale = image
    #cv2.imshow("scale", img_scale)
    img = cv2.cvtColor(img_scale, cv2.COLOR_BGR2GRAY);
    #cv2.imshow("2gray", img)
    gray = cv2.bilateralFilter(img, 11, 21, 21)
    #cv2.imshow("bilateral", gray)
    edged = cv2.Canny(gray, 0, 70)
    #cv2.imshow("edged", edged)
    image2, contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.imshow("image2", image2)
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

    if len(screenCnt) == 0:
        return None

    warped = four_point_transform(img_scale, screenCnt.reshape(4, 2))
    #cv2.imshow("warped", warped)
    height = warped.shape[0]
    width = warped.shape[1]
    #print ("width: {0}, height: {1}".format(width, height))
    xmargin = 10
    ymargin = 10
    crop_img = warped[ymargin:(height - 2 * ymargin), xmargin:(width - 2 * xmargin)]  # img[y: y + h, x: x + w]
    #cv2.imshow("cropped", crop_img)
    #cv2.waitKey(0)
    return crop_img


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
        if rect_area(numpy_letters[i]) < 50:
            remove_idx.add(i)
        else:
            for j in range(len(numpy_letters)):
                if i != j:
                    if rect_in_rect(numpy_letters[i], numpy_letters[j]):
                        remove_idx.add(i)

    # print (remove_idx)
    final_letters = [letter for (i, letter) in enumerate(numpy_letters) if i not in remove_idx]
    unwarped_image = image.copy()
    for l in final_letters:
        x = l[0]
        y = l[1]
        x2 = x + l[2]
        y2 = y + l[3]
        cv2.rectangle(unwarped_image, (x, y), (x2, y2), 3)
    return final_letters, unwarped_image

def remove_doubles_and_overlaps_for_single_letter(image, letters):
    final_letters, boxed_image = remove_doubles_and_overlaps(image, letters)
    minx = 1e10
    miny = 1e10
    maxx = -1e10
    maxy = -1e10
    if final_letters:
        for letter in final_letters:
            x = letter[0]
            x2 = x + letter[2]
            y = letter[1]
            y2 = y + letter[3]
            minx = min([x,  minx])
            maxx = max([x2, maxx])
            miny = min([y, miny])
            maxy = max([y2, maxy])
        #print("minx, maxx, miny, maxy = ", [minx, maxx, miny, maxy])
        cv2.rectangle(boxed_image, (minx,miny), (maxx,maxy), (0,0,0), 1)
        return [(minx, miny, maxx-minx, maxy-miny)], boxed_image
    return None, None

def contours_to_boundingboxes(cnts):
    letters = []
    for i, c in enumerate(cnts):
        contour = c[2]
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        x, y, w, h = cv2.boundingRect(contour)
        letters.append((x, y, w, h))
        # print(x, y, w, h)
    return letters


def find_contours(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY);
    # V = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2HSV))[2]
    # thresh = threshold_adaptive(V, 101, offset=15).astype("uint8") * 255
    # thresh = cv2.bitwise_not(thresh)
    # gray = thresh
    gray = cv2.bilateralFilter(gray, 5, 51, 51)
    edged = cv2.Canny(gray, 0, 100)
    image3, contours3, hierarchy3 = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = []
    found = set({})
    for c in contours3:
        M = cv2.moments(c)
        if M['m00']:
            cx = int(int(M['m10'] / M['m00']))
            cy = int(int(M['m01'] / M['m00']))
            if (cx, cy) not in found:
                found.add((cx, cy))
                cnts.append((cy, cx, c))
    return cnts


def dist(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def debug_display(title, list_of_images):
    if not list_of_images:
        return
    l = len(list_of_images)
    cols = int(np.ceil(np.sqrt(l)))
    rows = int(np.ceil(l / cols))
    height, width = list_of_images[0].shape
    total_image = np.zeros((height*cols,width*rows))
    counter = 0
    for c in range(cols):
        for r in range(rows):
            if counter < l:
                total_image[c*height : (c + 1)*height, r*width : (r + 1)*width] = list_of_images[counter]
                counter += 1
    cv2.imshow(title, total_image)
    cv2.waitKey(1)

def cutout_letters(unwarped_image, letters, xmargin=3, ymargin=3, desired_width=28, desired_height=28):
    unwarped_image = cv2.cvtColor(unwarped_image, cv2.COLOR_BGR2GRAY);
    #cv2.imshow("unwarped", unwarped_image)
    result = []
    prevX = None
    prevY = None
    for i, l in enumerate(sorted(letters, key=lambda x: (int(x[1] / Y_SQUASH), x[0]))):
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

        if distance > w * 3:
            new_word = True

        cropped_letter = unwarped_image[y:y + h, x:x + w]
        maxdim = max(h,w)
        if h > w:
            extra_height = 0
            extra_width = int((h - w)/2)
        else:
            extra_height = int((w - h)/2)
            extra_width = 0

        #blur = cv2.GaussianBlur(cropped_letter, (3, 3), sigmaX=1, sigmaY=1)
        blur = cv2.GaussianBlur(cropped_letter, (5, 5), 0)
        ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        #th3 = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
        #                            cv2.THRESH_BINARY, 11, 2)

        padded_cropped_letter = cv2.copyMakeBorder(th3, top=extra_height, bottom=extra_height,
                                                   left=extra_width, right = extra_width,
                                                   borderType=cv2.BORDER_CONSTANT, value=[255,255,255])
        current_width = padded_cropped_letter.shape[1]
        current_height = padded_cropped_letter.shape[0]
        #cv2.imshow("{0}".format(i + 1), padded_cropped_letter)
        scaled_cropped_letter = cv2.resize(padded_cropped_letter, None, fx=(desired_width - 2 * xmargin) / current_width,
                                           fy=(desired_height - 2 * ymargin) / current_height,
                                           interpolation=cv2.INTER_LINEAR)

        if (xmargin > 0) or (ymargin > 0):
            bordered = cv2.copyMakeBorder(scaled_cropped_letter, top=ymargin, bottom=ymargin,
                                          left=xmargin, right=xmargin,
                                          borderType=cv2.BORDER_CONSTANT,
                                          value=[255, 255, 255])
        else:
            bordered = scaled_cropped_letter

        # th3_blur = cv2.GaussianBlur(255-th3, (5, 5), 0)
        th3_inv_blur = 255 - bordered
        blur_th3 = th3_inv_blur
        #cv2.imshow("{0}".format(i + 1), th3_inv_blur)
        # cv2.waitKey(0)
        if new_word:
            result.append(None)
        #print("MAX: ", np.amax(blur_th3), " MIN: ", np.amin(blur_th3), " MEDIAN: ", np.median(blur_th3))
        result.append([blur_th3.copy(), (x + w/2, y + h/2)])

    visualization = [r[0] for r in result if r is not None]
    debug_display("found letters", visualization)

    return result

def cutout_grayscale_letters(unwarped_image, letters, xmargin=3, ymargin=3, desired_width=28, desired_height=28):
    #cv2.imshow("unwarped", unwarped_image)
    result = []
    for l in letters:
        new_word = False
        x = l[0]
        y = l[1]
        w = l[2]
        h = l[3]

        cropped_letter = unwarped_image[y:y + h, x:x + w]
        maxdim = max(h,w)
        if h > w:
            extra_height = 0
            extra_width = int((h - w)/2)
        else:
            extra_height = int((w - h)/2)
            extra_width = 0

        #blur = cv2.GaussianBlur(cropped_letter, (3, 3), sigmaX=1, sigmaY=1)
        blur = cv2.GaussianBlur(cropped_letter, (1, 1), 0)
        ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        #cv2.imshow("otsu", th3)
        #th4 = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
        #                            cv2.THRESH_BINARY, 11, 2)
        #cv2.imshow("adaptive", th4)

        #th5 = th3.copy()
        #cv2.multiply(255-th3, 255-th4, th5)
        #th3 = 255-th5 
        #cv2.imshow("multiplication", th3)
        #cv2.waitKey(0)

        padded_cropped_letter = cv2.copyMakeBorder(th3, top=extra_height, bottom=extra_height,
                                                   left=extra_width, right = extra_width,
                                                   borderType=cv2.BORDER_CONSTANT, value=[255,255,255])
        current_width = padded_cropped_letter.shape[1]
        current_height = padded_cropped_letter.shape[0]
        #cv2.imshow("{0}".format(i + 1), padded_cropped_letter)
        scaled_cropped_letter = cv2.resize(padded_cropped_letter, None, fx=(desired_width - 2 * xmargin) / current_width,
                                           fy=(desired_height - 2 * ymargin) / current_height,
                                           interpolation=cv2.INTER_LINEAR)

        if (xmargin > 0) or (ymargin > 0):
            bordered = cv2.copyMakeBorder(scaled_cropped_letter, top=ymargin, bottom=ymargin,
                                          left=xmargin, right=xmargin,
                                          borderType=cv2.BORDER_CONSTANT,
                                          value=[255, 255, 255])
        else:
            bordered = scaled_cropped_letter

        # th3_blur = cv2.GaussianBlur(255-th3, (5, 5), 0)
        th3_inv_blur = 255 - bordered
        blur_th3 = th3_inv_blur
        #cv2.imshow("{0}".format(i + 1), th3_inv_blur)
        # cv2.waitKey(0)
        #print("MAX: ", np.amax(blur_th3), " MIN: ", np.amin(blur_th3), " MEDIAN: ", np.median(blur_th3))
        result.append([blur_th3.copy(), (x + w/2, y + h/2)])

    visualization = [r[0] for r in result if r is not None]
    debug_display("found letters", visualization)

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
    # print(img.shape)
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


def cleanup_word(word, use_spellcheck_instead_of_commands_txt=False):
    word = word.replace("0", "O").replace("2","b").replace("8", "b").lower()
    if use_spellcheck_instead_of_commands_txt:
        if GLOBAL_hobj.spell(word):
            print(word)
            return word
        else:
            suggestions = GLOBAL_hobj.suggest(word)
            if suggestions:
                for s in suggestions:
                    if len(s) == len(word):
                        print(word, " cleaned up to: ", s, " from possible: ", suggestions)
                        return s.lower()
                print(word, " cleaned up to: ", suggestions[0], " from possible ", suggestions)
                return suggestions[0].lower()
            else:
                print("unrecognized word: ", word)
                return word
    else:
        corrected = fuzzy_correct(word, GLOBAL_fuzzylist)
        print("corrected {0} to {1}".format(word, corrected))
        return corrected

def fuzzy_correct(word, list_of_possible_words):
    closematch = difflib.get_close_matches(word, list_of_possible_words)
    if closematch:
        return closematch[0]
    return word

def main():
    bindir = "/home/shimpe/development/python/hippoglyph/EMNIST/bin"
    image = cv2.imread("/home/shimpe/development/python/hippoglyph/img.jpg")
    #cv2.imshow("original", image)
    model = load_model(bindir)
    mapping = pickle.load(open('%s/mapping.p' % bindir, 'rb'))
    
    unwarped_image = unwarp(image)
    letters, letter_image = find_letters(unwarped_image)
    cut_letters = cutout_letters(unwarped_image, letters)

    words = []
    current_word = ""
    wordX = 0
    wordY = 0
    wordLen = 0
    for l in cut_letters:
        if l is None:
            words.append([cleanup_word(current_word), (wordX, wordY)])
            current_word = ""
            wordX = 0
            wordY = 0
            wordLen = 0
        else:
            letter, pos = l[0], l[1]
            wordX += pos[0]
            wordY += pos[1]
            wordLen += 1
            current_word += predict(model, mapping, letter)
    if current_word:
        avgX = wordX/wordLen if wordLen != 0 else 0
        avgY = wordY/wordLen if wordLen != 0 else 0
        words.append((cleanup_word(current_word), (avgX, avgY)))

    print(" ".join([w[0] for w in words]))
    print(" ".join([str(pos[1]) for pos in words]))

    #cv2.imshow("letters", letter_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main2():
    #bindir = "c:\\deleteme\\hippoglyph\\hippoglyph\\EMNIST\\bin"
    #image = cv2.imread("c:\\deleteme\\hippoglyph\\hippoglyph\\diagnostics\\diagnostic_image.jpg")
    bindir = "/home/shimpe/development/python/hippoglyph/EMNIST/bin"
    image = cv2.imread("/home/shimpe/development/python/hippoglyph/diagnostics/diagnostic_image.jpg")


    #cv2.imshow("original", image)
    image = unwarp(image)
    #cv2.imshow("unwarped", image)
    result_norm_planes = remove_shadow(image)
    image = cv2.merge(result_norm_planes)
    #cv2.imshow("shadow removal", image);

    image = threshold_image(image)
    #cv2.imshow("threshold", image)
    #image = denoise_image(image)
    #cv2.imshow("denoise", image)
    all_letters = segment_letters(image)
    result = order_letters(all_letters)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def remove_shadow(image):
    rgb_planes = cv2.split(image)
    result_planes = []
    result_norm_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((7, 7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        norm_img = cv2.normalize(diff_img, diff_img, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        #        result_planes.append(diff_img)
        result_norm_planes.append(norm_img)
    image = cv2.merge(result_norm_planes)
    #    image = cv2.merge(result_planes)
    return image


def threshold_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY);
    image = cv2.bilateralFilter(image, 5, 21, 21)
    ret3, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#    image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
#    image = cv2.copyMakeBorder(image, 6, 6, 6, 6, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    return image


def denoise_image(image):
    morph = 255 - image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    image = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel)
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    image = 255 - image
    return image


def order_letters(all_letters):
    result = []
    prevX = None
    prevY = None
    maxh = -1e10
    for l in all_letters:
        h = l[0].shape[0]
        maxh = max([h,maxh])
    for i, l in enumerate(sorted(all_letters, key=lambda x: (int(x[1][1] / maxh), x[1][0]))):
        new_word = False
        x = l[1][0]
        y = l[1][1]
        w = l[0].shape[1]
        h = l[0].shape[0]
        if prevX is None:
            distance = 0
            prevX = x
            prevY = y
        else:
            distance = dist(prevX, prevY, x, y)
            prevX = x
            prevY = y

        if distance > w * 3:
            new_word = True

        if new_word:
            result.append(None)

        result.append(l)
    visualization = [r[0] for r in result if r is not None]
    debug_display("found letters", visualization)
    return result


def segment_letters(image):
    height, width = image.shape
    all_letters = []
    while True:
        mask = np.zeros((height + 2, width + 2), np.uint8)
        #cv2.imshow("mask before", mask)
        indexzero = np.argwhere(image == 0)
        if indexzero.size == 0:
            break
        indexzero = indexzero[0]
        seed = (indexzero[1], indexzero[0])
        floodflags = 4  # connectivity of 4
        floodflags |= (255 << 8)
        num, im, mask, rect = cv2.floodFill(image, mask, seed, (255, 0, 0), (0,) * 3, (0,) * 3, floodflags)
        #cv2.imshow("image", image)
        #cv2.imshow("mask", mask)
        #cv2.waitKey(0)
        mask = 255 - mask
        edged = cv2.Canny(mask, 0, 100)
        image3, contours3, hierarchy3 = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = []
        found = set({})
        for c in contours3:
            M = cv2.moments(c)
            if M['m00']:
                cx = int(int(M['m10'] / M['m00']))
                cy = int(int(M['m01'] / M['m00']))
                if (cx, cy) not in found:
                    found.add((cx, cy))
                    cnts.append((cy, cx, c))
        letters = contours_to_boundingboxes(cnts)
        if letters:
            final_letters, boxed_image = remove_doubles_and_overlaps_for_single_letter(mask, letters)
            #cv2.imshow("boxed", boxed_image)
            #cv2.waitKey(0)
            if final_letters:
                letter = cutout_grayscale_letters(mask, final_letters)
                if letter:
                    try:
                        letter_image, pos = letter[0][0], letter[0][1]
                        all_letters.append((letter_image, pos))
                    except IndexError as e:
                        print(e, letter)

    return all_letters

if __name__ == "__main__":
    main2()
