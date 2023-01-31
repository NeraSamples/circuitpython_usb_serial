"""
Read the Serial port to receive color data for the neopixel.
This uses a 4-neopixel Neopixel Trinkey

Example use:
echo "0,0,40:0,40,0:20,20,0:40,0,0" > /dev/cu.usbmodem144443133
for i in {1..255}; do echo "0,0,$i:0,$i,0:$i,$i,0:$i,0,0" > /dev/cu.usbmodem144443133; sleep 0.1; done
"""

import board
import time
import usb_cdc

################################################################
# init board's LEDs for visual output
# replace with your own pins and stuff
################################################################

pix = None
if hasattr(board, "NEOPIXEL"):
    import neopixel
    pix = neopixel.NeoPixel(board.NEOPIXEL, 4)
    pix.fill((32, 16, 0))
else:
    print("This board is not equipped with a Neopixel.")

################################################################
# loop-y-loop
################################################################

while True:
    # read the secondary serial line by line when there's data
    if usb_cdc.data.in_waiting > 0:
        data_in = usb_cdc.data.readline().strip()

        # try to convert the data to a list of colors
        colors = None
        if len(data_in) > 0:
            try:
                colors = [
                    [
                        int(x)
                        for x in color.split(b",")
                    ]
                    for color in data_in.split(b":")
                ]
            except Exception as ex:
                print("Error:", ex)
                colors = None

        # interpret
        if colors:
            for index, color in enumerate(colors):
                try:
                    pix[index] = color
                except Exception as ex:
                    print("Error:", ex, index,color)

    time.sleep(0.01)
