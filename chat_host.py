import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox, ttk
import sys
from queue import Queue
import base64
import uuid
import os
import glob

from Connections import HostConnection
from Messages import TextMessage, StickerFragment, Message

# AI was utilized for the GUI implementation.

HOST_PORT = 9392
message_queue = Queue()
gui_queue = Queue()
host_name = "HOST"
chat_host = None
sticker_buffers = {}  # {sticker_id: {'chunks': {}, 'total_chunks': int, 'sender_name': str}}
available_stickers = []  # List of sticker file paths


def receiver_thread(root):
    """Background thread that receives messages from clients."""
    global chat_host, sticker_buffers
    while True:
        try:
            chat_host.socket.settimeout(0.1)
            data = chat_host.receive()
            if data:
                # Handle sticker fragments
                if data.get("message_type") == "STICKER_FRAGMENT":
                    sticker_id = data.get("sticker_id")
                    chunk_index = int(data.get("chunk_index"))
                    total_chunks = int(data.get("total_chunks"))
                    fragment_data = data.get("fragment_data")
                    sender_name = data.get("sender_name")

                    # Initialize buffer for this sticker if needed
                    if sticker_id not in sticker_buffers:
                        sticker_buffers[sticker_id] = {
                            "chunks": {},
                            "total_chunks": total_chunks,
                            "sender_name": sender_name,
                        }

                    # Store this chunk
                    sticker_buffers[sticker_id]["chunks"][chunk_index] = fragment_data

                    # Relay fragment to all connected peers
                    fragment_msg = StickerFragment(
                        0,
                        sticker_id,
                        sender_name,
                        chunk_index,
                        total_chunks,
                        fragment_data,
                    )
                    message_queue.put(fragment_msg)

                    # Check if we have all chunks
                    if len(sticker_buffers[sticker_id]["chunks"]) == total_chunks:
                        # Reassemble the sticker
                        final_data = "".join(
                            sticker_buffers[sticker_id]["chunks"][i]
                            for i in range(total_chunks)
                        )
                        gui_queue.put(("STICKER", sender_name, final_data))
                        # Clean up buffer
                        del sticker_buffers[sticker_id]

                    # Update peer count
                    gui_queue.put(("PEER_COUNT", len(chat_host.connected_peers)))
                    continue

                if data.get("message_type") == "CHAT_MESSAGE":
                    sender = data.get("sender_name")
                    msg_text = data.get("message_text")
                    formatted_msg = f"[{sender}]: {msg_text}"

                    # Display in GUI
                    gui_queue.put(("MESSAGE", formatted_msg))

                    # Relay message to all connected peers
                    relay_msg = TextMessage(0, sender, msg_text)
                    message_queue.put(relay_msg)

                    # Update peer count
                    gui_queue.put(("PEER_COUNT", len(chat_host.connected_peers)))
        except Exception:
            continue


def broadcaster_thread():
    """Sends messages to all connected peers."""
    global chat_host
    while True:
        msg = message_queue.get()  # Blocking call

        formatted_msg = msg.to_message_format()

        # Check if this is a sticker fragment - use fire-and-forget broadcast
        msg_dict = Message.from_message_format(formatted_msg)
        if msg_dict.get("message_type") == "STICKER_FRAGMENT":
            chat_host.send_fragment_broadcast(formatted_msg)
        else:
            # Regular messages use ACK-confirmed sending
            peers_snapshot = list(chat_host.connected_peers)
            for peer in peers_snapshot:
                try:
                    chat_host.send(formatted_msg, peer)
                except Exception:
                    continue


def chunk_and_send(file_path: str):
    """Fragment and send a sticker image to all connected peers."""
    global host_name
    from math import ceil
    import time

    try:
        with open(file_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode("ascii")

        sticker_id = str(uuid.uuid4())
        chunk_size = 1024
        total_chunks = ceil(len(encoded) / chunk_size)
        chunk_index = 0

        # Display own sticker immediately
        gui_queue.put(("STICKER", host_name, encoded))

        for i in range(0, len(encoded), chunk_size):
            fragment = StickerFragment(
                0,
                sticker_id,
                host_name,
                chunk_index,
                total_chunks,
                encoded[i : i + chunk_size],
            )
            message_queue.put(fragment)
            chunk_index += 1
            # Small delay to avoid overwhelming the network
            time.sleep(0.001)
    except Exception as e:
        print(f"Error sending sticker: {e}")


def send_message(chat_text, input_entry):
    """Send a message from the host."""
    global host_name
    message_text = input_entry.get()
    if message_text.strip():
        m = TextMessage(0, host_name, message_text.strip())
        message_queue.put(m)

        # Display locally
        formatted = f"[{host_name}]: {message_text.strip()}"
        chat_text.config(state="normal")
        chat_text.insert("end", formatted + "\n")
        chat_text.see("end")
        chat_text.config(state="disabled")

        input_entry.delete(0, "end")


def check_queue(root, chat_text, title_label):
    """Check for new messages and updates from background threads."""
    while not gui_queue.empty():
        msg_data = gui_queue.get()
        msg_type = msg_data[0]

        if msg_type == "MESSAGE":
            data = msg_data[1]
            chat_text.config(state="normal")
            chat_text.insert("end", data + "\n")
            chat_text.see("end")
            chat_text.config(state="disabled")
        elif msg_type == "PEER_COUNT":
            data = msg_data[1]
            title_label.config(
                text=f"Host Server - Port: {HOST_PORT + 1} - Peers: {data}"
            )
        elif msg_type == "STICKER":
            sender_name = msg_data[1]
            sticker_data = msg_data[2]

            chat_text.config(state="normal")
            chat_text.insert("end", f"[{sender_name}] sent a sticker:\n")

            # Create and display the sticker image
            try:
                img = tk.PhotoImage(data=sticker_data)
                chat_text.image_create("end", image=img)
                chat_text.image_refs.append(
                    img
                )  # Keep reference to prevent garbage collection
                chat_text.insert("end", "\n")
            except Exception as e:
                chat_text.insert("end", f"[Error displaying sticker: {e}]\n")

            chat_text.see("end")
            chat_text.config(state="disabled")

    root.after(100, check_queue, root, chat_text, title_label)


def create_gui():
    """Create the main tkinter GUI for the host."""
    global chat_host, host_name

    root = tk.Tk()
    root.title(f"Chat Host - {host_name}")
    root.geometry("500x600")

    # Title label
    title_text = (
        f"Host Server - Port: {HOST_PORT + 1} - Peers: {len(chat_host.connected_peers)}"
    )
    title_label = tk.Label(
        root,
        text=title_text,
        font=("Arial", 12, "bold"),
        bg="#27ae60",
        fg="white",
        pady=10,
    )
    title_label.pack(fill="x")

    # Chat display area
    chat_frame = tk.Frame(root)
    chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

    chat_text = scrolledtext.ScrolledText(
        chat_frame,
        state="disabled",
        wrap="word",
        font=("Consolas", 10),
        bg="#ecf0f1",
        fg="#2c3e50",
    )
    chat_text.pack(fill="both", expand=True)

    # Store reference for images (future use)
    chat_text.image_refs = []

    # Input area
    input_frame = tk.Frame(root, bg="#2ecc71")
    input_frame.pack(fill="x", padx=10, pady=10)

    # Sticker selection
    sticker_frame = tk.Frame(input_frame, bg="#2ecc71")
    sticker_frame.pack(side="left", padx=(0, 10))

    sticker_label = tk.Label(
        sticker_frame, text="Sticker:", bg="#2ecc71", fg="white", font=("Arial", 9)
    )
    sticker_label.pack(side="left", padx=(0, 5))

    sticker_combo = ttk.Combobox(sticker_frame, width=15, state="readonly")
    sticker_names = [os.path.basename(s) for s in available_stickers]
    sticker_combo["values"] = sticker_names
    if sticker_names:
        sticker_combo.current(0)
    sticker_combo.pack(side="left")

    def send_sticker_clicked():
        if available_stickers and sticker_combo.get():
            idx = sticker_combo.current()
            if idx >= 0:
                # Run in background thread to avoid freezing GUI
                t = threading.Thread(
                    target=chunk_and_send, args=(available_stickers[idx],), daemon=True
                )
                t.start()

    sticker_btn = tk.Button(
        sticker_frame,
        text="Send",
        command=send_sticker_clicked,
        bg="#16a085",
        fg="white",
        font=("Arial", 9),
        padx=10,
    )
    sticker_btn.pack(side="left", padx=(5, 0))

    # Text message input
    input_entry = tk.Entry(input_frame, font=("Arial", 11))
    input_entry.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=5)

    send_btn = tk.Button(
        input_frame,
        text="Send",
        command=lambda: send_message(chat_text, input_entry),
        bg="#27ae60",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=20,
    )
    send_btn.pack(side="right")

    # Bind Enter key to send
    input_entry.bind("<Return>", lambda e: send_message(chat_text, input_entry))
    input_entry.focus()

    # Start queue checking
    root.after(100, check_queue, root, chat_text, title_label)

    return root


def main():
    global chat_host, host_name, available_stickers

    # Load available stickers
    sticker_dir = os.path.join(os.path.dirname(__file__), "stickers")
    if os.path.exists(sticker_dir):
        available_stickers = glob.glob(os.path.join(sticker_dir, "*.png"))
        available_stickers.extend(glob.glob(os.path.join(sticker_dir, "*.jpg")))
        available_stickers.extend(glob.glob(os.path.join(sticker_dir, "*.gif")))

    # Create a temporary root for dialogs
    temp_root = tk.Tk()
    temp_root.withdraw()

    # Get host name
    host_name = simpledialog.askstring(
        "Chat Host", "Enter host name:", initialvalue="HOST", parent=temp_root
    )
    if not host_name:
        host_name = "HOST"

    temp_root.destroy()

    try:
        # Initialize host connection
        chat_host = HostConnection(HOST_PORT + 1)
        chat_host.discovery_broadcast()

        # Create GUI first
        root = create_gui()

        # Start background threads
        t_recv = threading.Thread(target=receiver_thread, args=(root,), daemon=True)
        t_broadcast = threading.Thread(target=broadcaster_thread, daemon=True)
        t_recv.start()
        t_broadcast.start()

        # Run GUI
        root.mainloop()

    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        root_error = tk.Tk()
        root_error.withdraw()
        messagebox.showerror("Error", f"Host error: {e}")
        root_error.destroy()


if __name__ == "__main__":
    main()
