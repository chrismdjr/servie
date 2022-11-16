#!/usr/bin/env python3

from servie import client


def main():
    servie_client = client.Client("localhost", 4242)
    servie_client.connect()

    print(servie_client.receive().decode())


if __name__ == "__main__":
    main()