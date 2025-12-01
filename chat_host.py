import curses
import threading
import textwrap
import sys
from queue import SimpleQueue
from Connections import HostConnection
from Messages import TextMessage

HOST_PORT = 9392
message_queue = SimpleQueue()

raw_messages = []
display_lines = []
lock = threading.Lock()

# AI used for terminal UI.
# External library used: windows-curses for terminal UI

def receiver(chat_host, stdscr):
    while True:
        try:
            chat_host.socket.settimeout(0.1)
            data = chat_host.receive()
            if data and data.get("message_type") == "CHAT_MESSAGE":
                sender = data.get("sender_name")
                msg_text = data.get("message_text")
                formatted_msg = f"[{sender}]: {msg_text}"
                max_y, max_x = stdscr.getmaxyx()

                with lock:
                    raw_messages.append(formatted_msg)
                    display_lines.extend(textwrap.wrap(formatted_msg, width=max_x - 4))
                
                # Host rebroadcasts message to all connected peers
                relay_msg = TextMessage(0, sender, msg_text)
                message_queue.put(relay_msg)

        except Exception:
            continue

def broadcaster(chat_host):
    """Sends messages to ALL peers. Includes Fault Tolerance."""
    while True:
        # This is a blocking get, so it waits efficiently for a message
        msg = message_queue.get()

        # Convert once
        formatted_msg = msg.to_message_format()

        # Copy the list so we don't crash if the list changes size during iteration
        peers_snapshot = list(chat_host.connected_peers)

        for peer in peers_snapshot:
            try:
                chat_host.send(formatted_msg, peer)
            except Exception as e:
                continue


def rewrap_all_messages(width):
    global display_lines
    new_lines = []
    for msg in raw_messages:
        new_lines.extend(textwrap.wrap(msg, width=width))
    display_lines = new_lines


def draw_ui(stdscr, chat_host):
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(1)
    stdscr.timeout(50)

    input_buf = ""
    name = "HOST"
    last_h, last_w = stdscr.getmaxyx()

    while True:
        height, width = stdscr.getmaxyx()

        # Resize Handler
        if (height, width) != (last_h, last_w):
            with lock:
                rewrap_all_messages(width - 4)
            last_h, last_w = height, width

        stdscr.erase()
        stdscr.border()

        header = f" HOST SERVER (Port: {HOST_PORT}) - Peers: {len(chat_host.connected_peers)} "
        stdscr.addstr(0, 2, header[: width - 2])

        chat_height = height - 4

        with lock:
            visible_lines = display_lines[-chat_height:]

        for i, line in enumerate(visible_lines):
            try:
                stdscr.addstr(i + 1, 2, line)
            except curses.error:
                pass

        stdscr.addstr(height - 2, 2, "> " + input_buf)
        stdscr.refresh()

        try:
            ch = stdscr.getch()
        except KeyboardInterrupt:
            break

        if ch == -1:
            continue
        elif ch in (curses.KEY_ENTER, 10, 13):
            if input_buf.strip():
                msg = TextMessage(0, name, input_buf.strip())
                message_queue.put(msg)

                local_msg = f"[{name}]: {input_buf.strip()}"
                with lock:
                    raw_messages.append(local_msg)
                    display_lines.extend(textwrap.wrap(local_msg, width=width - 4))
                input_buf = ""
        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            input_buf = input_buf[:-1]
        elif 32 <= ch <= 126:
            if len(input_buf) < width - 5:
                input_buf += chr(ch)


if __name__ == "__main__":
    try:
        chat_host = HostConnection(HOST_PORT + 1)
        chat_host.discovery_broadcast()

        t_broadcast = threading.Thread(
            target=broadcaster, args=(chat_host,), daemon=True
        )
        t_broadcast.start()

        def main(stdscr):
            t_recv = threading.Thread(
                target=receiver, args=(chat_host, stdscr), daemon=True
            )
            t_recv.start()
            draw_ui(stdscr, chat_host)

        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit()
