import socket

import orjson


class RPCClient:
    def __init__(self, host: str, port: int, buffer_size: int=4096) -> None:
        self.__sock: socket.socket = None
        self.__address = (host, port)
        self.buffer_size = buffer_size

    def connect(self) -> None:
        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.connect(self.__address)
        except EOFError:
            raise Exception(f'Client was not able to connect to {self.__address}.')

    def disconnect(self) -> None:
        try:
            self.__sock.close()
        except:
            pass

    def __getattr__(self, __name: str):
        def execute(*args, **kwargs):
            data = orjson.dumps([__name, args, kwargs]).encode()
            self.__sock.sendall(data)
            data = bytearray()
            while 1:
                packet = self.__sock.recv(self.buffer_size)
                if not packet:
                    break
                data.extend(packet)
            return orjson.loads(data.decode())['data']
        return execute
