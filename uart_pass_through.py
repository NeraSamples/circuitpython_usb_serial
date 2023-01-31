"""
boot.py
	import usb_cdc
	usb_cdc.enable(data=True)
"""

import board
import usb_cdc

uart = board.UART()
usb = usb_cdc.data

while True:
	if uart.in_waiting:
		data = uart.read(uart.in_waiting)
		usb.write(data)
	if usb.in_waiting:
		data = usb.read(usb.in_waiting)
		uart.write(data)
