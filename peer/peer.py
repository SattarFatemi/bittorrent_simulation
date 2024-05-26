import argparse
import threading
import socket
import json
import time


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
        threading.Thread(target=self.send_alive).start()

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

    def send_alive(self):
        while True:
            self.alive()
            time.sleep(5)

    def alive(self):
        message = json.dumps({
            'command': 'alive',
            'peer_id': self.peer_id,
        }).encode()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(message, (self.tracker_ip, self.tracker_port))

    def share(self, filename):
        chunks = []
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                chunks.append(chunk)
        with self.lock:
            self.files[filename.split('/')[-1]] = chunks

        message = json.dumps({
            'command': 'share',
            'filename': filename.split('/')[-1],
            'peer_id': self.peer_id,
            'peer_address': f'127.0.0.1:{self.listen_port}',
            'num_chunks': len(chunks),
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
            result = json.loads(data.decode())

        chunks = []
        for chunk_id in range(result['num_chunks']):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                ip, port = result['peers'][0].split(':') # todo select peer randomly

                s.connect((ip, int(port)))
                s.send(f"{filename},{chunk_id}".encode())
                chunk = s.recv(1024)
                chunks.append(chunk)

        with open(f"downloaded_{filename}", 'wb') as f:
            for chunk in chunks:
                f.write(chunk)


def main():
    parser = argparse.ArgumentParser(description="P2P File Sharing")
    parser.add_argument("peer_id", type=str, help="The ID of the peer")
    parser.add_argument("--tracker_ip", type=str, default="127.0.0.1", help="Tracker IP address")
    parser.add_argument("--tracker_port", type=int, default=6771, help="Tracker port")
    parser.add_argument("--listen_port", type=int, default=52611, help="Listening port for this peer")

    args = parser.parse_args()

    peer = Peer(peer_id=args.peer_id, tracker_ip=args.tracker_ip, tracker_port=args.tracker_port, listen_port=args.listen_port)
    peer.start()

    while True:
        command = input("Enter command (share <filename> / get <filename> / exit): ").strip().split()
        if not command:
            continue
        if command[0] == "share" and len(command) == 2:
            peer.share(command[1])
        elif command[0] == "get" and len(command) == 2:
            peer.get(command[1])
        elif command[0] == "exit":
            print("Exiting...")
            break
        else:
            print("Invalid command. Please use 'share <filename>', 'get <filename>', or 'exit'.")


if __name__ == "__main__":
    main()
