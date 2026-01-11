"""
FFT Analyzer for real-time spectral analysis.
"""

import numpy as np
from scipy.signal import get_window

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from config.settings import (
    SAMPLE_RATE, FFT_SIZE, NUM_BANDS,
    FREQ_MIN, FREQ_MAX, SMOOTHING_FACTOR, PEAK_DECAY,
    DB_RANGE_MIN, DB_RANGE_MAX, MIC_GAIN
)
from src.analysis.audio_features import AudioFeatures


class FFTAnalyzer:
    """
    Real-time FFT analyzer with logarithmic frequency banding.

    Converts raw audio samples into frequency spectrum data
    suitable for visualization.
    """

    def __init__(self,
                 sample_rate: int = SAMPLE_RATE,
                 fft_size: int = FFT_SIZE,
                 num_bands: int = NUM_BANDS,
                 freq_min: float = FREQ_MIN,
                 freq_max: float = FREQ_MAX,
                 smoothing: float = SMOOTHING_FACTOR):
        """
        Initialize the FFT analyzer.

        Args:
            sample_rate: Audio sample rate in Hz
            fft_size: FFT window size
            num_bands: Number of output frequency bands
            freq_min: Minimum frequency to analyze (Hz)
            freq_max: Maximum frequency to analyze (Hz)
            smoothing: Exponential smoothing factor (0-1)
        """
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.num_bands = num_bands
        self.smoothing = smoothing

        # Pre-compute Hanning window
        self.window = get_window('hann', fft_size)

        # Pre-compute frequency bin edges (logarithmic spacing)
        self.band_edges = np.logspace(
            np.log10(freq_min),
            np.log10(freq_max),
            num_bands + 1
        )

        # Convert to FFT bin indices
        freqs = np.fft.rfftfreq(fft_size, 1 / sample_rate)
        self.band_indices = np.searchsorted(freqs, self.band_edges)

        # Ensure we don't exceed FFT size
        self.band_indices = np.clip(self.band_indices, 0, len(freqs) - 1)

        # Pre-compute frequency array for spectral centroid
        self.freqs = freqs

        # Smoothed output state
        self.smoothed_spectrum = np.zeros(num_bands)
        self.spectrum_peaks = np.zeros(num_bands)

        # Band boundaries for bass/mid/treble
        # Bass: 20-250 Hz, Mid: 250-4000 Hz, Treble: 4000-20000 Hz
        self.bass_end = np.searchsorted(self.band_edges, 250)
        self.mid_end = np.searchsorted(self.band_edges, 4000)

    def analyze(self, samples: np.ndarray) -> AudioFeatures:
        """
        Perform FFT analysis on audio samples.

        Args:
            samples: Audio samples as float32 array

        Returns:
            AudioFeatures containing spectrum and derived features
        """
        features = AudioFeatures(timestamp=0.0)

        # Ensure correct size
        if len(samples) < self.fft_size:
            samples = np.pad(samples, (0, self.fft_size - len(samples)))
        elif len(samples) > self.fft_size:
            samples = samples[-self.fft_size:]

        # Apply microphone gain boost
        samples = samples * MIC_GAIN

        # Apply window
        windowed = samples * self.window

        # Compute FFT
        spectrum = np.abs(np.fft.rfft(windowed))

        # Convert to dB scale
        spectrum_db = 20 * np.log10(spectrum + 1e-10)

        # Normalize to 0-1 range using configurable dB range
        db_range = DB_RANGE_MAX - DB_RANGE_MIN
        spectrum_norm = np.clip((spectrum_db - DB_RANGE_MIN) / db_range, 0, 1)

        # Group into bands
        bands = np.zeros(self.num_bands)
        for i in range(self.num_bands):
            start = self.band_indices[i]
            end = self.band_indices[i + 1]
            if start < end:
                bands[i] = np.mean(spectrum_norm[start:end])
            elif start == end and start < len(spectrum_norm):
                bands[i] = spectrum_norm[start]

        # Apply smoothing
        self.smoothed_spectrum = (
            self.smoothing * self.smoothed_spectrum +
            (1 - self.smoothing) * bands
        )

        # Update peaks with decay
        self.spectrum_peaks = np.maximum(
            self.spectrum_peaks - PEAK_DECAY,
            self.smoothed_spectrum
        )

        # Calculate bass, mid, treble energies
        if self.bass_end > 0:
            features.bass = np.mean(self.smoothed_spectrum[:self.bass_end])
        if self.mid_end > self.bass_end:
            features.mid = np.mean(self.smoothed_spectrum[self.bass_end:self.mid_end])
        if self.num_bands > self.mid_end:
            features.treble = np.mean(self.smoothed_spectrum[self.mid_end:])

        # Calculate RMS and peak
        features.rms = np.sqrt(np.mean(samples ** 2))
        features.peak = np.max(np.abs(samples))

        # Calculate spectral centroid (brightness)
        if np.sum(spectrum) > 0:
            features.spectral_centroid = (
                np.sum(self.freqs * spectrum) / np.sum(spectrum)
            )
            # Normalize to 0-1 (20Hz to 20kHz range)
            features.spectral_centroid = np.clip(
                (features.spectral_centroid - FREQ_MIN) / (FREQ_MAX - FREQ_MIN),
                0, 1
            )

        # Set spectrum data
        features.spectrum = self.smoothed_spectrum.copy()
        features.spectrum_peaks = self.spectrum_peaks.copy()

        return features

    def reset(self) -> None:
        """Reset the analyzer state (smoothed values and peaks)."""
        self.smoothed_spectrum = np.zeros(self.num_bands)
        self.spectrum_peaks = np.zeros(self.num_bands)
