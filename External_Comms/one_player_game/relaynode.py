import random
import socket
import json
import sshtunnel

# 172.31.214.173 - PGP
# 192.168.1.80  - Science

SERVER = 'localhost' 
PORT = 6200
ADDRESS = (SERVER, PORT)
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "[DISCONNECTED]"

_packet = dict()
_packet['ax'] = 0.0000
_packet['ay'] = 0.0000
_packet['az'] = 0.0000
_packet['gx'] = 0.0000
_packet['gy'] = 0.0000
_packet['gz'] = 0.0000

packet = dict()
packet['sensor_readings'] = _packet


def get_random_readings():
    _packet['ax'] = random.uniform(-20.0, 20.0)
    _packet['ay'] = random.uniform(-20.0, 20.0)
    _packet['az'] = random.uniform(-20.0, 20.0)
    _packet['gx'] = random.uniform(-150.0, 150.0)
    _packet['gy'] = random.uniform(-150.0, 150.0)
    _packet['gz'] = random.uniform(-150.0, 150.0)
    packet = list(_packet.values())
    # packet['sensor_readings'] = _packet

    return packet

def send(message, client):
    message = message.encode(FORMAT)
    message_length = len(message)
    # print(message_length)
    send_length = str(message_length).encode(FORMAT)
    print(send_length)
    
    # Add padding
    send_length += b' ' * (HEADER - len(send_length))
    print(send_length)
    client.send(send_length)
    client.send(message)
    print(message)
    print(client.recv(HEADER).decode(FORMAT))

def main():
    SUNFIRE_USERNAME = "likexuan"
    SUNFIRE_PASSWORD = "Zy980714"
    XILINX_USERNAME = "xilinx"
    XILINX_PASSWORD = "xilinx"

    SUNFIRE = "stu.comp.nus.edu.sg" 
    XILINX = "192.168.95.222"
    LOCAL_HOST = 'localhost'

    SSH_PORT = 22
    PORT = 6200
    
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

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDRESS)

    while True:
        global packet
        packet_temp = []
        # input("Please press enter to send a random dummy packet!")
        for i in range(20):
            packet_temp.append(get_random_readings())
        data = json.dumps(packet_temp)
        send(data, client)
        print(f"Packet has sent to Ultra96 -  {data}")

if __name__ == "__main__":
    main()
