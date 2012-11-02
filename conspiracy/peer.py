from .announcer import *


class Peer(object):

    def __init__(self, group_name, announce_addr, connect_addr):
        self._create_announcer(announce_addr)
        self._create_connect(connect_addr)

    def _create_announcer(self, addr):
        pass

    def _create_connect(self, addr):
        pass
    
