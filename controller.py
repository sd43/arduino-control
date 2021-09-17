from transport import Request, Response, TcpTransport

# Commands
WRITE = 'write'
READ  = 'read'

class Controller():
    def __init__(self):
        self.transport = None
        self.commandIndex = 0

        self.commLogger = None
        self.connectionCallbacks = []

    def setTransport(self, transport):
        if self.transport:
            self.transport.disconnect()

        self.transport = transport

    def setCommunicationLogger(self, commLogger):
        self.commLogger = commLogger

    def addConnectionCallback(self, fn):
        self.connectionCallbacks.append(fn)

    def removeConnectionCallback(self, fn):
        self.connectionCallbacks.remove(fn)

    def disconnect(self):
        if self.transport.disconnect():
            for fn in self.connectionCallbacks:
                fn(False)

    def connect(self):
        self.disconnect()
        self.transport.connect()
        for fn in self.connectionCallbacks:
            fn(True)

    def recv(self):
        response = self.transport.recv()
        if self.commLogger:
            self.commLogger({'type':'read', 'text': response})
        return response

    def send(self, text):
        if self.commLogger:
            self.commLogger({'type':'write', 'text': text})
        return self.transport.send(text)

    def command(self, command, args=[], idSuffix=''):
        if not self.transport.isConnected():
            raise Exception("not connected to server")

        self.commandIndex += 1
        commandId = '{}{}'.format(self.commandIndex, idSuffix)
        self.send(Request(id=commandId, cmd=command, args=args))

        response = self.recv()

        return response


