import numpy as np
from typing import Tuple

class Oscillator:
    WAVEFORMS = ['sine', 'square', 'sawtooth', 'triangle']

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def generate(self, frequency: float, num_samples: int,
                 phase: float, waveform: str = 'sine') -> Tuple[np.ndarray, float]:
        t = (np.arange(num_samples) + phase * self.sample_rate / frequency) / self.sample_rate
        angular_freq = 2 * np.pi * frequency

        if waveform == 'sine':
            samples = np.sin(angular_freq * t)
        elif waveform == 'square':
            samples = np.sign(np.sin(angular_freq * t))
        elif waveform == 'sawtooth':
            samples = 2 * (frequency * t % 1) - 1
        elif waveform == 'triangle':
            samples = 2 * np.abs(2 * (frequency * t % 1) - 1) - 1
        else:
            samples = np.sin(angular_freq * t)

        new_phase = (phase + num_samples * frequency / self.sample_rate) % 1.0

        return samples.astype(np.float32), new_phase
