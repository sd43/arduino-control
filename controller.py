import socket
import sys
import logging

# Commands
WRITE_PIN = 'write'
READ_PIN  = 'read'

class Output():
    def __init__(self, id, status, results):
        self.id = id
        self.status = status
        self.results = results

    def isSuccess(self):
        return self.status == 'ok'

    def errorMessage(self):
        if self.status == 'error':
            return self.results[0]
        return None

class Controller():
    def __init__(self):
        self.server = None
        self.sock = None
        self.commandId = 0
        self.connectTimeout = 2

        self.commLogger = None
        self.connectionCallback = None

        self.sockR, self.sockW = None, None

    def setServer(self, host, port):
        self.server = (host, port)

    def setCommunicationLogger(self, fn):
        self.commLogger = fn

    def setConnectionCallback(self, fn):
        self.connectionCallback = fn

    def disconnect(self):
        if self.sock:
            try:
                self.sock.close()
                self.sockR.close()
                self.sockW.close()
                self.sock = None
            except:
                pass
            finally:
                if self.connectionCallback:
                    self.connectionCallback(False)

    def connect(self):
        self.disconnect()

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.server)
            self.sockR = sock.makefile('r')
            self.sockW = sock.makefile('w')
            self.commandId = 0

            output = self.recv()
            logging.info("connected to server {}: {}".format(self.server, output))

            self.sock = sock

            if self.connectionCallback:
                self.connectionCallback(True)
        except Exception as e:
            logging.error("failed to connect to server {}".format(self.server))
            raise(e)

    def recv(self):
        try:
            text = self.sockR.readline()
        except Exception as e:
            logging.error("failed to read data: {}".format(str(e)))
            self.disconnect()
            raise(e)

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

        try:
            self.sockW.write(text + '\n');
            self.sockW.flush()
        except Exception as e:
            logging.error("failed to send data: {}".format(str(e)))
            self.disconnect()
            raise(e)

    def command(self, command, args=[]):
        if self.sock is None:
            raise Exception("not connected to server")

        self.commandId += 1
        argstr = ','.join([str(arg) for arg in args])
        s = '{}:{}:{}'.format(self.commandId, command, argstr)
        self.send(s)

        output = self.recv()
        parts = output.split(':')
        if len(parts) != 3:
            raise Exception('bad message format from server: "{}"'.format(output))
        commandId, status, results = parts
        results = results.split(',')

        return Output(id=commandId, status=status, results=results)

