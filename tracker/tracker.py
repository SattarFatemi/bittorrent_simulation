import socket
import threading
import json
import time


class Tracker:
    def __init__(self, ip='127.0.0.1', port=6771):
        self.ip = ip
        self.port = port
        self.files = {}  # {filename: {peer_id: peer_address}}
        self.chunks_data = {}  # {filename: int}
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
        num_chunks = message.get('num_chunks')

        if command == 'share':
            print(f"{peer_id} sharing {filename} at {peer_address}")
            with self.lock:
                if filename not in self.files:
                    self.files[filename] = {}
                    self.chunks_data[filename] = 0
                self.files[filename][peer_id] = peer_address
                self.chunks_data[filename] = num_chunks
            print(f"{peer_id} shared {filename} at {peer_address}")
            s.sendto(b'OK', addr)

        elif command == 'get':
            print(f"{peer_id} getting {filename}")

            self.gc()

            with self.lock:
                if filename in self.files:
                    peers = list(self.files[filename].values())
                    data = {
                        'peers': peers,
                        'num_chunks': self.chunks_data[filename],
                    }
                    response = json.dumps(data)
                    s.sendto(response.encode(), addr)
                else:
                    s.sendto(b'File not found', addr)

            print(f"{peer_id} got {filename}")

        elif command == 'alive':
            with self.lock:
                if peer_id not in self.peers:
                    self.peers[peer_id] = 0
                self.peers[peer_id] = time.time()
                print(f"{peer_id} is alive")


if __name__ == "__main__":
    tracker = Tracker()
    tracker.start()
