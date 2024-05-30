import socket
import pickle


class RPCClient:
    def __init__(self, host: str, port: int, max_recv_size: int=4194304) -> None:
        self.__sock: socket.socket = None
        self.__address = (host, port)
        self.max_recv_size = max_recv_size

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
            data = pickle.dumps([__name, args, kwargs], protocol=pickle.HIGHEST_PROTOCOL)
            self.__sock.sendall(data)
            data = self.__sock.recv(self.max_recv_size)
            return pickle.loads(data, encoding='utf8')
        return execute
