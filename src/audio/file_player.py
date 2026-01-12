import numpy as np
import sounddevice as sd
import threading
import os

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import SAMPLE_RATE, CHUNK_SIZE
from src.audio.audio_source import AudioSource
from src.audio.audio_buffer import AudioBuffer


class FilePlayer(AudioSource):
    def __init__(self, filepath: str,
                 sample_rate: int = SAMPLE_RATE,
                 chunk_size: int = CHUNK_SIZE):
        super().__init__(sample_rate, chunk_size)

        self.filepath = filepath
        self.filename = os.path.basename(filepath)

        self.audio_data = None
        self.duration = 0.0
        self.position = 0
        self.total_samples = 0

        self.buffer = AudioBuffer(chunk_size)
        self._stream = None
        self._playback_thread = None
        self._lock = threading.Lock()

        self._load_file()

    def _load_file(self) -> None:
        try:
            import librosa

            print(f"Loading: {self.filename}...")

            self.audio_data, sr = librosa.load(
                self.filepath,
                sr=self.sample_rate,
                mono=True
            )

            self.total_samples = len(self.audio_data)
            self.duration = self.total_samples / self.sample_rate

            print(f"Loaded: {self.duration:.1f}s, {sr}Hz")

        except Exception as e:
            print(f"Error loading file: {e}")
            raise

    def _audio_callback(self, outdata: np.ndarray, frames: int,
                        time_info: dict, status: sd.CallbackFlags) -> None:
        if status:
            print(f"Playback status: {status}")

        with self._lock:
            if self._paused or self.audio_data is None:
                outdata.fill(0)
                return

            end_pos = min(self.position + frames, self.total_samples)
            chunk = self.audio_data[self.position:end_pos]

            if len(chunk) < frames:
                chunk = np.pad(chunk, (0, frames - len(chunk)))
                self.position = 0
            else:
                self.position = end_pos

            outdata[:, 0] = chunk

            self.buffer.push(chunk.astype(np.float32))

    def start(self) -> None:
        if self._running:
            return

        if self.audio_data is None:
            raise RuntimeError("No audio data loaded")

        try:
            self._stream = sd.OutputStream(
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                dtype=np.float32,
                callback=self._audio_callback
            )
            self._stream.start()
            self._running = True
            print(f"Playing: {self.filename}")

        except Exception as e:
            print(f"Failed to start playback: {e}")
            self._running = False
            raise

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        self._running = False
        self.buffer.clear()
        print("Playback stopped")

    def get_samples(self) -> np.ndarray:
        return self.buffer.get_latest()

    def get_samples_for_fft(self, num_samples: int) -> np.ndarray:
        return self.buffer.get_samples(num_samples)

    def seek(self, position: float) -> None:
        with self._lock:
            sample_pos = int(position * self.sample_rate)
            self.position = max(0, min(sample_pos, self.total_samples))

    def seek_relative(self, offset: float) -> None:
        with self._lock:
            current_time = self.position / self.sample_rate
            new_time = current_time + offset
            self.seek(new_time)

    @property
    def current_time(self) -> float:
        with self._lock:
            return self.position / self.sample_rate

    @property
    def progress(self) -> float:
        if self.total_samples == 0:
            return 0.0
        with self._lock:
            return self.position / self.total_samples

    @property
    def name(self) -> str:
        return f"File: {self.filename}"