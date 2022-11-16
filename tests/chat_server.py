#!/usr/bin/env python3

from servie import server


class User:
    def __init__(self, name, sock):
        self.name = name
        self.sock = sock



class ChatServer(server.Server):
    def __init__(self, listen_ip, listen_port):
        # Build up our 
        super().__init__(listen_ip, listen_port, server_events={
            "on_start": self.on_start,
            "on_close": self.on_close,
            "on_disconnect_connection": self.on_disconnect_connection,
            "on_accept_connection": self.on_accept_connection,
            "on_service_connection": self.on_service_connection,
        })

    def on_start(self, *args, **kwargs):
        print(f"on_start: args={args} kwargs={kwargs}")

    def on_close(self, *args, **kwargs):
        print(f"on_close: args={args} kwargs={kwargs}")

    def on_disconnect_connection(self, *args, **kwargs):
        print(f"on_disconnect_connection: args={args} kwargs={kwargs}")

    def on_accept_connection(self, data, **kwargs):
        print(f"on_accept_connection: args={args} kwargs={kwargs}")
        #data.recv


    def on_service_connection(self, *args, **kwargs):
        print(f"on_service_connection: args={args} kwargs={kwargs}")


def main():
    chat_server = ChatServer("0.0.0.0", 4242)
    chat_server.start()


if __name__ == "__main__":
    main()
