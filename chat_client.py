import random
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
from queue import Queue

from Connections import PeerConnection
from Messages import TextMessage

# AI was utilized for the GUI implementation.

# Global state
gui_queue = Queue()
name = ""
joiner = None

def receiver_thread():
    """Background thread that receives messages from the network."""
    global joiner, name
    while True:
        try:
            joiner.socket.settimeout(1.0)
            r = joiner.receive()
            if r:
                # Skip our own messages to avoid duplication
                if r.get("sender_name") == name:
                    continue
                formatted = TextMessage.format(r)
                gui_queue.put(("MESSAGE", formatted))
        except Exception:
            continue


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
        msg_type, data = gui_queue.get()
        if msg_type == "MESSAGE":
            chat_text.config(state="normal")
            chat_text.insert("end", data + "\n")
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
    global joiner, name

    # Initialize connection
    port = random.randint(8000, 9000)
    joiner = PeerConnection(port)

    # Create a temporary root for dialogs
    temp_root = tk.Tk()
    temp_root.withdraw()

    # Get username
    name = simpledialog.askstring("PokeProtocol Chat Client", "Enter your name:", parent=temp_root)
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
