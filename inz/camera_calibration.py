import numpy as np
import cv2




cap = cv2.VideoCapture(1)

while True:
    (grabbed, fr) = cap.read()

    dst = cv2.undistort(fr, mtx, dist, None, newcameramtx)

    # crop the image
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]
    # cv2.imwrite('calibresult.png', dst)

    cv2.imshow('frame', dst)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

cv2.destroyAllWindows()