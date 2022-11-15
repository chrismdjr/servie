import socket, selectors, types

"""
on_pre_event: Runs before any event is triggered at any time.
on_post_event: Runs after any event is triggered at any time.
on_start: Runs once when the server is started.
on_loop_update: Runs whenever the main server loop continues. Deprecated.
on_close: Runs once after the server closes but before the program closes.
on_accept_connection: Runs when the server accepts a listening connection.
on_disconnect_connection: Runs when the server disconnects a connected client.
on_service_connection: Runs when the server services a connected client's connection.
"""


class Server:
    def __init__(self, host, port, server_events={}):
        """Initializes a server, but doesn't make it listen until start() is called."""
        self._selector = selectors.DefaultSelector() # Internal selector for multiplexing.
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Internal socket for socket-ing with.
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow us to use the same host and port multiple times, even on a crash.

        self.host = host
        self.port = port
        self._socks = []
        self._host_port_validate()

        self._sock.bind((self.host, self.port)) # Bind our socket server to our host and port.
        self.server_events = server_events


    def _host_port_validate(self):
        """Makes sure that the host and port specified is valid."""
        assert int(self.port) # Assert that the port is an int and not some garbage.


    def _handle_server_event(self, event_name, data, sock):
        """Handles custom server events."""
        if not self.server_events.get(event_name): # Does the event that we're trying to call even exist?
            return

        if self.server_events.get("on_pre_event"): # Do we have a pre event?
            self.server_events["on_pre_event"](event_name="on_pre_event", server_obj=self, data=None, sock=sock)

        self.server_events[event_name](event_name=event_name, server_obj=self, data=data, sock=sock) # Call our main event.

        if self.server_events.get("on_post_event"): # Do we have a post event?
            self.server_events["on_post_event"](event_name="on_post_event", server_obj=self, data=None, sock=sock)


    def _accept_new_connection(self, client_sock):
        """Internally connects a client to the server."""
        new_conn, new_addr = client_sock.accept() # Accept their connection.
        new_conn.setblocking(False) # No blocking.

        data = types.SimpleNamespace(addr=new_addr, recv=None) # Create a SimpleNamespace to hold this client's data in.
        events = selectors.EVENT_READ | selectors.EVENT_WRITE

        self._selector.register(new_conn, events=events, data=data) # Put our new client in the selector.
        self._handle_server_event(event_name="on_accept_connection", data=data, sock=client_sock) # Handle custom server event.


    def _service_connection(self, key, mask):
        """Internally service a client socket's connection by receiving it's data or sending data to it."""
        client_sock = key.fileobj
        client_data = key.data
        client_data.recv = None # Reset what they have received.

        if client_sock not in self._socks:
            self._socks.append(client_sock) # Add our sock to the internal socks list.

        if mask & selectors.EVENT_READ: # Read from the client socket.
            try: # This is an a try-except because there's a small chance that a client will disconnect when this is running, causing bad things.
                recv_data = client_sock.recv(1024) # Receive 1024 bytes of data from the client. XXX: ADD CLIENT SUPERSENDING SO THE SERVER IS BETTER

            except (ConnectionResetError):
                recv_data = None # When there's an error, we didn't get anything.

            if not recv_data: # We didn't get anything.
                self._selector.unregister(client_sock) # Remove client from our selector.
                client_sock.close() # Wipe them off of the face of the Earth.

                if client_sock in self._socks:
                    self._socks.remove(client_sock) # Remove our sock from the internal socks list.

                self._handle_server_event(event_name="on_disconnect_connection", data=client_data, sock=client_sock) # Handle custom server event.

            else:
                client_data.recv = recv_data # Add the data we got from them into their data.

        if mask & selectors.EVENT_WRITE: # Write to the client socket.
            self._handle_server_event(event_name="on_service_connection", data=client_data, sock=client_sock) # Handle custom server event.


    def send_to_sock(self, sock, data_string):
        sock.sendall(data_string)


    def send_to_all_socks(self, data_string):
        for sock in self._socks:
            sock.sendall(data_string)

    def start(self):
        """Starts a server on the specified host and port."""
        self._sock.listen() # Listen for a connection!
        self._sock.setblocking(False) # No blocking.

        self._selector.register(self._sock, selectors.EVENT_READ, data=None) # Registers the socket to be monitored by self._selector.select().
        self._handle_server_event(event_name="on_start", data=None, sock=None) # Handle custom server event.

        try:
            while True: # The main loop of the server.
                events = self._selector.select(timeout=None) # Check if we've got any sockets that are ready to talk to us.

                # self._handle_server_event(event_name="on_loop_update", data=None, sock=None) # Deprecated.

                for key, mask in events: # Iterate over all incoming sockets to decide what to do with them.
                    if not key.data: # Non-connected client that wants a new connection.
                        self._accept_new_connection(key.fileobj)

                    else: # Connected client who wants their connection serviced.
                        self._service_connection(key, mask)

        except (KeyboardInterrupt, EOFError):
            pass

        finally:
            self._selector.close()
            self._handle_server_event(event_name="on_close", data=None, sock=None) # Handle custom server event.
            