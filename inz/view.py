from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os, sys
import cv2
from inz.buoy import Buoy
from inz.frame import Frame
from inz.video_capture import Video

captured_points = []
clicked = False


class DoubleSlider(QGridLayout):
    _UPPER = "upper"
    _LOWER = "lower"

    def __init__(self, name):
        super().__init__()

        self.lower_label = QLabel("Lower {}".format(name))
        self.lower_slider = QSlider(Qt.Horizontal)
        self.lower_value = QLabel("0")

        self.upper_label = QLabel("Upper {}".format(name))
        self.upper_slider = QSlider(Qt.Horizontal)
        self.upper_value = QLabel("255")

        self.lower_slider.setValue(0)
        self.lower_slider.setRange(0, 255)
        self.lower_slider.setObjectName(self._LOWER)
        self.lower_slider.valueChanged.connect(self.value_changed)

        self.upper_slider.setRange(0, 255)
        self.upper_slider.setValue(255)
        self.upper_slider.setObjectName(self._UPPER)
        self.upper_slider.valueChanged.connect(self.value_changed)

        self.addWidget(self.lower_label, 0, 0)
        self.addWidget(self.lower_slider, 1, 0)
        self.addWidget(self.lower_value, 1, 1)
        self.addWidget(self.upper_label, 0, 2)
        self.addWidget(self.upper_slider, 1, 2)
        self.addWidget(self.upper_value, 1, 3)

    def value_changed(self):
        slider = self.sender()
        if slider.objectName() == self._LOWER:
            self.lower_value.setText(str(slider.value()))
            self.upper_slider.setMinimum(slider.value())
        else:
            self.upper_value.setText(str(slider.value()))
            self.lower_slider.setMaximum(slider.value())

    def get_range(self):
        return [self.lower_slider.value(), self.upper_slider.value()]


class SelectTemplate(QWidget):
    """ Select pattern to recognize on video.

    In this window user chooses photo taken before race, selects buoy and sets ranges on HSV color space.
    User should insert information about distance between him and buoy while photo was taken
    in order to calculate distance on video.
    """

    def __init__(self, buttons_num):
        """ Object initializer.


        :param buttons_num:
        """
        super().__init__()

        # Window title
        self.setWindowTitle("Wybieranie wzorca")

        # Path to photo with buoy to detect (template)
        self.image_path = ""

        # Distance from which photo was taken
        self.template_distance = 0

        # List contains ranges of HSV color palette
        self.range_list = []
        self.range_label = QTextEdit()
        self.range_label.setEnabled(False)

        self.selected_img_label = QLabel()
        self.template_image = QLabel()
        self.binary_img_label = QLabel()
        self.detected_buoy_img_label = QLabel()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_binary_image)

        # blank image prepares empty space for images
        blank = QPixmap('img/blank.jpg')
        scaled_blank = blank.scaled(QSize(self.selected_img_label.size()), Qt.KeepAspectRatio, Qt.FastTransformation)

        #
        img_labels = [self.selected_img_label, self.template_image, self.binary_img_label, self.detected_buoy_img_label]

        #
        for image in img_labels:
            image.setPixmap(scaled_blank)

        self.hue = DoubleSlider("Hue")
        self.hue.upper_slider.setMaximum(360)
        self.saturation = DoubleSlider("Saturation")
        self.value = DoubleSlider("Value")

        # Layout contains label and photo taken before race
        photo_v_box_layout = QVBoxLayout()

        # Layout contains label and buoy selected on selected_image by user
        template_v_box_layout = QVBoxLayout()

        # Layout containts label and binary image of buoy
        binary_v_box_layout = QVBoxLayout()

        # Layout contains label and image of buoy detected on image
        detected_v_box_layout = QVBoxLayout()

        horizontal_layouts_wrapper = QHBoxLayout()

        self.distance_v_layout = QVBoxLayout()
        distance_buttons_layout = QHBoxLayout()

        self.distance_buttons = [QPushButton("{} m".format(num+1)) for num in range(buttons_num)]

        for num, button in enumerate(self.distance_buttons):
            button.hide()
            button.number = num + 1
            button.clicked.connect(self.button_clicked)
            distance_buttons_layout.addWidget(button)

        self.distance_label = QLabel("DYSTANS OD BOI")
        self.distance_label.hide()

        self.template_label = QLabel("Zaznaczona boja:")
        self.photo_label = QLabel("Wzorzec:")
        self.binary_label = QLabel("Po binaryzacji:")
        self.detected_label = QLabel("Wykryta boja:")

        font = QFont('Josefin Sans', 10, QFont.Normal)
        self.distance_label.setFont(font)

        self.distance_v_layout.addWidget(self.distance_label)
        self.distance_v_layout.addLayout(distance_buttons_layout)
        self.distance_v_layout.addWidget(self.refresh_button)
        self.distance_v_layout.addWidget(self.range_label)

        v_box_layout = QVBoxLayout()
        h_box_layout = QHBoxLayout()

        explorer_button = QPushButton(QIcon(QPixmap('../icons/file_explorer.png')), "")
        explorer_button.clicked.connect(self.explorer_clicked)

        detect_button = QPushButton("Wykryj")
        detect_button.clicked.connect(lambda: self.detect_clicked(self.image_path[0]))

        self.selected_img_label.setPixmap(scaled_blank)

        self.template_image.setPixmap(scaled_blank)

        h_box_layout.addWidget(explorer_button)
        h_box_layout.addWidget(detect_button)

        photo_v_box_layout.addWidget(self.photo_label)
        photo_v_box_layout.addWidget(self.selected_img_label)

        template_v_box_layout.addWidget(self.template_label)
        template_v_box_layout.addWidget(self.template_image)

        binary_v_box_layout.addWidget(self.binary_label)
        binary_v_box_layout.addWidget(self.binary_img_label)

        detected_v_box_layout.addWidget(self.detected_label)
        detected_v_box_layout.addWidget(self.detected_buoy_img_label)

        horizontal_layouts_wrapper.addLayout(photo_v_box_layout)
        horizontal_layouts_wrapper.addLayout(template_v_box_layout)
        horizontal_layouts_wrapper.addLayout(binary_v_box_layout)
        horizontal_layouts_wrapper.addLayout(detected_v_box_layout)

        v_box_layout.addLayout(horizontal_layouts_wrapper)
        v_box_layout.addLayout(self.hue)
        v_box_layout.addLayout(self.saturation)
        v_box_layout.addLayout(self.value)
        v_box_layout.addLayout(self.distance_v_layout)
        v_box_layout.addLayout(h_box_layout)

        self.setLayout(v_box_layout)
        self.show()

    # TODO: Document and understand !

    def button_clicked(self):
        """

        :return:
        """
        sender = self.sender()
        for button in self.distance_buttons:
            if button.number == sender.number:
                button.setEnabled(False)
            else:
                button.setEnabled(True)

        self.template_distance = sender.number

    def refresh_binary_image(self):
        lower, upper = [], []
        path, file = os.path.split(self.image_path[0])
        img = cv2.imread(file)
        fr = Frame(img)
        filename = 'binary.jpg'
        for i in [self.hue, self.saturation, self.value]:
            lower.append(i.get_range()[0])
            upper.append(i.get_range()[1])

        self.range_list.append([lower, upper])
        text = self.range_label.toPlainText()
        new_txt = str(text) + "Hue: ({}, {}) Saturation ({}, {}) Value ({}, {})\n".format(lower[0], upper[0], lower[1], upper[1], lower[2], upper[2])
        self.range_label.setText(new_txt)
        fr.blur()
        fr.in_range(lower, upper)
        fr.closing(10, 5)

        cv2.imwrite(filename, fr.mask)
        buoy = Buoy()
        buoy.detect(fr)
        height, width, channel = fr.image.shape
        bytesPerLine = 3 * width
        qimg = QImage(fr.image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        # cv2.imwrite('det.jpg', fr.image)
        det = QPixmap(qimg)

        sc_det = det.scaled(QSize(self.selected_img_label.size()), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.detected_buoy_img_label.setPixmap(sc_det)
        bin = QPixmap(filename)
        scaled_image = bin.scaled(QSize(self.selected_img_label.size()), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.binary_img_label.setPixmap(scaled_image)



    def crop_template(self, path):
        """Marks area selected by user.

        This function helps extract buoy on image and separate it from the background.
        """

        def mouse_handler(event, x, y, flags=None, param=None):
            global clicked
            global captured_points
            clone = image.copy()

            if event == cv2.EVENT_LBUTTONDOWN:
                captured_points = [(x, y)]
                clicked = True

            if event == cv2.EVENT_LBUTTONUP:
                if clicked:
                    captured_points.append((x, y))
                    cv2.rectangle(image, captured_points[0], captured_points[1], (0, 255, 0), 1)
                clicked = False

            if event == cv2.EVENT_MOUSEMOVE:
                if clicked:
                    clone = image.copy()
                    cv2.rectangle(clone, captured_points[0], (x, y), (0, 255, 0), 1)
                cv2.imshow("image", clone)

        path, file = os.path.split(path)
        image = cv2.imread(file)
        cv2.imshow('image', image)
        clone = image.copy()
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", mouse_handler)
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('n'):
                cv2.destroyWindow('image')
                break

            if key == ord("r"):
                image = clone.copy()

        roi = clone[captured_points[0][1]:captured_points[1][1], captured_points[0][0]:captured_points[1][0]]

        return roi

    # TODO: Document and understand it!

    def explorer_clicked(self):
        """
        :return:
        """
        dialog = QFileDialog()
        self.image_path = dialog.getOpenFileName(self, 'Wybierz zdjęcie', os.getenv('HOME/img'), 'JPG(*.jpg)')
        roi = self.crop_template(self.image_path[0])
        retval = cv2.imwrite('roi.jpg', roi)

        cropped_buoy = QPixmap('roi.jpg')
        scaled_image = cropped_buoy.scaled(QSize(self.selected_img_label.size()), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.template_image.setPixmap(scaled_image)

        self.photo = QPixmap(self.image_path[0])
        self.scaled_photo = self.photo.scaled(QSize(self.selected_img_label.size()), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.selected_img_label.setPixmap(self.scaled_photo)

        for button in self.distance_buttons:
            button.show()

        self.distance_label.show()

    def detect_clicked(self, path):
        """

        :param path:
        :return:
        """

        path, file = os.path.split(path)
        temp = cv2.imread(file)

        template = Frame(temp)
        template.blur()
        template.in_range()
        template.closing(10, 5)

        buoy = Buoy(self.template_distance)
        buoy.detect(template)
        cv2.imshow('temp', template.image)

        video = Video('C:/Users/dudziec/PycharmProjects/Inżynierka/inz/img/boja_n.mp4')

        video.capture(buoy)
        video.clean()

        cv2.waitKey(0)
        cv2.destroyAllWindows()


app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
w = SelectTemplate(4)
app.exec_()
