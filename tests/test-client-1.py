#!/usr/bin/env python3

from servie import client


def main():
    servie_client = client.Client("localhost", 4242)
    servie_client.connect()

    print(servie_client.send_to_receive(b"foobar").decode())


if __name__ == "__main__":
    main()