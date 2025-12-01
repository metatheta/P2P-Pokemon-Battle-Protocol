import curses
import threading
import random
import sys
import textwrap
from Connections import PeerConnection
from Messages import TextMessage

# AI used for terminal UI.
# External library used: windows-curses for terminal UI


raw_messages = []
display_lines = []
lock = threading.Lock()


def receiver(joiner, name, stdscr):
    """Background thread to receive messages."""
    while True:
        try:
            joiner.socket.settimeout(0.5)
            r = joiner.receive()
            if r:
                if r.get("sender_name") == name:
                    continue

                msg_text = f"[{r.get('sender_name')}]: {r.get('message_text')}"

                # Get current width to wrap immediately
                max_y, max_x = stdscr.getmaxyx()
                chat_width = max_x - 4

                with lock:
                    raw_messages.append(msg_text)
                    # Wrap only the NEW message and add to display buffer
                    wrapped = textwrap.wrap(msg_text, width=chat_width)
                    display_lines.extend(wrapped)
        except Exception:
            continue


def rewrap_all_messages(width):
    """Helper to recalculate all lines only when window resizes."""
    global display_lines
    new_lines = []
    for msg in raw_messages:
        new_lines.extend(textwrap.wrap(msg, width=width))
    display_lines = new_lines


def draw_ui(stdscr, joiner, name):
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(1)  
    stdscr.timeout(50)  

    input_buf = ""
    last_h, last_w = stdscr.getmaxyx()

    while True:
        height, width = stdscr.getmaxyx()

        # Detect Resize to fix layout
        if (height, width) != (last_h, last_w):
            with lock:
                rewrap_all_messages(width - 4)
            last_h, last_w = height, width

        stdscr.erase()
        stdscr.border()


        title = f" Chat Client: {name} (Address: {joiner.socket.getsockname()}) "
        stdscr.addstr(0, 2, title[: width - 2])

        chat_height = height - 4

        with lock:
            visible_lines = display_lines[-chat_height:]

        for i, line in enumerate(visible_lines):
            try:
                stdscr.addstr(i + 1, 2, line)
            except curses.error:
                pass  # Ignore edge case errors

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
                m = TextMessage(joiner.send_sequence_number, name, input_buf.strip())
                joiner.send(m.to_message_format())

                local_msg = f"[{name}]: {input_buf.strip()}"
                with lock:
                    raw_messages.append(local_msg)
                    # Wrap immediate
                    display_lines.extend(textwrap.wrap(local_msg, width=width - 4))

                input_buf = ""

        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            input_buf = input_buf[:-1]
        elif 32 <= ch <= 126:
            if len(input_buf) < width - 5:
                input_buf += chr(ch)


if __name__ == "__main__":
    try:
        port = random.randint(8000, 9000)
        joiner = PeerConnection(port)
        print("Searching for host...")
        if joiner.wait_for_broadcast():
            user_name = input("Enter your name: ")

            t = threading.Thread(target=lambda: None)  # Placeholder

            def main(stdscr):
                t = threading.Thread(
                    target=receiver, args=(joiner, user_name, stdscr), daemon=True
                )
                t.start()
                draw_ui(stdscr, joiner, user_name)

            curses.wrapper(main)
        else:
            print("No host found.")
    except KeyboardInterrupt:
        sys.exit()
