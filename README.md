## Serial sample codes

Circuitpython enables communication with the host computer it is connected to via a USB serial port. These examples show how to do it in different basic scenarios on the Circuitpython side and example host-side scripts using python. You can of course use any programming language on the host side.


- [The documentation of the module](https://docs.circuitpython.org/en/latest/shared-bindings/usb_cdc/index.html#module-usb_cdc) list all the functions available.
- [This guide uses the usb_cdc module to send sensor data to the PC](https://learn.adafruit.com/diy-trinkey-no-solder-air-quality-monitor/circuitpython).
- [Another guide uses serial to communicate "remote procedure calls"](https://learn.adafruit.com/macropad-remote-procedure-calls-over-usb-to-control-home-assistant).


## The Second Serial Channel

The default serial channel also hosts the REPL, so you can't communicate through it while looking at the REPL, and some characters can interrupt the code (ctrl-C) so it's not suited for binary data.

Since Circuitpython 7, it is possible to enable a second serial channel for binary communication without limitations and without losing the REPL, so you can still see debug prints and errors.

Using the data serial channel requires creating a `boot.py` file containing the following code. The file requires a reset to be active after it's created the first time (it runs when the board boots).

- [`boot.py`](boot.py)

```py
import usb_cdc
usb_cdc.enable(data=True)
```

### Caveat

Some chips, like the ESP32-S2 and S3 have a limited available amount of USB endpoints so you will need to disable the console or the drive to enable data. You could use the web workflow to access the REPL or the drive during development.

Note that you can use the REPL serial port with `usb_cdc.console`, but usb_cdc (and the data channel) is not available on boards that don't have USB OTG, like the original ESP32 or the ESP32-C3 and C6.

## Host Serial Ports

The serial ports of your boards are available on your computer, depending on the operating system, for example `COM*` on Windows, `/dev/cu.usbmodem*` on MacOS, `/dev/ttyACM*` on linux.

To help find the serial ports (REPL or data) on the host side, the `find_serial_port.py` script lists the ports per board and per type (if present). It requires the `adafruit_board_toolkit` module.
```
pip3 install adafruit_board_toolkit
```

- [`find_serial_port.py`](find_serial_port.py)

I also developped a command line python tool to help gather information on the connected devices called [discotool](https://github.com/Neradoc/discotool). It can be used as a library to find a board and its ports by serial number, drive name, and other criteria (see the examples in the discotool repository).

## The Example Scripts

These scripts use a loop in Circuitpython to communicate with the host computer without blocking. That means that you can run some other code in the same loop, that doesn't have to wait until it receives a message from the host.

Some parts use the json library, not always available on small SAMD21 (M0) boards, due to lack of space, but they can still be used as templates to insert your own code instead.

These scripts use `readline()`, assuming that the host always sends entire lines ending in a return character. Of course you don't have to do that and can read N bytes at a time, blocking or not.

Each example has 3 files.

- The "host" script that must be run on the computer with python 3, by giving the serial port of the board as argument to the command line. The script requires pyserial to be installed.
```
pip3 install pyserial
```
- Two board codes that can be renamed to `code.py` or imported from it.
    - One that will listen or output to the REPL (or console) serial channel.
    - One that will listen or output to the data serial channel.

## Serial Send

Send data from the host computer to the board.

The host computer sends cycling color data regularly to the board, using JSON encoding to change the color on the board. For testing purposes the code will print out the color to the REPL.

The board is expected to have a built-in neopixel. If it doesn't, replace it with external neopixels, a dotstar or a screen, etc. It might require to install the `neopixel` library from the library bundle, though it is included in the Circuitpython firmware on some boards.

- [`serial_send-host.py`](serial_send/serial_send-host.py)
- [`serial_send_data-code.py`](serial_send/serial_send_data-code.py)
- [`serial_send_repl-code.py`](serial_send/serial_send_repl-code.py)

## Serial Read

Read data sent by the board to the host computer.

The board is sending sensor data to the serial port, trying the CPU temperature first, and sending a randomly fluctuating value if it was not available. You would of course change the `generate_some_data` function to read a sensor connected to or embeded on the board.

The values are sent in a simple text format that can be displayed in the Mu graphics panel to draw a line graph over time. The host computer code just prints out the values.

- [`serial_read-host.py`](serial_read/serial_read-host.py)
- [`serial_read_data-code.py`](serial_read/serial_read_data-code.py)
- [`serial_read_repl-code.py`](serial_read/serial_read_repl-code.py)

## Serial Exchange

Bidirectional serial communication.

This shows a two-way communication using JSON data between the board and the host computer. The computer code uses the `asyncio` module for asynchronous execution and prompts the user for a color by name (list in the code) or `(r,g,b)` values and sends it to the board, which will display the color on it's built-in neopixel. The keyword `blink` will make the on-board monochrome LED (if any) blink once.

The board sends button presses that the host prints out. It makes a best effort to detect an existing built-in button. For example the A button on the Circuit Playground boards, or the boot button on ESP boards.

The board is expected to have a built-in neopixel. If it doesn't, replace it with external neopixels, a dotstar, a screen, etc. It might require to install the relevant libraires (`neopixel`, `adafruit_dotstar`, etc.) from the library bundle.

- [`serial_exchange-host.py`](serial_exchange/serial_exchange-host.py)
- [`serial_exchange_data-code.py`](serial_exchange/serial_exchange_data-code.py)
- [`serial_exchange_repl-code.py`](/serial_exchangeserial_exchange_repl-code.py)
