import socket
import threading
import queue
import random
import json
import base64
from audioop import add
from concurrent.futures import thread
from re import L, S
from tkinter.tix import TCL_TIMER_EVENTS
from tracemalloc import start
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import paho.mqtt.client as mqtt
from random import randrange, uniform
from GameState import GameState
from time import time, sleep
from mlp import get_output_from_FPGA

BROKER ="broker.hivemq.com"

queue_to_ai = queue.Queue()
queue_p1_game_logic = queue.Queue()
queue_p2_game_logic = queue.Queue()
queue_to_eval = queue.Queue()
queue_to_visualizer = queue.Queue()

class ReceiveFromRelayNode:
    def __init__(self) -> None:
        self.SERVER = 'localhost'   # Get IP Address of this device
        self.PORT = 5257            #8080
        self.PORT2 = 5256
        self.ADDRESS = ('', self.PORT)
        self.ADDRESS2 = ('', self.PORT2)
        self.HEADER = 64 
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = "[DISCONNECTED]"
        # Server
    

        # TCP Create a socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print("server")
        self.server2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print("server2")

        # Bind the socket to an address
        self.server.bind(self.ADDRESS)
        # print("bind")
        self.server2.bind(self.ADDRESS2)
        # print("bind2")


    def handle_client(self, connection, address):
        print(f"[NEW CONNECTION] {address} is now established.")

        # Receive Message from RelayNode
        while True:
            message_length_in_byte = (connection.recv(self.HEADER)).decode(self.FORMAT)
            # print(message_length_in_byte)
            if message_length_in_byte:
                message_length_in_int = int(message_length_in_byte)
                message = connection.recv(message_length_in_int).decode(self.FORMAT)
                
                queue_to_ai.put(message)

                if message == self.DISCONNECT_MESSAGE:
                    break

                # print(f"{address}: {message}")
                connection.send("Message received!".encode(self.FORMAT))

        connection.close()

    def run(self):
        # print(t5.is_alive())
        print("STARTING - Server is starting...", flush = True)
        self.server.listen()
        print(f"LISTENING - Server is listening on {self.SERVER} {self.PORT}", flush = True)
        self.server2.listen()
        print(f"LISTENING - Server is listening on {self.SERVER} {self.PORT2}", flush = True)

        while True:
            connection, address = self.server.accept()
            # print("connect", flush = True)
            thread1 = threading.Thread(target = self.handle_client, args = (connection, address))
            # print("thread", flush = True)
            thread1.start()
            # print("start", flush = True)
            connection2, address2 = self.server2.accept()
            # print("connect2", flush = True)
            thread2 = threading.Thread(target = self.handle_client, args = (connection2, address2))
            # print("thread2", flush = True)
            thread2.start()
            # print("start2", flush = True)
            count = threading.active_count() - 1
            print(f"ACTIVE CONNECTIONS - {str(count)}") 


p1_shot = False
p2_shot = False

class FPGA():

    lastRecordedTime = 0
    TIME_THRESHOLD = 0.35

    p1NeedToClear = False
    p2NeedToClear = False


    def __init__(self) -> None:
        pass
    

    # Get AI predicited actions
    def sendP1DataToFPGA(self, imu_list_p1):
        action_int_p1 = get_output_from_FPGA(imu_list_p1)
        if action_int_p1 == 0:
            action_p1 = 'grenade'
        elif action_int_p1 == 1:
           action_p1 = 'reload'
        elif action_int_p1 == 2:
            action_p1 = 'shield'
        elif action_int_p1 == 3:
            action_p1 = 'none'
        else:
            action_p1 = 'logout'
        
        imu_list_p1 = []
       
        print(f"Action P1 Predicted by AI - {action_p1}")
        if action_p1 != 'none':
            if action_p1 != 'grenade':
                queue_p1_game_logic.put(action_p1)
            else:
                grenade_query_p1 = 'g1'
                # queue_to_visualizer.queue.clear()
                queue_to_visualizer.put(grenade_query_p1)
        else:
            queue_to_visualizer.put('n1')

        # stopReceivingData = False
        if action_int_p1 != 3:
            self.lastRecordedTime = time()
            self.p1NeedToClear = True
    

    def sendP2DataToFPGA(self, imu_list_p2):
        action_int_p2 = get_output_from_FPGA(imu_list_p2)
        if action_int_p2 == 0:
            action_p2 = 'grenade'
        elif action_int_p2 == 1:
           action_p2 = 'reload'
        elif action_int_p2 == 2:
            action_p2 = 'shield'
        elif action_int_p2 == 3:
            action_p2 = 'none'
        else:
            action_p2 = 'logout'
        
        imu_list_p2 = []
       
        print(f"Action P2 Predicted by AI - {action_p2}")
        if action_p2 != 'none':
            if action_p2 != 'grenade':
                queue_p2_game_logic.put(action_p2)
            else:
                grenade_query_p2 = 'g2'
                # queue_to_visualizer.queue.clear()
                queue_to_visualizer.put(grenade_query_p2)
        else:
            queue_to_visualizer.put('n2')

        # stopReceivingData = False
        if action_int_p2 != 3:
            self.lastRecordedTime = time()
            self.p2NeedToClear = True

    def run(self):
        # print(t5.is_alive())
        action_p1 = ''
        action_p2 = ''
        i = 0

        lastAETimeRecorded = 0
        lastBDTimeRecorded = 0
        SHOOT_THRESHOLD = 0.5
        global p1_shot 
        global p2_shot
        p1_shot = False
        p2_shot = False
        imu_list_p1 = []
        imu_list_p2 = []
        

        while True:
            try:
                sensor_readings = queue_to_ai.get(timeout=self.TIME_THRESHOLD)
                if lastAETimeRecorded != 0 and time() - lastAETimeRecorded > SHOOT_THRESHOLD:
                    queue_p1_game_logic.put("shoot")
                    # print(f"Action P1 Predicted by AI - {action_p1} {p2_shot}")
                    print(f"Action P1 - shoot {p2_shot}")
                    lastAETimeRecorded = 0
                if lastBDTimeRecorded != 0 and time() - lastBDTimeRecorded > SHOOT_THRESHOLD:
                    queue_p2_game_logic.put("shoot")
                    # print(f"Action P2 Predicted by AI - {action_p2} {p1_shot}")
                    print(f"Action P2 - shoot {p1_shot}")
                    lastBDTimeRecorded = 0
                    
            except:
                if len(imu_list_p1) > 20:
                    self.sendP1DataToFPGA(imu_list_p1)
                
                if len(imu_list_p2) > 20:
                    self.sendP2DataToFPGA(imu_list_p2)
                
                imu_list_p1 = []
                imu_list_p2 = []

                if lastAETimeRecorded != 0 and time() - lastAETimeRecorded > SHOOT_THRESHOLD:
                    queue_p1_game_logic.put("shoot")
                    print(f"Action P1 - shoot {p2_shot}")
                    # print(f"Action P1 Predicted by AI - {action_p1} {p2_shot}")
                    lastAETimeRecorded = 0
                if lastBDTimeRecorded != 0 and time() - lastBDTimeRecorded > SHOOT_THRESHOLD:
                    queue_p2_game_logic.put("shoot")
                    print(f"Action P2 - shoot {p1_shot}")
                    # print(f"Action P2 Predicted by AI - {action_p2} {p1_shot}")
                    lastBDTimeRecorded = 0

                continue

            if self.p1NeedToClear:
                currTime = time()
                if currTime - self.lastRecordedTime >= 1:
                    self.p1NeedToClear = False

            if self.p2NeedToClear:
                currTime = time()
                if currTime - self.lastRecordedTime >= 1:
                    self.p2NeedToClear = False
                

            
            i+=1
            # print(f"FPGA has received - {sensor_readings}")
            letter = sensor_readings[4]

            sensor_readings = sensor_readings[8:].split(', "')
            sensor_readings = [e.strip() for e in sensor_readings]
            sensor_readings = [e.strip('"') for e in sensor_readings]
            sensor_readings = [e.strip(']') for e in sensor_readings]
            sensor_readings = [e.strip('"') for e in sensor_readings]
            try:
                sensor_readings = [float(e)/100 for e in sensor_readings]
            except:
                continue

            # imu sensor readings for P1
            if letter == 'C':
                if self.p1NeedToClear:
                    continue
                if len(imu_list_p1) < 25:                   
                    imu_list_p1.append(sensor_readings)
                if len(imu_list_p1) >= 25:
                    self.sendP1DataToFPGA(imu_list_p1)
                    imu_list_p1= []
            
            # imu sensor readings for P2
            if letter == 'F':
                if self.p2NeedToClear:
                    continue
                if len(imu_list_p2) < 25:
                    imu_list_p2.append(sensor_readings)
                if len(imu_list_p2) >= 25:
                    self.sendP2DataToFPGA(imu_list_p2)
                    imu_list_p2= []
            

            # P1 shoot
            if letter == 'B':
                p1_shot = True
                if time() - lastBDTimeRecorded <= SHOOT_THRESHOLD:
                    queue_p2_game_logic.put("shoot")
                    print(f"Action P2 - shoot {p1_shot}")
                    lastBDTimeRecorded = 0
                else:
                    lastBDTimeRecorded = time()
            
            if letter == 'E':
                p2_shot = True
                if time() - lastAETimeRecorded <= SHOOT_THRESHOLD:
                    queue_p1_game_logic.put("shoot")
                    print(f"Action P1- shoot {p2_shot}")
                    lastAETimeRecorded = 0
                else:
                    lastAETimeRecorded = time()

            if letter == 'A':
                #action_p1 = 'shoot'
                if time() - lastAETimeRecorded <= SHOOT_THRESHOLD:
                    queue_p1_game_logic.put("shoot")
                    print(f"Action P1- shoot {p2_shot}")
                    lastAETimeRecorded = 0
                else:
                    lastAETimeRecorded = time()

             # P2 shoot
            if letter == 'D':
                # action_p2 = 'shoot'
                if time() - lastBDTimeRecorded <= SHOOT_THRESHOLD:
                    queue_p2_game_logic.put("shoot")
                    print(f"Action P2 - shoot {p1_shot}")
                    lastBDTimeRecorded = 0
                else:
                    lastBDTimeRecorded = time()

                      
global_game_state_in_dict = dict()
needUpdate = False

class GameEngine():

    def __init__(self) -> None:
        self.p1_action = 'none'
        self.p2_action = 'none'
        self.p1_hit = False
        self.p2_hit = False
        self.p1_g_hit = False
        self.p2_g_hit = False
        self.game_state = GameState()
        self.game_state_in_dict = self.game_state.get_dict()
    

    def run(self):
        
        # print(t5.is_alive())
        global needUpdate
        global p1_shot
        global p2_shot

        while True:
            action_or_grenade_result_p1 = ''
            action_or_grenade_result_p2 = ''
            self.p1_hit = p1_shot
            self.p2_hit = p2_shot
            #print(f"P1 hit - {p1_shot}")
            #print(f"P2 hit - {p2_shot}")

            if queue_p1_game_logic.qsize() != queue_p2_game_logic.qsize() :
                print("logic queue unequal.")
                print("p1: ", queue_p1_game_logic.qsize())
                print("p2: ", queue_p2_game_logic.qsize())
                queue_p1_game_logic.queue.clear()
                queue_p2_game_logic.queue.clear()
            else:
                action_or_grenade_result_p1 = queue_p1_game_logic.get() # True, False, action string
                action_or_grenade_result_p2 = queue_p2_game_logic.get()

                print(f"Game Engine has received - {action_or_grenade_result_p1} | {action_or_grenade_result_p2}")

            # Overwrite the gamestate to be ground truth received from eval_server
            if needUpdate == True:
                
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
            if action_or_grenade_result_p1 != '' and action_or_grenade_result_p2 != '':
                if type(action_or_grenade_result_p1) == str:
                    self.p1_action = action_or_grenade_result_p1
                else:
                    self.p1_action = 'grenade'
                    self.p2_g_hit = action_or_grenade_result_p1
                
                if type(action_or_grenade_result_p2) == str:
                    self.p2_action = action_or_grenade_result_p2
                else:
                    self.p2_action = 'grenade'
                    self.p1_g_hit = action_or_grenade_result_p2

                # Game Logic
                # Grenade -> opponent hp never -30 -> still remain problems
                self.game_state.update_players(self.p1_action, self.p2_action, self.p1_hit, self.p2_hit, self.p1_g_hit, self.p2_g_hit)
                self.game_state_in_dict = self.game_state.get_dict()
                p1_shot = False
                p2_shot = False
                self.p1_g_hit = False
                self.p1_g_hit = False
    
                # print("p1: ", queue_p1_game_logic.qsize())
                # print("p2: ", queue_p2_game_logic.qsize())
                
                queue_to_eval.put(self.game_state_in_dict)
                # print("Data published to eval.")
                queue_to_visualizer.put(self.game_state_in_dict)
            
        
          

class EvalClient():
    def __init__(self) -> None:
        #self.SERVER = '172.31.214.173' PGP
        #self.SERVER = '172.25.107.232' COM3 
        #self.SERVER = socket.gethostbyname(socket.gethostname())
        #self.SERVER = '137.132.92.184'

        # self.SERVER = 'localhost'
        # self.SERVER = '172.25.96.44'
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
                # self.stop()
            msg = data.decode("utf8")  # Decode raw bytes to UTF-8

        except ConnectionResetError:
            print('Connection Reset')
            # self.stop()
        return msg

    def run(self):
        # print(t5.is_alive())
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
            #print(f"Eval Client - has received {correct_game_state}")

            # re-calibration
            # Convert type str to dict
            correct_game_state_in_dict = json.loads(correct_game_state)
            needUpdate = True
            global_game_state_in_dict = correct_game_state_in_dict
            

            
            # Send to Visualizer - recalibration
            # queue_to_visualizer.put(correct_game_state_in_dict)

            # The whole process DONE!
            
class MQTT():

    global grenade_query

    def __init__(self) -> None:
        
        #self.mqttBroker ="test.mosquitto.org"
        #self.mqttBroker ="broker.emqx.io"
        self.publisher = mqtt.Client("Publisher")
        self.subscriber = mqtt.Client("Subcriber")
        # self.connected_flag = False
        
        # def on_connect(client, data, flags, rc):
        #     if rc == 0:
        #         self.connected_flag = True
        
        # self.publisher.on_connect = on_connect
        # self.publisher.connect(self.mqttBroker, port=1883)
        # while not self.connected_flag:
        #     print("connecting")
        #     sleep(1)

            
        # self.publisher.publish("Capstone/Ultra96Send", "n1") 
        
        self.grenade_query = 'g'
        # self.subscriber.connect(self.mqttBroker, port=1883)
        self.grenade_action_p1 = "g1"
        self.grenade_action_p2 = "g2"
        self.has_received = False

    def on_message(self, client, userdata, message):
        
        global grenade_query
        grenade_hit = str(message.payload.decode("utf-8"))

        if grenade_hit is not None:
            self.has_received = True
            if grenade_hit == 't1':
                grenade_hit = bool(True)
                queue_p1_game_logic.put(grenade_hit)
            elif grenade_hit == 'f1':
                    grenade_hit = bool(False)
                    queue_p1_game_logic.put(grenade_hit)
            elif grenade_hit == 't2':
                    grenade_hit = bool(True)
                    queue_p2_game_logic.put(grenade_hit)
            elif grenade_hit == 'f2':
                    grenade_hit = bool(False)
                    queue_p2_game_logic.put(grenade_hit)

        print(f'Visualizer has responded Grenade Result - {grenade_hit}')
       

    
def mqtt_run():
    # print("t5 is running")
    global grenade_query

    while True:
        # Two types of message str-grenade dict-game state
        grenade_query_or_game_state = queue_to_visualizer.get()
        
        if type(grenade_query_or_game_state) == str:
            if grenade_query_or_game_state == 'n1' or grenade_query_or_game_state =='n2':
                mqtt1.publisher.connect(BROKER, port=1883)
                # print("MQTT Publisher is connected")
                p = mqtt1.publisher.publish("Capstone/Ultra96Send", grenade_query_or_game_state)
                # print(f"Publish result: {p[0]}")
                # print("publish n1/n2")
            else:

                mqtt1.publisher.connect(BROKER, port=1883)
                # print("MQTT Publisher is connected")
                mqtt1.publisher.publish("Capstone/Ultra96Send", grenade_query_or_game_state)
                grenade_query = grenade_query_or_game_state
                print("Ultra96 has sent - Grenade Query")

                mqtt1.has_received = False
                mqtt1.subscriber.connect(BROKER, port=1883)
                # print("MQTT Subscriber is connected")
                mqtt1.subscriber.loop_start()

                mqtt1.subscriber.subscribe("Capstone/VisualizerReply")
                mqtt1.subscriber.on_message=mqtt1.on_message

            
                if mqtt1.has_received == True:
                    mqtt1.subscriber.loop_stop() 

        else:
            game_state_in_json = json.dumps(grenade_query_or_game_state)
            mqtt1.publisher.publish("Capstone/Ultra96Send", game_state_in_json)
            print(f"Ultra96 has published - {grenade_query_or_game_state}")            

receive_from_relay_node = ReceiveFromRelayNode()
fpga = FPGA()
game_engine = GameEngine()
eval_client = EvalClient()
mqtt1 = MQTT()
mqtt1.publisher.connect(BROKER, port=1883)
# print("MQTT Publisher is connected")
mqtt1.subscriber.connect(BROKER, port=1883)
# print("MQTT Subscriber is connected")

# mqtt1.publisher.publish("Capstone/Ultra96Send", "n1")

t1 = threading.Thread(target=receive_from_relay_node.run)
t2 = threading.Thread(target=fpga.run)
t3 = threading.Thread(target=game_engine.run)
t4 = threading.Thread(target=eval_client.run)
t5 = threading.Thread(target=mqtt_run)

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