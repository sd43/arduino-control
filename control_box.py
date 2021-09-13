from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator

class SliderControl(QWidget):
    def __init__(self, low=0, high=100, parent=None):
        super(SliderControl, self).__init__(parent)

        layout = QHBoxLayout()
        layout.addWidget(QLabel(str(low)))

        slider = QSlider(orientation=Qt.Horizontal)
        slider.setMinimum(low)
        slider.setMaximum(high)
        layout.addWidget(slider, stretch=4)

        layout.addWidget(QLabel(str(high)))

        textEdit = QLineEdit()
        textEdit.setValidator(QIntValidator(low, high))
        layout.addWidget(textEdit, stretch=1)

        textEdit.setText(str(slider.value()))

        slider.valueChanged.connect(lambda value: None if textEdit.text() == str(value) else textEdit.setText(str(value)))
        textEdit.returnPressed.connect(lambda: slider.setValue(int(textEdit.text())))

        self.setLayout(layout)

class SwitchControl(QWidget):
    def __init__(self, parent=None):
        super(SwitchControl, self).__init__(parent)

        layout = QHBoxLayout()

        self.button = QPushButton()
        self.button.setCheckable(True)
        self.button.toggled.connect(lambda checked: self.updateLabel())
        layout.addWidget(self.button)

        self.updateLabel()
        self.setLayout(layout)

    def updateLabel(self):
        checked = self.button.isChecked()
        self.button.setText('ON' if checked else 'OFF')
        self.button.setStyleSheet('background-color: "red"' if checked else 'background-color: "grey"')


class ControlWidget(QWidget):
    def __init__(self, controlConfig, parent=None):
        super(ControlWidget, self).__init__(parent)

        c = controlConfig

        layout = QVBoxLayout()

        header = QHBoxLayout()
        header.addWidget(QLabel('<b>' + c.name + '</b>'))
        layout.addLayout(header)

        w = None
        # TODO handle signals
        if c.controlType == 'analogOutput':
            w = SliderControl(low=c.min or 0, high=c.max or 255)
        elif c.controlType == 'digitalOutput':
            button = SwitchControl()
            w = button
        else:
            raise Exception('Unsupported control type {}'.format(c.type))

        layout.addWidget(w)
        self.setLayout(layout)
        

class ControlBox(QWidget):
    def __init__(self, config=None, columns=3, parent=None):
        super(ControlBox, self).__init__(parent)
        self.config = config

        self.layout = QGridLayout()
        self.controlWidgets = [ ControlWidget(c) for c in self.config ]

        for i in range(len(self.controlWidgets)):
            row = i // columns
            column = i % columns

            self.layout.addWidget(self.controlWidgets[i], row, column)

        self.setLayout(self.layout)

