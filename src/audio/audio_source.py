from abc import ABC, abstractmethod
import numpy as np

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from config.settings import SAMPLE_RATE, CHUNK_SIZE


class AudioSource(ABC):
    def __init__(self, sample_rate: int = SAMPLE_RATE, chunk_size: int = CHUNK_SIZE):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self._running = False
        self._paused = False

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def get_samples(self) -> np.ndarray:
        pass

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def toggle_pause(self) -> bool:
        self._paused = not self._paused
        return self._paused

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def name(self) -> str:
        return self.__class__.__name__