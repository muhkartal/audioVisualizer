"""
Beat Detector using spectral flux onset detection.
"""

import numpy as np
from collections import deque
import time

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from config.settings import (
    MIN_BEAT_INTERVAL, BEAT_THRESHOLD, BEAT_HISTORY_LENGTH
)


class BeatDetector:
    """
    Real-time beat detection using spectral flux analysis.

    Detects beats by analyzing changes in the frequency spectrum
    over time and identifying significant energy increases.
    """

    def __init__(self,
                 history_length: int = BEAT_HISTORY_LENGTH,
                 threshold: float = BEAT_THRESHOLD,
                 min_interval: float = MIN_BEAT_INTERVAL):
        """
        Initialize the beat detector.

        Args:
            history_length: Number of frames to keep for average calculation
            threshold: Beat detection sensitivity (lower = more sensitive)
            min_interval: Minimum time between detected beats (seconds)
        """
        self.history_length = history_length
        self.threshold = threshold
        self.min_interval = min_interval

        # State
        self.previous_spectrum = None
        self.flux_history = deque(maxlen=history_length)
        self.last_beat_time = 0
        self.beat_times = deque(maxlen=20)  # For tempo estimation

        # Output
        self.is_beat = False
        self.beat_strength = 0.0
        self.tempo_bpm = 0.0

    def detect(self, spectrum: np.ndarray) -> tuple:
        """
        Detect beats from the current spectrum.

        Args:
            spectrum: Current frequency spectrum (normalized 0-1)

        Returns:
            Tuple of (is_beat, beat_strength, tempo_bpm)
        """
        current_time = time.time()
        self.is_beat = False
        self.beat_strength = 0.0

        if self.previous_spectrum is None:
            self.previous_spectrum = spectrum.copy()
            return (False, 0.0, self.tempo_bpm)

        # Calculate spectral flux (sum of positive differences)
        diff = spectrum - self.previous_spectrum
        flux = np.sum(np.maximum(diff, 0))

        # Store for history
        self.flux_history.append(flux)
        self.previous_spectrum = spectrum.copy()

        # Need enough history for comparison
        if len(self.flux_history) < self.history_length // 2:
            return (False, 0.0, self.tempo_bpm)

        # Calculate local average and threshold
        avg_flux = np.mean(self.flux_history)
        flux_threshold = avg_flux * self.threshold

        # Check for beat
        time_since_last = current_time - self.last_beat_time

        if flux > flux_threshold and time_since_last >= self.min_interval:
            self.is_beat = True
            self.beat_strength = min(1.0, (flux - avg_flux) / (avg_flux + 0.01))
            self.last_beat_time = current_time

            # Record beat time for tempo estimation
            self.beat_times.append(current_time)

            # Estimate tempo
            self._estimate_tempo()

        return (self.is_beat, self.beat_strength, self.tempo_bpm)

    def _estimate_tempo(self) -> None:
        """Estimate tempo from beat intervals."""
        if len(self.beat_times) < 4:
            return

        # Calculate intervals between beats
        times = list(self.beat_times)
        intervals = [times[i+1] - times[i] for i in range(len(times) - 1)]

        # Filter out outliers (intervals too short or too long)
        valid_intervals = [i for i in intervals if 0.2 < i < 2.0]

        if len(valid_intervals) < 2:
            return

        # Calculate average interval
        avg_interval = np.mean(valid_intervals)

        # Convert to BPM
        if avg_interval > 0:
            self.tempo_bpm = 60.0 / avg_interval

            # Clamp to reasonable range
            while self.tempo_bpm < 60:
                self.tempo_bpm *= 2
            while self.tempo_bpm > 180:
                self.tempo_bpm /= 2

    def reset(self) -> None:
        """Reset the beat detector state."""
        self.previous_spectrum = None
        self.flux_history.clear()
        self.beat_times.clear()
        self.last_beat_time = 0
        self.is_beat = False
        self.beat_strength = 0.0
        self.tempo_bpm = 0.0

    def set_sensitivity(self, sensitivity: float) -> None:
        """
        Set beat detection sensitivity.

        Args:
            sensitivity: Value from 0 (very sensitive) to 1 (less sensitive)
        """
        # Map sensitivity to threshold (inverse relationship)
        self.threshold = 1.0 + sensitivity * 2.0
