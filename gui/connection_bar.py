import logging

from comm.transport import TcpTransport

from PyQt5.QtWidgets import *

class ConnectionBar(QWidget):
    def __init__(self, controller, parent=None):
        super(ConnectionBar, self).__init__(parent)

        self.controller = controller

        layout = QHBoxLayout()
        self.wServer = QLineEdit('localhost:5000')
        self.wConnect = QPushButton('Connect')
        self.wDisconnect = QPushButton('Disconnect')
        self.wDisconnect.hide()

        self.wServer.returnPressed.connect(self.onConnect)
        self.wConnect.clicked.connect(self.onConnect)
        self.wDisconnect.clicked.connect(self.onDisconnect)

        layout.addWidget(QLabel('Server:'))
        layout.addWidget(self.wServer)
        layout.addWidget(self.wConnect)
        layout.addWidget(self.wDisconnect)

        self.setLayout(layout)

    def onConnect(self):
        logging.info("connecting to server...")
        addrParts = self.wServer.text().split(':')
        if len(addrParts) != 2:
            self.showError('Invalid server address: ' + self.wServer.text())
        else:
            host = addrParts[0]
            try:
                port = int(addrParts[1])
                transport = TcpTransport(host, port)
                self.controller.setTransport(transport)
                self.controller.connect()

                self.wServer.setEnabled(False)
                self.wDisconnect.show()
                self.wConnect.hide()
            except ValueError:
                self.showError('Invalid port: ' + addrParts[1])
            except Exception as e:
                self.showError('Failed to connect to server: ' + str(e))

    def onDisconnect(self):
        try:
            self.controller.disconnect()
        except Exception as e:
            self.showError('Failed to disconnect: ' + str(e))

        self.wServer.setEnabled(True)
        self.wDisconnect.hide()
        self.wConnect.show()

    def showError(self, message):
        QMessageBox.critical(self, 'Error', message)

