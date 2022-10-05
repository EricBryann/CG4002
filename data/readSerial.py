import serial
import time

ser = serial.Serial('/dev/cu.usbmodem1101')
ser.flushInput()

i = 50
t_end = time.time() + 15
print("Wait for 15 secs before reading data")
while(time.time() < t_end):
    continue
    
while True:
    f1 = open("shield/ypr" + str(i) + ".txt", "a")
    f2 = open("shield/accel" + str(i) + ".txt", "a")
    ser.flushInput()
    ser.flushOutput()
    print("Start your action for file " + str(i))

    #t_end = time.time() + 3
    while True:
        try:
            ser_bytes = ser.readline()
            decoded_bytes = ser_bytes.decode("utf-8")
            yprAccel = decoded_bytes.split("||")
            print(yprAccel[0])
            print(yprAccel[1])
            f1.write(yprAccel[0] + "\n")
            f2.write(yprAccel[1])
        except:
            print("Stop taking data")
            break

    t_end = time.time() + 5
    print("Put down your hand to reset")
    while time.time() < t_end:
        continue
    i += 1
