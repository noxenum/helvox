import tkinter as tk
from tkinter import filedialog, ttk

from helvox.utils.audio import Recorder


class SettingsDialog:
    def __init__(self, parent: tk.Tk, recorder: Recorder) -> None:
        self.recorder = recorder
        self.result = None

        # Create modal dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("600x300")
        self.dialog.resizable(False, False)

        # Make it modal
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = (
            parent.winfo_x()
            + (parent.winfo_width() // 2)
            - (self.dialog.winfo_width() // 2)
        )
        y = (
            parent.winfo_y()
            + (parent.winfo_height() // 2)
            - (self.dialog.winfo_height() // 2)
        )
        self.dialog.geometry(f"+{x}+{y}")

        self.setup_ui()

        # Handle window close button
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def setup_ui(self) -> None:
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky="nswe")

        # Output Folder Selection
        folder_frame = ttk.LabelFrame(main_frame, text="Output Folder", padding="10")
        folder_frame.grid(row=0, column=0, sticky="we", pady=(0, 15))

        self.folder_var = tk.StringVar(value=str(self.recorder.output_folder))
        ttk.Label(folder_frame, textvariable=self.folder_var, wraplength=400).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        ttk.Button(folder_frame, text="Browse...", command=self.select_folder).grid(
            row=0, column=1, padx=5, pady=5
        )

        # Audio Device Selection
        device_frame = ttk.LabelFrame(
            main_frame, text="Audio Input Device", padding="10"
        )
        device_frame.grid(row=1, column=0, sticky="we", pady=(0, 15))

        self.device_var = tk.StringVar(value=self.recorder.selected_device or "")
        self.device_combo = ttk.Combobox(
            device_frame, textvariable=self.device_var, state="readonly", width=50
        )
        self.device_combo.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Button(device_frame, text="Refresh", command=self.refresh_devices).grid(
            row=0, column=1, padx=5, pady=5
        )

        # Populate devices
        self.refresh_devices()

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(10, 0))

        ttk.Button(button_frame, text="OK", command=self.on_ok, width=12).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel, width=12).grid(
            row=0, column=1, padx=5
        )

        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

    def select_folder(self) -> None:
        folder = filedialog.askdirectory(
            title="Select Output Folder", initialdir=self.recorder.output_folder
        )
        if folder:
            self.folder_var.set(folder)

    def refresh_devices(self) -> None:
        self.recorder.refresh_audio_devices()
        device_names = list(self.recorder.device_map.keys())
        self.device_combo["values"] = device_names

        if device_names and not self.device_var.get():
            self.device_var.set(device_names[0])

    def on_ok(self) -> None:
        self.result = {
            "output_folder": self.folder_var.get(),
            "device": self.device_var.get(),
        }
        self.dialog.destroy()

    def on_cancel(self) -> None:
        self.result = None
        self.dialog.destroy()

    def show(self) -> dict | None:
        self.dialog.wait_window()
        return self.result
