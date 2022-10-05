import serial
ser = serial.Serial('/dev/cu.usbmodem1401')
ser.flushInput()

f1 = open("grenade/ypr10.txt", "a")
f2 = open("grenade/accel10.txt", "a")

while True:
    try:
        ser_bytes = ser.readline()
        decoded_bytes = ser_bytes.decode("utf-8")
        #print(decoded_bytes, end="")
        yprAccel = decoded_bytes.split("||")
        print(yprAccel[0])
        print(yprAccel[1])
        f1.write(yprAccel[0] + "\n")
        f2.write(yprAccel[1])
    except:
        print("Keyboard Interrupt")
        break
