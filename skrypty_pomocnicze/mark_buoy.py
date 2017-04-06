import cv2
import imutils
import os

refPt = []
cropping = False


def click_and_crop(event, x, y, flags, param):
    global refPt, cropping

    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True

    elif event == cv2.EVENT_LBUTTONUP:
        refPt.append((x, y))
        cropping = False

        cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 1)
        cv2.imshow("image", image)

path = "../images/"

positive = ""
image_num = 0
for subdir, dirs, files in os.walk(path):
    for file in files:
        image = cv2.imread(os.path.join(subdir, file))
        clone = image.copy()
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", click_and_crop)
        while True:
            cv2.imshow('image', image)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('n'):
                break

            if key == ord("r"):
                image = clone.copy()
        image_num += 1
        cv2.imwrite('../frames/image{}.jpg'.format(image_num), clone)

        positive += "positives/image{}.jpg 1 {} {} {} {}\n".format(image_num, refPt[0][0], refPt[0][1], refPt[1][0] - refPt[0][0],
                                                         refPt[1][1] - refPt[0][1])
        roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
        cv2.imshow('roi', roi)

with open('positive2.txt', 'w') as file:
    file.write(positive)

cv2.destroyAllWindows()
