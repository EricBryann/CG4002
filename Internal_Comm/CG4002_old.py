from bluepy import btle
from threading import Thread
from bluepy.btle import BTLEDisconnectError
from struct import *
from random import *
from sys import getsizeof
from time import time, sleep


class ScanDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        pass


class MyDelegate(btle.DefaultDelegate):

    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.message_received = 0
        self.ended = False
        self.queue = []
        self.message = []
        self.total_message_size = 0
        self.start_time = 0
        self.end_time = 0
        self.counter = 1
        # ... initialise here

    def handleNotification(self, cHandle, data):
        #self.queue += data


        # data = str(data, "utf-8")
        if len(data) == 13:
            data = list(unpack('!chhhhhh', data))
            for i in data:
                self.queue.append(str(i))

        if len(self.queue) >= 7:
            self.message = self.queue[:7]
            self.queue = self.queue[7:]

            print(self.counter, self.message)
            self.counter += 1

        # if self.start_time == 0:
        #     self.start_time = time()
        #
        # # print("test")
        # data = str(data, "utf-8")   #decode packet
        # self.message += data
        # if data[-1] == ">":
        #     print(self.message)
        #     self.message = ""

        # self.total_message_size += getsizeof(data)
        # if self.message_received < 5001:
        #     #print ("rw:",data)
        #     # self.message = data
        #     # self.message_received += 1
        #     # print(self.message_received, ":", self.message)
        #     # self.message = ""
        #     for i in data:
        #         if i == '<':    # start marker, start of data packet
        #             # if len(self.message) > 0:
        #             #     print("error:", len(self.message), self.message)
        #             #     exit(0)
        #             self.message = ""   # Reset message, get ready for new message
        #         self.message += i
        #         if i == '>': #or len(self.message)>=80:    # end marker, end of message.
        #             self.message_received += 1
        #             print(self.message_received, ":", self.message)
        #             self.message = ""   #Reset message, get ready for future packets.
        # elif self.ended==False:
        #     self.end_time = time()
        #     time_elapsed = self.end_time - self.start_time
        #     print(f"End of transmission, total size transferred: {round((self.total_message_size/1000)/time_elapsed, 5)}kB/s")
        #     self.ended = True


# Initialisation  -------
def connectBLE(mac_address):
    # print(mac_address)
    p = btle.Peripheral(mac_address)    # Searches for beetle
    p.setDelegate(MyDelegate())

    # Setup to turn notifications on, e.g.
    service_uuid = "0000dfb0-0000-1000-8000-00805f9b34fb"
    svc = p.getServiceByUUID(service_uuid)
    char_uuid = "0000dfb1-0000-1000-8000-00805f9b34fb"
    ch = svc.getCharacteristics(char_uuid)[0]

    setup_data = b"\x01\00"
    p.writeCharacteristic(ch.valHandle + 1, setup_data)
    c = svc.getCharacteristics()[0]
    c.write(bytes("start".encode()))       # Sends handshake to arduino

    # Main loop --------
    while True:
        if p.waitForNotifications(5):
            # handleNotification() was called
            c.write(bytes("ok".encode()))
        else:
            c.write(bytes("start".encode()))




#'''
try:
    beetle1 = Thread(target=connectBLE, args=["d0:39:72:bf:c1:c9"])
    beetle1.start()
except:
    print("failed to connect to beetle 1")
#'''

#'''
try:
    beetle2 = Thread(target=connectBLE, args=["d0:39:72:bf:ca:c0"])
    beetle2.start()
except:
    print("failed to connect to beetle 2")
#'''

#'''
try:
    beetle3 = Thread(target=connectBLE, args=["d0:39:72:bf:c1:e2"])
    beetle3.start()
except:
    print("failed to connect to beetle 3")
#'''

'''
try:
    beetle4 = Thread(target=connectBLE, args=["d0:39:72:bf:c6:26"])
    beetle4.start()
except:
    print("failed to connect to beetle 4")
'''

while True:
    #'''
    if not beetle1.is_alive():
        print("beetle4-3")
        try:
            beetle1 = Thread(target=connectBLE, args=["d0:39:72:bf:c1:c9"])
            beetle1.start()
        except BTLEDisconnectError:
            pass
    #'''

    #'''
    if not beetle2.is_alive():
        print("beetle2")
        try:
            beetle2 = Thread(target=connectBLE, args=["d0:39:72:bf:ca:c0"])
            beetle2.start()
        except BTLEDisconnectError:
            pass
    #'''

    #'''
    if not beetle3.is_alive():
        print("beetle3")
        try:
            beetle3 = Thread(target=connectBLE, args=["d0:39:72:bf:c1:e2"])
            beetle3.start()
        except BTLEDisconnectError:
            pass

    #'''

    '''
    if not beetle4.is_alive():
        try:
            beetle4 = Thread(target=connectBLE, args=["d0:39:72:bf:c6:26"])
            beetle4.start()
        except BTLEDisconnectError:
            pass
    '''
