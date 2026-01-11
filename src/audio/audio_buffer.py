"""
Thread-safe ring buffer for audio samples.
"""

import threading
from collections import deque
import numpy as np

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from config.settings import CHUNK_SIZE, BUFFER_SIZE


class AudioBuffer:
    """
    Thread-safe ring buffer for storing audio chunks.

    Uses a deque with a maximum length to automatically discard
    old samples when new ones are added.
    """

    def __init__(self, chunk_size: int = CHUNK_SIZE, max_chunks: int = BUFFER_SIZE):
        """
        Initialize the audio buffer.

        Args:
            chunk_size: Number of samples per chunk
            max_chunks: Maximum number of chunks to store
        """
        self.chunk_size = chunk_size
        self.max_chunks = max_chunks
        self._buffer = deque(maxlen=max_chunks)
        self._lock = threading.Lock()
        self._latest_chunk = np.zeros(chunk_size, dtype=np.float32)

    def push(self, samples: np.ndarray) -> None:
        """
        Add audio samples to the buffer.

        Args:
            samples: Audio samples as numpy array (will be converted to float32)
        """
        # Ensure samples are float32 and normalized
        if samples.dtype != np.float32:
            samples = samples.astype(np.float32)

        # Handle stereo by converting to mono
        if len(samples.shape) > 1:
            samples = np.mean(samples, axis=1)

        with self._lock:
            self._buffer.append(samples.copy())
            self._latest_chunk = samples.copy()

    def get_latest(self) -> np.ndarray:
        """
        Get the most recent audio chunk.

        Returns:
            Most recent audio samples as float32 array
        """
        with self._lock:
            return self._latest_chunk.copy()

    def get_all(self) -> np.ndarray:
        """
        Get all samples in the buffer concatenated.

        Returns:
            All buffered samples as a single float32 array
        """
        with self._lock:
            if len(self._buffer) == 0:
                return np.zeros(self.chunk_size, dtype=np.float32)
            return np.concatenate(list(self._buffer))

    def get_samples(self, num_samples: int) -> np.ndarray:
        """
        Get the most recent N samples from the buffer.

        Args:
            num_samples: Number of samples to retrieve

        Returns:
            Most recent samples as float32 array (zero-padded if not enough)
        """
        all_samples = self.get_all()

        if len(all_samples) >= num_samples:
            return all_samples[-num_samples:]
        else:
            # Zero-pad if we don't have enough samples
            result = np.zeros(num_samples, dtype=np.float32)
            result[-len(all_samples):] = all_samples
            return result

    def clear(self) -> None:
        """Clear all samples from the buffer."""
        with self._lock:
            self._buffer.clear()
            self._latest_chunk = np.zeros(self.chunk_size, dtype=np.float32)

    @property
    def is_empty(self) -> bool:
        """Check if the buffer is empty."""
        with self._lock:
            return len(self._buffer) == 0

    @property
    def num_chunks(self) -> int:
        """Get the number of chunks currently in the buffer."""
        with self._lock:
            return len(self._buffer)

    @property
    def total_samples(self) -> int:
        """Get the total number of samples in the buffer."""
        with self._lock:
            return sum(len(chunk) for chunk in self._buffer)
