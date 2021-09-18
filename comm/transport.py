import logging

import socket
import serial, serial.tools.list_ports

class Request():
    def __init__(self, cmd, args, id=None):
        self.id = id
        self.cmd = cmd
        self.args = args

    def __str__(self):
        argstr =  ', '.join([str(x) for x in self.args])
        return '{:12} {}({})'.format(self.id, self.cmd, argstr)

class Response():
    def __init__(self, status, results=[], id=None):
        self.id = id
        self.status = status
        self.results = results

    def isSuccess(self):
        return self.status == 'ok'

    def errorMessage(self):
        if self.status == 'error':
            return self.results[0]
        return None

    def __str__(self):
        resstr =  ','.join([str(x) for x in self.results])
        return '{:12} {}({})'.format(self.id or '', self.status, resstr)

class TcpTransport():
    def __init__(self, host=None, port=None):
        if host is not None and port is not None:
            self.server = (host, port)
        self.sock = None
        self.sockR, self.sockW = None, None

    def isConnected(self):
        return self.sock != None

    def setAddress(self, host, port):
        if self.isConnected():
            raise Exception('cannot set TCP address if already connected')

        self.server = (host, port)

    def connect(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.server)
            self.sockR = sock.makefile('r')
            self.sockW = sock.makefile('w')

            output = self.recv()

            if output.status == 'connected':
                logging.debug("connected to server {}: {}".format(self.server, output))
            else:
                self.disconnect()
                raise Exception("Unexpected connection status: {} (full response: {})", output.status, output)

            self.sock = sock
        except Exception as e:
            logging.error("failed to connect to server {}".format(self.server))
            raise(e)
        
    def disconnect(self):
        if self.isConnected():
            try:
                self.sock.close()
                self.sockR.close()
                self.sockW.close()
                self.sock = None
            except:
                pass
            finally:
                return True
        return False

    def recv(self):
        try:
            text = self.sockR.readline()
        except Exception as e:
            logging.error("failed to read data: {}".format(str(e)))
            self.disconnect()
            raise(e)

        text = text.rstrip('\n\r')
        logging.debug("recv {}".format(text))

        parts = text.split(':')
        if len(parts) != 3:
            raise Exception('bad message format from server: "{}"'.format(output))
        commandId, status, results = parts
        results = results.split(',')

        return Response(id=commandId, status=status, results=results)

    def send(self, request):
        argstr = ','.join([str(arg) for arg in request.args])
        text = '{}:{}:{}'.format(request.id, request.cmd, argstr)
        logging.debug("send {}".format(text))

        try:
            self.sockW.write(text + '\n');
            self.sockW.flush()
        except Exception as e:
            logging.error("failed to send data: {}".format(str(e)))
            self.disconnect()
            raise(e)

class SerialTransport():
    def __init__(self):
        pass

    def setSerialPort(self, serialPortDevice, baudRate):
        self.device = serialPortDevice
        self.baudRate = baudRate

    def getSerialPorts():
        ports = {port.device: port.name for port in serial.tools.list_ports.comports()}
        return ports

    def isConnected(self):
        pass

    def ping(self):
        req = Request(id='connect',cmd='ping')
        self.send(req)

    def connect(self):
        self.serial = serial.Serial(self.device, self.baudRate, timeout=5)

        try:
            self.ping()
        except Exception as e:
            logging.error("failed to connect to server {}".format(self.server))
            raise(e)
        
    def disconnect(self):
        if self.isConnected():
            try:
                self.serial.close()
            finally:
                return True
        return False

    def recv(self):
        try:
            text = self.serial.readline()
        except Exception as e:
            logging.error("failed to read data: {}".format(str(e)))
            self.disconnect()
            raise(e)

        text = text.rstrip('\n\r')
        logging.debug("recv {}".format(text))

        parts = text.split(':')
        if len(parts) != 3:
            raise Exception('bad message format from server: "{}"'.format(output))
        commandId, status, results = parts
        results = results.split(',')

        return Response(id=commandId, status=status, results=results)

    def send(self, request):
        argstr = ','.join([str(arg) for arg in request.args])
        text = '{}:{}:{}\n'.format(request.id, request.cmd, argstr)
        logging.debug("send {}".format(text))

        try:
            self.serial.write(text.encode())
        except Exception as e:
            logging.error("failed to send data: {}".format(str(e)))
            self.disconnect()
            raise(e)

