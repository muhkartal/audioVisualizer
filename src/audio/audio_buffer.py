import threading
from collections import deque
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import CHUNK_SIZE, BUFFER_SIZE


class AudioBuffer:
    def __init__(self, chunk_size: int = CHUNK_SIZE, max_chunks: int = BUFFER_SIZE):
        self.chunk_size = chunk_size
        self.max_chunks = max_chunks
        self._buffer = deque(maxlen=max_chunks)
        self._lock = threading.Lock()
        self._latest_chunk = np.zeros(chunk_size, dtype=np.float32)

    def push(self, samples: np.ndarray) -> None:
        if samples.dtype != np.float32:
            samples = samples.astype(np.float32)

        if len(samples.shape) > 1:
            samples = np.mean(samples, axis=1)

        with self._lock:
            self._buffer.append(samples.copy())
            self._latest_chunk = samples.copy()

    def get_latest(self) -> np.ndarray:
        with self._lock:
            return self._latest_chunk.copy()

    def get_all(self) -> np.ndarray:
        with self._lock:
            if len(self._buffer) == 0:
                return np.zeros(self.chunk_size, dtype=np.float32)
            return np.concatenate(list(self._buffer))

    def get_samples(self, num_samples: int) -> np.ndarray:
        all_samples = self.get_all()

        if len(all_samples) >= num_samples:
            return all_samples[-num_samples:]
        else:
            result = np.zeros(num_samples, dtype=np.float32)
            result[-len(all_samples):] = all_samples
            return result

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()
            self._latest_chunk = np.zeros(self.chunk_size, dtype=np.float32)

    @property
    def is_empty(self) -> bool:
        with self._lock:
            return len(self._buffer) == 0

    @property
    def num_chunks(self) -> int:
        with self._lock:
            return len(self._buffer)

    @property
    def total_samples(self) -> int:
        with self._lock:
            return sum(len(chunk) for chunk in self._buffer)