import socket


class Client:
    def __init__(self, host, port):
        """Initializes a client, but doesn't make it connect until connect() is called."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Internal socket for socket-ing with.

        self.host = host
        self.port = port
        self._host_port_validate()

        self.server_addr = (self.host, self.port)


    def _host_port_validate(self):
        """Makes sure that the host and port specified is valid."""
        assert int(self.port) # Assert that the port is an int and not some garbage.


    def connect(self):
        """Connects a client to the specified host and port."""
        self._sock.connect(self.server_addr) # Connect to the server's address.


    def disconnect(self):
        """Disconnects a client from the specified host and port."""
        self._sock.close()


    def send(self, data):
        """Send some data to the server."""
        self._sock.sendall(data)
        return data.encode()


    def send_to_receive(self, data, size=1024):
        """Send some data to and recieve some data from the server."""
        self._sock.sendall(data)
        return self.receive(size)


    def receive(self, size=1024):
        """Recieve some data from the server."""
        new_data = self._sock.recv(size)
        return new_data
