import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from helvox.utils.audio import Recorder


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root

        self.recorder = Recorder(
            output_folder=Path.cwd() / "recordings", sample_rate=48000, channels=1
        )

        self.setup_window()
        self.setup_ui()
        self.refresh_audio_devices()

    def setup_window(self) -> None:
        self.root.title("Helvox")
        self.root.geometry("800x600")

        # Set minimum window size
        self.root.minsize(600, 400)

        # Optional: Set app icon (if you have one)
        icon_path = Path(__file__).parent / "resources" / "icons" / "app.ico"
        if icon_path.exists():
            self.root.iconbitmap(icon_path)

    def setup_ui(self) -> None:
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nswe")

        # Output Folder Selection
        folder_frame = ttk.LabelFrame(main_frame, text="Output Folder", padding="5")
        folder_frame.grid(row=1, column=0, columnspan=3, sticky="we", pady=5)

        self.folder_var = tk.StringVar(value=f"Output: {Path.cwd() / 'recordings'}")
        ttk.Label(folder_frame, textvariable=self.folder_var, wraplength=500).grid(
            row=0, column=0, sticky=tk.W, padx=5
        )
        ttk.Button(folder_frame, text="Select Folder", command=self.select_folder).grid(
            row=0, column=1, padx=5
        )

        # Audio Device Selection
        device_frame = ttk.LabelFrame(
            main_frame, text="Audio Input Device", padding="5"
        )
        device_frame.grid(row=2, column=0, columnspan=3, sticky="we", pady=5)

        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(
            device_frame, textvariable=self.device_var, state="readonly", width=60
        )
        self.device_combo.grid(row=0, column=0, padx=5)
        ttk.Button(
            device_frame, text="Refresh", command=self.refresh_audio_devices
        ).grid(row=0, column=1, padx=5)

        # Recording Controls
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=3, pady=10)

        self.record_btn = ttk.Button(
            control_frame,
            text="⏺ Start Recording",
            command=self.toggle_recording,
            state=tk.NORMAL,
        )
        self.record_btn.grid(row=0, column=0, padx=5)

        self.play_btn = ttk.Button(
            control_frame,
            text="▶ Play",
            command=self.recorder.play_audio_data,
            state=tk.NORMAL,
        )
        self.play_btn.grid(row=0, column=1, padx=5)

        self.save_btn = ttk.Button(
            control_frame,
            text="💾 Save",
            command=self.save_audio,
            state=tk.NORMAL,
        )
        self.save_btn.grid(row=0, column=2, padx=5)

    def refresh_audio_devices(self) -> None:
        self.recorder.refresh_audio_devices()

        device_names = list(self.recorder.device_map.keys())
        self.device_combo["values"] = device_names

        if device_names:
            self.device_var.set(device_names[0])

    def select_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.recorder.update_output_folder(folder)
            self.folder_var.set(f"Output: {folder}")

    def toggle_recording(self) -> None:
        if not self.recorder.recording:
            self.recorder.start_recording(self.device_var.get())
            self.record_btn.config(text="⏹ Stop Recording")
        else:
            self.recorder.stop_recording()
            self.record_btn.config(text="⏺ Start Recording")

    def save_audio(self) -> None:
        self.recorder.save_audio("test")
