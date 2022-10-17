import threading
from bluepy import btle
from threading import Thread
from bluepy.btle import BTLEDisconnectError
from sys import getsizeof
from time import time, sleep
from struct import unpack
import queue
import json
import socket
import sshtunnel

SERVER = 'localhost' 
PORT = 5127
ADDRESS = (SERVER, PORT)
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "[DISCONNECTED]"

queue_to_ultra96 = queue.Queue()

def send(message, client):
    message = message.encode(FORMAT)
    message_length = len(message)
    send_length = str(message_length).encode(FORMAT)
    
    # Add padding
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(HEADER).decode(FORMAT))


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

        if len(data) == 13:
            data = list(unpack('!chhhhhh', data))
            for i in data:
                self.queue.append(str(i))
        else:
            print("Error")


        while len(self.queue) >= 7:
            self.message = self.queue[:7]
            self.queue = self.queue[7:]

            queue_to_ultra96.put(self.message)
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


'''
class MyDelegate(btle.DefaultDelegate):

    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.message_received = 0
        self.ended = False
        self.message = ""
        self.total_message_size = 0
        self.start_time = 0
        self.end_time = 0
        # ... initialise here

    def handleNotification(self, cHandle, data):
        if self.start_time == 0:
            self.start_time = time()
        data = str(data, "utf-8")   #decode packet
        self.total_message_size += getsizeof(data)
        if self.message_received < 5001:
            for i in data:
                if i == '<':    # start marker, start of data packet
                    self.message = ""   # Reset message, get ready for new message
                self.message += i
                if i == '>':    # end marker, end of message.
                    self.message_received += 1
                    # print(self.message_received, ":", self.message)
                    queue_to_ultra96.put(self.message)
                    self.message = ""   #Reset message, get ready for future packets.
        elif self.ended==False:
            self.end_time = time()
            time_elapsed = self.end_time - self.start_time
            print(f"End of transmission, total size transferred: {round((self.total_message_size/1000)/time_elapsed, 5)}kB/s")
            self.ended = True
'''

class SendRaw:
  def __init__(self) -> None:
    pass

  def run(self):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDRESS)
    while True:
	    global packet
	    packet = queue_to_ultra96.get()
	    data = json.dumps(packet)
	    send(data, client)
	    print(f"Packet has sent to Ultra96 -  {data}")

# Initialisation  -------
def connectBLE(mac_address):
    p = btle.Peripheral(mac_address)    # Searches for beetle
    p.setDelegate(MyDelegate())

    service_uuid = "0000dfb0-0000-1000-8000-00805f9b34fb"
    svc = p.getServiceByUUID(service_uuid)
    char_uuid = "0000dfb1-0000-1000-8000-00805f9b34fb"
    ch = svc.getCharacteristics(char_uuid)[0]

    # Setup to turn notifications on, e.g.
    setup_data = b"\x01\00"
    p.writeCharacteristic(ch.valHandle + 1, setup_data)
    c = svc.getCharacteristics()[0]
    c.write(bytes("start".encode()))       # Sends handshake to arduino

    # Main loop --------
    while True:
        if p.waitForNotifications(5.0):
            # handleNotification() was called
            c.write(bytes("ok".encode()))
        else:
            #Resend initial handshake after 5 seconds if no notification from Arduino.
            c.write(bytes("start".encode()))


# Create SSH Tunneling
SUNFIRE_USERNAME = "likexuan"
SUNFIRE_PASSWORD = "Zy980714"
XILINX_USERNAME = "xilinx"
XILINX_PASSWORD = "xilinx"

SUNFIRE = "stu.comp.nus.edu.sg" 
XILINX = "192.168.95.222"
LOCAL_HOST = 'localhost'

SSH_PORT = 22

tunnel1 = sshtunnel.open_tunnel(
    ssh_address_or_host=(SUNFIRE, SSH_PORT), 
    remote_bind_address=(XILINX, SSH_PORT), 
    ssh_username=SUNFIRE_USERNAME, 
    ssh_password=SUNFIRE_PASSWORD, 
)
tunnel1.start()
print(f'Connection to tunnel1 {SUNFIRE}:{SSH_PORT} established!')
print("LOCAL PORT:", tunnel1.local_bind_port)
    
tunnel2 = sshtunnel.open_tunnel(
        ssh_address_or_host=(LOCAL_HOST, tunnel1.local_bind_port), 
        remote_bind_address=(LOCAL_HOST, PORT),
        ssh_username=XILINX_USERNAME, 
        ssh_password=XILINX_PASSWORD, 
        local_bind_address=(LOCAL_HOST, PORT), 
        
)
tunnel2.start()
print(f"Connection to tunnel2 {XILINX}:{PORT} established!")
print("LOCAL PORT:", tunnel2.local_bind_port)


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

receive_raw_data = SendRaw()
t1 = threading.Thread(target=receive_raw_data.run)
t1.start()
#t1.join()

while True:
    #'''
    if not beetle1.is_alive():
        try:
            beetle1 = Thread(target=connectBLE, args=["d0:39:72:bf:c1:c9"])
            beetle1.start()
        except BTLEDisconnectError:
            pass
    #'''

    #'''
    if not beetle2.is_alive():
        try:
            beetle2 = Thread(target=connectBLE, args=["d0:39:72:bf:ca:c0"])
            beetle2.start()
        except BTLEDisconnectError:
            pass
    #'''

    #'''
    if not beetle3.is_alive():
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


