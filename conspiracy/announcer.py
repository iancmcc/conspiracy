import sys
import struct
from collections import defaultdict

from gevent import socket, sleep


__all__ = ['MulticastAnnouncer', 'KombuAnnouncer']


def parse_mcast(addr):
    pass


ANNOUNCERS = {
    'multicast': MulticastAnnouncer,
    'amqp': KombuAnnouncer
}


class Announcer(object):

    def __new__(cls, addr, *args, **kwargs):
        """
        Use it as a factory.
        """
        newcls = cls
        for scheme, klass in ANNOUNCERS.iteritems():
            if addr.startswith(scheme) and cls is not klass:
                newcls = klass
        return object.__new__(newcls, addr, *args, **kwargs)

    def __init__(self, addr):
        self._addr = addr

    def listen(self):
        pass

    def announce(self, callback):
        pass


class MulticastAnnouncer(Announcer):
    pass


class KombuAnnouncer(Announcer):
    pass
