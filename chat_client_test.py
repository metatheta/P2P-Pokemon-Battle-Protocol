import random
import sys
import time

from Connections import PeerConnection
from Messages import TextMessage

if __name__ == "__main__":
    port = random.randint(8000, 9000)
    joiner = PeerConnection(port)
    print(f"Initialized: {joiner.socket.getsockname()}")
    name = "Allen " + str(random.randint(1, 100))

    print(f"This client's name is {name}")
    success = joiner.wait_for_broadcast()
    if success:
        message = TextMessage(joiner.send_sequence_number, name, "Hello World!")
        msg_sent = joiner.send(message.to_message_format())
        if msg_sent:
            print("Sent chat message and received acknowledgement")

        print("Listening for messages from other clients...")
        start_time = time.time()
        while time.time() - start_time < 15:  # Listen for 15 seconds
            try:
                joiner.socket.settimeout(1.0)
                received = joiner.receive()
                if received:
                    formatted = TextMessage.format(received)
                    print(formatted)
            except Exception:
                continue

        print("Exiting client")
