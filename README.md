````markdown
# P2P File Sharing System (with Tracker)

This project implements a simple **peer-to-peer (P2P) file sharing system** with a centralized **tracker** for coordination. Peers can share files, download files from others, and the tracker maintains metadata about which peers own which files.

---

## Features

### Peer
- Share local files by splitting them into chunks.
- Download files from other peers in the network.
- Send periodic `alive` signals to the tracker.
- Keep logs of file transfers (chunks, peers, timestamps).
- Graceful exit handling.

### Tracker
- Keeps track of available files and peers.
- Provides a list of peers sharing a requested file.
- Handles peer heartbeats and removes inactive peers.
- Provides request and system logs.

---

## Requirements

- Python 3.8+
- No external libraries required (uses only the Python standard library).

---

## Setup

1.  Clone the repository:
    ```bash
    git clone [https://github.com/your-username/p2p-filesharing.git](https://github.com/your-username/p2p-filesharing.git)
    cd p2p-filesharing
    ```

2.  Create a `data/` directory to store files for sharing:
    ```bash
    mkdir data
    ```

3.  Add the files you want to share into the `data/` directory.

---

## Usage

### Start the Tracker

Run the tracker script. By default, it listens on `127.0.0.1:6771`.

```bash
python tracker.py
````

**Available Tracker Commands:**

  - `logs request` → Show only share/get logs.
  - `logs-all` → Show all logs (alive, exit, share, get).
  - `logs_file <filename>` → Show logs related to a specific file.
  - `exit` → Exit tracker.

### Start a Peer

Run the peer script with a unique ID.

```bash
python peer.py <peer_id>
```

**Example:**

```bash
python peer.py 1
```

**Available Peer Commands:**

  - `share <filename>` → Share a file from the `data/` folder.
  - `get <filename>` → Download a file shared in the network.
  - `logs request` → Show peer logs of downloaded chunks.
  - `exit` → Exit the peer and notify the tracker.

-----

## Example Workflow

1.  **Start the tracker in one terminal:**

    ```bash
    python tracker.py
    ```

2.  **Start two peers, each in a separate terminal:**

    ```bash
    # Terminal for Peer 1
    python peer.py 1
    ```

    ```bash
    # Terminal for Peer 2
    python peer.py 2
    ```

3.  **On Peer 1, share a file (type this into the running peer's prompt):**

    ```text
    > share example.txt
    ```

4.  **On Peer 2, download the file (type this into the other peer's prompt):**

    ```text
    > get example.txt
    ```

5.  **View logs on either peer:**

    ```text
    > logs request
    ```

<!-- end list -->

```
```
