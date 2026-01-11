"""
Audio file player using librosa and sounddevice.
"""

import numpy as np
import sounddevice as sd
import threading
import os

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from config.settings import SAMPLE_RATE, CHUNK_SIZE
from src.audio.audio_source import AudioSource
from src.audio.audio_buffer import AudioBuffer


class FilePlayer(AudioSource):
    """
    Audio file player for MP3/WAV and other formats.

    Uses librosa for loading and sounddevice for playback,
    providing samples to the visualization pipeline.
    """

    def __init__(self, filepath: str,
                 sample_rate: int = SAMPLE_RATE,
                 chunk_size: int = CHUNK_SIZE):
        """
        Initialize file player with an audio file.

        Args:
            filepath: Path to audio file
            sample_rate: Target sample rate (will resample if needed)
            chunk_size: Number of samples per chunk
        """
        super().__init__(sample_rate, chunk_size)

        self.filepath = filepath
        self.filename = os.path.basename(filepath)

        # Audio data
        self.audio_data = None
        self.duration = 0.0
        self.position = 0
        self.total_samples = 0

        # Playback
        self.buffer = AudioBuffer(chunk_size)
        self._stream = None
        self._playback_thread = None
        self._lock = threading.Lock()

        # Load the file
        self._load_file()

    def _load_file(self) -> None:
        """Load the audio file using librosa."""
        try:
            import librosa

            print(f"Loading: {self.filename}...")

            # Load with librosa (automatically resamples)
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
        """
        Callback for sounddevice playback.

        Args:
            outdata: Output buffer to fill
            frames: Number of frames requested
            time_info: Timing information
            status: Status flags
        """
        if status:
            print(f"Playback status: {status}")

        with self._lock:
            if self._paused or self.audio_data is None:
                outdata.fill(0)
                return

            # Get the next chunk of audio
            end_pos = min(self.position + frames, self.total_samples)
            chunk = self.audio_data[self.position:end_pos]

            # Pad if we're at the end
            if len(chunk) < frames:
                chunk = np.pad(chunk, (0, frames - len(chunk)))
                # Loop back to start
                self.position = 0
            else:
                self.position = end_pos

            # Fill output buffer
            outdata[:, 0] = chunk

            # Also fill the visualization buffer
            self.buffer.push(chunk.astype(np.float32))

    def start(self) -> None:
        """Start audio playback."""
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
        """Stop audio playback."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        self._running = False
        self.buffer.clear()
        print("Playback stopped")

    def get_samples(self) -> np.ndarray:
        """Get the latest audio samples from the buffer."""
        return self.buffer.get_latest()

    def get_samples_for_fft(self, num_samples: int) -> np.ndarray:
        """Get samples for FFT analysis."""
        return self.buffer.get_samples(num_samples)

    def seek(self, position: float) -> None:
        """
        Seek to a position in the audio.

        Args:
            position: Position in seconds
        """
        with self._lock:
            sample_pos = int(position * self.sample_rate)
            self.position = max(0, min(sample_pos, self.total_samples))

    def seek_relative(self, offset: float) -> None:
        """
        Seek relative to current position.

        Args:
            offset: Offset in seconds (positive or negative)
        """
        with self._lock:
            current_time = self.position / self.sample_rate
            new_time = current_time + offset
            self.seek(new_time)

    @property
    def current_time(self) -> float:
        """Get current playback position in seconds."""
        with self._lock:
            return self.position / self.sample_rate

    @property
    def progress(self) -> float:
        """Get playback progress (0-1)."""
        if self.total_samples == 0:
            return 0.0
        with self._lock:
            return self.position / self.total_samples

    @property
    def name(self) -> str:
        """Get the name of this audio source."""
        return f"File: {self.filename}"
