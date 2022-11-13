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

GRENADE = 'grenade'
RELOAD = 'reload'
SHIELD = 'shield'
NONE = 'none'
LOGOUT = 'logout'
SHOOT = 'shoot'

PORT_1 = 5256
PORT_2 = 5257

EVAL_IP = '137.132.92.184'
EVAL_PORT = 9999

DATA_TO_ACCEPT_FOR_AI = 25
DATA_TO_ACCEPT_FOR_AI_MIN = 20

queue_to_ai = queue.Queue()
queue_p1_game_logic = queue.Queue()
queue_p2_game_logic = queue.Queue()
queue_to_eval = queue.Queue()
queue_to_visualizer = queue.Queue()

class ReceiveFromRelayNode:
    def __init__(self, port) -> None:
        # self.SERVER = 'localhost'   # Get IP Address of this device
        self.SERVER = 'localhost'
        self.PORT = port
        self.ADDRESS = ('', self.PORT)
        self.HEADER = 64 
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = "[DISCONNECTED]"

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDRESS)
    
    def run(self):
        print("STARTING - Server is starting...")
        self.server.listen()
        print(f"LISTENING - Server is listening on {self.SERVER} {self.PORT}")

        connection, address = self.server.accept()

        print(f"[NEW CONNECTION] {address} is now established.")

        # Receive Message from RelayNode
        while True:
            message_length_in_byte = (connection.recv(self.HEADER)).decode(self.FORMAT)
            if message_length_in_byte:
                message_length_in_int = int(message_length_in_byte)
                message = connection.recv(message_length_in_int).decode(self.FORMAT)

                queue_to_ai.put(message)

                if message == self.DISCONNECT_MESSAGE:
                    break

                # print(f"{address}: {message}")
                connection.send("Message received!".encode(self.FORMAT))

        connection.close()

class Player_Action():
    SHOOT_THRESHOLD = 0.5

    def __init__(self, player, player_queue, none_string, grenade_string, shoot_symbol, shot_symbol, IMU_symbol):
        self.player = player
        self.player_queue = player_queue
        self.none_string = none_string
        self.grenade_string = grenade_string

        self.IMU_symbol = IMU_symbol
        self.shoot_symbol = shoot_symbol
        self.shot_symbol = shot_symbol

        self.last_action_recorded_time = 0
        self.should_clear_player_data = False
        self.last_shoot_shot_recorded_time = 0
        self.is_player_shot = False
        self.is_player_grenade_hit = False
        self.imu_list = []

    def get_action_string_from_FPGA(self):
        action_int = get_output_from_FPGA(self.imu_list)
        if action_int == 0:
            return GRENADE
        
        if action_int == 1:
            return RELOAD
        
        if action_int == 2:
            return SHIELD

        if action_int == 3:
            return NONE

        return LOGOUT

    def send_player_data_to_FPGA(self):
        action = self.get_action_string_from_FPGA()

        print(f"Action {self.player} Predicted by AI - {action}")

        if action == NONE:
            queue_to_visualizer.put(self.none_string)
            return
            
        self.last_action_recorded_time = time()
        self.should_clear_player_data = True

        if action == GRENADE:
            queue_to_visualizer.put(self.grenade_string)
            return

        self.player_queue.put(action)
    
    def handle_shoot_shot_window(self, other_player):
        if  self.last_shoot_shot_recorded_time != 0 and time() - self.last_shoot_shot_recorded_time > self.SHOOT_THRESHOLD:
            self.player_queue.put(SHOOT)
            print(f"Action {self.player} - shoot {other_player.is_player_shot}")
            self.last_shoot_shot_recorded_time = 0


    def handle_sensor_readings_timeout(self, other_player):
        if len(self.imu_list) > DATA_TO_ACCEPT_FOR_AI_MIN:
            self.send_player_data_to_FPGA()
        
        self.imu_list = []
        self.handle_shoot_shot_window(other_player)
    
    def check_data_clear(self):
        if time() - self.last_action_recorded_time >= 1:
            self.should_clear_player_data = False
    
    def handle_input(self, input_symbol, sensor_readings, other_player):
        if input_symbol == self.IMU_symbol:
            if self.should_clear_player_data:
                return
            if len(self.imu_list) < DATA_TO_ACCEPT_FOR_AI:
                self.imu_list.append(sensor_readings)
            else:
                self.send_player_data_to_FPGA()
                self.imu_list = []
            
        if input_symbol == self.shoot_symbol:
            if time() - self.last_shoot_shot_recorded_time <= self.SHOOT_THRESHOLD:
                self.player_queue.put(SHOOT)
                print(f"Action {self.player} - shoot {other_player.is_player_shot}")
                self.last_shoot_shot_recorded_time = 0
            else:
                self.last_shoot_shot_recorded_time = time()

        #B
        if input_symbol == self.shot_symbol:
            self.is_player_shot = True
            if time() - other_player.last_shoot_shot_recorded_time <= self.SHOOT_THRESHOLD:
                other_player.player_queue.put(SHOOT)
                print(f"Action {other_player.player} - shoot {self.is_player_shot}")
                other_player.last_shoot_shot_recorded_time = 0
            else:
                other_player.last_shoot_shot_recorded_time = time()

class FPGA():
    TIMEOUT_THRESHOLD = 0.35

    def __init__(self, player_1, player_2):
        self.player_1 = player_1
        self.player_2 = player_2
    
    def parse_sensor_readings(self, sensor_readings):
        letter = sensor_readings[4]

        sensor_readings = sensor_readings[8:].split(', "')
        sensor_readings = [e.strip() for e in sensor_readings]
        sensor_readings = [e.strip('"') for e in sensor_readings]
        sensor_readings = [e.strip(']') for e in sensor_readings]
        sensor_readings = [e.strip('"') for e in sensor_readings]
        try:
            sensor_readings = [float(e)/100 for e in sensor_readings]
        except:
            raise Exception()

        return letter, sensor_readings

    def run(self):
        while True:
            try:
                sensor_readings = queue_to_ai.get(timeout = self.TIMEOUT_THRESHOLD)
                self.player_1.handle_shoot_shot_window(self.player_2)
                self.player_2.handle_shoot_shot_window(self.player_1)
            except:
                self.player_1.handle_sensor_readings_timeout(self.player_2)
                self.player_2.handle_sensor_readings_timeout(self.player_1)
                continue
            
            self.player_1.check_data_clear()
            self.player_2.check_data_clear()

            try:
                letter, sensor_readings = self.parse_sensor_readings(sensor_readings)
            except Exception as e: 
                print(e)
                continue

            self.player_1.handle_input(letter, sensor_readings, self.player_2)
            self.player_2.handle_input(letter, sensor_readings, self.player_1)

global_game_state_in_dict = dict()
need_update = False

class GameEngine():
    def __init__(self, player_1, player_2) -> None:
        self.player_1 = player_1
        self.player_2 = player_2
        self.game_state = GameState()
        self.game_state_in_dict = self.game_state.get_dict()

    def run(self):
        global global_game_state_in_dict
        global need_update
        while True:
            action_p1 = ''
            action_p2 = ''
            if queue_p1_game_logic.qsize() != queue_p2_game_logic.qsize() :
                print("logic queue unequal.")
                print("p1: ", queue_p1_game_logic.qsize())
                print("p2: ", queue_p2_game_logic.qsize())
                # while not queue_p1_game_logic.empty():
                #     queue_p1_game_logic.get()
                # while not queue_p2_game_logic.empty():
                #     queue_p2_game_logic.get()
                queue_p1_game_logic.queue.clear()
                queue_p2_game_logic.queue.clear()
            else:
                action_p1 = queue_p1_game_logic.get()
                action_p2 = queue_p2_game_logic.get()

                print(f"Game Engine has received - {action_p1} | {action_p2}")

            if need_update:
                need_update = False
                
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

            if action_p1 != '' and action_p2 != '':
                print("Send to eval server", action_p1, action_p2, self.player_1.is_player_shot, self.player_2.is_player_shot, self.player_1.is_player_grenade_hit, self.player_2.is_player_grenade_hit)
                self.game_state.update_players(action_p1, action_p2, self.player_1.is_player_shot, self.player_2.is_player_shot, self.player_1.is_player_grenade_hit, self.player_2.is_player_grenade_hit)
                self.game_state_in_dict = self.game_state.get_dict()
                
                self.player_1.is_player_shot = False
                self.player_2.is_player_shot = False
                self.player_1.is_player_grenade_hit = False
                self.player_2.is_player_grenade_hit = False

                queue_to_eval.put(self.game_state_in_dict)
                queue_to_visualizer.put(self.game_state_in_dict)

class EvalClient():
    def __init__(self) -> None:
        #self.SERVER = '172.31.214.173' PGP
        #self.SERVER = '172.25.107.232' COM3 
        #self.SERVER = socket.gethostbyname(socket.gethostname())
        #self.SERVER = '137.132.92.184'

        self.SERVER = EVAL_IP
        self.PORT = EVAL_PORT
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
        global need_update
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
            need_update = True
            global_game_state_in_dict = correct_game_state_in_dict

class MQTT():
    def __init__(self, player_1, player_2) -> None:
        #self.mqttBroker ="test.mosquitto.org"
        #self.mqttBroker ="broker.emqx.io"
        self.publisher = mqtt.Client("Publisher")
        self.subscriber = mqtt.Client("Subcriber")
        self.player_1 = player_1
        self.player_2 = player_2
        self.has_received_from_visualizer = False

    def on_message(self, client, userdata, message):
        grenade_hit = str(message.payload.decode("utf-8"))

        if grenade_hit is not None:
            self.has_received_from_visualizer = True
            if grenade_hit == 't1':
                self.player_1.is_player_grenade_hit = True
                self.player_1.player_queue.put(GRENADE)
            elif grenade_hit == 'f1':
                self.player_1.is_player_grenade_hit = False
                self.player_1.player_queue.put(GRENADE)
            elif grenade_hit == 't2':
                self.player_2.is_player_grenade_hit = True
                self.player_2.player_queue.put(GRENADE)
            elif grenade_hit == 'f2':
                self.player_2.is_player_grenade_hit = False
                self.player_2.player_queue.put(GRENADE)

        print(f'Visualizer has responded Grenade Result - {grenade_hit}')

def mqtt_run():
    VISUALIZER_RESPONSE_TIMEOUT = 4
    def handle_visualizer_not_responding(grenade_query):
        time = 0
        while not mqtt1.has_received_from_visualizer and time < VISUALIZER_RESPONSE_TIMEOUT:
            sleep(1)
            time += 1

        if not mqtt1.has_received_from_visualizer:
            mqtt1.has_received_from_visualizer = True
            grenade_hit = ''
            # guess that grenade will not hit
            if grenade_query[1] == '1':
                player_1.is_player_grenade_hit = False
                player_1.player_queue.put(GRENADE)
                grenade_hit = 'f1'
            else:
                player_2.is_player_grenade_hit = False
                player_2.player_queue.put(GRENADE)
                grenade_hit = 'f2'

            print(f'Guessing Grenade Result - {grenade_hit}')


    while True:
        grenade_query_or_game_state = queue_to_visualizer.get()

        if type(grenade_query_or_game_state) == str:
            mqtt1.publisher.connect(BROKER, port=1883)
            mqtt1.publisher.publish("Capstone/Ultra96Send", grenade_query_or_game_state)

            if grenade_query_or_game_state != 'n1' and grenade_query_or_game_state != 'n2':
                grenade_query = grenade_query_or_game_state
                print("Ultra96 has sent - Grenade Query")

                mqtt1.has_received_from_visualizer = False
                mqtt1.subscriber.connect(BROKER, port=1883)
                mqtt1.subscriber.loop_start()

                mqtt1.subscriber.subscribe("Capstone/VisualizerReply")
                mqtt1.subscriber.on_message = mqtt1.on_message

                t = threading.Thread(target = handle_visualizer_not_responding, args=[grenade_query])
                t.start()

                if mqtt1.has_received_from_visualizer:
                    mqtt1.subscriber.loop_stop()
                    
                t.join()

        else:
            game_state_in_json = json.dumps(grenade_query_or_game_state)
            mqtt1.publisher.connect(BROKER, port=1883)
            mqtt1.publisher.publish("Capstone/Ultra96Send", game_state_in_json)
            print(f"Ultra96 has published - {grenade_query_or_game_state}")            

player_1 = Player_Action('p1', queue_p1_game_logic, 'n1', 'g1', 'A', 'B', 'C')
player_2 = Player_Action('p2', queue_p2_game_logic, 'n2', 'g2', 'D', 'E', 'F')
receive_from_relay_node_1 = ReceiveFromRelayNode(PORT_1)
receive_from_relay_node_2 = ReceiveFromRelayNode(PORT_2)
fpga = FPGA(player_1, player_2)
game_engine = GameEngine(player_1, player_2)
eval_client = EvalClient()
mqtt1 = MQTT(player_1, player_2)
mqtt1.publisher.connect(BROKER, port=1883)
mqtt1.subscriber.connect(BROKER, port=1883)


t1 = threading.Thread(target = receive_from_relay_node_1.run)
t2 = threading.Thread(target = receive_from_relay_node_2.run)
t3 = threading.Thread(target = fpga.run)
t4 = threading.Thread(target = game_engine.run)
t5 = threading.Thread(target = eval_client.run)
t6 = threading.Thread(target = mqtt_run)

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
t6.start()

t1.join()
t2.join()
t3.join()
t4.join()
t5.join()
t6.join()
