import socket
import threading
import json
import os


class Peer:
    def __init__(self, peer_id, tracker_ip='127.0.0.1', tracker_port=6771, listen_port=52611):
        self.peer_id = peer_id
        self.tracker_ip = tracker_ip
        self.tracker_port = tracker_port
        self.listen_port = listen_port
        self.files = {}
        self.lock = threading.Lock()

    def start(self):
        threading.Thread(target=self.listen).start()

    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', self.listen_port))
            s.listen(5)
            print(f"Peer {self.peer_id} listening on 127.0.0.1:{self.listen_port}")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_request, args=(conn, addr)).start()

    def handle_request(self, conn, addr):
        data = conn.recv(1024).decode()
        filename, chunk_id = data.split(',')
        chunk_id = int(chunk_id)
        with self.lock:
            chunk = self.files[filename][chunk_id]
        conn.send(chunk)
        conn.close()

    def share(self, filename):
        with open(filename, 'rb') as f:
            chunks = [f.read(1024) for _ in iter(lambda: f.read(1024), b'')]
        with self.lock:
            self.files[filename] = chunks

        message = json.dumps({
            'command': 'share',
            'filename': filename,
            'peer_id': self.peer_id,
            'peer_address': f'127.0.0.1:{self.listen_port}'
        }).encode()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(message, (self.tracker_ip, self.tracker_port))

    def get(self, filename):
        message = json.dumps({
            'command': 'get',
            'filename': filename,
            'peer_id': self.peer_id,
            'peer_address': f'127.0.0.1:{self.listen_port}'
        }).encode()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(message, (self.tracker_ip, self.tracker_port))
            data, _ = s.recvfrom(1024)
            peers = json.loads(data.decode())

        chunks = []
        for peer in peers:
            ip, port = peer.split(':')
            port = int(port)
            for chunk_id in range(len(self.files[filename])):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((ip, port))
                    s.send(f"{filename},{chunk_id}".encode())
                    chunk = s.recv(1024)
                    chunks.append(chunk)

        with open(f"downloaded_{filename}", 'wb') as f:
            for chunk in chunks:
                f.write(chunk)


if __name__ == "__main__":
    peer = Peer(peer_id='peer1')
    peer.start()
    peer.share('testfile.txt')
    peer.get('testfile.txt')
