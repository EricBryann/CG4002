import random
import socket
import json
import sshtunnel

# 172.31.214.173 - PGP
# 192.168.1.80  - Science

SERVER = 'localhost' 
PORT = 5200
ADDRESS = (SERVER, PORT)
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "[DISCONNECTED]"

_packet = dict()
_packet['shoot'] = False
_packet['hit'] = False
_packet['g_scope'] = 0.0000
_packet['a_meter'] = 0.0000

packet = dict()
packet['p1_sensor_readings'] = _packet


def get_random_readings(packet):
    is_shoot = random.choice([True, False])
    is_hit = random.choice([True, False])
    _packet['shoot'] = is_shoot
    _packet['hit'] = is_hit
    _packet['g_scope'] = random.uniform(0, 180.0)
    _packet['a_meter'] = random.uniform(0, 10.0)
    packet = dict()
    packet['p1_sensor_readings'] = _packet

    return packet

def send(message, client):
    message = message.encode(FORMAT)
    message_length = len(message)
    send_length = str(message_length).encode(FORMAT)
    
    # Add padding
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
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
    PORT = 5200
    
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
        input("Please press enter to send a random dummy packet!")
        packet = get_random_readings(packet)
        data = json.dumps(packet)
        send(data, client)
        print(f"Packet P1 has sent to Ultra96 -  {data}")

if __name__ == "__main__":
    main()