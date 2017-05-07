from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import cv2
from inz.buoy import Buoy
from inz.frame import Frame
from inz.video_capture import Video
import matplotlib.pyplot as plt
import functools

captured_points = []
clicked = False

BINARY_FILENAME = 'binary.jpg'
DETECTED_FILENAME = 'detected.jpg'


class DoubleSlider(QGridLayout):
    """

    """
    _UPPER = "upper"
    _LOWER = "lower"

    def __init__(self, name):
        """

        :param name:
        """
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
        """

        :return:
        """
        slider = self.sender()
        if slider.objectName() == self._LOWER:
            self.lower_value.setText(str(slider.value()))
            self.upper_slider.setMinimum(slider.value())
        else:
            self.upper_value.setText(str(slider.value()))
            self.lower_slider.setMaximum(slider.value())

    def disable(self):
        """

        :return:
        """
        self.upper_slider.setEnabled(False)
        self.lower_slider.setEnabled(False)

    def enable(self):
        """

        :return:
        """
        self.upper_slider.setEnabled(True)
        self.lower_slider.setEnabled(True)

    def set_range(self, a, b):
        """

        :param a:
        :param b:
        :return:
        """
        self.lower_slider.setValue(a)
        self.upper_slider.setValue(b)

    def get_range(self):
        """

        :return:
        """
        return [self.lower_slider.value(), self.upper_slider.value()]


class SelectTemplate(QWidget):
    """ Select pattern to recognize on video.

    In this window user chooses photo taken before race, selects buoy and sets ranges on HSV color space.
    User should insert information about distance between him and buoy while photo was taken
    in order to calculate distance on video.
    """

    def __init__(self, yacht_coordinates, buoy_coordinates, calibration_coefficients):
        """ Object initializer.


        :param buttons_num:
        """
        super().__init__()

        self.yacht_coordinates = yacht_coordinates
        self.buoy_coordinates = buoy_coordinates
        self.calibration_coefficients = calibration_coefficients
        #
        buttons_num = 4
        #
        self.operations = []
        # Window title
        self.setWindowTitle("Wybieranie wzorca")
        # Path to photo with buoy to detect (template)
        self.image_path = ""
        #
        self.roi_selected_by_user = None
        # Distance from which photo was taken
        self.template_distance = 0
        # Main grid layout
        self.grid = QGridLayout()
        #
        self.current_state = 0
        # thi
        self.masks = []
        #
        hsv_ranges_label = QLabel()

        #
        self.range_auto_detect = QPushButton("Wykryj automatycznie")
        self.range_auto_detect.setStyleSheet("color: blue")
        self.range_auto_detect.clicked.connect(self.detect_colors)

        # List contains ranges of HSV color palette
        self.range_list = []
        self.range_text_edit = QTextEdit()
        self.current_text = ""
        self.range_text_edit.setReadOnly(True)

        # State handling buttons
        self.add_button = QPushButton(QIcon(QPixmap('../icons/add.png')), "")

        self.state_handling_buttons = [self.add_button]

        # Connect state handling buttons
        self.add_button.clicked.connect(self.on_add_button_clicked)

        # Morphological operation buttons
        erode_button = QPushButton("Erode")
        dilate_button = QPushButton("Dilate")
        open_button = QPushButton("Opening")
        close_button = QPushButton("Closing")

        self.morphological_operation_buttons = [erode_button, dilate_button, open_button, close_button]

        erode_button.clicked.connect(lambda: self.perform_morphological_operation('erosion', self.binary_image, 10))
        dilate_button.clicked.connect(lambda: self.perform_morphological_operation('dilation', self.binary_image, 10))
        open_button.clicked.connect(lambda: self.perform_morphological_operation('opening', self.binary_image, 10))
        close_button.clicked.connect(lambda: self.perform_morphological_operation('closing', self.binary_image, 10))

        morphological_operations_label = QLabel()

        self.selected_img_label = QLabel()
        self.template_image = QLabel()
        self.binary_img_label = QLabel()
        self.detected_buoy_img_label = QLabel()

        # blank image prepares empty space for images
        blank = QPixmap('img/blank.jpg')
        scaled_blank = blank.scaled(QSize(self.selected_img_label.size()), Qt.KeepAspectRatio, Qt.FastTransformation)

        blank_spaces = [[QLabel("Wzorzec"), self.selected_img_label],
                        [QLabel("Zaznaczona boja:"), self.template_image],
                        [QLabel("Po binaryzacji:"), self.binary_img_label],
                        [QLabel("Wykryta boja:"), self.detected_buoy_img_label]]

        for number, blank_space in enumerate(blank_spaces):
            self.set_widget(blank_space[0], blank_space[0].text(), self.grid, 0, number * 3, 1, 3)
            blank_space[1].setPixmap(scaled_blank)
            self.grid.addWidget(blank_space[1], 1, number * 3, 5, 3)

        self.hue = DoubleSlider("Hue")
        self.hue.set_range(165, 185)
        self.hue.upper_slider.setMaximum(360)
        self.saturation = DoubleSlider("Saturation")
        self.saturation.set_range(150, 250)
        self.value = DoubleSlider("Value")
        self.value.set_range(150, 250)

        #
        self.distance_label = QLabel()
        self.distance_label.hide()

        # User choose from which distance photo was taken
        self.distance_buttons = [QPushButton("{} m".format(num+1)) for num in range(buttons_num)]

        for num, button in enumerate(self.distance_buttons):
            button.hide()
            button.number = num + 1
            button.clicked.connect(self.distance_button_clicked)
            self.grid.addWidget(button, 11, num + 7)

        #
        self.explorer_button = QPushButton(QIcon(QPixmap('../icons/file_explorer.png')), "")
        self.explorer_button.clicked.connect(self.explorer_clicked)

        #
        self.detect_button = QPushButton(QIcon(QPixmap('../icons/play.png')), "")
        self.detect_button.clicked.connect(self.detect_clicked)
        self.detect_button.setMinimumHeight(140)

        self.grid.addWidget(self.explorer_button, 6, 5, 1, 4)
        self.grid.addWidget(self.detect_button, 6, 9, 3, 3)

        self.grid.addLayout(self.hue, 7, 0, 1, 3)
        self.grid.addLayout(self.saturation, 8, 0, 1, 3)
        self.grid.addLayout(self.value, 9, 0, 1, 3)

        self.grid.addWidget(self.range_text_edit, 7, 3, 3, 6)

        # Add morphological operation buttons to grid

        self.grid.addWidget(erode_button, 11, 3)
        self.grid.addWidget(dilate_button, 11, 4)
        self.grid.addWidget(open_button, 11, 5)
        self.grid.addWidget(close_button, 11, 6)

        # Add state handling buttons to grid
        self.grid.addWidget(self.add_button, 6, 3, 1, 2)

        #
        self.grid.addWidget(self.range_auto_detect, 10, 0, 1, 3)
        #
        self.set_widget(hsv_ranges_label, "Wybierz zasięg kolorów:", self.grid, 6, 0, 1, 3)
        self.set_widget(morphological_operations_label, "Operacje morfologiczne:", self.grid, 10, 3, 1, 4)
        self.set_widget(self.distance_label, "Dystans od boi", self.grid, 10, 7, 1, 4)

        self.setLayout(self.grid)
        self.before_photo_selection_state()
        self.show()

    # TODO: Document it

    def before_photo_selection_state(self):
        for button in self.state_handling_buttons + self.morphological_operation_buttons:
            button.setEnabled(False)
        # self.detect_button.setEnabled(False)
        self.range_auto_detect.setEnabled(False)
        self.hue.disable()
        self.saturation.disable()
        self.value.disable()

    def after_photo_selection_state(self):
        for button in self.morphological_operation_buttons:
            button.setEnabled(True)

        self.add_button.setEnabled(True)
        self.range_auto_detect.setEnabled(True)
        self.hue.enable()
        self.saturation.enable()
        self.value.enable()
        self.explorer_button.setEnabled(False)

    def distance_button_clicked(self):
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

    def detect_colors(self):
        hues = []
        saturations = []
        values = []
        copy = self.roi.copy()
        copy = cv2.cvtColor(copy, cv2.COLOR_BGR2HSV)
        r, c, _ = copy.shape

        for r in copy:
            for c in r:
                hues.append(c[0])
                saturations.append(c[1])
                values.append(c[2])
        plt.hist(hues, bins=255, histtype='step', color='red', label='Hue')
        plt.hist(saturations, bins=250, histtype='step', color='green', label='Saturation')
        plt.hist(values, bins=250, histtype='step', color='blue', label='Value')
        plt.show()

    @staticmethod
    def set_widget(label, text, layout, row, column, height, width):
        label.setText(text)
        font = QFont('Josefin Sans', 10, QFont.Normal)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(font)
        label.setStyleSheet("color: blue; border: 1px solid blue")
        layout.addWidget(label, row, column, height, width)

    def on_add_button_clicked(self):
        """ Function handles on add_button clicked event.

        Po kliknięciu w przycisk Add funkcja dodaje zakres kolorów do listy, a
        następnie wywołuje funkcję która korzystając z tego zakresu tworzy obraz binarny.

        :return:
        """

        # Lists declaration
        # Lower - minimum values of HSV components
        # Upper - maximum values of HSV components
        lower, upper = [], []

        # zamiana zasięgu każdego typu na listy zawierające tylko najmniejsze i tylko największe wartości
        # zasięg górny i dolny
        for i in [self.hue, self.saturation, self.value]:
            lower.append(i.get_range()[0])
            upper.append(i.get_range()[1])

        # add new range to list of all ranges
        self.range_list.append([lower, upper])
        # create new text with new data on the end
        self.current_text = "Hue: ({}, {}) Saturation ({}, {}) Value ({}, {})\n".format(lower[0], upper[0],
                                                                                        lower[1], upper[1],
                                                                                        lower[2], upper[2])
        # w tym tekscie znajdują się informacje o zmianach w obrazie binarnym
        self.range_text_edit.setText(self.range_text_edit.toPlainText() + self.current_text)

        # binaryzacja obrazu kolory na obrazie poza zakresem będą czarne, a z zakresu białe
        self.binary_image.in_range([[lower, upper]])

        # jeżeli stan jest rózny od zera to znaczy że była więcej niż jedna zmiana
        # nowa maska jest tworzona z logicznej alternatywy maski poprzedniej i obecnej
        if self.current_state != 0:
            new_mask = cv2.bitwise_or(self.masks[self.current_state - 1], self.binary_image.mask)
            self.binary_image.mask = new_mask
        # jeżeli nie było wprowadzonych żadnych zmian to teraźniejsza maska staje się nową
        else:
            new_mask = self.binary_image.mask

        # lista zawierająca historię zmian
        self.masks.append(new_mask)
        # Add mask to masks list
        self.current_state += 1

        # zapisywanie do pliku obrazu binarnego i obrazu z wykrytą boją
        cv2.imwrite(BINARY_FILENAME, new_mask)
        # cv2.imwrite(DETECTED_FILENAME, self.binary_image.image)
        self.detect_object_on_photo()
        # wywyoływanie funkcji wyświetlającej zapisane obrazy na ekranie
        self.binary_image.image = self.original.copy()
        self.refresh_image(BINARY_FILENAME, self.binary_img_label)
        # self.refresh_image(DETECTED_FILENAME, self.detected_buoy_img_label)
        #
        if self.current_state > 2:
            self.add_button.setEnabled(False)

    def detect_object_on_photo(self):
        binary_buoy = Buoy()
        #
        binary_buoy.detect(self.binary_image, False)
        #
        cv2.imwrite(DETECTED_FILENAME, self.binary_image.image)
        #
        self.refresh_image(DETECTED_FILENAME, self.detected_buoy_img_label)

    def perform_morphological_operation(self, operation_type, image, kernel_size, iterations=1):
        """ Wykonaj wybraną operację morfologiczną na dostarczonym obrazie binarnym.

        Funkcja wykonuje operację morfologiczną na obrazie binarnym przekazanym w parametrze.
        Zapisuje informację o przeprowadzonej informacji w polu tekstowym widocznym na ekranie.
        Wyświetla obraz PO przeprowadzonej operacji, a następnie wywołuje funkcję, która
        wykryje obiekt za pomocną nowego obrazu binarnego.

        :param operation_type: jeden z czterech dostępnych operacji morfologicznych
        :param image: obraz binarny
        :param kernel_size: rozmiar kernela
        :param iterations: liczba iteracji (domyślnie 1)
        :return:
        """
        # słownik zawierający nazwę operacji -> funkcją wykonująca tę operację
        types_dict = {'erosion': image.erode, 'dilation': image.dilate,
                      'opening': image.opening, 'closing': image.closing}

        # słownik zawierający nazwe operacji -> funkcja wykonująca tę operację
        # utworzony w celu zapamiętania operacji przeprowadzonej na wzorcu i odtworzenia
        # tych samych operacji na każdej klatce obrazu z kamery
        video_types_dict = {'erosion': self.binary_image.erode, 'dilation': self.binary_image.dilate,
                            'opening': self.binary_image.opening, 'closing': self.binary_image.closing}
        # zapisywanie informacji do pola tekstowego
        self.range_text_edit.setText(str(self.range_text_edit.toPlainText() + operation_type.capitalize() + "\n"))
        # liczba przeprowadzonych operacji na obrazie wzrasta o 1
        self.current_state += 1
        # wywołanie funkcji ze słownika
        types_dict[operation_type](kernel_size, iterations)
        # dodaj przeprowadzoną operację do listy
        operation = functools.partial(video_types_dict[operation_type], kernel_size)
        self.operations.append(operation)
        # zapisanie nowego obrazu binarnego do pliku
        cv2.imwrite(BINARY_FILENAME, self.binary_image.mask)
        # wyświetlenie nowego obrazu binarnego na ekranie
        self.refresh_image(BINARY_FILENAME, self.binary_img_label)
        # oryginalny obraz (bez narysowanych okręgów) jako obraz na którym będą rysowane okręgi (miejsca wykrycia obiektu)
        self.binary_image.image = self.original.copy()
        # wywołanie funkcji wykrywającej obiekt na nowym obrazie binarnym
        self.detect_object_on_photo()

    def refresh_image(self, filename, label):
        """ Funkcja wyświetla nowy obraz binarny na ekranie.

        Funckja wczytuje obraz binarny z pliku, zmienia jego rozmiary aby pasowały do pola
        przeznaczonego na obraz, a następnie umieszcza ten obraz w polu.
        :return:
        """

        # stworzenie obiektu QPixmap rpzechowyjącego obraz binarny
        bin = QPixmap(filename)
        # skalowanie obrazu
        scaled_image = bin.scaled(QSize(self.selected_img_label.size()), Qt.KeepAspectRatio, Qt.FastTransformation)
        # ustawianie obrazu na etykiecie
        label.setPixmap(scaled_image)

    @staticmethod
    def crop_template(filename):
        """ Zaznacza obszar wybrany przez użytkownika.

        Funkcja pomaga wyodrębnić boję na zdjęciu.
        Zwraca zaznaczony obszar.
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

        image = cv2.imread(filename)
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

    def explorer_clicked(self):
        """ Obsługa przycisku "explorer button".

        Po przyciśnięciu na przycisk otwierane jest okno dialogowe do wybrania pliku.
        Plik to zdjęcie boi zrobione z określonej odległości.
        """

        # select file
        dialog = QFileDialog()
        self.image_path = dialog.getOpenFileName(self, 'Wybierz zdjęcie', os.getenv('HOME/img'), 'JPG(*.jpg)')

        # split path to extract filename
        path, file = os.path.split(self.image_path[0])

        self.original = cv2.imread(file)
        copy = self.original.copy()
        # crop field selected by user and save it to variable roi
        self.roi = self.crop_template(file)
        cv2.cvtColor(self.roi, cv2.COLOR_BGR2HSV)
        # wycinek zaznaczony przez użytkownika
        roi_width, roi_heigth, _ = self.roi.shape
        self.roi_selected_by_user = Buoy(width=roi_width, height=roi_heigth)

        cv2.imwrite('roi.jpg', self.roi)
        cropped_buoy = QPixmap('roi.jpg')

        scaled_image = cropped_buoy.scaled(QSize(self.selected_img_label.size()), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.template_image.setPixmap(scaled_image)
        self.photo = QPixmap(self.image_path[0])
        self.scaled_photo = self.photo.scaled(QSize(self.selected_img_label.size()), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.selected_img_label.setPixmap(self.scaled_photo)

        self.binary_image = Frame(copy)

        self.binary_image.blur()
        self.binary_image.in_range([[[0, 0, 0], [0, 0, 0]]])

        self.masks.append(self.binary_image.mask)
        self.current_state += 1
        for button in self.distance_buttons:
            button.show()

        self.distance_label.show()
        self.after_photo_selection_state()

    def detect_clicked(self):
        """ Funkcja obsłuująca wciśnięcie przycisku 'Start'.

        Funkcja rozpoczyna przetwarzanie obrazu dostarczonego z wybranego źródłą (kamery internetowej lub
        nagrania wideo).
        """

        buoy = Buoy(distance=self.template_distance)

        buoy.set_size(self.roi_selected_by_user.height)
        buoy.ranges = self.range_list
        video = Video(1, self.operations,
                      self.yacht_coordinates, self.buoy_coordinates, self.calibration_coefficients)

        video.capture(self.binary_image, buoy)
        video.clean()

        cv2.waitKey(0)
        cv2.destroyAllWindows()
