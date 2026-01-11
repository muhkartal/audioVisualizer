"""
Abstract base class for audio sources.
"""

from abc import ABC, abstractmethod
import numpy as np

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from config.settings import SAMPLE_RATE, CHUNK_SIZE


class AudioSource(ABC):
    """
    Abstract base class defining the interface for all audio sources.

    Subclasses must implement start(), stop(), and get_samples() methods.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE, chunk_size: int = CHUNK_SIZE):
        """
        Initialize the audio source.

        Args:
            sample_rate: Audio sample rate in Hz
            chunk_size: Number of samples per chunk
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self._running = False
        self._paused = False

    @abstractmethod
    def start(self) -> None:
        """Start audio capture/playback."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop audio capture/playback."""
        pass

    @abstractmethod
    def get_samples(self) -> np.ndarray:
        """
        Get the latest audio samples.

        Returns:
            Audio samples as float32 array normalized to [-1, 1]
        """
        pass

    def pause(self) -> None:
        """Pause the audio source."""
        self._paused = True

    def resume(self) -> None:
        """Resume the audio source."""
        self._paused = False

    def toggle_pause(self) -> bool:
        """
        Toggle pause state.

        Returns:
            New pause state (True if paused, False if playing)
        """
        self._paused = not self._paused
        return self._paused

    @property
    def is_running(self) -> bool:
        """Check if the audio source is running."""
        return self._running

    @property
    def is_paused(self) -> bool:
        """Check if the audio source is paused."""
        return self._paused

    @property
    def name(self) -> str:
        """Get the name of this audio source."""
        return self.__class__.__name__
