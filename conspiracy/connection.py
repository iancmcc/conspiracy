
class Connection(object):

    def send(self, data, type_):
        pass

    def listen(self, callback):
        pass


class DirectConnection(Connection):
    pass


class KombuConnection(Connection):
    pass
