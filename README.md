## P2P File Sharing System (with Tracker)

This project implements a simple **peer-to-peer (P2P) file sharing system** with a centralized **tracker** for coordination. Peers can share files and download them from others. The tracker maintains essential metadata about which peers possess which files.

---

## Features

### Peer
* **Share** local files by splitting them into chunks.
* **Download** files from other peers in the network.
* Send periodic `alive` signals (heartbeats) to the tracker.
* Keep logs of file transfers (chunks, peers, timestamps).
* Handle **graceful exit** to notify the tracker.

### Tracker
* Keeps track of **available files and active peers**.
* Provides a list of peers sharing a requested file.
* Handles peer **heartbeats** and removes inactive peers.
* Provides request and system logs.

---

## Requirements

* **Python 3.8+**
* No external libraries required (uses only the Python standard library).

---

## Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/p2p-filesharing.git](https://github.com/your-username/p2p-filesharing.git)
    cd p2p-filesharing
    ```

2.  **Create a data/ directory** to store files:
    ```bash
    mkdir data
    ```

3.  **Add files** you want to share inside the `data/` directory.

---

## Usage

### Start the Tracker

Run the tracker (default: `127.0.0.1:6771`):

```bash
python tracker.py
