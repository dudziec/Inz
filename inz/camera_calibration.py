import numpy as np
import cv2
import glob

# kryteria wykonania
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# przygotuj punkty obiektu, jak np (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((7*9, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:7].T.reshape(-1, 2)

# Tablice do przechowywania punktów obiektu i punktów obrazu ze wszystkich zdjęć.

objpoints = []  # punkty 3d ze świata rzeczywistego
imgpoints = []  # punkty 2d na płaszczyźnie obrazu

images = ["coordination_images/image" + str(i) + ".jpg" for i in range(1, 13)]

print(images)

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow('gray', gray)
    # Znajdź wierzchołki szachownicy
    ret, corners = cv2.findChessboardCorners(gray, (9, 7), None)
    # Jeżeli znaleziono, dodaj punkty obiektu, punkty obrazu (po zwiększeniu przybliżenia)
    if ret:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        print("Before show")
        img = cv2.drawChessboardCorners(img, (9, 7), corners2, ret)
        cv2.imshow('img', img)

    cv2.waitKey(500)

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print(ret, mtx, dist, rvecs, tvecs)


cv2.destroyAllWindows()
