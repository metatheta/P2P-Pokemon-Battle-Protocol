import random
import sys
import threading
import textwrap
from collections import deque

try:
    import msvcrt
except ImportError:
    msvcrt = None

from Connections import PeerConnection
from Messages import TextMessage

CHAT_HEIGHT = 20
CHAT_WIDTH = 60
msg_queue = deque(maxlen=CHAT_HEIGHT)
input_buf = ""

# AI was utilized only for the terminal UI.

def receiver():
    while True:
        try:
            joiner.socket.settimeout(1.0)
            r = joiner.receive()
            if r:
                if r.get("sender_name") == name:
                    continue
                msg_queue.append(TextMessage.format(r))
                redraw()
        except:
            continue


def redraw():
    sys.stdout.write("\x1b[2J\x1b[H")

    lines = []
    # Create a snapshot to avoid runtime errors if modified by other thread
    current_msgs = list(msg_queue)

    for m in current_msgs:
        # Wrap text to fit inside the box (width - 2 for borders)
        wrapped = textwrap.wrap(m, width=CHAT_WIDTH - 2)
        if not wrapped:
            lines.append("")
        else:
            lines.extend(wrapped)

    # Keep only the last CHAT_HEIGHT lines
    display_lines = lines[-CHAT_HEIGHT:]

    # Pad with empty lines at the top if needed
    while len(display_lines) < CHAT_HEIGHT:
        display_lines.insert(0, "")

    # Draw the box
    print("+" + "-" * (CHAT_WIDTH - 2) + "+")
    for line in display_lines:
        print(f"|{line.ljust(CHAT_WIDTH - 2)}|")
    print("+" + "-" * (CHAT_WIDTH - 2) + "+")

    print("> " + input_buf, end="", flush=True)


def input_loop():
    global input_buf
    input_buf = ""
    while True:
        if msvcrt:
            ch_byte = msvcrt.getch()
            if ch_byte == b"\r":
                ch = "\n"
            elif ch_byte == b"\x08":
                ch = "\x7f"
            elif ch_byte == b"\x03":  # Ctrl+C
                sys.exit()
            else:
                try:
                    ch = ch_byte.decode("utf-8")
                except:
                    continue
        else:
            ch = sys.stdin.read(1)

        if ch == "\n":
            if input_buf.strip():
                m = TextMessage(joiner.send_sequence_number, name, input_buf.strip())
                joiner.send(m.to_message_format())
                msg_queue.append(f"[{name}]: {input_buf.strip()}")
            input_buf = ""
            redraw()
        elif ch == "\x7f":
            input_buf = input_buf[:-1]
            redraw()
        else:
            if ch.isprintable():
                input_buf += ch
                redraw()


if __name__ == "__main__":
    port = random.randint(8000, 9000)
    joiner = PeerConnection(port)
    name = input("Enter your name: ")
    if joiner.wait_for_broadcast():
        t = threading.Thread(target=receiver, daemon=True)
        t.start()
        redraw()
        input_loop()
