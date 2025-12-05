import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import sys
import io
from queue import Queue

from Connections import PeerConnection
from Data import Data
from HostPeer import HostPeer
from JoinerPeer import JoinerPeer
from SpectatorPeer import SpectatorPeer
from GuiIO import GuiIO
import GuiIO as IO  # Backend code expects IO module

# Import modules for simulation flags
import HostPeer as HostPeerModule
import JoinerPeer as JoinerPeerModule

# Chat imports
import chat_host
import chat_client


# AI utilized for GUI implementation.

class TextRedirector(io.StringIO):
    """Redirects stdout to a text widget."""

    def __init__(self, text_widget, tag=None):
        super().__init__()
        self.text_widget = text_widget
        self.tag = tag
        self.queue = Queue()
        self.verbose_enabled = True
        self.filter_keywords = [
            "Host sent",
            "Broadcasting",
            "Computation",
            "Dict:",
            "Battler located",
            "Calculations confirmed",
            "Self damage computation",
            "Enemy damage computation",
            # UDP/Connections.py verbose messages
            "Attempt to send",
            "Timed out, resending",
            "Message successfully sent",
            "Matching ACK received",
            "Duplicate packet",
            "New peer from",
            "ACKed",
            "buffering message",
            "Timeout reached",
            "Broadcasted using",
            "Sent ACK to",
        ]

    def write(self, string):
        # Filter logic
        if not self.verbose_enabled:
            for kw in self.filter_keywords:
                if kw in string:
                    return
        self.queue.put(string)

    def flush(self):
        pass


class GuiGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("P2P Pokemon Battle Protocol")
        self.root.geometry("1200x700")

        # Set up GuiIO root
        GuiIO.set_root(self.root)

        # Enable GUI mode in IO module
        import IO as IO_module

        IO_module.set_gui_mode(GuiIO)

        # Initialize data
        Data.populate_match_ups()
        Data.populate_pokemon_data()

        # Game state
        self.game_thread = None
        self.chat_thread = None
        self.choice = None
        self.username = None
        self.text_redirector = None

        # Chat state
        self.chat_active = False
        self.chat_text = None

        self.setup_ui()

    def setup_ui(self):
        """Set up the main UI."""
        # Title
        title_label = tk.Label(
            self.root,
            text="P2P Pokemon Battle Protocol",
            font=("Arial", 16, "bold"),
            bg="#e74c3c",
            fg="white",
            pady=15,
        )
        title_label.pack(fill="x")

        # Main container - split view
        main_container = tk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # LEFT SIDE - Game Log
        game_frame = tk.Frame(main_container)
        game_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        game_label = tk.Label(
            game_frame, text="Game Log:", font=("Arial", 11, "bold"), anchor="w"
        )
        game_label.pack(fill="x")

        self.log_text = scrolledtext.ScrolledText(
            game_frame,
            state="disabled",  # Make read-only
            wrap="word",
            font=("Consolas", 11),  # Increased from 9
            bg="#1e1e1e",
            fg="#00ff00",
            insertbackground="white",
        )
        self.log_text.pack(fill="both", expand=True)

        # Register battle status callback
        GuiIO.register_status_callback(self.update_battle_ui)

        # Register chat update callback
        GuiIO.register_chat_update_callback(self.check_chat_queue)

        # New: BATTLE STATUS FRAME (Top of Game Log)
        self.battle_status_frame = tk.Frame(game_frame, bg="#2c3e50", pady=5)
        self.battle_status_frame.pack(fill="x", side="top", before=self.log_text)

        # Player Side (Left)
        player_frame = tk.Frame(self.battle_status_frame, bg="#2c3e50")
        player_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.player_name_label = tk.Label(
            player_frame,
            text="Player",
            font=("Arial", 10, "bold"),
            fg="#2ecc71",
            bg="#2c3e50",
        )
        self.player_name_label.pack(anchor="w")

        self.player_hp_bar = ttk.Progressbar(
            player_frame, orient="horizontal", length=150, mode="determinate"
        )
        self.player_hp_bar.pack(fill="x", pady=(2, 0))

        self.player_hp_label = tk.Label(
            player_frame,
            text="HP: --/--",
            font=("Consolas", 9),
            fg="white",
            bg="#2c3e50",
        )
        self.player_hp_label.pack(anchor="w")

        # VS Label
        tk.Label(
            self.battle_status_frame,
            text="VS",
            font=("Arial", 12, "bold", "italic"),
            fg="#f1c40f",
            bg="#2c3e50",
        ).pack(side="left", padx=5)

        # Enemy Side (Right)
        enemy_frame = tk.Frame(self.battle_status_frame, bg="#2c3e50")
        enemy_frame.pack(side="right", fill="both", expand=True, padx=10)

        self.enemy_name_label = tk.Label(
            enemy_frame,
            text="Opponent",
            font=("Arial", 10, "bold"),
            fg="#e74c3c",
            bg="#2c3e50",
        )
        self.enemy_name_label.pack(anchor="e")

        self.enemy_hp_bar = ttk.Progressbar(
            enemy_frame, orient="horizontal", length=150, mode="determinate"
        )
        self.enemy_hp_bar.pack(fill="x", pady=(2, 0))

        self.enemy_hp_label = tk.Label(
            enemy_frame,
            text="HP: --/--",
            font=("Consolas", 9),
            fg="white",
            bg="#2c3e50",
        )
        self.enemy_hp_label.pack(anchor="e")

        # CONTROL PANEL UPDATES (Verbose Logging)
        control_frame = tk.Frame(self.root, bg="#34495e", pady=10)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Verbose Toggle
        self.verbose_enabled = tk.BooleanVar(value=True)
        verbose_check = tk.Checkbutton(
            control_frame,
            text="Verbose Log",
            variable=self.verbose_enabled,
            bg="#34495e",
            fg="white",
            selectcolor="#2c3e50",
            activebackground="#34495e",
            activeforeground="white",
            command=self.update_redirector_verbosity,
        )
        verbose_check.pack(side="right", padx=10)

        # Packet Loss Simulation Toggle
        self.packet_loss_enabled = tk.BooleanVar(value=False)
        packet_loss_check = tk.Checkbutton(
            control_frame,
            text="Simulate Packet Loss",
            variable=self.packet_loss_enabled,
            bg="#34495e",
            fg="white",
            selectcolor="#2c3e50",
            activebackground="#34495e",
            activeforeground="white",
            command=self.toggle_packet_loss,
        )
        packet_loss_check.pack(side="right", padx=10)

        # Damage Mismatch Simulation Toggle
        self.damage_mismatch_enabled = tk.BooleanVar(value=False)
        damage_mismatch_check = tk.Checkbutton(
            control_frame,
            text="Simulate Damage Mismatch",
            variable=self.damage_mismatch_enabled,
            bg="#34495e",
            fg="white",
            selectcolor="#2c3e50",
            activebackground="#34495e",
            activeforeground="white",
            command=self.toggle_damage_mismatch,
        )
        damage_mismatch_check.pack(side="right", padx=10)

        # Start button (Moved into existing control_frame creation flow logic)
        self.start_btn = tk.Button(
            control_frame,
            text="Start Game",
            command=self.start_game,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
        )
        self.start_btn.pack(side="left", padx=5)

        # Create and configure text redirector
        self.text_redirector = TextRedirector(self.log_text)
        self.text_redirector.verbose_enabled = True
        sys.stdout = self.text_redirector

        # RIGHT SIDE - Chat
        chat_frame = tk.Frame(main_container, bg="#34495e")
        chat_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.chat_label = tk.Label(
            chat_frame,
            text="Chat (Not Active)",
            font=("Arial", 11, "bold"),
            anchor="w",
            bg="#34495e",
            fg="white",
        )
        self.chat_label.pack(fill="x", pady=(0, 5))

        self.chat_text = scrolledtext.ScrolledText(
            chat_frame,
            state="disabled",
            wrap="word",
            font=("Consolas", 10),
            bg="#ecf0f1",
            fg="#2c3e50",
        )
        self.chat_text.pack(fill="both", expand=True)
        self.chat_text.image_refs = []

        # Chat input area
        chat_input_frame = tk.Frame(chat_frame, bg="#34495e")
        chat_input_frame.pack(fill="x", pady=(5, 0))

        # Sticker selection
        sticker_subframe = tk.Frame(chat_input_frame, bg="#34495e")
        sticker_subframe.pack(side="left", padx=(0, 5))

        sticker_label = tk.Label(
            sticker_subframe,
            text="Sticker:",
            bg="#34495e",
            fg="white",
            font=("Arial", 9),
        )
        sticker_label.pack(side="left", padx=(0, 3))

        self.sticker_combo = ttk.Combobox(sticker_subframe, width=12, state="readonly")
        self.sticker_combo.pack(side="left")

        self.sticker_btn = tk.Button(
            sticker_subframe,
            text="Send",
            command=self.send_sticker,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 9),
            padx=8,
            state="disabled",
        )
        self.sticker_btn.pack(side="left", padx=(3, 0))

        # Text input
        self.chat_input = tk.Entry(
            chat_input_frame, font=("Arial", 10), state="disabled"
        )
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=3)

        self.chat_send_btn = tk.Button(
            chat_input_frame,
            text="Send",
            command=self.send_chat_message,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            state="disabled",
        )
        self.chat_send_btn.pack(side="right")

        self.chat_input.bind("<Return>", lambda e: self.send_chat_message())

        # Start periodic updates
        self.root.after(100, self.update_log)
        self.root.after(100, self.check_gui_inputs)

    def update_log(self):
        """Update log text from stdout redirector."""
        while not self.text_redirector.queue.empty():
            msg = self.text_redirector.queue.get()
            self.log_text.config(state="normal")
            self.log_text.insert("end", msg)
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.root.after(100, self.update_log)

    def check_gui_inputs(self):
        """Check for pending GUI input requests from game thread."""
        GuiIO.check_input_queue()

        # Also check chat queue if active
        if self.chat_active:
            self.check_chat_queue()

        self.root.after(100, self.check_gui_inputs)

    def update_redirector_verbosity(self):
        """Update the text redirector's verbose setting."""
        if self.text_redirector:
            new_state = self.verbose_enabled.get()
            self.text_redirector.verbose_enabled = new_state
            status = "ENABLED" if new_state else "DISABLED"
            print(f"[DEBUG] Verbose logging {status}")

    def toggle_packet_loss(self):
        """Toggle packet loss simulation."""
        from Connections import LogicalConnection

        enabled = self.packet_loss_enabled.get()
        LogicalConnection.simulate_packet_loss = enabled
        status = "ENABLED" if enabled else "DISABLED"
        print(f"[SIMULATION] Packet loss simulation {status}")

    def toggle_damage_mismatch(self):
        """Toggle damage calculation mismatch simulation."""
        enabled = self.damage_mismatch_enabled.get()
        HostPeerModule.simulate_damage_mismatch = enabled
        JoinerPeerModule.simulate_damage_mismatch = enabled
        status = "ENABLED" if enabled else "DISABLED"
        print(f"[SIMULATION] Damage mismatch simulation {status}")

    def update_battle_ui(
        self, my_name, my_hp, my_max_hp, enemy_name, enemy_hp, enemy_max_hp
    ):
        """Update the battle status UI."""
        # Update Player
        self.player_name_label.config(text=my_name.title())
        self.player_hp_label.config(text=f"HP: {int(max(0, my_hp))}/{int(my_max_hp)}")
        self.player_hp_bar["maximum"] = my_max_hp
        self.player_hp_bar["value"] = max(0, my_hp)

        # Update Enemy
        self.enemy_name_label.config(text=enemy_name.title())
        self.enemy_hp_label.config(
            text=f"HP: {int(max(0, enemy_hp))}/{int(enemy_max_hp)}"
        )
        self.enemy_hp_bar["maximum"] = enemy_max_hp
        self.enemy_hp_bar["value"] = max(0, enemy_hp)

    def start_shutdown_countdown(self):
        """Start a 10-second countdown before shutting down."""
        print("\n" + "=" * 50)
        print("Game ended. Application will close in 10 seconds...")
        print("=" * 50)

        def countdown(seconds_left):
            if seconds_left > 0:
                print(f"Closing in {seconds_left} seconds...")
                self.root.after(1000, lambda: countdown(seconds_left - 1))
            else:
                print("Shutting down...")
                self.root.quit()

        countdown(10)

    def start_game(self):
        """Start the game in a separatethread."""
        self.start_btn.config(state="disabled")
        self.game_thread = threading.Thread(target=self.game_loop, daemon=True)
        self.game_thread.start()

    def game_loop(self):
        """The main game loop running in a background thread."""
        normal_ending = False
        try:
            choice = GuiIO.get_role()
            self.choice = choice

            # Ask for username using thread-safe GuiIO
            self.username = GuiIO.ask_username("Username", "Enter your name:")

            # Start chat based on role
            if choice == 1:
                # Host
                chat_host.host_name = self.username
                self.start_chat_host()
            else:
                # Connector
                chat_client.name = self.username
                self.start_chat_client()

            match choice:
                case 1:
                    print("Starting as Host...")
                    _hostPeer = HostPeer()
                    print("End of the game, thank you for playing")
                    normal_ending = True
                case 2:
                    connection = PeerConnection(0, verbose_flag=True)
                    print("Waiting for host broadcast...")
                    if connection.wait_for_broadcast():
                        choice = GuiIO.get_connector_role()
                        match choice:
                            case 1:
                                print("Starting as Spectator...")
                                _spectator = SpectatorPeer(connection)
                                normal_ending = True
                            case 2:
                                print("Starting as Battler...")
                                _joiner = JoinerPeer(connection)
                                normal_ending = True
                    else:
                        print("Failed to connect to host!")
        except Exception as e:
            print(f"Game error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            # Check if game ended normally by seeing if we completed without error
            # If HostPeer() or JoinerPeer() completed, normal_ending would be True
            # For now, always keep GUI open on failure - user must close manually
            try:
                # Only shutdown if no exception occurred
                if "normal_ending" in locals() and normal_ending:
                    self.start_shutdown_countdown()
                else:
                    print("\n" + "=" * 50)
                    print("=== Game ended ===")
                    print("Please close the window manually when you're done.")
                    print("=" * 50)
            except:
                pass  # Ensure finally block doesn't fail

    def start_chat_host(self):
        """Start chat host in the same window."""
        try:
            # Initialize host connection
            chat_host.chat_host = chat_host.HostConnection(chat_host.HOST_PORT + 1)
            chat_host.chat_host.discovery_broadcast()

            # Load stickers
            sticker_names = [
                chat_host.os.path.basename(s) for s in chat_host.available_stickers
            ]
            self.sticker_combo["values"] = sticker_names
            if sticker_names:
                self.sticker_combo.current(0)

            # Enable chat UI
            self.chat_active = True
            self.chat_label.config(text=f"Chat - {self.username} (HOST)", bg="#27ae60")
            self.chat_input.config(state="normal")
            self.chat_send_btn.config(state="normal")
            self.sticker_btn.config(state="normal")

            # Start threads
            t_recv = threading.Thread(target=self.chat_host_receiver, daemon=True)
            t_broadcast = threading.Thread(
                target=chat_host.broadcaster_thread, daemon=True
            )
            t_recv.start()
            t_broadcast.start()

        except Exception as e:
            print(f"Chat host error: {e}")

    def chat_host_receiver(self):
        """Receiver thread for chat host."""
        while True:
            try:
                chat_host.chat_host.socket.settimeout(0.1)
                data = chat_host.chat_host.receive()
                if data:
                    # Handle sticker fragments
                    if data.get("message_type") == "STICKER_FRAGMENT":
                        sticker_id = data.get("sticker_id")
                        chunk_index = int(data.get("chunk_index"))
                        total_chunks = int(data.get("total_chunks"))
                        fragment_data = data.get("fragment_data")
                        sender_name = data.get("sender_name")

                        if sticker_id not in chat_host.sticker_buffers:
                            chat_host.sticker_buffers[sticker_id] = {
                                "chunks": {},
                                "total_chunks": total_chunks,
                                "sender_name": sender_name,
                            }

                        chat_host.sticker_buffers[sticker_id]["chunks"][chunk_index] = (
                            fragment_data
                        )

                        # Relay fragment
                        fragment_msg = chat_host.StickerFragment(
                            0,
                            sticker_id,
                            sender_name,
                            chunk_index,
                            total_chunks,
                            fragment_data,
                        )
                        chat_host.message_queue.put(fragment_msg)

                        # Check if complete
                        if (
                            len(chat_host.sticker_buffers[sticker_id]["chunks"])
                            == total_chunks
                        ):
                            final_data = "".join(
                                chat_host.sticker_buffers[sticker_id]["chunks"][i]
                                for i in range(total_chunks)
                            )
                            chat_host.gui_queue.put(
                                ("STICKER", sender_name, final_data)
                            )
                            del chat_host.sticker_buffers[sticker_id]
                        continue

                    if data.get("message_type") == "CHAT_MESSAGE":
                        sender = data.get("sender_name")
                        msg_text = data.get("message_text")
                        formatted_msg = f"[{sender}]: {msg_text}"
                        chat_host.gui_queue.put(("MESSAGE", formatted_msg))

                        # Relay
                        relay_msg = chat_host.TextMessage(0, sender, msg_text)
                        chat_host.message_queue.put(relay_msg)
            except Exception:
                continue

    def start_chat_client(self):
        """Start chat client in the same window."""
        try:
            # Initialize connection with port 0 (system auto-assigns available port)
            chat_client.joiner = PeerConnection(0)

            # Wait for broadcast
            if not chat_client.joiner.wait_for_broadcast():
                messagebox.showerror(
                    "Connection Failed", "Failed to connect to chat host!"
                )
                return

            # Load stickers
            sticker_names = [
                chat_client.os.path.basename(s) for s in chat_client.available_stickers
            ]
            self.sticker_combo["values"] = sticker_names
            if sticker_names:
                self.sticker_combo.current(0)

            # Enable chat UI
            self.chat_active = True
            self.chat_label.config(text=f"Chat - {self.username}", bg="#2c3e50")
            self.chat_input.config(state="normal")
            self.chat_send_btn.config(state="normal")
            self.sticker_btn.config(state="normal")

            # Start receiver thread
            t = threading.Thread(target=chat_client.receiver_thread, daemon=True)
            t.start()

        except Exception as e:
            print(f"Chat client error: {e}")

    def check_chat_queue(self):
        """Check for chat messages to display."""
        if self.choice == 1:
            # Host
            while not chat_host.gui_queue.empty():
                msg_data = chat_host.gui_queue.get()
                self.display_chat_message(msg_data)
        else:
            # Client
            while not chat_client.gui_queue.empty():
                msg_data = chat_client.gui_queue.get()
                self.display_chat_message(msg_data)

    def display_chat_message(self, msg_data):
        """Display a chat message in the chat text widget."""
        msg_type = msg_data[0]

        if msg_type == "MESSAGE":
            data = msg_data[1]
            self.chat_text.config(state="normal")
            self.chat_text.insert("end", data + "\n")
            self.chat_text.see("end")
            self.chat_text.config(state="disabled")
        elif msg_type == "STICKER":
            sender_name = msg_data[1]
            sticker_data = msg_data[2]

            self.chat_text.config(state="normal")
            self.chat_text.insert("end", f"[{sender_name}] sent a sticker:\n")

            try:
                img = tk.PhotoImage(data=sticker_data)
                self.chat_text.image_create("end", image=img)
                self.chat_text.image_refs.append(img)
                self.chat_text.insert("end", "\n")
            except Exception as e:
                self.chat_text.insert("end", f"[Error displaying sticker: {e}]\n")

            self.chat_text.see("end")
            self.chat_text.config(state="disabled")

    def send_chat_message(self):
        """Send a chat message."""
        message_text = self.chat_input.get()
        if not message_text.strip():
            return

        if self.choice == 1:
            # Host
            m = chat_host.TextMessage(0, self.username, message_text.strip())
            chat_host.message_queue.put(m)

            # Display locally
            formatted = f"[{self.username}]: {message_text.strip()}"
            self.chat_text.config(state="normal")
            self.chat_text.insert("end", formatted + "\n")
            self.chat_text.see("end")
            self.chat_text.config(state="disabled")
        else:
            # Client
            m = chat_client.TextMessage(
                chat_client.joiner.send_sequence_number,
                self.username,
                message_text.strip(),
            )
            chat_client.joiner.send(m.to_message_format())

            # Display locally
            formatted = f"[{self.username}]: {message_text.strip()}"
            self.chat_text.config(state="normal")
            self.chat_text.insert("end", formatted + "\n")
            self.chat_text.see("end")
            self.chat_text.config(state="disabled")

        self.chat_input.delete(0, "end")

    def send_sticker(self):
        """Send a sticker."""
        if not self.sticker_combo.get():
            return

        idx = self.sticker_combo.current()
        if idx < 0:
            return

        if self.choice == 1:
            # Host
            if idx < len(chat_host.available_stickers):
                t = threading.Thread(
                    target=chat_host.chunk_and_send,
                    args=(chat_host.available_stickers[idx],),
                    daemon=True,
                )
                t.start()
        else:
            # Client
            if idx < len(chat_client.available_stickers):
                t = threading.Thread(
                    target=chat_client.chunk_and_send,
                    args=(chat_client.available_stickers[idx],),
                    daemon=True,
                )
                t.start()

    def run(self):
        """Start the main GUI loop."""
        self.root.mainloop()
        # Restore stdout on exit
        sys.stdout = sys.__stdout__


if __name__ == "__main__":
    app = GuiGame()
    app.run()
