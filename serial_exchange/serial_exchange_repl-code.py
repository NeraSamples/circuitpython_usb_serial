"""
Listens to the REPL port, without using the usb_cdc module.
Receives color information and displays it on the NEOPIXEL.
Receives blink command and blinks once.
Sends button press and release.
"""

import board
import digitalio
import json
import time
import supervisor
import sys

################################################################
# select the serial REPL port
################################################################

serial = sys.stdin

################################################################
# init board's LEDs for visual output
# replace with your own pins and stuff
################################################################

pix = None
if hasattr(board, "NEOPIXEL"):
    import neopixel

    pix = neopixel.NeoPixel(board.NEOPIXEL, 1)
    pix.fill((32, 16, 0))
else:
    print("This board is not equipped with a Neopixel.")

led = None
for ledname in ["LED", "L", "RED_LED", "BLUE_LED"]:
    if hasattr(board, ledname):
        led = digitalio.DigitalInOut(getattr(board, ledname))
        led.switch_to_output()
        led.value = False
        print(ledname)
        break

################################################################
# init board's button for acknowledging user interaction
# replace with your own pins and stuff
# - the code tries its best to find a default button
# - two fixed default values on some boards (for my tests)
################################################################

# boards with buttons:
BUTTONS_CANDIDATES = [
    "BUTTON",
    "BUTTON_USR",
    "BUTTON_USER",
    "BUTTON_A",
    "BUTTON_X",
    "BUTTON_UP",
    "BUTTON1",
    "BUTTON_1",
    "BOOT",
    "BOOT0",
]
for btn_pin in BUTTONS_CANDIDATES:
    if hasattr(board, btn_pin):
        button = digitalio.DigitalInOut(getattr(board, btn_pin))
        button.switch_to_input(digitalio.Pull.UP)
        button_id = btn_pin
        break
else:  # no break
    """
    Change the BUTTON pin to match your setup, and button_id
    """
    # this is an example for the pico
    if hasattr(board, "GP3"):
        pin = board.GP3
    # this is an example for most boards/feathers
    elif hasattr(board, "A2"):
        pin = board.A2
    # pin = board.SOMEPIN
    button = digitalio.DigitalInOut(pin)
    button.switch_to_input(digitalio.Pull.UP)
    button_id = repr(pin).replace("board.", "")

################################################################
# prepare values for the loop
################################################################

if button:
    button_past = button.value

################################################################
# loop-y-loop
################################################################

while True:
    # add to that dictionary to send the data at the end of the loop
    data_out = {}

    # read the REPL serial line by line when there's data
    if supervisor.runtime.serial_bytes_available:
        data_in = serial.readline()

        # try to convert the data to a dict (with JSON)
        data = None
        if len(data_in) > 0:
            try:
                data = json.loads(data_in)
            except ValueError:
                data = {"raw": data_in}

        # interpret
        if isinstance(data, dict):

            # change the color of the neopixel
            if "color" in data:
                print(data["color"])
                if pix is not None:
                    pix.fill(data["color"])

            # blinking without sleep is left as an exercise
            if "blink" in data and led is not None:
                led.value = True
                time.sleep(0.25)
                led.value = False
                time.sleep(0.25)

    # read the buttons and send the info to the serial
    if button and button_past != button.value:
        button_past = button.value
        if not button.value:
            data_out["buttons"] = [{"status": "PRESSED", "id": button_id}]
        else:
            data_out["buttons"] = [{"status": "RELEASED", "id": button_id}]

    # send the data out once everything to be sent is gathered
    if data_out:
        print(json.dumps(data_out))

    time.sleep(0.1)
