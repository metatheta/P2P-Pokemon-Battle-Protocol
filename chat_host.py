import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import sys
from queue import Queue

from Connections import HostConnection
from Messages import TextMessage

# AI was utilized for the GUI implementation.

HOST_PORT = 9392
message_queue = Queue()
gui_queue = Queue()
host_name = "HOST"
chat_host = None


def receiver_thread(root):
    """Background thread that receives messages from clients."""
    global chat_host
    while True:
        try:
            chat_host.socket.settimeout(0.1)
            data = chat_host.receive()
            if data and data.get("message_type") == "CHAT_MESSAGE":
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
        peers_snapshot = list(chat_host.connected_peers)

        for peer in peers_snapshot:
            try:
                chat_host.send(formatted_msg, peer)
            except Exception:
                continue


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
        msg_type, data = gui_queue.get()
        if msg_type == "MESSAGE":
            chat_text.config(state="normal")
            chat_text.insert("end", data + "\n")
            chat_text.see("end")
            chat_text.config(state="disabled")
        elif msg_type == "PEER_COUNT":
            title_label.config(
                text=f"Host Server - Port: {HOST_PORT + 1} - Peers: {data}"
            )

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
    global chat_host, host_name

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
