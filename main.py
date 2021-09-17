#!/usr/bin/env python

import logging

from config import JsonConfig
from gui.window import MainWindow
from comm.controller import Controller

from PyQt5.QtWidgets import *

if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')

    cfg = JsonConfig( controlsFile='data/controls.json', commandsFile='data/commands.json')

    app = QApplication([])

    controller = Controller()
    controlWindow = MainWindow(config=cfg, controller=controller)
    controlWindow.show()
    app.exec_()


