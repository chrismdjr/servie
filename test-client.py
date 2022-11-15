#!/usr/bin/env python3

from servie import client
import time


def main():
    servie_client = client.Client("localhost", 4242)
    servie_client.connect()

    things = ["foobar", "not foobar", "also not foobar"]

    while True:
        for thing in things:
            print(servie_client.send_to_receive(thing.encode()).decode())
            time.sleep(1)


if __name__ == "__main__":
    main()