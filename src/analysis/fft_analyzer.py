import numpy as np
from scipy.signal import get_window

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import (
    SAMPLE_RATE, FFT_SIZE, NUM_BANDS,
    FREQ_MIN, FREQ_MAX, SMOOTHING_FACTOR, PEAK_DECAY,
    DB_RANGE_MIN, DB_RANGE_MAX, MIC_GAIN
)
from src.analysis.audio_features import AudioFeatures


class FFTAnalyzer:
    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        fft_size: int = FFT_SIZE,
        num_bands: int = NUM_BANDS,
        freq_min: float = FREQ_MIN,
        freq_max: float = FREQ_MAX,
        smoothing: float = SMOOTHING_FACTOR
    ):
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.num_bands = num_bands
        self.smoothing = smoothing

        self.window = get_window('hann', fft_size)

        self.band_edges = np.logspace(
            np.log10(freq_min),
            np.log10(freq_max),
            num_bands + 1
        )

        freqs = np.fft.rfftfreq(fft_size, 1 / sample_rate)
        self.band_indices = np.searchsorted(freqs, self.band_edges)

        self.band_indices = np.clip(self.band_indices, 0, len(freqs) - 1)

        self.freqs = freqs

        self.smoothed_spectrum = np.zeros(num_bands)
        self.spectrum_peaks = np.zeros(num_bands)

        self.bass_end = np.searchsorted(self.band_edges, 250)
        self.mid_end = np.searchsorted(self.band_edges, 4000)

    def analyze(self, samples: np.ndarray) -> AudioFeatures:
        features = AudioFeatures(timestamp=0.0)

        if len(samples) < self.fft_size:
            samples = np.pad(samples, (0, self.fft_size - len(samples)))
        elif len(samples) > self.fft_size:
            samples = samples[-self.fft_size:]

        samples = samples * MIC_GAIN

        windowed = samples * self.window

        spectrum = np.abs(np.fft.rfft(windowed))

        spectrum_db = 20 * np.log10(spectrum + 1e-10)

        db_range = DB_RANGE_MAX - DB_RANGE_MIN
        spectrum_norm = np.clip((spectrum_db - DB_RANGE_MIN) / db_range, 0, 1)

        bands = np.zeros(self.num_bands)
        for i in range(self.num_bands):
            start = self.band_indices[i]
            end = self.band_indices[i + 1]
            if start < end:
                bands[i] = np.mean(spectrum_norm[start:end])
            elif start == end and start < len(spectrum_norm):
                bands[i] = spectrum_norm[start]

        self.smoothed_spectrum = (
            self.smoothing * self.smoothed_spectrum +
            (1 - self.smoothing) * bands
        )

        self.spectrum_peaks = np.maximum(
            self.spectrum_peaks - PEAK_DECAY,
            self.smoothed_spectrum
        )

        if self.bass_end > 0:
            features.bass = np.mean(self.smoothed_spectrum[:self.bass_end])
        if self.mid_end > self.bass_end:
            features.mid = np.mean(self.smoothed_spectrum[self.bass_end:self.mid_end])
        if self.num_bands > self.mid_end:
            features.treble = np.mean(self.smoothed_spectrum[self.mid_end:])

        features.rms = np.sqrt(np.mean(samples ** 2))
        features.peak = np.max(np.abs(samples))

        if np.sum(spectrum) > 0:
            features.spectral_centroid = (
                np.sum(self.freqs * spectrum) / np.sum(spectrum)
            )
            features.spectral_centroid = np.clip(
                (features.spectral_centroid - FREQ_MIN) / (FREQ_MAX - FREQ_MIN),
                0,
                1
            )

        features.spectrum = self.smoothed_spectrum.copy()
        features.spectrum_peaks = self.spectrum_peaks.copy()

        return features

    def reset(self) -> None:
        self.smoothed_spectrum = np.zeros(self.num_bands)
        self.spectrum_peaks = np.zeros(self.num_bands)