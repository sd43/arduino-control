import logging

from comm.transport import TcpTransport, SerialTransport

from PyQt5.QtWidgets import *

class ConnectionBar(QTabWidget):
    def __init__(self, controller, parent=None):
        super(ConnectionBar, self).__init__(parent)

        self.tcpTab = TcpConnectionBar(controller)
        self.serialTab = SerialConnectionBar(controller)

        self.addTab(self.tcpTab, "TCP")
        self.addTab(self.serialTab, "Serial")

class TcpConnectionBar(QWidget):
    def __init__(self, controller, parent=None):
        super(TcpConnectionBar, self).__init__(parent)

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
                transport = TcpTransport()
                transport.setAddress(host, port)

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

class SerialConnectionBar(QWidget):
    def __init__(self, controller, parent=None):
        super(SerialConnectionBar, self).__init__(parent)

        self.controller = controller
        self.serialPorts = {}

        layout = QHBoxLayout()
        self.wSerialPort = QComboBox()
        self.updateSerialPortList()
        self.baudRates = [2400, 4800, 9600, 14400, 19200, 2800, 38400, 57600, 76800, 115200]
        self.wBaudRate = QComboBox()
        for b in self.baudRates:
            self.wBaudRate.addItem(str(b))

        self.wConnect = QPushButton('Connect')
        self.wDisconnect = QPushButton('Disconnect')
        self.wDisconnect.hide()

        self.wConnect.clicked.connect(self.onConnect)
        self.wDisconnect.clicked.connect(self.onDisconnect)

        layout.addWidget(QLabel('Serial Port:'))
        layout.addWidget(self.wSerialPort)
        layout.addWidget(QLabel('Baud Rate:'))
        layout.addWidget(self.wBaudRate)
        layout.addWidget(self.wConnect)
        layout.addWidget(self.wDisconnect)

        self.setLayout(layout)

    def updateSerialPortList(self):
        serialPorts = SerialTransport.getSerialPorts()
        self.serialPorts = sorted(
                [ {'name': serialPorts[port], 'device': port } for port in serialPorts ],
                key=lambda port: port['name']
        )

        self.wSerialPort.clear()
        for port in self.serialPorts:
            self.wSerialPort.addItem(port['name'])

    def onConnect(self):
        logging.info("connecting to server...")

        serialPort = self.serialPorts[self.wSerialPort.currentIndex()]
        baudRate = self.baudRates[self.wBaudRate.currentIndex()]

        try:
            transport = SerialTransport()
            transport.setSerialPort(serialPort['device'], baudRate)

            self.controller.setTransport(transport)
            self.controller.connect()

            self.wSerialPort.setEnabled(False)
            self.wBaudRate.setEnabled(False)
            self.wDisconnect.show()
            self.wConnect.hide()
        except Exception as e:
            self.showError('Failed to connect to server: ' + str(e))

    def onDisconnect(self):
        try:
            self.controller.disconnect()
        except Exception as e:
            self.showError('Failed to disconnect: ' + str(e))

        self.wSerialPort.setEnabled(True)
        self.wBaudRate.setEnabled(True)
        self.wDisconnect.hide()
        self.wConnect.show()

    def showError(self, message):
        QMessageBox.critical(self, 'Error', message)

