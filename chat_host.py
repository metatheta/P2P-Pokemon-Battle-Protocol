import curses
import threading
from queue import SimpleQueue
from Connections import HostConnection
from Messages import TextMessage

HOST_PORT = 9392
CHAT_WIDTH = 60
CHAT_HEIGHT = 20

chat_host = HostConnection(HOST_PORT + 1)
chat_host.discovery_broadcast()

message_queue = SimpleQueue()
msg_list = []


def format_chat_message(message: dict) -> str:
    return f"[{message.get('sender_name')}]: {message.get('message_text')}"


def receiver():
    while True:
        data = chat_host.receive()
        if data and data.get("message_type") == "CHAT_MESSAGE":
            msg_list.append(format_chat_message(data))


def broadcaster():
    while True:
        while not message_queue.empty():
            msg = message_queue.get()
            for peer in chat_host.connected_peers:
                chat_host.send(msg.to_message_format(), peer)


def chat_ui(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    input_win = curses.newwin(1, CHAT_WIDTH, CHAT_HEIGHT + 1, 0)
    chat_win = curses.newwin(CHAT_HEIGHT, CHAT_WIDTH, 0, 0)
    chat_win.scrollok(True)
    input_buf = ""

    while True:
        # draw chat window
        chat_win.erase()
        start_line = max(0, len(msg_list) - CHAT_HEIGHT)
        for i, line in enumerate(msg_list[start_line:]):
            chat_win.addstr(i, 0, line[: CHAT_WIDTH - 1])
        chat_win.refresh()

        # draw input window
        input_win.erase()
        input_win.addstr(0, 0, "> " + input_buf)
        input_win.refresh()

        # handle key input
        ch = input_win.getch()
        if ch in (curses.KEY_ENTER, 10, 13):
            if input_buf.strip():
                name = "HOST"
                msg = TextMessage(0, name, input_buf.strip())
                message_queue.put(msg)
                msg_list.append(f"[{name}]: {input_buf.strip()}")
            input_buf = ""
        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            input_buf = input_buf[:-1]
        elif 32 <= ch <= 126:
            input_buf += chr(ch)


if __name__ == "__main__":
    t_recv = threading.Thread(target=receiver, daemon=True)
    t_broadcast = threading.Thread(target=broadcaster, daemon=True)
    t_recv.start()
    t_broadcast.start()
    curses.wrapper(chat_ui)

# TODO fix UI and change client to use curses