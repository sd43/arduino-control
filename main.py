#!/usr/bin/env python

import logging

from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QStyleFactory, QWidget, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

from control import Controller

class ControlWindow(QDialog):
    def __init__(self, parent=None):
        super(ControlWindow, self).__init__(parent)

        self.createConnectionBar()
        self.createControlBox()

        mainLayout = QGridLayout()
        mainLayout.addLayout(self.connectionBar, 0, 0, 1, 1)
        mainLayout.addLayout(self.controlBox, 1, 0, 1, 2)
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

        layout.addWidget(QLabel('server:'))
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

    def setController(self, controller):
        self.controller = controller

if __name__ == '__main__':
    app = QApplication([])

    controller = Controller()
    controlWindow = ControlWindow()
    controlWindow.setController(controller)
    controlWindow.show()
    app.exec_()


