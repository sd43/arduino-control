#!/usr/bin/env python

import logging

from config import JsonConfig
from gui.window import MainWindow
from comm.controller import Controller
from comm.control_state import ControlState

from comm.control import AnalogOutputControl, DigitalOutputControl

from PyQt5.QtWidgets import *

def createControlsFromConfig(controlConfig):
    controls = []
    for c in controlConfig:
        control = None
        if c.controlType == 'analogOutput':
            control = AnalogOutputControl(c, controller)
        elif c.controlType == 'digitalOutput':
            control = DigitalOutputControl(c, controller)
        else:
            raise Exception('Unsupported control type {}'.format(c.type))
        controls.append(control)

    return controls

if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')

    cfg = JsonConfig(configFile='data/example.json')

    app = QApplication([])

    controller = Controller()
    controlState = ControlState(controller, "data/controlState.json")
    controls = createControlsFromConfig(cfg.getControls())
    for control in controls:
        controlState.addControl(control)
    try:
        controlState.readStatesFromFile()
    except Exception as e:
        pass

    controlWindow = MainWindow(config=cfg, controller=controller, controls=controls)
    controlWindow.show()
    app.exec_()

