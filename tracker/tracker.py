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
        self.logs = []

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
            with self.lock:
                if filename not in self.files:
                    self.files[filename] = {}
                    self.chunks_data[filename] = 0
                self.files[filename][peer_id] = peer_address
                self.chunks_data[filename] = num_chunks

            self.logs.append({
                'command': 'share',
                'peer_id': peer_id,
                'filename': filename,
                'timestamp': time.time(),
                'status': 'success'
            })
            s.sendto(b'OK', addr)

        elif command == 'get':
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
                    self.logs.append({
                        'command': 'get',
                        'peer_id': peer_id,
                        'filename': filename,
                        'peers': peers,
                        'timestamp': time.time(),
                        'status': 'success'
                    })
                else:
                    s.sendto(b'File not found', addr)
                    self.logs.append({
                        'command': 'get',
                        'peer_id': peer_id,
                        'filename': filename,
                        'timestamp': time.time(),
                        'status': 'failure'
                    })

        elif command == 'alive':
            with self.lock:
                if peer_id not in self.peers:
                    self.peers[peer_id] = 0
                self.peers[peer_id] = time.time()
                self.logs.append({
                    'command': 'alive',
                    'peer_id': peer_id,
                    'timestamp': time.time(),
                })

    def show_request_logs(self):
        for log in self.logs:
            if log['command'] in ['get', 'share']:
                print(log)

    def show_all_logs(self):
        for log in self.logs:
            print(log)

    def show_file_logs(self, filename):
        found = False
        for log in self.logs:
            if log.get('filename') == filename:
                print(log)
                found = True
        if not found:
            print(f"No logs found for file {filename}")

def main():
    tracker = Tracker()

    threading.Thread(target=tracker.start).start()

    while True:
        command = input("Enter command (logs request / logs-all / logs_file <filename> / exit): ").strip().split()
        if not command:
            continue
        if command[0] == "logs" and command[1] == "request":
            tracker.show_request_logs()
        elif command[0] == "logs-all":
            tracker.show_all_logs()
        elif command[0] == "logs_file" and len(command) == 3:
            tracker.show_file_logs(command[2])
        elif command[0] == "exit":
            print("Exiting...")
            break
        else:
            print("Invalid command. Please use 'logs request', 'logs-all', 'logs_file <filename>', or 'exit'.")

if __name__ == "__main__":
    main()
