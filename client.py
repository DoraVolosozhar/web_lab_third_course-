import socket
import json
import threading
import time


class Client:
    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = port
        self.sock = socket.socket()

    def connect(self):
        try:
            handler_thread = threading.Thread(target=self.handler)
            handler_thread.daemon = True
            handler_thread.start()
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            print("Shutting down client....")
            self.disconnect()

    def handler(self):
        self.sock.connect((self.host, self.port))
        print(f'{self.name}: Conected to {self.host}:{self.port}')

        try:
            message = self.sock.recv(1024).decode('utf-8')
            if message != 'You are connected!':
                print(message)
                return

            self.send_info()
            while True:
                response = self.sock.recv(8192)
                raw = json.loads(response)

                m = f"{self.name} recieved: \n"
                for client in raw:
                    m += str(client) + "\n"
                print(m)

        except ConnectionResetError:
            print('Connection closed!')
            self.sock.close()
        
    def disconnect(self):
        self.sock.close()

    def send_info(self):
        raw = {"id": self.name}
        raw_str = json.dumps(raw)
        self.sock.send(bytes(raw_str, 'utf-8'))
