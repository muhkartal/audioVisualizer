import numpy as np
import sounddevice as sd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import SAMPLE_RATE, CHUNK_SIZE
from src.audio.audio_source import AudioSource
from src.audio.audio_buffer import AudioBuffer


class MicrophoneInput(AudioSource):
    def __init__(self,
                 sample_rate: int = SAMPLE_RATE,
                 chunk_size: int = CHUNK_SIZE,
                 device: int = None):
        super().__init__(sample_rate, chunk_size)
        self.device = device
        self.buffer = AudioBuffer(chunk_size)
        self._stream = None

    def _audio_callback(self, indata: np.ndarray, frames: int,
                        time_info: dict, status: sd.CallbackFlags) -> None:
        if status:
            print(f"Audio callback status: {status}")

        if not self._paused:
            audio = indata[:, 0] if len(indata.shape) > 1 else indata.flatten()
            self.buffer.push(audio.astype(np.float32))

    def start(self) -> None:
        if self._running:
            return

        try:
            self._stream = sd.InputStream(
                device=self.device,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                dtype=np.float32,
                callback=self._audio_callback
            )
            self._stream.start()
            self._running = True
            print(f"Microphone started: {sd.query_devices(self.device)['name'] if self.device else 'Default device'}")
        except Exception as e:
            print(f"Failed to start microphone: {e}")
            self._running = False
            raise

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self._running = False
        self.buffer.clear()
        print("Microphone stopped")

    def get_samples(self) -> np.ndarray:
        return self.buffer.get_latest()

    def get_samples_for_fft(self, num_samples: int) -> np.ndarray:
        return self.buffer.get_samples(num_samples)

    @staticmethod
    def list_devices() -> list:
        devices = sd.query_devices()
        input_devices = []
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
        return input_devices

    @property
    def name(self) -> str:
        if self.device is not None:
            try:
                return f"Mic: {sd.query_devices(self.device)['name']}"
            except (IndexError, KeyError, sd.PortAudioError):
                pass
        return "Microphone"