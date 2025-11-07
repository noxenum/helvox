from pathlib import Path
from typing import Union

import numpy as np
import sounddevice as sd
import soundfile as sf
from sounddevice import CallbackFlags


class Recorder:
    def __init__(
        self,
        output_folder: Union[str, Path],
        sample_rate: int = 48000,
        channels: int = 1,
    ) -> None:
        self.recording = False
        self.monitoring = False
        self.output_folder = Path(output_folder)
        self.sample_rate = sample_rate
        self.channels = channels

        self.device_map = {}
        self.current_level = -60.0  # dB
        self.full_audio = None

        self.monitor_stream = None
        self.stream = None

        self.selected_device = ""

    def get_audio_devices(self) -> dict:
        devices = sd.query_devices()
        device_map = {}

        for idx, device in enumerate(devices):
            if device["max_input_channels"] > 0:
                device_name = f"{device['name']}"
                device_map[device_name] = idx

        return device_map

    def refresh_audio_devices(self) -> None:
        self.device_map = self.get_audio_devices()

    def calculate_rms_db(self, audio_data: np.ndarray) -> float:
        if len(audio_data) == 0:
            return -60.0

        # Calculate RMS
        rms = np.sqrt(np.mean(audio_data**2))

        # Convert to dB (with floor to avoid log(0))
        if rms > 0:
            db = 20 * np.log10(rms)
        else:
            db = -60.0

        return max(-60.0, min(0.0, db))

    def start_monitoring(self) -> None:
        if self.monitoring:
            self.stop_monitoring()

        device_idx = self.device_map.get(self.selected_device)
        if device_idx is None:
            return

        self.monitoring = True

        def monitor_callback(indata: np.ndarray, frames, time, status: CallbackFlags):
            if status:
                print(status)

            # Calculate level
            self.current_level = self.calculate_rms_db(indata)

        try:
            self.monitor_stream = sd.InputStream(
                device=device_idx,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=monitor_callback,
            )
            self.monitor_stream.start()
        except Exception as e:
            print(f"Error starting monitor stream: {e}")
            self.monitoring = False

    def stop_monitoring(self) -> None:
        if self.monitoring and self.monitor_stream:
            try:
                self.monitor_stream.stop()
                self.monitor_stream.close()
            except Exception as e:
                print(f"Error stopping monitor stream: {e}")
            finally:
                self.monitoring = False
                self.monitor_stream = None
                self.current_level = -60.0

    def get_current_level(self) -> float:
        return self.current_level

    def start_recording(self):
        if not self.selected_device:
            return

        device_idx = self.device_map.get(self.selected_device)

        # Stop monitoring while recording
        if self.monitoring:
            self.stop_monitoring()

        self.recording = True
        self.audio_data = []

        def callback(indata: np.ndarray, frames, time, status: CallbackFlags):
            if status:
                print(status)
            self.audio_data.append(indata.copy())

            # Update level during recording
            self.current_level = self.calculate_rms_db(indata)

        self.stream = sd.InputStream(
            device=device_idx,
            channels=self.channels,
            samplerate=self.sample_rate,
            callback=callback,
        )

        self.stream.start()

    def stop_recording(self) -> None:
        if self.recording and self.stream:
            self.stream.stop()
            self.stream.close()
            self.recording = False

            if self.audio_data:
                self.full_audio = np.concatenate(self.audio_data, axis=0)

            # Restart monitoring after recording stops
            self.start_monitoring()

    def save_audio(self, filename: str) -> None:
        if not self.output_folder.exists():
            self.output_folder.mkdir(parents=True, exist_ok=True)

        audio_path = Path(self.output_folder, f"{filename}.flac")
        sf.write(audio_path, self.full_audio, self.sample_rate, format="FLAC")

    def play_audio_data(self):
        if self.full_audio is not None:
            sd.play(self.full_audio, self.sample_rate)

    def check_playback(self) -> bool:
        return sd.get_stream().active

    def update_output_folder(self, folder: Union[str, Path]) -> None:
        self.output_folder = Path(folder)
