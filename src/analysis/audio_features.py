"""
Data class for audio features extracted from analysis.
"""

from dataclasses import dataclass, field
import numpy as np
from typing import Optional


@dataclass
class AudioFeatures:
    """
    Container for extracted audio features.

    Holds all the audio analysis data that visualizers use
    to create their displays.
    """

    # Frequency spectrum data
    spectrum: np.ndarray = field(default_factory=lambda: np.zeros(64))

    # Band energies (bass, mid, treble)
    bass: float = 0.0
    mid: float = 0.0
    treble: float = 0.0

    # Overall amplitude
    rms: float = 0.0
    peak: float = 0.0

    # Beat detection
    is_beat: bool = False
    beat_strength: float = 0.0
    tempo_bpm: float = 0.0

    # Spectral characteristics
    spectral_centroid: float = 0.0  # "Brightness" of sound

    # Peak values for visualization (with decay)
    spectrum_peaks: np.ndarray = field(default_factory=lambda: np.zeros(64))

    # Timestamp
    timestamp: float = 0.0

    def copy(self) -> 'AudioFeatures':
        """Create a copy of this AudioFeatures instance."""
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
        """Get overall energy (average of bass, mid, treble)."""
        return (self.bass + self.mid + self.treble) / 3.0

    @property
    def low_mid_high(self) -> tuple:
        """Get bass, mid, treble as a tuple."""
        return (self.bass, self.mid, self.treble)
