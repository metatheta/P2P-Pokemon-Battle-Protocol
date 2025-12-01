# Opens in a separate window allowing you to chat - assumes you are the client
import random
import sys

from Connections import PeerConnection
from Messages import ChatMessage, TextMessage

def prompt_msg_type() -> str:
    while True:
        print("Content types:\n[1] Text\n[2] Sticker\n[3] Exit Chat Room")
        match input("Enter your choice: ").strip():
            case "1":
                return "TEXT"
            case "2":
                return "STICKER"
            case "3":
                return "EXIT"
            case _:
                print("Please pick one of the choices.")


def message_menu() -> bool:
    content_type = prompt_msg_type()
    match content_type:
        case "TEXT":
            send_text()
        case "STICKER":
            send_sticker()
        case "EXIT":
            sys.exit(0)


def send_text():
    msg = input("Enter message content: ").strip()
    message = TextMessage(joiner.sequence_number, name, msg)
    joiner.send(message.to_message_format())

def send_sticker():
    pass


if __name__ == "__main__":
    port = random.randint(8000, 9000)
    joiner = PeerConnection(port)
    print(f"Initialized: {joiner.socket.getsockname()}")
    name = input("Enter your name: ")

    success = True
    if success:
        while True:
            message_menu()

