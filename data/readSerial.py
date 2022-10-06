import serial
import time

"""
To generate data, connect Arduino Beetle with your laptop using the USB to micro-USB cable, then check your port number.

Then when you have changed to the correct port, run this python code in your terminal, you will first have 15 seconds to
prepare, then when you see the "Start your action for file x" prompt, perform your action. 

When you finished an action, press CTRL C one time and shake your hand a bit to flush the input, this will be counted as
one data.

Then you need to wait until the next "Start your action for file x appears, then you do the action again.

For each person, please help me generate at least 100 data for each action (grenade, reload, shield, end game movement),
the more action you generated the better our model accuracy :D

Btw, make sure when you wear the wristband with sensor, the IMU sensor (the blue colour one) is facing outwards (which
means that battery is at the right, not left!)

Thank you!!!!!
"""

# for Windows, go to Arduino IDE to see which COM is used, then change below code to
# ser = serial.Serial('COM3') # for example it is COM3

# for Mac, go to terminal, use the command ls /dev/cu.usbmodem then press TAB and see which one appears, copy the whole
# thing to the code below:
ser = serial.Serial('COM3')
ser.flushInput()

# change this i variable to rename the data file, for example if you have trained 20 data and stopped. After a while
# if you want to generate data again, can change the name of i to say 21, so that it will continue with ypr21.txt.
i = 1
t_end = time.time() + 15
print("Wait for 15 secs before reading data")
while(time.time() < t_end):
    continue
    
while True:
    # change the file name below to collect each data, for each person, you need to collect:
    # train/grenade/ypr_(your name)         -> f1
    # train/grenade/accel_(your name)       -> f2
    # train/reload/ypr_(your name)          -> f1
    # train/reload/accel_(your name)        -> f2
    # train/shield/ypr_(your name)          -> f1
    # train/shield/accel_(your name)        -> f2
    # train/end/ypr_(your name)             -> f1
    # train/end/accel_(your name)           -> f2
    # train/noise/ypr_(your name)           -> f1
    # train/noise/accel_(your name)         -> f2
    # test/grenade/ypr_(your name)          -> f1
    # test/grenade/accel_(your name)        -> f2
    # test/reload/ypr_(your name)           -> f1
    # test/reload/accel_(your name)         -> f2
    # test/shield/ypr_(your name)           -> f1
    # test/shield/accel_(your name)         -> f2
    # test/end/ypr_(your name)              -> f1
    # test/end/accel_(your name)            -> f2
    # test/noise/ypr_(your name)            -> f1
    # test/noise/accel_(your name)          -> f2
    # To fill in (your name), can follow this:
    # Eric: e
    # ShuHao: s
    # KeXuan: k
    # Vignesh: v
    # RuiYang: r
    # eg: f1 = open("train/shield/ypr_r.txt", "a")
    # if you receive message saying that you do not have the directory, can create the folder with the name first.
    f1 = open("train/reload/ypr" + str(i) + ".txt", "a")
    f2 = open("train/reload/accel" + str(i) + ".txt", "a")
    ser.flushInput()
    ser.flushOutput()
    print("Start your action for file " + str(i))

    #t_end = time.time() + 3
    while True:
        try:
            ser_bytes = ser.readline()
            decoded_bytes = ser_bytes.decode("utf-8")
            yprAccel = decoded_bytes.split("||")
            print(yprAccel[0])  # if you are using MAC, use print(yprAccel[0] + '\n') to format the text file
            print(yprAccel[1])
            f1.write(yprAccel[0])
            f2.write(yprAccel[1])
        except:
            print("Stop taking data")
            break

    t_end = time.time() + 5
    print("Put down your hand to reset")
    while time.time() < t_end:
        continue
    i += 1
