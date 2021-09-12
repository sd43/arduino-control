#!/usr/bin/env python

import logging
from config import JsonConfig
from window import MainWindow

from PyQt5.QtWidgets import *

from control import Controller

if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')

    cfg = JsonConfig(commandsFile='commands.json')

    app = QApplication([])

    controller = Controller()
    controlWindow = MainWindow(config=cfg)
    controlWindow.setController(controller)
    controlWindow.show()
    app.exec_()


