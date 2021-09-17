#!/usr/bin/env python

import logging
import socket
import sys

logging.basicConfig(level=logging.DEBUG)

STATUS_OK = 'ok'
STATUS_ERROR = 'error'
STATUS_CONNECTED = 'connected'

def reply(s, id, status, arguments=None):
    if arguments is None:
        arguments = []
    s.sendall('{}:{}:{}\n'.format(id, status, ','.join(arguments)).encode())

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', 5000))

sock.listen(5)

controlState = {}

while True:
    conn, addr = sock.accept()

    logging.info('client connected')

    try:
        r = conn.makefile(mode='r')
        w = conn

        reply(w, '_', STATUS_CONNECTED)

        while True:
            line = r.readline()
            if not line:
                break

            logging.info('read line: ' + line)
            line = line.strip()
            parts = line.split(':')

            if len(parts) < 3:
                logging.info('bad command: ' + line)
                reply(w, '_', STATUS_ERROR, ['bad command'])
                continue

            id = parts[0]
            command = parts[1]
            arguments = parts[2]
            if arguments:
                arguments = arguments.split(',')
            else:
                arguments = []

            status = ''
            results = []

            disconnect = False

            if command == 'ping':
                status = STATUS_OK
                results = [ 'pong' ]
            elif command == 'close':
                status = STATUS_OK
                disconnect = True
            elif command == 'read':
                if len(arguments) != 1:
                    status = STATUS_ERROR
                    results = [ 'bad arguments' ]
                else:
                    control = arguments[0]
                    if control not in controlState:
                        controlState[control] = 0
                    status = STATUS_OK
                    results = [ str(controlState[control]) ]
            elif command == 'write':
                if len(arguments) != 2:
                    status = STATUS_ERROR
                    results = [ 'bad arguments' ]
                else:
                    control = arguments[0]
                    value = arguments[1]
                    controlState[control] = value
                    status = STATUS_OK
            else:
                status = STATUS_ERROR
                results = [ 'unknown command ' + command ]

            reply(w, id, status, results)

            if disconnect:
                break
    except Exception as e:
        logging.error('caught exception: {}'.format(e))
    finally:
        logging.info('closing connection')
        r.close()
        conn.close()

