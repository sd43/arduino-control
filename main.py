#!/usr/bin/env python

import logging
from config import JsonConfig

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator

from control import Controller

class ControlWindow(QDialog):
    def __init__(self, parent=None, config=None):
        super(ControlWindow, self).__init__(parent)

        self.config = config

        self.createConnectionBar()
        self.createControlBox()
        self.createCommandBox()
        self.createLogBox()

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(self.connectionBar)

        tabWidget = QTabWidget()
        controlTab = QWidget()
        controlTab.setLayout(self.controlBox)
        tabWidget.addTab(controlTab, "Control")
        commandTab = QWidget()
        commandTab.setLayout(self.commandBox)
        tabWidget.addTab(commandTab, "Command")
        mainLayout.addWidget(tabWidget)

        mainLayout.addLayout(self.logBox)

        self.setLayout(mainLayout)

    def showError(self, message):
        QMessageBox.critical(self, 'Error', message)

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

                    wServer.setReadOnly(True)
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

            wServer.setReadOnly(False)
            wDisconnect.hide()
            wConnect.show()

        wConnect.clicked.connect(onConnect)
        wDisconnect.clicked.connect(onDisconnect)

        layout.addWidget(QLabel('Server:'))
        layout.addWidget(wServer)
        layout.addWidget(wConnect)
        layout.addWidget(wDisconnect)

        self.connectionBar = layout

    def createControlBox(self):
        layout = QGridLayout()
        wButton1 = QPushButton('button 1')
        wButton2 = QPushButton('button 2')
        wButton3 = QPushButton('button 3')
        wButton4 = QPushButton('button 4')

        layout.addWidget(wButton1, 0, 0)
        layout.addWidget(wButton2, 0, 1)
        layout.addWidget(wButton3, 1, 0)
        layout.addWidget(wButton4, 1, 1)

        self.controlBox = layout

    def createCommandBox(self):
        items = self.config.getCommands()

        layout = QGridLayout()
        row = 0 

        layout.addWidget(QLabel('<i>Command</i>'), row, 0)
        layout.addWidget(QLabel('<i>Inputs</i>'), row, 1)
        layout.addWidget(QLabel('<i>Outputs</i>'), row, 2)
        layout.addWidget(QLabel('<i>Send</i>'), row, 3)

        for item in items:
            row += 1
            layout.addWidget(QLabel('<b>'+item['label']+'</b>'), row, 0)
            wInputs = []
            wOutputs = []

            if len(item['inputs']) > 0:
                wLayout = QHBoxLayout()
                for inp in item['inputs']:
                    wInput = QLineEdit(placeholderText=inp['name'])
                    if inp['type'] == 'int':
                        wInput.setValidator(QIntValidator(0, 999999))

                    wInputs.append(wInput)
                    wLayout.addWidget(wInput)
                layout.addLayout(wLayout, row, 1)

            if len(item['outputs']) > 0:
                wLayout = QHBoxLayout()
                for out in item['outputs']:
                    wOutput = QLineEdit(placeholderText=out['name'])
                    wOutput.setReadOnly(True)
                    wOutputs.append(wOutput)
                    wLayout.addWidget(wOutput)
                layout.addLayout(wLayout, row, 2)

            def onSendCallback(command, wInputs, wOutputs):
                def fn():
                    try:
                        args = [ w.text() for w in wInputs ]
                        output = self.controller.command(command, args)
                        for (wOutput, output) in zip(wOutputs, output.split(',')):
                            wOutput.setText(output)

                    except Exception as e:
                        self.showError('Failed to send command: ' + str(e))
                return fn

            wSend = QPushButton('->')
            wSend.clicked.connect(onSendCallback(item['command'], wInputs, wOutputs))
            layout.addWidget(wSend, row, 3)

        self.commandBox = layout

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

if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')

    cfg = JsonConfig(commandsFile='commands.json')

    app = QApplication([])

    controller = Controller()
    controlWindow = ControlWindow(config=cfg)
    controlWindow.setController(controller)
    controlWindow.show()
    app.exec_()


