import os
import logging
import html

from PyQt5.QtWidgets import *

from control_box import ControlBox
from command_box import CommandBox
from connection_bar import ConnectionBar

class MainWindow(QMainWindow):
    def __init__(self, config, controller, parent=None):
        super(MainWindow, self).__init__(parent)

        self.config = config
        self.setController(controller)

        self.setWindowTitle('Control Over Ethernet')
        self.createMenus()

        self.createConnectionBar()
        self.createControlBox()
        self.createCommandBox()
        self.createLogBox()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.connectionBar)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.controlBox, "Control")
        self.tabWidget.addTab(self.commandBox, "Command")
        mainLayout.addWidget(self.tabWidget)

        mainLayout.addWidget(self.logBox)

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)
        self.enableControls(False)

    def createMenus(self):
        fileMenu = self.menuBar().addMenu('&File')
        exitAction = QAction('E&xit')
        exitAction.triggered.connect(lambda: os.exit(0))
        fileMenu.addAction(exitAction)

    def showError(self, message):
        QMessageBox.critical(self, 'Error', message)

    def enableControls(self, enable=True):
        for i in range(0, self.tabWidget.count()):
            self.tabWidget.widget(i).setEnabled(enable)

    def createConnectionBar(self):
        self.connectionBar = ConnectionBar(self.controller)

    def createControlBox(self):
        config = self.config.getControls()
        self.controlBox = ControlBox(config=config, controller=self.controller, columns=2)

    def createCommandBox(self):
        config = self.config.getCommands()
        self.commandBox = CommandBox(config=config, controller=self.controller)

    def createLogBox(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Message Log'))

        self.logBoxTextEdit = QPlainTextEdit()
        self.logBoxTextEdit.setReadOnly(True)

        layout.addWidget(self.logBoxTextEdit)

        frame = QGroupBox()
        frame.setLayout(layout)
        self.logBox = frame

    def addLogEntry(self, logEntry):
        if 'type' in logEntry:
            color = 'black'
            type_ = logEntry['type']

            if logEntry['type'] == 'read':
                color = 'blue'
                type_ = 'RECEIVE'
            elif logEntry['type'] == 'write':
                color = 'brown'
                type_ = 'SEND'

            text = '<pre><font color="{}"><b>{:<9}</b></font> '.format(color, type_) + html.escape(str(logEntry['text'])) + '</pre>'

            self.logBoxTextEdit.appendHtml(text)
        else:
            text = str(logEntry)
            self.logBoxTextEdit.appendPlainText(text)

    def setController(self, controller):
        self.controller = controller
        self.controller.addConnectionCallback(lambda connected: self.enableControls(connected))
        self.controller.setCommunicationLogger(self.addLogEntry)

