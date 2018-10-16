#! /usr/bin/env python3

import os
import socket
from threading import Thread
from framedSock import FramedStreamSock
import time
from threading import Lock

import params

storage_dir = 'serverFiles/'  # directory used to send/receive files
if not os.path.exists(storage_dir):
    os.makedirs(storage_dir)

switches_var_defaults = (
    (('-l', '--listenPort'), 'listenPort', 50001),
    (('-d', '--debug'), 'debug', False),  # boolean (set if present)
    (('-?', '--usage'), 'usage', False),  # boolean (set if present)
)

prog_name = 'file_server'
param_map = params.parse_params(switches_var_defaults)

debug, listenPort = param_map['debug'], param_map['listenPort']

if param_map['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # listener socket
bind_addr = ('127.0.0.1', listenPort)
lsock.bind(bind_addr)
lsock.listen(5)
print('Listening on:', bind_addr)

lock = Lock()


class ServerThread(Thread):
    request_count = 0  # one instance / class

    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()

    def run(self):
        while True:
            data = self.fsock.receive_file()
            if data:
                filename, contents = data
                if filename and contents:  # file received successfully
                    with lock:
                        # try forcing a race condition
                        request_num = ServerThread.request_count
                        time.sleep(0.001)
                        ServerThread.request_count = request_num + 1

                        with open(storage_dir + filename, 'wb') as file:
                            file.write(contents)
                            print('Request number:', request_num)
                            print(' Downloaded file:', filename)
                    continue
                else:
                    print(' Filename or contents empty')
            else:
                print('Connection ended with', addr)
                exit()


while True:
    sock, addr = lsock.accept()
    print('Connection received from', addr)
    ServerThread(sock, debug)
