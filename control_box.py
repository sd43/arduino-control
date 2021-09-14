from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator

from control import AnalogOutputControl, DigitalOutputControl

class Slider(QWidget):
    def __init__(self, control, low=0, high=100, parent=None):
        super(Slider, self).__init__(parent)

        layout = QHBoxLayout()
        layout.addWidget(QLabel(str(low)))

        self.slider = QSlider(orientation=Qt.Horizontal)
        self.slider.setMinimum(low)
        self.slider.setMaximum(high)
        self.slider.setTracking(False)
        layout.addWidget(self.slider, stretch=4)

        layout.addWidget(QLabel(str(high)))

        self.textEdit = QLineEdit()
        self.textEdit.setValidator(QIntValidator(low, high))
        layout.addWidget(self.textEdit, stretch=1)

        self.textEdit.setText(str(self.slider.value()))

        self.slider.valueChanged.connect(self.sliderValueChangedCallback)
        self.textEdit.returnPressed.connect(lambda: self.slider.setValue(int(self.textEdit.text())))

        self.setLayout(layout)

        self.control = control
        self.control.addOnChangeCallback(lambda value: self.slider.setValue(int(value)))

    def sliderValueChangedCallback(self, value):
        if self.textEdit.text() != str(value):
            self.textEdit.setText(str(value))

        self.control.setValue(value)

class Switch(QWidget):
    def __init__(self, control, parent=None):
        super(Switch, self).__init__(parent)

        self.control = control

        layout = QHBoxLayout()

        self.button = QPushButton()
        self.button.setCheckable(True)
        self.button.toggled.connect(lambda checked: self.onToggleCallback(checked))
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.control.addOnChangeCallback(self.onChangeCallback)

    def onToggleCallback(self, checked):
        self.control.setOn(checked)

    def onChangeCallback(self, value):
        on = value != 0
        if on:
            self.button.setChecked(True)
            self.button.setText('ON ({})'.format(value))
            self.button.setStyleSheet('background-color: "red"')
        else:
            self.button.setChecked(False)
            self.button.setText('OFF ({})'.format(value))
            self.button.setStyleSheet('background-color: "grey"')

class ControlWidget(QWidget):
    def __init__(self, controlConfig, controller, parent=None):
        super(ControlWidget, self).__init__(parent)

        c = controlConfig

        layout = QVBoxLayout()

        header = QHBoxLayout()
        header.addWidget(QLabel('<b>' + c.name + '</b>'))
        layout.addLayout(header)

        w = None
        # TODO handle signals
        if c.controlType == 'analogOutput':
            control = AnalogOutputControl(c, controller)
            w = Slider(low=c.min or 0, high=c.max or 255, control=control)
        elif c.controlType == 'digitalOutput':
            control = DigitalOutputControl(c, controller)
            button = Switch(control)
            w = button
        else:
            raise Exception('Unsupported control type {}'.format(c.type))

        layout.addWidget(w)
        self.setLayout(layout)
        

class ControlBox(QWidget):
    def __init__(self, config, controller, columns=3, parent=None):
        super(ControlBox, self).__init__(parent)
        self.config = config
        self.controller = controller

        layout = QGridLayout()
        self.controlWidgets = [ ControlWidget(c, controller) for c in self.config ]

        for i in range(len(self.controlWidgets)):
            row = i // columns
            column = i % columns

            layout.addWidget(self.controlWidgets[i], row, column)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(layout)
        self.mainLayout.addStretch(1)
        self.setLayout(self.mainLayout)

