from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys, os, cv2
from inz.buoy import Buoy
from inz.frame import Frame
from inz.video_capture import Video


class SelectTemplate(QWidget):
    def __init__(self, buttons_num):
        super().__init__()
        self.setWindowTitle("Wybieranie wzorca")
        self.image_path = ""
        self.label = QLabel()
        self.template_distance = 0

        self.distance_v_layout = QVBoxLayout()
        distance_buttons_layout = QHBoxLayout()

        self.distance_buttons = [QPushButton("{} m".format(num+1)) for num in range(buttons_num)]

        for num, button in enumerate(self.distance_buttons):
            button.hide()
            button.number = num + 1
            button.clicked.connect(self.button_clicked)
            distance_buttons_layout.addWidget(button)

        self.distance_label = QLabel("DYSTANS OD BOJI")
        self.distance_label.hide()

        font = QFont('Josefin Sans', 10, QFont.Normal)
        self.distance_label.setFont(font)

        self.distance_v_layout.addWidget(self.distance_label)
        self.distance_v_layout.addLayout(distance_buttons_layout)

        v_box_layout = QVBoxLayout()
        h_box_layout = QHBoxLayout()

        explorer_button = QPushButton(QIcon(QPixmap('../icons/file_explorer.png')), "")
        explorer_button.clicked.connect(self.explorer_clicked)

        detect_button = QPushButton("Wykryj")
        detect_button.clicked.connect(lambda: self.detect_clicked(self.image_path[0]))

        image = QPixmap('blank.jpg')
        scaled_image = image.scaled(QSize(self.label.size()), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.label.setPixmap(scaled_image)

        h_box_layout.addWidget(explorer_button)
        h_box_layout.addWidget(detect_button)

        v_box_layout.addWidget(self.label)
        v_box_layout.addLayout(self.distance_v_layout)
        v_box_layout.addLayout(h_box_layout)

        self.setLayout(v_box_layout)
        self.show()

    def button_clicked(self):
        sender = self.sender()
        for button in self.distance_buttons:
            if button.number == sender.number:
                button.setEnabled(False)
            else:
                button.setEnabled(True)

        self.template_distance = sender.number

    def explorer_clicked(self):
        dialog = QFileDialog()
        self.image_path = dialog.getOpenFileName(self, 'Wybierz zdjęcie', os.getenv('HOME'), 'JPG(*.jpg)')
        image = QPixmap(self.image_path[0])
        scaled_image = image.scaled(QSize(self.label.size()), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.label.setPixmap(scaled_image)

        for button in self.distance_buttons:
            button.show()

        self.distance_label.show()

    def detect_clicked(self, path):
        path, file = os.path.split(path)
        temp = cv2.imread(file)

        template = Frame(temp)
        template.blur()
        template.in_range()
        template.closing(10, 5)

        buoy = Buoy(self.template_distance)
        buoy.detect(template)

        video = Video('boja_n.mp4')
        self.hide()

        video.capture(buoy)
        video.clean()

        # cv2.imshow('image', template.image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


class ThreadClass(QThread):

    sig = pyqtSignal(int)

    def __init__(self, parent=None):
        super(ThreadClass, self).__init__(parent)
        self.sig.connect

app = QApplication(sys.argv)
w = SelectTemplate(4)
sys.exit(app.exec_())

