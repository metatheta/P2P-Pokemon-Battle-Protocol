import random
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox, ttk
from queue import Queue
import base64
import uuid
import os
import glob

from Connections import PeerConnection
from Messages import TextMessage, StickerFragment

# AI was utilized for the GUI implementation.

# Global state
gui_queue = Queue()
name = ""
joiner = None
sticker_buffers = {}  # {sticker_id: {'chunks': {}, 'total_chunks': int, 'sender_name': str}}
available_stickers = []  # List of sticker file paths


def receiver_thread():
    """Background thread that receives messages from the network."""
    global joiner, name, sticker_buffers
    while True:
        try:
            joiner.socket.settimeout(1.0)
            r = joiner.receive()
            if r:
                # Handle sticker fragments
                if r.get("message_type") == "STICKER_FRAGMENT":
                    sticker_id = r.get("sticker_id")
                    chunk_index = int(r.get("chunk_index"))
                    total_chunks = int(r.get("total_chunks"))
                    fragment_data = r.get("fragment_data")
                    sender_name = r.get("sender_name")

                    # Skip our own messages to avoid duplication (stickers)
                    if r.get("sender_name") == name:
                        continue

                    # Initialize buffer for this sticker if needed
                    if sticker_id not in sticker_buffers:
                        sticker_buffers[sticker_id] = {
                            "chunks": {},
                            "total_chunks": total_chunks,
                            "sender_name": sender_name,
                        }

                    # Store this chunk
                    sticker_buffers[sticker_id]["chunks"][chunk_index] = fragment_data

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
                    continue

                formatted = TextMessage.format(r)
                # Skip our own messages to avoid duplication (text messages)
                if r.get("sender_name") == name:
                    continue

                gui_queue.put(("MESSAGE", formatted))
        except Exception:
            continue


def chunk_and_send(file_path: str):
    """Fragment and send a sticker image."""
    global joiner, name
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
        gui_queue.put(("STICKER", name, encoded))

        for i in range(0, len(encoded), chunk_size):
            fragment = StickerFragment(
                0,  # Sequence number will be injected by send_fragment
                sticker_id,
                name,
                chunk_index,
                total_chunks,
                encoded[i : i + chunk_size],
            )
            joiner.send_fragment(fragment.to_message_format())
            chunk_index += 1
            # Small delay to avoid overwhelming the network
            time.sleep(0.001)
    except Exception as e:
        print(f"Error sending sticker: {e}")


def send_message(chat_text, input_entry):
    """Send a message to the network."""
    global joiner, name
    message_text = input_entry.get()
    if message_text.strip():
        m = TextMessage(joiner.send_sequence_number, name, message_text.strip())
        joiner.send(m.to_message_format())

        # Display our own message locally
        formatted = f"[{name}]: {message_text.strip()}"
        chat_text.config(state="normal")
        chat_text.insert("end", formatted + "\n")
        chat_text.see("end")
        chat_text.config(state="disabled")

        input_entry.delete(0, "end")


def check_queue(root, chat_text):
    """Check for new messages from the receiver thread."""
    while not gui_queue.empty():
        msg_data = gui_queue.get()
        msg_type = msg_data[0]

        if msg_type == "MESSAGE":
            data = msg_data[1]
            chat_text.config(state="normal")
            chat_text.insert("end", data + "\n")
            chat_text.see("end")
            chat_text.config(state="disabled")
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

    root.after(100, check_queue, root, chat_text)


def create_gui():
    """Create the main tkinter GUI."""
    global joiner, name

    root = tk.Tk()
    root.title(f"Chat Client - {name}")
    root.geometry("500x600")

    # Title label
    title_text = f"Chat Client: {name} ({joiner.socket.getsockname()})"
    title_label = tk.Label(
        root,
        text=title_text,
        font=("Arial", 12, "bold"),
        bg="#2c3e50",
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
    input_frame = tk.Frame(root, bg="#34495e")
    input_frame.pack(fill="x", padx=10, pady=10)

    # Sticker selection
    sticker_frame = tk.Frame(input_frame, bg="#34495e")
    sticker_frame.pack(side="left", padx=(0, 10))

    sticker_label = tk.Label(
        sticker_frame, text="Sticker:", bg="#34495e", fg="white", font=("Arial", 9)
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
        bg="#9b59b6",
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
        bg="#3498db",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=20,
    )
    send_btn.pack(side="right")

    # Bind Enter key to send
    input_entry.bind("<Return>", lambda e: send_message(chat_text, input_entry))
    input_entry.focus()

    # Start queue checking
    root.after(100, check_queue, root, chat_text)

    return root


def main():
    global joiner, name, available_stickers

    # Load available stickers
    sticker_dir = os.path.join(os.path.dirname(__file__), "stickers")
    if os.path.exists(sticker_dir):
        available_stickers = glob.glob(os.path.join(sticker_dir, "*.png"))
        available_stickers.extend(glob.glob(os.path.join(sticker_dir, "*.jpg")))
        available_stickers.extend(glob.glob(os.path.join(sticker_dir, "*.gif")))

    # Initialize connection
    port = random.randint(8000, 9000)
    joiner = PeerConnection(port)

    # Create a temporary root for dialogs
    temp_root = tk.Tk()
    temp_root.withdraw()

    # Get username
    name = simpledialog.askstring(
        "PokeProtocol Chat Client", "Enter your name:", parent=temp_root
    )
    if not name:
        name = "User"

    temp_root.destroy()

    # Wait for host broadcast (this happens in background, no blocking)
    if not joiner.wait_for_broadcast():
        root_error = tk.Tk()
        root_error.withdraw()
        messagebox.showerror("Connection Failed", "Failed to connect to host!")
        root_error.destroy()
        return

    # Start receiver thread
    t = threading.Thread(target=receiver_thread, daemon=True)
    t.start()

    # Create and run the GUI
    root = create_gui()
    root.mainloop()


if __name__ == "__main__":
    main()
