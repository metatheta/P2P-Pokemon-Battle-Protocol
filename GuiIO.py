from tkinter import simpledialog, messagebox
import queue
from Data import Data
from Templates import Move


class GuiIO:
    """
    A thread-safe replacement for the IO class that interacts with the GUI.
    """

    input_queue = queue.Queue()
    result_queue = queue.Queue()
    root = None
    status_callback = None

    @staticmethod
    def set_root(root):
        GuiIO.root = root

    @staticmethod
    def register_status_callback(callback):
        """Register a callback to update the battle status UI."""
        GuiIO.status_callback = callback

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
                result = simpledialog.askinteger(
                    "Role Selection",
                    "Choose your role:\n1] Host\n2] Connector (Joiner/Spectator)",
                    parent=GuiIO.root,
                    minvalue=1,
                    maxvalue=2,
                )
                if result is not None:
                    return result
                messagebox.showwarning(
                    "Required", "You must select a role to continue!", parent=GuiIO.root
                )

        return GuiIO._request_input(_ask_role)

    @staticmethod
    def print_role_list():
        print("Role selection requested...")

    @staticmethod
    def get_connector_role() -> int:
        def _ask_connector():
            while True:
                result = simpledialog.askinteger(
                    "Connector Role",
                    "Choose your role:\n1] Spectator\n2] Battler",
                    parent=GuiIO.root,
                    minvalue=1,
                    maxvalue=2,
                )
                if result is not None:
                    return result
                messagebox.showwarning(
                    "Required", "You must select a role to continue!", parent=GuiIO.root
                )

        return GuiIO._request_input(_ask_connector)

    @staticmethod
    def ask_pokemon() -> str:
        def _ask_poke():
            name = simpledialog.askstring(
                "Pokemon Selection", "Enter Pokemon Name:", parent=GuiIO.root
            )
            return name

        while True:
            name = GuiIO._request_input(_ask_poke)
            if not name or not name.strip():

                def show_warning():
                    messagebox.showwarning(
                        "Required", "You must enter a Pokemon name!", parent=GuiIO.root
                    )

                GuiIO._execute_on_main_thread(show_warning)
                continue
            if name.lower() in Data.pokemonDataDictionary:
                return name.lower()

            def show_error():
                messagebox.showerror(
                    "Error", f"Pokemon '{name}' not found!", parent=GuiIO.root
                )

            GuiIO._execute_on_main_thread(show_error)

    @staticmethod
    def ask_move() -> str:
        def _ask_moves():
            return simpledialog.askstring(
                "Move Selection",
                "Enter 4 move numbers (1-36) separated by commas:\n(Check console/log for list)",
                parent=GuiIO.root,
            )

        print("Available Moves:")
        GuiIO.print_moves()

        while True:
            answer = GuiIO._request_input(_ask_moves)
            if not answer or not answer.strip():

                def show_warning():
                    messagebox.showwarning(
                        "Required", "You must enter move numbers!", parent=GuiIO.root
                    )

                GuiIO._execute_on_main_thread(show_warning)
                continue

            try:
                nums = [int(x) for x in answer.split(",")]
            except ValueError:
                print("Invalid format. Use numbers separated by commas.")

                def show_error():
                    messagebox.showerror(
                        "Error",
                        "Invalid format! Use numbers separated by commas.",
                        parent=GuiIO.root,
                    )

                GuiIO._execute_on_main_thread(show_error)
                continue

            def is_valid(x):
                return 0 < x <= 36

            if len(nums) != 4 or len(nums) != len(set(nums)):
                print("Must select exactly 4 unique moves.")

                def show_error():
                    messagebox.showerror(
                        "Error",
                        "Must select exactly 4 unique moves!",
                        parent=GuiIO.root,
                    )

                GuiIO._execute_on_main_thread(show_error)
                continue
            if not all(is_valid(x) for x in nums):
                print("Move numbers must be between 1 and 36.")

                def show_error():
                    messagebox.showerror(
                        "Error",
                        "Move numbers must be between 1 and 36!",
                        parent=GuiIO.root,
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

                result = simpledialog.askinteger(
                    "Choose Attack", msg, parent=GuiIO.root, minvalue=1, maxvalue=4
                )
                if result is not None:
                    return result
                messagebox.showwarning(
                    "Required",
                    "You must select an attack to continue!",
                    parent=GuiIO.root,
                )

        result = GuiIO._request_input(_choose, pokemonName, moveTuple)
        return result - 1

    @staticmethod
    def ask_username(title: str = "Username", prompt: str = "Enter your name:") -> str:
        """Ask for username in a thread-safe way."""

        def _ask():
            while True:
                result = simpledialog.askstring(title, prompt, parent=GuiIO.root)
                if result and result.strip():
                    return result.strip()
                messagebox.showwarning(
                    "Required", "You must enter a name to continue!", parent=GuiIO.root
                )

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
