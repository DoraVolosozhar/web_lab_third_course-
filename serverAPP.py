import socket
import json
import threading
import time
import datetime
import argparse


class Server:
    def __init__(self, host, port, delay):
        self.socket = socket.socket()
        self.host = host
        self.port = port

        self.delay = delay
        self.timer_flag = False
        self.timer_start = 0
        self.clients = {}
        self.mutex = threading.Lock()

    def timer(self):
        self.timer_start = datetime.datetime.now()
        timing = time.time()

        while True:
            if time.time() - timing < self.delay:
                time.sleep(0.5)
                continue

            self.send_clients()
            timing = time.time()

    def handler(self, client, addr):
        client.send('You are connected!'.encode('utf-8'))
        info = client.recv(1024).decode('utf-8')
        self.add_client(client, addr, json.loads(info))

        while True:
            try:
                client.recv(1).decode('utf-8')  # Пингуем
                time.sleep(0.5)
            except ConnectionResetError:
                self.del_client(addr)
                break

    def add_client(self, client, addr, data):
        print(addr)
        self.mutex.acquire()
        self.clients[addr] = {
            "client": client,
            "connected": datetime.datetime.now(),
            "id": data["id"]
        }
        self.mutex.release()

    def del_client(self, addr):
        self.mutex.acquire()
        client = self.clients.pop(addr, None)
        client["client"].close()
        print(f'Client {client["id"]} {addr} disconnected!')
        self.mutex.release()

    def get_client(self, addr):
        self.mutex.acquire()
        client = self.clients[addr]
        self.mutex.release()

        return client

    def send_clients(self):
        self.mutex.acquire()

        clients = []
        timer = self.timer_start.strftime("%Y-%m-%d %H:%M:%S")
        for addr, client in self.clients.items():
            clients.append({
                "name": client["id"],
                "addr": addr,
                "connected": client["connected"].strftime("%Y-%m-%d %H:%M:%S"),
                "timer": timer
            })

        raw_str = json.dumps(clients)
        for _, client in self.clients.items():
            client["client"].send(bytes(raw_str, 'utf-8'))

        self.mutex.release()

    def receive(self):
        while True:
            client, address = self.socket.accept()
            print(f'Connected with {str(address)}')
            if not self.timer_flag:  # Если клиент подключился, а таймер не запущен - запускаем его
                timer_thread = threading.Thread(target=self.timer)
                timer_thread.daemon = True
                timer_thread.start()
                self.timer_flag = True
            # Запускаем обработчик клиента в отдельном потоке
            handler_thread = threading.Thread(target=self.handler, args=(client, address))
            handler_thread.daemon = True
            handler_thread.start()

    def run(self):
        print('Server started...')
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)

        try:
            main_thread = threading.Thread(target=self.receive)
            main_thread.daemon = True
            main_thread.start()
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            print("Shutting down server....")


def cmdline_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("host", type=str, help="Server host")
    p.add_argument("port", type=int, help="Server port")
    p.add_argument("-d", "--delay", type=int, default=12, help="Server delay")

    return p.parse_args()


if __name__ == '__main__':
    args = cmdline_args()
    Server(args.host, args.port, args.delay).run()


