import threading
import socket


class ReceiveFromRelayNode:
    def __init__(self) -> None:
        self.SERVER = 'localhost'   # Get IP Address of this device
        self.PORT = 5254            #8080
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
        i = 101
        connection.settimeout(1.5)
        # Receive Message from RelayNode
        while True:

            f1 = open('../dataset/real/train/imu1/end/ypr_r' + str(i) + ".txt", "w")
            f2 = open("../dataset/real/train/imu1/end/accel_r" + str(i) + ".txt", "w")
            print("Start your action for file " + str(i))
            while True:
                try:
                    message_length_in_byte = (connection.recv(self.HEADER)).decode(self.FORMAT)
                    message_length_in_int = 0
                    if message_length_in_byte:
                        message_length_in_int = int(message_length_in_byte)
                    message = connection.recv(message_length_in_int).decode(self.FORMAT)

                    message = message[8:].split(', "')
                    message = [e.strip() for e in message]
                    message = [e.strip('"') for e in message]
                    message = [e.strip(']') for e in message]
                    message = [e.strip('"') for e in message]
                    message = [float(e)/100 for e in message]

                    Accel = message[0:3]
                    ypr = message[3:]
                    print(ypr)
                    print(Accel)
                    # print(str(ypr)[1:-1])
                    f1.write(str(ypr)[1:-1] + '\n')
                    f2.write(str(Accel)[1:-1] + '\n')
                except:
                    print("Stop taking data")
                    break

            i += 1

    def run(self):
        print("STARTING - Server is starting...")
        self.server.listen()
        print(f"LISTENING - Server is listening on {self.SERVER} {self.PORT}")

        while True:
            connection, address = self.server.accept()
            self.handle_client(connection, address)


receive_from_relay_node = ReceiveFromRelayNode()
receive_from_relay_node.run()
