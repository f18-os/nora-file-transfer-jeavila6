import re

MAX_SIZE = 100  # max num of bytes to send/receive


class FramedStreamSock:
    sockNum = 0

    def __init__(self, sock, debug=False, name=None):
        self.sock, self.debug = sock, debug
        self.rbuf = b''  # receive buffer
        if name:
            self.name = name
        else:  # make default name
            self.name = 'FramedStreamSock-%d' % FramedStreamSock.sockNum
            FramedStreamSock.sockNum += 1

    def __repr__(self):
        return self.name

    def send_file(self, filename, storage_dir):
        with open(storage_dir + filename, 'rb') as br:
            contents = br.read()
        # msg is in format <filename_length>:<filename><contents_length>:<contents>
        msg = str(len(filename)).encode() + b':' + filename.encode() + str(len(contents)).encode() + b':' + contents
        try:
            while len(msg):
                nsent = self.sock.send(msg)
                msg = msg[nsent:]
        except BrokenPipeError:
            return False
        return True

    def receive_file(self):
        state = 'get_filename_len'
        filename_length = -1
        contents_length = -1
        filename = ''  # TODO why is this here?

        while True:

            if state == 'get_filename_len':  # state 0: reading filename length
                match = re.match(b'([^:]+):(.*)', self.rbuf, re.DOTALL | re.MULTILINE)  # look for colon
                if match:
                    print(' Receiving file...')
                    filename_len, self.rbuf = match.groups()
                    try:
                        filename_length = int(filename_len)
                    except ValueError:
                        if len(self.rbuf):
                            print(' Badly formed filename length: ', filename_len)
                            return None
                    state = 'get_filename'

            if state == 'get_filename':  # state 1: reading filename
                if len(self.rbuf) >= filename_length:
                    filename_encoded = self.rbuf[0:filename_length]
                    self.rbuf = self.rbuf[filename_length:]
                    filename = filename_encoded.decode()
                    state = 'get_contents_len'

            if state == 'get_contents_len':  # state 2: reading contents length
                match = re.match(b'([^:]+):(.*)', self.rbuf, re.DOTALL | re.MULTILINE)  # look for colon
                if match:
                    contents_len, self.rbuf = match.groups()
                    try:
                        contents_length = int(contents_len)
                    except ValueError:
                        if len(self.rbuf):
                            print(' Badly formed contents length: ', contents_len)
                            return None
                    state = 'get_contents'

            if state == 'get_contents':  # state 3: reading contents
                if len(self.rbuf) >= contents_length:
                    contents = self.rbuf[0:contents_length]
                    self.rbuf = self.rbuf[contents_length:]
                    return filename, contents

            r = self.sock.recv(MAX_SIZE)  # receive MAX_SIZE bytes
            self.rbuf += r
            if len(r) == 0:  # nothing to receive
                if len(self.rbuf) != 0:
                    print(' Incomplete message')
                return None
