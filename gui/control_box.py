from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator

from comm.control import AnalogOutputControl, DigitalOutputControl

class Slider(QWidget):
    def __init__(self, control, low=0, high=100, parent=None):
        super(Slider, self).__init__(parent)

        self.control = control

        layout = QHBoxLayout()
        layout.addWidget(QLabel(str(low)))

        self.slider = QSlider(orientation=Qt.Horizontal)
        self.slider.setMinimum(low)
        self.slider.setMaximum(high)
        layout.addWidget(self.slider, stretch=4)

        layout.addWidget(QLabel(str(high)))

        self.textEdit = QLineEdit()
        self.textEdit.setValidator(QIntValidator(low, high))
        layout.addWidget(self.textEdit, stretch=1)

        self.textEdit.setText(str(self.slider.value()))

        # value of the underlying control is only changed on these events
        self.slider.sliderReleased.connect(self.sliderReleasedCallback)
        self.textEdit.returnPressed.connect(self.returnPressedCallback)

        # these events only trigger updation of the UI
        self.slider.sliderPressed.connect(self.sliderMovedCallback)
        self.slider.sliderMoved.connect(self.sliderMovedCallback)
        self.slider.valueChanged.connect(self.sliderMovedCallback)

        self.setLayout(layout)

        self.control.addOnChangeCallback(lambda value: self.slider.setValue(int(value)))

    def returnPressedCallback(self):
        value = int(self.textEdit.text())
        self.slider.setValue(value)
        self.control.setValue(value)

    def sliderMovedCallback(self):
        value = self.slider.sliderPosition()
        if self.textEdit.text() != str(value):
            self.textEdit.setText(str(value))

    def sliderReleasedCallback(self):
        value = self.slider.sliderPosition()
        self.control.setValue(value)
        self.sliderMovedCallback()

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
    def __init__(self, control, parent=None):
        super(ControlWidget, self).__init__(parent)

        layout = QVBoxLayout()

        header = QHBoxLayout()
        header.addWidget(QLabel('<b>' + control.control.name + '</b>'))
        layout.addLayout(header)

        w = None
        c = control.control
        # TODO handle signals
        if control.control.controlType == 'analogOutput':
            w = Slider(low=c.min or 0, high=c.max or 255, control=control)
        elif control.control.controlType == 'digitalOutput':
            button = Switch(control)
            w = button
        else:
            raise Exception('Unsupported control type {}'.format(control.type))

        layout.addWidget(w)
        self.setLayout(layout)
        

class ControlBox(QWidget):
    def __init__(self, controls, columns=3, parent=None):
        super(ControlBox, self).__init__(parent)
        self.controls = controls

        layout = QGridLayout()
        self.controlWidgets = [ ControlWidget(control) for control in controls ]

        for i in range(len(self.controlWidgets)):
            row = i // columns
            column = i % columns

            layout.addWidget(self.controlWidgets[i], row, column)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(layout)
        self.mainLayout.addStretch(1)
        self.setLayout(self.mainLayout)

