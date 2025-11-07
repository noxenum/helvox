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
        level_frame.grid(row=1, column=0, sticky="ns", pady=5, padx=5)

        self.level_canvas = tk.Canvas(level_frame, width=40, height=200, bg="black")
        self.level_canvas.grid(row=0, column=0, sticky="ns", padx=5, pady=5)

        self.level_text = tk.StringVar(value="Level: 0 dB")
        ttk.Label(level_frame, textvariable=self.level_text).grid(
            row=1, column=0, sticky=tk.W, padx=5
        )

        # Waveform Visualization
        waveform_frame = ttk.LabelFrame(main_frame, text="Recording", padding="5")
        waveform_frame.grid(row=2, column=0, columnspan=3, sticky="we", pady=5)

        self.waveform_canvas = tk.Canvas(waveform_frame, height=60, bg="black")
        self.waveform_canvas.grid(row=0, column=0, sticky="we", padx=5, pady=5)
        waveform_frame.columnconfigure(0, weight=1)

        self.duration_text = tk.StringVar(value="Duration: 0.0 seconds")
        ttk.Label(waveform_frame, textvariable=self.duration_text).grid(
            row=1, column=0, sticky=tk.W, padx=5
        )

        # Recording Controls
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, pady=10)

        self.record_btn = ttk.Button(
            control_frame,
            text="Start Recording",
            command=self.toggle_recording,
            state=tk.NORMAL,
        )
        self.record_btn.grid(row=0, column=0, padx=5)

        self.play_btn = ttk.Button(
            control_frame,
            text="Preview",
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

        if height > 1:  # Only draw if canvas is visible
            # Clear canvas
            self.level_canvas.delete("all")

            # Convert dB to normalized value (0-1)
            db_min = -60
            db_max = 0
            normalized = max(0, min(1, (level - db_min) / (db_max - db_min)))

            # Number of segments
            num_segments = 20
            segment_height = height / num_segments
            segment_spacing = 2  # Pixels between segments

            # Draw segments from bottom to top
            for i in range(num_segments):
                segment_normalized = i / num_segments
                segment_y = height - (i + 1) * segment_height

                # Determine if segment should be lit
                is_lit = normalized >= segment_normalized

                # Determine color based on position
                if i >= int(num_segments * 0.9):  # Top 10% red
                    color = "red" if is_lit else "darkred"
                elif i >= int(num_segments * 0.7):  # Next 20% yellow
                    color = "yellow" if is_lit else "darkgoldenrod4"
                else:  # Bottom 70% green
                    color = "green2" if is_lit else "darkgreen"

                # Draw segment
                self.level_canvas.create_rectangle(
                    2,  # Left margin
                    segment_y + segment_spacing / 2,
                    width - 2,  # Right margin
                    segment_y + segment_height - segment_spacing / 2,
                    fill=color,
                    outline="",
                )

            # Draw tick marks and dB labels every 10 dB
            for i in range(0, 7):
                db_value = db_min + (i * 10)
                y_pos = height * (1 - (db_value - db_min) / (db_max - db_min))
                # Tick mark
                self.level_canvas.create_line(0, y_pos, 5, y_pos, fill="gray", width=1)
                # dB label
                self.level_canvas.create_text(
                    width + 15,
                    y_pos,
                    text=f"{db_value}",
                    fill="white",
                    anchor="w",
                    font=("Arial", 7),
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
            self.update_waveform()

    def update_waveform(self) -> None:
        # Update duration text
        duration = self.recorder.get_duration()
        self.duration_text.set(f"Duration: {duration:.1f} seconds")

        # Get waveform data
        waveform = self.recorder.get_waveform_data()

        # Get canvas dimensions
        width = self.waveform_canvas.winfo_width()
        height = self.waveform_canvas.winfo_height()
        center_y = height // 2

        # Clear canvas
        self.waveform_canvas.delete("all")

        # Draw vertical bars
        bar_width = max(1, width // len(waveform) // 2)
        for i, value in enumerate(waveform):
            x = int((i / len(waveform)) * width)
            # Scale the value to half the height (since we're drawing from center)
            bar_height = int(value * (height / 2))
            # Draw vertical bar centered at center_y
            if bar_height != 0:  # Only draw if there's a visible amplitude
                self.waveform_canvas.create_line(
                    x,
                    center_y - bar_height,
                    x,
                    center_y + bar_height,
                    fill="orange red",
                    width=bar_width,
                    capstyle=tk.ROUND,
                    joinstyle=tk.ROUND,
                )

    def save_audio(self) -> None:
        self.recorder.save_audio("test")

    def on_closing(self) -> None:
        self.recorder.stop_monitoring()
        if self.recorder.recording:
            self.recorder.stop_recording()
        self.root.destroy()
        self.root.destroy()
