#! /usr/bin/env python3

import os
import random
import re
import socket
import sys
from threading import Thread
import time

import params
from framedSock import FramedStreamSock

storage_dir = 'clientFiles/'  # directory used to send/receive files

switches_var_defaults = (
    (('-s', '--server'), 'server', '127.0.0.1:50001'),
    (('-d', '--debug'), 'debug', False),  # boolean (set if present)
    (('-?', '--usage'), 'usage', False),  # boolean (set if present)
)

prog_name = 'file_client'
param_map = params.parse_params(switches_var_defaults)
server, usage, debug = param_map['server'], param_map['usage'], param_map['debug']

if usage:
    params.usage()

try:
    server_host, server_port = re.split(':', server)
    server_port = int(server_port)
except:
    print('Could not parse server:port from ', server)
    sys.exit(1)


class ClientThread(Thread):
    def __init__(self, server_host, server_port, filename, storage_dir, debug=0):
        Thread.__init__(self, daemon=False)
        self.server_host, self.server_port, self.debug = server_host, server_port, debug
        self.filename, self.storage_dir = filename, storage_dir
        self.start()

    def run(self):
        s = None
        for res in socket.getaddrinfo(server_host, server_port, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                if debug:
                    print(' Creating sock: af=%d, type=%d, proto=%d' % (af, socktype, proto))
                s = socket.socket(af, socktype, proto)
            except socket.error as msg:
                if debug:
                    print(" error: %s" % msg)
                s = None
                continue
            try:
                if debug:
                    print(' Attempting to connect to: %s' % repr(sa))
                s.connect(sa)
            except socket.error as msg:
                if debug:
                    print(' Error: %s' % msg)
                s.close()
                s = None
                continue
            break

        if s is None:
            print('could not open socket')
            sys.exit(1)

        fs = FramedStreamSock(s, debug=debug)
        if fs.send_file(filename, storage_dir):  # message sent successfully
            print(' File sent successfully:', filename)
        else:
            print(' File failed to send:', filename)
            exit()


# print files available for sending, assume storage_dir is in same directory
files = os.listdir(storage_dir)
print('Files available for sending:')
for file in files:
    print(' {} ({} bytes)'.format(file, os.path.getsize(storage_dir + file)))

# create num_of_sends threads to send a random file
num_of_sends = 100
print('Sending {} files'.format(num_of_sends))
filename = random.choice(files)
for i in range(num_of_sends):
    print('Sending:', filename)
    ct = ClientThread(server_host, server_port, filename, storage_dir)
