import typing
import socket
import inspect
import traceback
from threading import Thread

import orjson


class RPCServer:
    """A simple RPC Server
    """
    def __init__(self, host: str, port: int, buffer_size: int=4096, max_threads: int=0) -> None:
        self.host = host; self.port = port; self.address = (self.host, self.port)
        self._methods: typing.Dict[str, typing.Callable] = {}
        self.buffer_size = buffer_size
        self.max_threads = max_threads

    def register_method(self, func: typing.Callable) -> None:
        """register a method

        Args:
            func (Callable): _description_
        """
        self._methods.update({func.__name__: func})

    def register_instance(self, instance: object) -> None:
        """register an instace with it's methods

        Args:
            instance (object): _description_
        """
        for func_name, func in inspect.getmembers(instance, predicate=inspect.ismethod):
            if not func_name.startswith('_'):
                self._methods.update({func_name: func})

    def run(self) -> None:
        """run rpc server
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(self.address); sock.listen(self.max_threads)
            print(f'server is listening at {self.address}')
            while 1:
                try:
                    client, address = sock.accept()
                    Thread(target=self.__handle__, args=(client, address)).start()
                except KeyboardInterrupt:
                    break


    def __handle__(self, client: socket.socket, address: typing.Tuple) -> None:
        """handle client connection

        Args:
            client (socket.socket): _description_
            address (Tuple): _description_
        """

        # received requests from client until client close connection
        while 1:
            try:
                data = bytearray()
                while 1:
                    packet = client.recv(self.buffer_size)
                    if not packet:
                        break
                    data.extend(packet)

                func_name, args, kwargs = orjson.loads(data.decode())
            except Exception as ex:
                print(f'client {address} disconnected, {ex}')
                break

            try:
                data = self._methods[func_name](*args, **kwargs)
                client.sendall(orjson.dumps({'data': data}).encode())

            except Exception as ex:
                client.sendall(orjson.dumps({'data': ex}).encode())
                traceback.print_exc()

        client.close()
