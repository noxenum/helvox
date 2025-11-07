import tkinter as tk
from pathlib import Path
from tkinter import ttk

from platformdirs import user_config_path

from helvox.ui.settings import SettingsDialog
from helvox.utils.audio import Recorder


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root

        self.recorder = Recorder(
            output_folder=Path.cwd() / "recordings", sample_rate=48000, channels=1
        )

        self.settings_path = (
            user_config_path(appname="helvox", appauthor="noxenum") / "config.ini"
        )

        self.setup_window()
        self.setup_ui()

        # Show settings dialog on startup
        self.show_settings()

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

        # Settings button at the top
        settings_frame = ttk.Frame(main_frame)
        settings_frame.grid(row=0, column=0, columnspan=3, sticky="we", pady=(0, 10))

        ttk.Button(settings_frame, text="Settings", command=self.show_settings).pack(
            side=tk.RIGHT
        )

        # Mic Level Meter
        level_frame = ttk.LabelFrame(main_frame, text="Input Level", padding="5")
        level_frame.grid(row=1, column=0, columnspan=3, sticky="we", pady=5)

        self.level_canvas = tk.Canvas(level_frame, height=30, bg="black")
        self.level_canvas.grid(row=0, column=0, sticky="we", padx=5, pady=5)
        level_frame.columnconfigure(0, weight=1)

        self.level_text = tk.StringVar(value="Level: 0 dB")
        ttk.Label(level_frame, textvariable=self.level_text).grid(
            row=1, column=0, sticky=tk.W, padx=5
        )

        # Recording Controls
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=10)

        self.record_btn = ttk.Button(
            control_frame,
            text="Start Recording",
            command=self.toggle_recording,
            state=tk.NORMAL,
        )
        self.record_btn.grid(row=0, column=0, padx=5)

        self.play_btn = ttk.Button(
            control_frame,
            text="Play",
            command=self.recorder.play_audio_data,
            state=tk.NORMAL,
        )
        self.play_btn.grid(row=0, column=1, padx=5)

        self.save_btn = ttk.Button(
            control_frame,
            text="Save",
            command=self.save_audio,
            state=tk.NORMAL,
        )
        self.save_btn.grid(row=0, column=2, padx=5)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

    def show_settings(self) -> None:
        self.recorder.load_settings(self.settings_path)
        dialog = SettingsDialog(self.root, self.recorder)
        result = dialog.show()

        if result:
            # Apply settings
            self.recorder.update_output_folder(result["output_folder"])
            self.recorder.update_selected_device(result["device"])
            self.recorder.speaker_id = result["speaker_id"]
            self.recorder.speaker_dialect = result["speaker_dialect"]

            self.recorder.save_settings(self.settings_path)

            self.start_monitoring()

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
        if self.recorder.selected_device:
            self.recorder.start_monitoring()
            self.update_level_meter()

    def toggle_recording(self) -> None:
        if not self.recorder.recording:
            self.recorder.start_recording()
            self.record_btn.config(text="Stop Recording")
        else:
            self.recorder.stop_recording()
            self.record_btn.config(text="Start Recording")

    def save_audio(self) -> None:
        self.recorder.save_audio("test")

    def on_closing(self) -> None:
        self.recorder.stop_monitoring()
        if self.recorder.recording:
            self.recorder.stop_recording()
        self.root.destroy()
        self.root.destroy()
