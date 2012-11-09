import sys
import struct
from collections import defaultdict

from gevent import socket, sleep


SEPARATOR = "|"
MCAST_ADDRESS = "239.1.1.123"
TIMEOUT = 5
PORT=50123


class MulticastListener(object):

    def __init__(self, port=PORT, group=MCAST_ADDRESS):
        self._group = group
        self._port = port
        self._shutdown = False
        self._sock = None
        self._callbacks = defaultdict(set)

    def listen(self):
        self._sock = sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                          socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('', self._port))
        except socket.error as e:
            if e.errno==48:
                self._port += 1
                return self.listen()
        mreq = struct.pack("4sl", socket.inet_aton(self._group),
                           socket.INADDR_ANY)
        sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 1)
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)

        while not self._shutdown:
            try:
                data, addr = sock.recvfrom(1024)
                command, data = data.decode('ascii').split(SEPARATOR, 1)
            except Exception:
                continue
            if command in self._callbacks:
                response_cmd = "{0}_response".format(command)
                for callback in self._callbacks[command]:
                    result = callback(data, addr)
                    if result is not None:
                        msg = SEPARATOR.join((response_cmd, result))
                        sock.sendto(msg.encode('ascii'), addr)

    def shutdown(self):
        self._shutdown = True

    def subscribe(self, command, callback):
        self._callbacks[command].add(callback)



class MulticastRequester(object):
    def __init__(self, port=PORT, ip=MCAST_ADDRESS):
        self._group = (ip, port)
        sock = self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL,
                        struct.pack('b', 33))
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)

    def request(self, command, data):
        self.sock.settimeout(TIMEOUT)
        msg = SEPARATOR.join((command, data)).encode('ascii')
        self.sock.sendto(msg, self._group)
        response_cmd = "{0}_response".format(command)
        responses = []
        i = 0
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                cmd, data = data.decode('ascii').split(SEPARATOR, 1)
                if cmd == response_cmd:
                    yield addr, data
                    i += 1
            except socket.timeout:
                print "Received {0} responses within the timeout".format(i)
                break
            except Exception:
                continue


def test():
    cmd = sys.argv[1]

    def listener_callback(data, addr):
        print "Received: {data} from {addr}".format(**locals())
        return "Echoing back {data}".format(data=data)

    if cmd == 'listen':
        listener = MulticastListener()
        listener.subscribe('test', listener_callback)
        listener.listen()

    elif cmd == 'request':
        requester = MulticastRequester()
        for response in requester.request('test', 'something'):
            print response


if __name__ == "__main__":
    test()


