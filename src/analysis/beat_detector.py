import numpy as np
from collections import deque
import time

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from config.settings import (
    MIN_BEAT_INTERVAL, BEAT_THRESHOLD, BEAT_HISTORY_LENGTH
)


class BeatDetector:
    def __init__(
        self,
        history_length: int = BEAT_HISTORY_LENGTH,
        threshold: float = BEAT_THRESHOLD,
        min_interval: float = MIN_BEAT_INTERVAL
    ):
        self.history_length = history_length
        self.threshold = threshold
        self.min_interval = min_interval

        self.previous_spectrum = None
        self.flux_history = deque(maxlen=history_length)
        self.last_beat_time = 0
        self.beat_times = deque(maxlen=20)

        self.is_beat = False
        self.beat_strength = 0.0
        self.tempo_bpm = 0.0

    def detect(self, spectrum: np.ndarray) -> tuple:
        current_time = time.time()
        self.is_beat = False
        self.beat_strength = 0.0

        if self.previous_spectrum is None:
            self.previous_spectrum = spectrum.copy()
            return (False, 0.0, self.tempo_bpm)

        diff = spectrum - self.previous_spectrum
        flux = np.sum(np.maximum(diff, 0))

        self.flux_history.append(flux)
        self.previous_spectrum = spectrum.copy()

        if len(self.flux_history) < self.history_length // 2:
            return (False, 0.0, self.tempo_bpm)

        avg_flux = np.mean(self.flux_history)
        flux_threshold = avg_flux * self.threshold

        time_since_last = current_time - self.last_beat_time

        if flux > flux_threshold and time_since_last >= self.min_interval:
            self.is_beat = True
            self.beat_strength = min(1.0, (flux - avg_flux) / (avg_flux + 0.01))
            self.last_beat_time = current_time

            self.beat_times.append(current_time)

            self._estimate_tempo()

        return (self.is_beat, self.beat_strength, self.tempo_bpm)

    def _estimate_tempo(self) -> None:
        if len(self.beat_times) < 4:
            return

        times = list(self.beat_times)
        intervals = [times[i+1] - times[i] for i in range(len(times) - 1)]

        valid_intervals = [i for i in intervals if 0.2 < i < 2.0]

        if len(valid_intervals) < 2:
            return

        avg_interval = np.mean(valid_intervals)

        if avg_interval > 0:
            self.tempo_bpm = 60.0 / avg_interval

            while self.tempo_bpm < 60:
                self.tempo_bpm *= 2
            while self.tempo_bpm > 180:
                self.tempo_bpm /= 2

    def reset(self) -> None:
        self.previous_spectrum = None
        self.flux_history.clear()
        self.beat_times.clear()
        self.last_beat_time = 0
        self.is_beat = False
        self.beat_strength = 0.0
        self.tempo_bpm = 0.0

    def set_sensitivity(self, sensitivity: float) -> None:
        self.threshold = 1.0 + sensitivity * 2.0