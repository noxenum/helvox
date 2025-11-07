import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

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

        # Start monitoring after UI is set up
        self.start_monitoring()

    def setup_window(self) -> None:
        self.root.title("Helvox")
        self.root.geometry("800x600")

        # Set minimum window size
        self.root.minsize(600, 400)

        # Set app icon
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
        self.device_combo.bind("<<ComboboxSelected>>", self.on_device_changed)

        ttk.Button(
            device_frame, text="Refresh", command=self.refresh_audio_devices
        ).grid(row=0, column=1, padx=5)

        # Mic Level Meter
        level_frame = ttk.LabelFrame(main_frame, text="Input Level", padding="5")
        level_frame.grid(row=3, column=0, columnspan=3, sticky="we", pady=5)

        self.level_canvas = tk.Canvas(level_frame, height=30, bg="black")
        self.level_canvas.grid(row=0, column=0, sticky="we", padx=5, pady=5)
        level_frame.columnconfigure(0, weight=1)

        self.level_text = tk.StringVar(value="Level: 0 dB")
        ttk.Label(level_frame, textvariable=self.level_text).grid(
            row=1, column=0, sticky=tk.W, padx=5
        )

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

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)

    def update_level_meter(self) -> None:
        level = self.recorder.get_current_level()

        # Update level text
        self.level_text.set(f"Level: {level:.1f} dB")

        # Get canvas dimensions
        width = self.level_canvas.winfo_width()
        height = self.level_canvas.winfo_height()

        if width > 1:  # Only draw if canvas is visible
            # Clear canvas
            self.level_canvas.delete("all")

            # Convert dB to normalized value (0-1)
            # Typical range: -60 dB (silence) to 0 dB (max)
            db_min = -60
            db_max = 0
            normalized = max(0, min(1, (level - db_min) / (db_max - db_min)))

            # Calculate bar width
            bar_width = int(width * normalized)

            # Determine color based on level
            if normalized < 0.7:
                color = "green"
            elif normalized < 0.9:
                color = "yellow"
            else:
                color = "red"

            # Draw the level bar
            if bar_width > 0:
                self.level_canvas.create_rectangle(
                    0, 0, bar_width, height, fill=color, outline=""
                )

            # Draw tick marks every 10 dB
            for i in range(0, 7):
                db_value = db_min + (i * 10)
                x_pos = int(width * (db_value - db_min) / (db_max - db_min))
                self.level_canvas.create_line(
                    x_pos, 0, x_pos, height, fill="gray", width=1
                )

        # Schedule next update
        self.root.after(50, self.update_level_meter)

    def start_monitoring(self) -> None:
        if self.device_var.get():
            self.recorder.start_monitoring()
            self.update_level_meter()

    def on_device_changed(self, event=None) -> None:
        if self.device_var.get():
            self.recorder.selected_device = self.device_var.get()
            self.recorder.stop_monitoring()
            self.recorder.start_monitoring()

    def refresh_audio_devices(self) -> None:
        self.recorder.refresh_audio_devices()

        device_names = list(self.recorder.device_map.keys())
        self.device_combo["values"] = device_names

        if device_names:
            self.device_var.set(device_names[0])
            self.on_device_changed()

    def select_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.recorder.update_output_folder(folder)
            self.folder_var.set(f"Output: {folder}")

    def toggle_recording(self) -> None:
        if not self.recorder.recording:
            self.recorder.start_recording()
            self.record_btn.config(text="⏹ Stop Recording")
        else:
            self.recorder.stop_recording()
            self.record_btn.config(text="⏺ Start Recording")

    def save_audio(self) -> None:
        self.recorder.save_audio("test")

    def on_closing(self) -> None:
        self.recorder.stop_monitoring()
        if self.recorder.recording:
            self.recorder.stop_recording()
        self.root.destroy()
