import urllib.request
import cv2
import os
import numpy as np
import imutils
from subprocess import call


def store_raw_images(directory, url, color=cv2.IMREAD_GRAYSCALE, size=(400, 400)):
    neg_images_link = url
    neg_image_urls = urllib.request.urlopen(neg_images_link).read().decode()
    pic_num = 1
    if not os.path.exists(directory):
        os.makedirs(directory)

    for i in neg_image_urls.split('\n'):
        try:
            print(i)
            urllib.request.urlretrieve(i, directory + "/" + str(pic_num) + ".jpg")
            img = cv2.imread(directory + "/" + str(pic_num) + ".jpg", color)
            resized_image = cv2.resize(img, size)
            cv2.imwrite(directory + "/" + str(pic_num) + ".jpg", resized_image)
            pic_num += 1

        except Exception as e:
            print(str(e))


def change_size(old_path, new_path, image_num=0):
    for subdir, dirs, files in os.walk(old_path):
        for file in files:
            image = cv2.imread(os.path.join(subdir, file))
            # resized = imutils.resize()
            resized = cv2.resize(image, (27, 46))
            image_num += 1
            cv2.imwrite(new_path + '/image{}.jpg'.format(image_num), resized)
    cv2.destroyAllWindows()


def video_to_images(video_path, directory):
    cap = cv2.VideoCapture(video_path)
    frame_num = 0

    while True:
        ret, frame = cap.read()
        frame = imutils.resize(frame, width=400)
        frame = imutils.rotate(frame, 270)
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1) and 0xFF
        if key == ord('q'):
            break

        frame_num += 1
        if frame_num % 5 == 0:
            cv2.imwrite(directory + "/buoy{}.jpg".format(frame_num), frame)
    cap.release()
    cv2.destroyAllWindows()


def create_negatives(directories):
    image_number = 0
    text = ""
    for directory in directories:
        for subdir, dirs, files in os.walk(directory):
            for file in files:
                image_number += 1
                image = cv2.imread(os.path.join(subdir, file))
                cv2.imwrite('../negative/image{}.jpg'.format(image_number), image)
                text += 'negative/image{}.jpg\n'.format(image_number)

    with open('../negative.txt', 'w') as file:
        file.write(text)
    cv2.destroyAllWindows()


def is_correct(file):
    with open(file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        words = line.split()
        image = cv2.imread("../" + words[0])

        y1 = int(words[3])
        y2 = y1 + int(words[5])

        x1 = int(words[2])
        x2 = x1 + int(words[4])

        roi = image[y1:y2, x1:x2]
        cv2.imshow('image', roi)
        cv2.imshow('org', image)
        cv2.waitKey(0)
    cv2.destroyAllWindows()


def change_color(directory, new_directory, new_color):
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            image = cv2.imread(file)
            gray = cv2.cvtColor(image, new_color)
            cv2.imwrite(new_directory + "/" + file, gray)

def find_uglies():
    match = False
    for file_type in ['folder']:
        for img in os.listdir(file_type):
            for ugly in os.listdir('uglies'):
                try:
                    current_image_path = str(file_type) + '/' + str(img)
                    ugly = cv2.imread('uglies/' + str(ugly))
                    question = cv2.imread(current_image_path)
                    if ugly.shape == question.shape and not (np.bitwise_xor(ugly, question).any()):
                        print('That is one ugly pic! Deleting!')
                        print(current_image_path)
                        os.remove(current_image_path)
                except Exception as e:
                    print(str(e))


def rotate_wideo(path_to_video):
    cap = cv2.VideoCapture(path_to_video)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    vw = cv2.VideoWriter('boja.avi', fourcc, 20.0, (1920, 1080))
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_r = imutils.rotate(frame, 270)
        # cv2.imshow('Frame', frame_r)
        vw.write(frame_r)


def cut_object(input_directory, output_directory):
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

    image_num = 0
    for subdir, dirs, files in os.walk(input_directory):
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
            roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
            print(output_directory + '/image{}.jpg'.format(image_num))
            cv2.imwrite(output_directory + '/image{}.jpg'.format(image_num), roi)


def rename(input_directory,output_directory):
    image_num = 0
    for subdir, dirs, files in os.walk(input_directory):
        for file in files:
            for i in range(13):
                image_num += 1
                image = cv2.imread(os.path.join(subdir, file))
                cv2.imwrite(output_directory + '/image{}.jpg'.format(image_num), image)

def cut_black_bars(video_path):
    cap = cv2.VideoCapture(video_path)
    out_directory = 'boja.avi'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(out_directory, fourcc, 20.0, (1920, 1080))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        width, height = frame.shape[:-1]
        print(height - width)
        roi = frame[]
        cv2.imshow('roi', roi)
        out.write(roi)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

cut_black_bars('../inz/boja_n.mp4')
dirs = ['folder1', 'folder2', 'folder3', 'folder4', '../negatives']
# create_negatives(dirs)
# rotate_wideo('../video/boja.mp4')
# change_size('../red_boja', '../zdj_boji')
# cut_object('../red_boja', '../red_boja_cut')
# rename('../negative', '../negative2')
# img = cv2.imread('buoy.jpg', cv2.IMREAD_GRAYSCALE)
# cv2.imwrite('buoygray.jpg', img)
# video_to_images('../bojared_fullhd.mp4', '../red_boja')
# find_uglies()
# store_raw_images('folder4', 'http://image-net.org/api/text/imagenet.synset.geturls?wnid=n00017222')