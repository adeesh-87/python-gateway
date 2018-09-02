import serial


coordInitStream = bytearray.fromhex("10 02 16 00 00 00 00 00 00 00 00 02 02 00 00 10 03 3F")
print coordInitStream
with serial.Serial("/dev/ttyS0", 57600, timeout=10) as ser:
    ser.write(coordInitStream)
    x = ser.read(100)
    print x
    ser.close()
