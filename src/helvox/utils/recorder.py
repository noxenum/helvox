import configparser
from pathlib import Path
from typing import Union

import numpy as np
import sounddevice as sd
import soundfile as sf
from sounddevice import CallbackFlags

from helvox.utils.data import read_dataset
from helvox.utils.trim import trim_silence


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
        self.trimmed_audio = None

        self.monitor_stream = None
        self.stream = None

        self.selected_device = ""
        self.speaker_id = "unknown"
        self.speaker_dialect = "AG"
        self.input_file = ""
        self.output_file = ""

        self.input_data = []
        self.input_index = {}
        self.output_data = []
        self.output_index = {}

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

                self.trimmed_audio = trim_silence(
                    self.full_audio,
                    sample_rate=self.sample_rate,
                    aggressiveness=2,
                    frame_duration_ms=30,
                    padding_duration_s=0.1,
                )

            # Restart monitoring after recording stops
            self.start_monitoring()

    def save_audio(self, filename: str) -> None:
        audio_path = self.output_folder / self.speaker_id / "audio" / f"{filename}.flac"

        if not audio_path.parent.exists():
            audio_path.parent.mkdir(parents=True, exist_ok=True)

        sf.write(audio_path, self.trimmed_audio, self.sample_rate, format="FLAC")

    def play_audio_data_full_audio(self):
        self.play_audio_data(self.full_audio)

    def play_audio_data_trimmed_audio(self):
        self.play_audio_data(self.trimmed_audio)

    def play_audio_data(self, audio):
        if audio is not None:
            sd.play(audio, self.sample_rate)

    def check_playback(self) -> bool:
        return sd.get_stream().active

    def get_duration_full_audio(self) -> float:
        return self.get_duration(self.full_audio)

    def get_duration_trimmed_audio(self) -> float:
        return self.get_duration(self.trimmed_audio)

    def get_duration(self, audio) -> float:
        if audio is not None:
            return len(audio) / self.sample_rate
        return 0.0

    def get_waveform_full_audio(self, num_points: int = 100) -> list[float]:
        return self.get_waveform_data(audio=self.full_audio, num_points=num_points)

    def get_waveform_trimmed_audio(self, num_points: int = 100) -> list[float]:
        return self.get_waveform_data(audio=self.trimmed_audio, num_points=num_points)

    def get_waveform_data(self, audio, num_points: int = 100) -> list[float]:
        if audio is None:
            return [0] * num_points

        # Flatten audio data and normalize to [-1, 1]
        data = audio.flatten()
        max_val = np.max(np.abs(data))
        if max_val > 0:
            data = data / max_val

        # Downsample by taking max and min in segments
        samples_per_point = len(data) // (
            num_points // 2
        )  # We'll get 2 points per segment
        if samples_per_point < 1:
            return list(data) + [0] * (num_points - len(data))

        waveform = []
        for i in range(num_points // 2):
            start = i * samples_per_point
            end = start + samples_per_point
            if start < len(data):
                segment = data[start : min(end, len(data))]
                # Get both max and min for symmetric display
                waveform.extend([float(np.max(segment)), float(np.min(segment))])
            else:
                waveform.extend([0.0, 0.0])

        return waveform[:num_points]  # Ensure we return exactly num_points

    def update_output_folder(self, folder: Union[str, Path]) -> None:
        self.output_folder = Path(folder)

    def update_selected_device(self, device_name: str) -> None:
        self.selected_device = device_name

    def restart_monitoring(self) -> None:
        self.stop_monitoring()
        self.start_monitoring()

    def save_settings(self, config_path: Path) -> None:
        if not config_path.parent.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)

        config = configparser.ConfigParser()
        config["Settings"] = {
            "output_folder": str(self.output_folder),
            "selected_device": self.selected_device,
            "speaker_id": self.speaker_id,
            "speaker_dialect": self.speaker_dialect,
            "input_file": self.input_file,
        }

        with open(config_path, "w") as configfile:
            config.write(configfile)

    def load_settings(self, config_path: Path) -> None:
        if not config_path.exists():
            return

        config = configparser.ConfigParser()
        config.read(config_path)

        settings = config["Settings"]
        self.output_folder = Path(
            settings.get("output_folder", str(self.output_folder))
        )
        self.selected_device = settings.get("selected_device", self.selected_device)
        self.speaker_id = settings.get("speaker_id", self.speaker_id)
        self.speaker_dialect = settings.get("speaker_dialect", self.speaker_dialect)
        self.input_file = settings.get("input_file", self.input_file)

        self.output_file = self.output_folder / self.speaker_id / "output.json"

        self.load_input_data()
        self.load_output_data()

    def load_input_data(self) -> None:
        if len(self.input_file) > 0 and Path(self.input_file).exists():
            self.input_data = read_dataset(Path(self.input_file))
            self.input_index = {str(d["id"]): d for d in self.input_data}
        else:
            self.input_data = []

    def load_output_data(self) -> None:
        if len(str(self.output_file)) > 0 and Path(self.output_file).exists():
            self.output_data = read_dataset(Path(self.output_file))
            self.output_index = {str(d["id"]): d for d in self.output_data}
        else:
            self.output_data = []

    def get_sample_by_id(self, id: Union[int, dict]) -> dict:
        id_str = str(id)
        return self.output_index.get(id_str) or self.input_index.get(id_str) or {}
