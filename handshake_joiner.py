# first idle, waiting for broadcast
import random

from Connections import PeerConnection
port = random.randint(8000, 9000)
joiner = PeerConnection(port)
print(f"Initialized: {joiner.socket.getsockname()}")

success = joiner.wait_for_broadcast()
if success:
    print(f"Joiner saved host data as: {joiner.host_addr}")