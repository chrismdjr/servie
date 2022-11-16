#!/usr/bin/env python3

from servie import server


def custom_start(event_name, server_obj, data, sock):
    print(f"Started server [{server_obj.host}:{server_obj.port}].")


def custom_close(event_name, server_obj, data, sock):
    print("Closing server...")


def custom_disconnect_connection(event_name, server_obj, data, sock):
    print(f"Client [{data.addr[0]}] has disconnected.")


def custom_accept_connection(event_name, server_obj, data, sock):
    print(f"Client [{data.addr[0]}] has connected.")


def custom_service_connection(event_name, server_obj, data, sock):
    if not data.recv:
        return

    server_obj.send_to_all_socks(b"Hey, a client said something!")


def main():
    servie_server = server.Server("0.0.0.0", 4242, server_events={
        "on_start": custom_start,
        "on_close": custom_close,
        "on_disconnect_connection": custom_disconnect_connection,
        "on_accept_connection": custom_accept_connection,
        "on_service_connection": custom_service_connection,
    })

    servie_server.start()


if __name__ == "__main__":
    main()