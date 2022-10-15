import socket
import threading
from threading import Lock
import queue
import random
import json
import socket
import json
import base64
from audioop import add
from concurrent.futures import thread
from re import L
from turtle import hideturtle
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import paho.mqtt.client as mqtt
from random import randrange, uniform
from GameState import GameState
from mlp import get_output_from_FPGA
from time import time, sleep


queue_to_ai = queue.Queue()
queue_to_game_logic = queue.Queue()
queue_to_eval = queue.Queue()
queue_to_visualizer = queue.Queue()

stopReceivingData = False
lock = Lock()

class ReceiveFromRelayNode:
    # global stopReceivingData
    # global queue_to_ai
    def __init__(self) -> None:
        self.SERVER = 'localhost'   # Get IP Address of this device
        self.PORT = 5127         #8080
        self.ADDRESS = ('', self.PORT)
        self.HEADER = 64 
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = "[DISCONNECTED]"
        # Server

        # TCP Create a socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to an address
        self.server.bind(self.ADDRESS)


    def handle_client(self, connection, address):
        print(f"[NEW CONNECTION] {address} is now established.")

        # Receive Message from RelayNode
        while True:
            message_length_in_byte = (connection.recv(self.HEADER)).decode(self.FORMAT)
            # print (message_length_in_byte)
            if message_length_in_byte:
                message_length_in_int = int(message_length_in_byte)
                message = connection.recv(message_length_in_int).decode(self.FORMAT)
                
                # if not stopReceivingData:
                queue_to_ai.put(message)
                # else:
                    # queue_to_ai.queue.clear()
                # else:
                #     if not queue_to_ai.empty():
                #         queue_to_ai = queue.Queue()

                if message == self.DISCONNECT_MESSAGE:
                    break

                # print(f"{address}: {message}")
                connection.send("Message received!".encode(self.FORMAT))

        connection.close()

    def run(self):
        print("STARTING - Server is starting...")
        self.server.listen()
        print(f"LISTENING - Server is listening on {self.SERVER} {self.PORT}")

        while True:
            connection, address = self.server.accept()
            thread = threading.Thread(target = self.handle_client, args = (connection, address))
            thread.start()
            count = threading.active_count() - 1
            print(f"ACTIVE CONNECTIONS - {str(count)}") 

class FPGA():
    lastRecordedTime = 0
    TIME_THRESHOLD = 1
    shouldSleep = False

    def __init__(self) -> None:
        pass

    def sendDataToQueue(self, new_list):
        # print(new_list)
        # stopReceivingData = True
        action_int = get_output_from_FPGA(new_list)
        if action_int == 0:
            action = 'grenade'
        elif action_int == 1:
            action = 'reload'
        elif action_int == 2:
            action = 'shield'
        elif action_int == 3:
            action = 'none'
        else:
            action = 'logout'
        new_list = []
        # print(action_int)
        print(f"Action Predicated by AI - {action}")
        if action != 'none':
            if action != 'grenade':
                queue_to_game_logic.put(action)
            else:
                queue_to_visualizer.put(action)

        # stopReceivingData = False
        if action_int != 3:
            self.lastRecordedTime = time()
            self.shouldSleep = True

    def run(self):
        action = ''
        i = 0

        new_list = []

        while True:
            try:
                sensor_readings = queue_to_ai.get(timeout=self.TIME_THRESHOLD)
            except:
                if len(new_list) > 20:
                    self.sendDataToQueue(new_list)
                
                new_list = []
                continue

            if self.shouldSleep:
                # print("SLEEPING!")
                currTime = time()
                if currTime - self.lastRecordedTime >= 2.2:
                    self.shouldSleep = False
                else:
                    queue_to_ai.queue.clear()
                    continue

            i+=1
            # print(i)
            
            
            # print(f"FPGA has received - {sensor_readings}, {len(sensor_readings)}, {type(sensor_readings)}")

            letter = sensor_readings[4]
            # print(letter)
            
            sensor_readings = sensor_readings[8:].split(', "')
            sensor_readings = [e.strip() for e in sensor_readings]
            sensor_readings = [e.strip('"') for e in sensor_readings]
            sensor_readings = [e.strip(']') for e in sensor_readings]
            sensor_readings = [e.strip('"') for e in sensor_readings]
            sensor_readings = [float(e)/100 for e in sensor_readings]
            
            if letter == 'z':
                if len(new_list) < 25:
                    new_list.append(sensor_readings)
                if len(new_list) >= 25:
                    self.sendDataToQueue(new_list)
                    new_list = []
                    
                # self.lastRecordedTime = time()
    
            else:
                if letter == 'A':
                    action = 'shoot'
                
                if letter == "B":
                    action = 'shot'
                
                queue_to_game_logic.put(action)

                
global_game_state_in_dict = dict()
needUpdate = False
class GameEngine():
    global hit 
    def __init__(self) -> None:
        self.p1_action = 'none'
        self.p2_action = 'none'
        self.p1_hit = False
        self.p2_hit = False
        self.game_state = GameState()
        self.game_state_in_dict = self.game_state.get_dict()
  
    def run(self):
        global needUpdate
        while True:
            action_or_grenade_result = queue_to_game_logic.get()
            if type(action_or_grenade_result) == str:
                if action_or_grenade_result != 'shot':
                    self.p1_action = action_or_grenade_result
                else:
                    continue # do nothing, wait for next round
            else:
                self.p1_action = 'grenade'
                if  action_or_grenade_result == False: 
                    self.game_state.player_2.hp += 30
            
            if needUpdate:
                needUpdate = False

                self.game_state.player_1.hp = global_game_state_in_dict['p1']['hp']
                self.game_state.player_1.bullets = global_game_state_in_dict['p1']['bullets']
                self.game_state.player_1.grenades = global_game_state_in_dict['p1']['grenades']
                self.game_state.player_1.shield_time = global_game_state_in_dict['p1']['shield_time']
                self.game_state.player_1.shield_health = global_game_state_in_dict['p1']['shield_health']
                self.game_state.player_1.num_deaths = global_game_state_in_dict['p1']['num_deaths']
                self.game_state.player_1.num_shield = global_game_state_in_dict['p1']['num_shield']
                self.game_state.player_2.hp = global_game_state_in_dict['p2']['hp']
                self.game_state.player_2.bullets = global_game_state_in_dict['p2']['bullets']
                self.game_state.player_2.grenades = global_game_state_in_dict['p2']['grenades']
                self.game_state.player_2.shield_time = global_game_state_in_dict['p2']['shield_time']
                self.game_state.player_2.shield_health = global_game_state_in_dict['p2']['shield_health']
                self.game_state.player_2.num_deaths = global_game_state_in_dict['p2']['num_deaths']
                self.game_state.player_2.num_shield = global_game_state_in_dict['p2']['num_shield']

            self.game_state.update_players(self.p1_action, self.p2_action)
            self.game_state_in_dict = self.game_state.get_dict()
            queue_to_eval.put(self.game_state_in_dict)
            queue_to_visualizer.put(self.game_state_in_dict)
            print(f"Game Engine has received - {action_or_grenade_result}")
            

class EvalClient():
    def __init__(self) -> None:
        #self.SERVER = '172.31.214.173' PGP
        #self.SERVER = '172.25.107.232' COM3 
        #self.SERVER = socket.gethostbyname(socket.gethostname())

        # self.SERVER = 'localhost' 
        self.SERVER = '137.132.92.184'
        self.PORT = 9999
        self.ADDRESS = (self.SERVER, self.PORT)
        self.HEADER = 64
        self.FORMAT = 'utf-8'
        self.key = "PLSPLSPLSPLSWORK"
        
        # Create a socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        self.client.connect(self.ADDRESS)

    def recv_correct_game_state(self):
        game_state_received = None
        try:

            data = b''
            while not data.endswith(b'_'):
                _d = self.client.recv(1)
                if not _d:
                    data = b''
                    break
                data += _d
            if len(data) == 0:
                print('no more data from the client')
                self.stop()

            data = data.decode("utf-8")
            length = int(data[:-1])

            data = b''
            while len(data) < length:
                _d = self.client.recv(length - len(data))
                if not _d:
                    data = b''
                    break
                data += _d
            if len(data) == 0:
                print('no more data from the client')
                self.stop()
            msg = data.decode("utf8")  # Decode raw bytes to UTF-8

        except ConnectionResetError:
            print('Connection Reset')
            self.stop()
        return msg

    def run(self):
        global needUpdate
        global global_game_state_in_dict
        while True:
            game_state_in_dict = queue_to_eval.get()
            data = json.dumps(game_state_in_dict)

            plaintext_bytes = pad(data.encode("utf-8"), 16)

            secret_key_bytes = self.key.encode("utf-8")
            cipher = AES.new(secret_key_bytes, AES.MODE_CBC)
            iv_bytes = cipher.iv

            ciphertext_bytes = cipher.encrypt(plaintext_bytes)
            message = base64.b64encode(iv_bytes + ciphertext_bytes)

            m = str(len(message))+'_'

            try:
                self.client.sendall(m.encode("utf-8"))
                self.client.sendall(message)
                print("Eval Client - messages has sent out!")
            except OSError:
                print("Connection - has terminated")

            correct_game_state = self.recv_correct_game_state()
            print(f"Eval Client - has received {correct_game_state}")

            # Convert type str to dict
            correct_game_state_in_dict = json.loads(correct_game_state)
            global_game_state_in_dict = correct_game_state_in_dict
            needUpdate = True
            # print(type(correct_game_state_in_dict))

            
            # Send to Visualizer - recalibration
            queue_to_visualizer.put(correct_game_state_in_dict)

            # The whole process DONE!
            
class MQTT():
    def __init__(self) -> None:
        self.mqttBroker ="broker.hivemq.com"
        #self.mqttBroker ="mqtt.eclipseprojects.io"
        self.publisher = mqtt.Client("Publisher")
        self.publisher.connect(self.mqttBroker, port=1883) 
        self.greande_query = 'g'
        self.subscriber = mqtt.Client("Subcriber")
        self.subscriber.connect(self.mqttBroker, port=1883)
        self.grenade_action = "g"
        self.has_received = False

    def on_message(self, client, userdata, message):
        start_time = time()
        grenade_hit = str(message.payload.decode("utf-8"))
        if grenade_hit is not None:
            self.has_received = True
            if grenade_hit == 't':
                grenade_hit = bool(True)
            else:
                grenade_hit = bool(False)
        end_time = time()


        print(f'Visualizer has responded Grenade Result - {grenade_hit}')
        
        queue_to_game_logic.put(grenade_hit)


    def run(self):
        while True:
            # Two types of message str-grenade dict-game state
            grenade_query_or_game_state = queue_to_visualizer.get()
         
            if type(grenade_query_or_game_state) == str:
                self.publisher.publish("Capstone/Ultra96Send", (self.grenade_action))
                print("Ultra96 has sent - Grenade Query")

                self.has_received = False
                self.subscriber.loop_start()
                
                self.subscriber.subscribe("Capstone/VisualizerReply")
                self.subscriber.on_message=self.on_message

                if self.has_received == True:
                    self.subscriber.loop_stop()
                

            else:
                # game_state_in_json = json.dumps(grenade_query_or_game_state)
                self.publisher.publish("Capstone/Ultra96Send", json.dumps(grenade_query_or_game_state))
                print(f"Ultra96 has published - {grenade_query_or_game_state}")
                # Send to Visualizer DONE!!
            


receive_from_relay_node = ReceiveFromRelayNode()
fpga = FPGA()
game_engine = GameEngine()
eval_client = EvalClient()
mqtt = MQTT()

t1 = threading.Thread(target=receive_from_relay_node.run)
t2 = threading.Thread(target=fpga.run)
t3 = threading.Thread(target=game_engine.run)
t4 = threading.Thread(target=eval_client.run)
t5 = threading.Thread(target=mqtt.run)

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()

t1.join()
t2.join()
t3.join()
t4.join()
t5.join()