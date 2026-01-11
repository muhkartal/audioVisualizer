from dataclasses import dataclass, field
import numpy as np
from typing import Optional


@dataclass
class AudioFeatures:
    spectrum: np.ndarray = field(default_factory=lambda: np.zeros(64))

    bass: float = 0.0
    mid: float = 0.0
    treble: float = 0.0

    rms: float = 0.0
    peak: float = 0.0

    is_beat: bool = False
    beat_strength: float = 0.0
    tempo_bpm: float = 0.0

    spectral_centroid: float = 0.0

    spectrum_peaks: np.ndarray = field(default_factory=lambda: np.zeros(64))

    timestamp: float = 0.0

    def copy(self) -> 'AudioFeatures':
        return AudioFeatures(
            spectrum=self.spectrum.copy(),
            bass=self.bass,
            mid=self.mid,
            treble=self.treble,
            rms=self.rms,
            peak=self.peak,
            is_beat=self.is_beat,
            beat_strength=self.beat_strength,
            tempo_bpm=self.tempo_bpm,
            spectral_centroid=self.spectral_centroid,
            spectrum_peaks=self.spectrum_peaks.copy(),
            timestamp=self.timestamp
        )

    @property
    def energy(self) -> float:
        return (self.bass + self.mid + self.treble) / 3.0

    @property
    def low_mid_high(self) -> tuple:
        return (self.bass, self.mid, self.treble)