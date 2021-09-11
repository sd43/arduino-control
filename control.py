import socket
import sys
import logging

class Controller():
    def __init__(self):
        self.server = None
        self.sock = None
        self.commandId = 0

    def setServer(self, host, port):
        self.server = (host, port)

    def disconnect(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass

    def connect(self):
        self.disconnect()

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(self.server)
            self.commandId = 0
            logging.info("connected to server {}".format(self.server))
        except Exception as e:
            logging.error("failed to connect to server {}".format(self.server))
            raise(e)

    def sendCommand(self, command, args=[]):
        if self.sock is None:
            raise Exception("not connected to server")

        argstr = ','.join([str(arg) for arg in args])
        s = '{}:{}:{}'.format(self.commandId, command, argstr)
        self.sock.sendall(s.encode())

