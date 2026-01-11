"""
Microphone input audio source using sounddevice.
"""

import numpy as np
import sounddevice as sd

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from config.settings import SAMPLE_RATE, CHUNK_SIZE
from src.audio.audio_source import AudioSource
from src.audio.audio_buffer import AudioBuffer


class MicrophoneInput(AudioSource):
    """
    Live microphone audio capture using sounddevice.

    Uses a callback-based approach for low-latency audio capture.
    Audio is stored in a thread-safe ring buffer.
    """

    def __init__(self,
                 sample_rate: int = SAMPLE_RATE,
                 chunk_size: int = CHUNK_SIZE,
                 device: int = None):
        """
        Initialize microphone input.

        Args:
            sample_rate: Audio sample rate in Hz
            chunk_size: Number of samples per chunk
            device: Input device index (None for default)
        """
        super().__init__(sample_rate, chunk_size)
        self.device = device
        self.buffer = AudioBuffer(chunk_size)
        self._stream = None

    def _audio_callback(self, indata: np.ndarray, frames: int,
                        time_info: dict, status: sd.CallbackFlags) -> None:
        """
        Callback function called by sounddevice for each audio chunk.

        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Timing information
            status: Status flags
        """
        if status:
            print(f"Audio callback status: {status}")

        if not self._paused:
            # Convert to mono if stereo and normalize
            audio = indata[:, 0] if len(indata.shape) > 1 else indata.flatten()
            self.buffer.push(audio.astype(np.float32))

    def start(self) -> None:
        """Start microphone capture."""
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
        """Stop microphone capture."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self._running = False
        self.buffer.clear()
        print("Microphone stopped")

    def get_samples(self) -> np.ndarray:
        """
        Get the latest audio samples from the buffer.

        Returns:
            Latest audio chunk as float32 array
        """
        return self.buffer.get_latest()

    def get_samples_for_fft(self, num_samples: int) -> np.ndarray:
        """
        Get samples for FFT analysis.

        Args:
            num_samples: Number of samples needed for FFT

        Returns:
            Audio samples as float32 array
        """
        return self.buffer.get_samples(num_samples)

    @staticmethod
    def list_devices() -> list:
        """
        List available audio input devices.

        Returns:
            List of input device information dictionaries
        """
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
        """Get the name of this audio source."""
        if self.device is not None:
            try:
                return f"Mic: {sd.query_devices(self.device)['name']}"
            except:
                pass
        return "Microphone"
