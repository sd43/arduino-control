from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

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
            slider = QSlider(orientation=Qt.Horizontal)
            slider.setMinimum(c.min or 0)
            slider.setMaximum(c.max or 255)
            w = slider
        elif c.controlType == 'digitalOutput':
            button = QPushButton()
            button.setCheckable(True)
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



