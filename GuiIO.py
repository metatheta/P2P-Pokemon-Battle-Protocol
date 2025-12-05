import tkinter as tk
from tkinter import messagebox
import queue
import time
from Data import Data
from Templates import Move

# AI utilized for GUI implementation.

class NonModalDialog:
    """A non-modal dialog that doesn't block the main window."""

    def __init__(
        self, title, prompt, dialog_type="string", minvalue=None, maxvalue=None
    ):
        self.result = None
        self.dialog = tk.Toplevel()
        self.dialog.title(title)
        self.dialog_type = dialog_type
        self.minvalue = minvalue
        self.maxvalue = maxvalue

        # Center the dialog
        self.dialog.geometry("400x150")
        self.dialog.transient()  # Float on top but don't block

        # Prompt label
        tk.Label(
            self.dialog, text=prompt, wraplength=350, justify="left", padx=10, pady=10
        ).pack()

        # Entry field
        self.entry = tk.Entry(self.dialog, width=40)
        self.entry.pack(padx=10, pady=5)
        self.entry.focus_set()

        # Buttons frame
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=10)

        ok_btn = tk.Button(btn_frame, text="OK", command=self._on_ok, width=10)
        ok_btn.pack(side="left", padx=5)

        cancel_btn = tk.Button(
            btn_frame, text="Cancel", command=self._on_cancel, width=10
        )
        cancel_btn.pack(side="left", padx=5)

        # Bind Enter key
        self.entry.bind("<Return>", lambda e: self._on_ok())

        # Don't use grab_set() - this is what makes dialogs modal
        # self.dialog.grab_set()

    def _on_ok(self):
        value = self.entry.get()

        if self.dialog_type == "integer":
            try:
                int_value = int(value)
                if self.minvalue is not None and int_value < self.minvalue:
                    messagebox.showwarning(
                        "Invalid", f"Value must be at least {self.minvalue}"
                    )
                    return
                if self.maxvalue is not None and int_value > self.maxvalue:
                    messagebox.showwarning(
                        "Invalid", f"Value must be at most {self.maxvalue}"
                    )
                    return
                self.result = int_value
            except ValueError:
                messagebox.showwarning("Invalid", "Please enter a valid integer")
                return
        else:
            self.result = value

        self.dialog.destroy()

    def _on_cancel(self):
        self.result = None
        self.dialog.destroy()

    def show(self):
        """Show the dialog and wait for result while keeping the main loop responsive."""
        # Instead of wait_window() which blocks, we poll the dialog state
        # This allows the main event loop to continue processing chat updates
        while self.dialog.winfo_exists():
            try:
                # Update both the dialog AND the main root window
                # This ensures chat messages and other updates continue to process
                self.dialog.update()
                if GuiIO.root:
                    GuiIO.root.update()
                    # Also process idle tasks to ensure chat messages are shown
                    GuiIO.root.update_idletasks()

                # Manually trigger chat update if callback is registered
                if GuiIO.chat_update_callback:
                    GuiIO.chat_update_callback()

                # Small sleep to prevent CPU spinning
                time.sleep(0.01)
            except tk.TclError:
                # Dialog was destroyed
                break
        return self.result


class GuiIO:
    """
    A thread-safe replacement for the IO class that interacts with the GUI.
    """

    input_queue = queue.Queue()
    result_queue = queue.Queue()
    root = None
    status_callback = None
    chat_update_callback = None  # New callback for chat updates

    @staticmethod
    def set_root(root):
        GuiIO.root = root

    @staticmethod
    def register_status_callback(callback):
        """Register a callback to update the battle status UI."""
        GuiIO.status_callback = callback

    @staticmethod
    def register_chat_update_callback(callback):
        """Register a callback to update chat messages."""
        GuiIO.chat_update_callback = callback

    @staticmethod
    def update_battle_status(
        my_name, my_hp, my_max_hp, enemy_name, enemy_hp, enemy_max_hp
    ):
        """Queue a status update for the main thread."""
        if GuiIO.status_callback:
            GuiIO._execute_on_main_thread(
                GuiIO.status_callback,
                my_name,
                my_hp,
                my_max_hp,
                enemy_name,
                enemy_hp,
                enemy_max_hp,
            )

    @staticmethod
    def _request_input(func, *args, **kwargs):
        """Helper to send a request to the main thread and wait for result."""
        if not GuiIO.root:
            raise RuntimeError("GuiIO root not set")

        # Puts a callable (func with args) into the input queue for the main thread to execute
        GuiIO.input_queue.put((func, args, kwargs))

        # Blocking wait for the result
        return GuiIO.result_queue.get()

    @staticmethod
    def _execute_on_main_thread(func, *args, **kwargs):
        """Execute something on main thread without waiting for result (for notifications)."""
        if not GuiIO.root:
            raise RuntimeError("GuiIO root not set")

        # Put a special marker to indicate no result is expected
        GuiIO.input_queue.put((func, args, kwargs, True))  # True = no result needed

    @staticmethod
    def get_role() -> int:
        def _ask_role():
            while True:
                dialog = NonModalDialog(
                    "Role Selection",
                    "Choose your role:\n1] Host\n2] Connector (Joiner/Spectator)",
                    dialog_type="integer",
                    minvalue=1,
                    maxvalue=2,
                )
                result = dialog.show()
                if result is not None:
                    return result
                messagebox.showwarning(
                    "Required", "You must select a role to continue!"
                )

        return GuiIO._request_input(_ask_role)

    @staticmethod
    def print_role_list():
        print("Role selection requested...")

    @staticmethod
    def get_connector_role() -> int:
        def _ask_connector():
            while True:
                dialog = NonModalDialog(
                    "Connector Role",
                    "Choose your role:\n1] Spectator\n2] Battler",
                    dialog_type="integer",
                    minvalue=1,
                    maxvalue=2,
                )
                result = dialog.show()
                if result is not None:
                    return result
                messagebox.showwarning(
                    "Required", "You must select a role to continue!"
                )

        return GuiIO._request_input(_ask_connector)

    @staticmethod
    def ask_pokemon() -> str:
        def _ask_poke():
            dialog = NonModalDialog("Pokemon Selection", "Enter Pokemon Name:")
            name = dialog.show()
            return name

        while True:
            name = GuiIO._request_input(_ask_poke)
            if not name or not name.strip():

                def show_warning():
                    messagebox.showwarning("Required", "You must enter a Pokemon name!")

                GuiIO._execute_on_main_thread(show_warning)
                continue
            if name.lower() in Data.pokemonDataDictionary:
                return name.lower()

            def show_error():
                messagebox.showerror("Error", f"Pokemon '{name}' not found!")

            GuiIO._execute_on_main_thread(show_error)

    @staticmethod
    def ask_move() -> str:
        def _ask_moves():
            dialog = NonModalDialog(
                "Move Selection",
                "Enter 4 move numbers (1-36) separated by commas:\n(Check console/log for list)",
            )
            return dialog.show()

        print("Available Moves:")
        GuiIO.print_moves()

        while True:
            answer = GuiIO._request_input(_ask_moves)
            if not answer or not answer.strip():

                def show_warning():
                    messagebox.showwarning("Required", "You must enter move numbers!")

                GuiIO._execute_on_main_thread(show_warning)
                continue

            try:
                nums = [int(x) for x in answer.split(",")]
            except ValueError:
                print("Invalid format. Use numbers separated by commas.")

                def show_error():
                    messagebox.showerror(
                        "Error", "Invalid format! Use numbers separated by commas."
                    )

                GuiIO._execute_on_main_thread(show_error)
                continue

            def is_valid(x):
                return 0 < x <= 36

            if len(nums) != 4 or len(nums) != len(set(nums)):
                print("Must select exactly 4 unique moves.")

                def show_error():
                    messagebox.showerror("Error", "Must select exactly 4 unique moves!")

                GuiIO._execute_on_main_thread(show_error)
                continue
            if not all(is_valid(x) for x in nums):
                print("Move numbers must be between 1 and 36.")

                def show_error():
                    messagebox.showerror(
                        "Error", "Move numbers must be between 1 and 36!"
                    )

                GuiIO._execute_on_main_thread(show_error)
                continue
            break
        return answer

    @staticmethod
    def print_moves():
        moveDict = Data.moveDictionary
        number = 1
        row = ""

        for key, move in moveDict.items():
            row += f"{number}] {move.name:<25}"
            if number % 3 == 0:
                print(row)
                row = ""
            number += 1
        if row:
            print(row)

    @staticmethod
    def choose_attack(pokemonName: str, moveTuple: tuple[Move]) -> int:
        def _choose(p_name, m_tuple):
            while True:
                msg = f"Choose attack for {p_name}:\n"
                for i, move in enumerate(m_tuple):
                    msg += f"{i + 1}] {move.name} ({move.category}, {move.moveType})\n"

                dialog = NonModalDialog(
                    "Choose Attack", msg, dialog_type="integer", minvalue=1, maxvalue=4
                )
                result = dialog.show()
                if result is not None:
                    return result
                messagebox.showwarning(
                    "Required", "You must select an attack to continue!"
                )

        result = GuiIO._request_input(_choose, pokemonName, moveTuple)
        return result - 1

    @staticmethod
    def ask_username(title: str = "Username", prompt: str = "Enter your name:") -> str:
        """Ask for username in a thread-safe way."""

        def _ask():
            while True:
                dialog = NonModalDialog(title, prompt)
                result = dialog.show()
                if result and result.strip():
                    return result.strip()
                messagebox.showwarning("Required", "You must enter a name to continue!")

        return GuiIO._request_input(_ask)

    @staticmethod
    def check_input_queue():
        """Called by the main GUI loop to check for pending input requests."""
        while not GuiIO.input_queue.empty():
            item = GuiIO.input_queue.get()
            if len(item) == 4:  # Has no-result marker
                func, args, kwargs, _ = item
                func(*args, **kwargs)  # Execute but don't put result
            else:  # Normal request with result
                func, args, kwargs = item
                result = func(*args, **kwargs)
                GuiIO.result_queue.put(result)
