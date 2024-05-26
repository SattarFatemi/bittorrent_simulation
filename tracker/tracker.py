import socket
import threading
import json


class Tracker:
    def __init__(self, ip='127.0.0.1', port=6771):
        self.ip = ip
        self.port = port
        self.files = {}  # {filename: {peer_id: peer_address}}
        self.lock = threading.Lock()

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
            with self.lock:
                if filename in self.files:
                    peers = list(self.files[filename].values())
                    response = json.dumps(peers)
                    s.sendto(response.encode(), addr)
                else:
                    s.sendto(b'File not found', addr)


if __name__ == "__main__":
    tracker = Tracker()
    tracker.start()
