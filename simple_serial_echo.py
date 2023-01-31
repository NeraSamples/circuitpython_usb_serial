import usb_cdc
serial = usb_cdc.data
badcode = False
while True:
    if serial.in_waiting:
        received = serial.read()
        try:
            data = received.decode().upper().encode()
            data = data.replace(b"\r",b"\r\n")
            data = b'<' + data + b'>'
            if badcode:
                data = b']' + data
                badcode = False
        except UnicodeError:
            if badcode:
                data = received
            else:
                data = b'[' + received
            badcode = True
        serial.write(data)
        # print(received)
    else:
        if badcode:
            badcode = False
            serial.write(b']')
