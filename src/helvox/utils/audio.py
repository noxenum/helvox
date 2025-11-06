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
        self.output_folder = Path(output_folder)
        self.sample_rate = sample_rate
        self.channels = channels

        self.device_map = {}

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

    def start_recording(self, device_name: str):
        device_idx = self.device_map[device_name]
        self.recording = True
        self.audio_data = []

        def callback(indata: np.ndarray, frames, time, status: CallbackFlags):
            if status:
                print(status)
            self.audio_data.append(indata.copy())

        self.stream = sd.InputStream(
            device=device_idx,
            channels=self.channels,
            samplerate=self.sample_rate,
            callback=callback,
        )

        self.stream.start()

    def stop_recording(self) -> None:
        if self.recording:
            self.stream.stop()
            self.stream.close()
            self.recording = False

            if self.audio_data:
                self.full_audio = np.concatenate(self.audio_data, axis=0)

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
