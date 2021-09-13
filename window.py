import os
import logging

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator

from control_box import ControlBox
from command_box import CommandBox

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
        mainLayout.addLayout(self.connectionBar)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.controlBox, "Control")
        self.tabWidget.addTab(self.commandBox, "Command")
        mainLayout.addWidget(self.tabWidget)

        mainLayout.addLayout(self.logBox)

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
        layout = QHBoxLayout()
        wServer = QLineEdit('localhost:5000')
        wConnect = QPushButton('Connect')
        wDisconnect = QPushButton('Disconnect')
        wDisconnect.hide()

        def onConnect():
            logging.info("connecting to server...")
            addrParts = wServer.text().split(':')
            if len(addrParts) != 2:
                self.showError('Invalid server address: ' + wServer.text())
            else:
                host = addrParts[0]
                try:
                    port = int(addrParts[1])
                    self.controller.setServer(host, port)
                    self.controller.connect()

                    wServer.setEnabled(False)
                    wDisconnect.show()
                    wConnect.hide()
                except ValueError:
                    self.showError('Invalid port: ' + addrParts[1])
                except Exception as e:
                    self.showError('Failed to connect to server: ' + str(e))

        def onDisconnect():
            try:
                self.controller.disconnect()
            except Exception as e:
                self.showError('Failed to disconnect: ' + str(e))

            wServer.setEnabled(True)
            wDisconnect.hide()
            wConnect.show()

        wServer.returnPressed.connect(onConnect)
        wConnect.clicked.connect(onConnect)
        wDisconnect.clicked.connect(onDisconnect)

        layout.addWidget(QLabel('Server:'))
        layout.addWidget(wServer)
        layout.addWidget(wConnect)
        layout.addWidget(wDisconnect)

        self.connectionBar = layout

    def createControlBox(self):
        config = self.config.getControls()
        self.controlBox = ControlBox(config=config, columns=2)

    def createCommandBox(self):
        config = self.config.getCommands()
        self.commandBox = CommandBox(config=config, controller=self.controller)

    def createLogBox(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel('Message Log'))

        self.logBoxTextEdit = QPlainTextEdit()
        self.logBoxTextEdit.setReadOnly(True)

        layout.addWidget(self.logBoxTextEdit)

        self.logBox = layout

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

            text = '<pre><font color="{}"><b>{:<9}</b></font> '.format(color, type_) + logEntry['text'] + '</pre>'

            self.logBoxTextEdit.appendHtml(text)
        else:
            text = str(logEntry)
            self.logBoxTextEdit.appendPlainText(text)

    def setController(self, controller):
        self.controller = controller
        self.controller.setCommunicationLogger(self.addLogEntry)
        self.controller.setConnectionCallback(lambda connected: self.enableControls(connected))

