import socket
import sys
import logging

class Controller():
    def __init__(self):
        self.server = None
        self.sock = None
        self.commandId = 0
        self.connectTimeout = 2

        self.commLogger = None

        self.sockR, self.sockW = None, None

    def setServer(self, host, port):
        self.server = (host, port)

    def setCommunicationLogger(self, fn):
        self.commLogger = fn

    def disconnect(self):
        if self.sock:
            try:
                self.sock.close()
                self.sockR.close()
                self.sockW.close()
            except:
                pass

    def connect(self):
        self.disconnect()

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(self.server)
            self.sockR = self.sock.makefile('r')
            self.sockW = self.sock.makefile('w')
            self.commandId = 0

            output = self.recv()
            logging.info("connected to server {}: {}".format(self.server, output))
        except Exception as e:
            logging.error("failed to connect to server {}".format(self.server))
            raise(e)

    def recv(self):
        text = self.sockR.readline()
        text = text.rstrip('\n\r')
        logging.info("recv {}".format(text))
        if self.commLogger:
            self.commLogger({'type':'read', 'text': text})
        return text

    def send(self, text):
        text = text.rstrip('\n\r')
        logging.info("send {}".format(text))
        if self.commLogger:
            self.commLogger({'type':'write', 'text': text})
        self.sockW.write(text + '\n');
        self.sockW.flush()

    def command(self, command, args=[]):
        if self.sock is None:
            raise Exception("not connected to server")

        self.commandId += 1
        argstr = ','.join([str(arg) for arg in args])
        s = '{}:{}:{}'.format(self.commandId, command, argstr)
        self.send(s)

        output = self.recv()
        return output


