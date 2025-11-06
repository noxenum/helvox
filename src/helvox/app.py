import tkinter as tk
from pathlib import Path


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.setup_window()

    def setup_window(self) -> None:
        self.root.title("Helvox")
        self.root.geometry("800x600")

        # Set minimum window size
        self.root.minsize(600, 400)

        # Optional: Set app icon (if you have one)
        icon_path = Path(__file__).parent / "resources" / "icons" / "app.ico"
        if icon_path.exists():
            self.root.iconbitmap(icon_path)
