# coding: utf-8

import zmq


class ManagerClient(object):
    #TODO: test it!
    #TODO: validate all received data (types, keys etc.)
    #TODO: use some kind of encryption?

    def __init__(self):
        self.context = zmq.Context()
        self.api_host_port = None
        self.broadcast_host_port = None

    def connect(self, api_host_port=None, broadcast_host_port=None):
        if api_host_port is not None:
            self.api_host_port = api_host_port
            self.api_connection_string = 'tcp://{}:{}'.format(*api_host_port)
            self._manager_api = self.context.socket(zmq.REQ)
            self._manager_api.connect(self.api_connection_string)
            self._manager_api.linger = 0
        if broadcast_host_port is not None:
            self.broadcast_host_port = broadcast_host_port
            self.broadcast_connection_string = \
                    'tcp://{}:{}'.format(*broadcast_host_port)
            self._manager_broadcast = self.context.socket(zmq.SUB)
            self._manager_broadcast.connect(self.broadcast_connection_string)
            self._manager_broadcast.linger = 0

    def send_api_request(self, json):
        self._manager_api.send_json(json)

    def get_api_reply(self):
        return self._manager_api.recv_json()

    def broadcast_subscribe(self, subscribe_to):
        return self._manager_broadcast.setsockopt(zmq.SUBSCRIBE, subscribe_to)

    def broadcast_unsubscribe(self, unsubscribe_to):
        return self._manager_broadcast.setsockopt(zmq.UNSUBSCRIBE,
                                                 unsubscribe_to)

    def broadcast_poll(self, timeout=0):
        return self._manager_broadcast.poll(timeout)

    def api_poll(self, timeout=0):
        return self._manager_api.poll(timeout)

    def broadcast_receive(self):
        return self._manager_broadcast.recv()

    def __del__(self):
        self.close_sockets()

    def close_sockets(self):
        sockets = ['_manager_api', '_manager_broadcast']
        for socket in sockets:
            if hasattr(self, socket):
                getattr(self, socket).close()

def create_pipeline(api_host_port, data, timeout=1):
    client = ManagerClient()
    client.connect(api_host_port=api_host_port)
    client.send_api_request({'command': 'add pipeline', 'data': data})
    if client.api_poll(timeout):
        result = client.get_api_reply()
    else:
        result = False
    client.close_sockets()
    return result

def get_config_from_manager(api_host_port, timeout=5):
    client = ManagerClient()
    client.connect(api_host_port=api_host_port)
    client.send_api_request({'command': 'get configuration'})
    if client.api_poll(timeout):
        result = client.get_api_reply()
    else:
        result = None
    client.close_sockets()
    return result