import socket
import threading
import json
import time


class Tracker:
    def __init__(self, ip='127.0.0.1', port=6771):
        self.ip = ip
        self.port = port
        self.files = {}  # {filename: {peer_id: peer_address}}
        self.lock = threading.Lock()
        self.peers = {}

    def clean(self, peer_id):
        with self.lock:
            for file in self.files.values():
                if peer_id in file:
                    del file[peer_id]

        return

    def gc(self):
        for peer in self.peers:
            if self.peers[peer] < time.time() - 30:
                self.clean(peer)

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((self.ip, self.port))
            print(f"Tracker listening on {self.ip}:{self.port}")
            while True:
                data, addr = s.recvfrom(1024)
                threading.Thread(target=self.handle_request, args=(data, addr, s)).start()

    def handle_request(self, data, addr, s):

        message = json.loads(data.decode())
        command = message['command']
        filename = message.get('filename')
        peer_id = message.get('peer_id')
        peer_address = message.get('peer_address')

        if command == 'share':
            with self.lock:
                if filename not in self.files:
                    self.files[filename] = {}
                self.files[filename][peer_id] = peer_address
            print(f"{peer_id} sharing {filename} at {peer_address}")
            s.sendto(b'OK', addr)

        elif command == 'get':
            self.gc()

            with self.lock:
                if filename in self.files:
                    peers = list(self.files[filename].values())
                    response = json.dumps(peers)
                    s.sendto(response.encode(), addr)
                else:
                    s.sendto(b'File not found', addr)

        elif command == 'alive':
            with self.lock:
                if peer_id not in self.peers:
                    self.peers[peer_id] = 0
                self.peers[peer_id] = time.time()


if __name__ == "__main__":
    tracker = Tracker()
    tracker.start()
