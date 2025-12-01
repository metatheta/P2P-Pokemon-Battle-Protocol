# Opens in a separate window allowing you to chat - assumes you are the host
import threading
import time
from queue import SimpleQueue
from Connections import HostConnection
from Messages import TextMessage

HOST_PORT = 9392
chat_host = HostConnection(HOST_PORT + 1)
# This connection object should be fed by the script invoking the subprocess

chat_host.discovery_broadcast()
print(f"Connections: {chat_host.connected_peers}")
# In the future we only need to run this once and then the connections can be
# created with the game address + port details but port is + 1

message_queue = SimpleQueue()


def receive():
    while True:
        data = chat_host.receive()
        if data:
            if data.get("message_type") == "CHAT_MESSAGE":
                message_queue.put(data)


def broadcast():
    while True:
        while not message_queue.empty():
            message = message_queue.get()
            formatted = TextMessage.format(message)
            print(formatted)

            message_str = ""
            for k, v in message.items():
                message_str += f"{k}: {v}\n"

            for peer in chat_host.connected_peers.keys():
                chat_host.send(message_str, peer)

t1 = threading.Thread(target=receive, daemon=True)
t2 = threading.Thread(target=broadcast, daemon=True)

t1.start()
t2.start()

start_time = time.time()
while time.time() - start_time < 10:
    time.sleep(0.5)
print("Exiting after 10s")