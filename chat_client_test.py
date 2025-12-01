import random
import sys

from Connections import PeerConnection
from Messages import ChatMessage, TextMessage

if __name__ == "__main__":
    port = random.randint(8000, 9000)
    joiner = PeerConnection(port)
    print(f"Initialized: {joiner.socket.getsockname()}")
    name = "Allen"

    success = joiner.wait_for_broadcast()
    if success:
        message = TextMessage(joiner.sequence_number, name, "Hello World!")
        msg_sent = joiner.send(message.to_message_format())
        if msg_sent:
            print("Sent chat message and received acknowledgement")


