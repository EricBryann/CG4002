import socket
import json
import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import time

SERVER = 'localhost' #"192.168.1.80" # socket.gethostbyname(socket.gethostname()) # Get IP Address of this device
PORT = 8989
ADDRESS = (SERVER, PORT)
HEADER = 64 #
FORMAT = 'utf-8'
key = "PLSPLSPLSPLSWORK"

# Create a Socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
client.connect(ADDRESS)

_player = dict()
_player['hp']               = 100
_player['action']           = 'none'
_player['bullets']          = 6
_player['grenades']         = 2
_player['shield_time']      = 3
_player['shield_health']    = 0
_player['num_deaths']       = 0
_player['num_shield']       = 3

player = dict()
player['p1'] = _player
player['p2'] = _player

data = json.dumps(player)

plaintext_bytes = pad(data.encode("utf-8"), 16)

secret_key_bytes = key.encode("utf-8")
cipher = AES.new(secret_key_bytes, AES.MODE_CBC)
iv_bytes = cipher.iv

ciphertext_bytes = cipher.encrypt(plaintext_bytes)
message = base64.b64encode(iv_bytes + ciphertext_bytes)

m = str(len(message))+'_'

try:
    client.sendall(m.encode("utf-8"))
    client.sendall(message)
except OSError:
    print("Connection terminated")


for i in range(20):
    #input("Please send dummy data: ")
    time.sleep(1)
    print(client.recv(2048).decode("utf-8"))
try:
    client.sendall(m.encode("utf-8"))
    client.sendall(message)
except OSError:
   print("Connection terminated")