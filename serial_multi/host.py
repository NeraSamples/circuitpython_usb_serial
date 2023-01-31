"""
This script connects to the provided serial port.
It sends color commands or other commands as a dictionary encoded in json.
It receives button press from the serial port and displays what it gets.
"""
import argparse
import json
import math
import re
import serial
import sys
import time
from aioconsole import ainput
import asyncio
import click

color_names = {
    "aqua": (0, 255, 255),
    "black": (0, 0, 0),
    "blue": (0, 0, 255),
    "green": (0, 128, 0),
    "orange": (255, 165, 0),
    "pink": (240, 32, 128),
    "purple": (128, 0, 128),
    "red": (255, 0, 0),
    "white": (255, 255, 255),
    "yellow": (255, 255, 0),
}


def setup_serial(port, channel):
    """
    Helper to connect and reconnet to the serial channel
    """
    if channel is None:
        try:
            channel = serial.Serial(port)
            channel.timeout = 0.05
        except Exception as ex:
            print(ex)
            channel = None
    return channel


def error_serial(channel):
    """
    Helper to handle serial errors
    """
    if channel != None:
        channel.close()
        channel = None
        print("Exception on read, did the board disconnect ?")
    return None


async def read_serial(port):
    """
    Loop reading the serial IN and treat the message with a print
    """
    print("read_serial", port)
    channel = None
    while True:
        channel = setup_serial(port, channel)
        line = None
        try:
            line = channel.readline()[:-2]
        except KeyboardInterrupt:
            print("KeyboardInterrupt - quitting")
            exit()
        except Exception:
            channel = error_serial(channel)
            await asyncio.sleep(1)
            continue

        data = {}
        if line != b"":
            try:
                data = json.loads(line.decode("utf8"))
            except Exception:
                data = {"raw": line.decode("utf8")}

        # identifier
        if "id" in data:
            ident = data["id"]
        else:
            ident = "??"

        # receive button information and print it out
        if "buttons" in data:
            for button in data["buttons"]:
                if button["status"] == "RELEASED":
                    print(f"Button {button['id']} clicked on {ident}")

        # temperature
        if "temperature" in data:
            temp = data["temperature"]
            print(f"Temperature {ident}: {temp}°C")

        # unidentified data sent by the board, helps with testing
        if "raw" in data:
            print(f"Board {ident} sent: {data['raw']}")

        await asyncio.sleep(0.1)


async def send_serial(port):
    """
    Loop on a data provider (here a user prompt) and send the data.
    """
    print("send_serial", port)
    channel = None
    while True:
        channel = setup_serial(port, channel)
        try:
            print(f"Sending Hello {port}")
            channel.write(json.dumps("Hello").encode("utf8"))
        except Exception as ex:
            print(ex)
            channel = error_serial(channel)
        await asyncio.sleep(2)


@click.command()
@click.argument("serial_ports", nargs=-1,)
def main(serial_ports):
	if len(serial_ports) == 0:
		click.secho("No port specified", fg="red")
	else:
		for port in serial_ports:
			asyncio.ensure_future(read_serial(port))
			asyncio.ensure_future(send_serial(port))
		asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
	main()
