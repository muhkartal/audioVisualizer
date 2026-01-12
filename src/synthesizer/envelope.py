from dataclasses import dataclass
import numpy as np

@dataclass
class ADSREnvelope:
    attack: float = 0.01
    decay: float = 0.1
    sustain: float = 0.7
    release: float = 0.3

    def get_amplitude(self, time_since_start: float,
                      time_since_release: float = None) -> float:
        if time_since_release is not None:
            release_amp = self._get_amplitude_at_release(time_since_start - time_since_release)
            if time_since_release >= self.release:
                return 0.0
            return release_amp * (1.0 - time_since_release / self.release)

        if time_since_start < self.attack:
            return time_since_start / self.attack

        time_after_attack = time_since_start - self.attack
        if time_after_attack < self.decay:
            decay_progress = time_after_attack / self.decay
            return 1.0 - (1.0 - self.sustain) * decay_progress

        return self.sustain

    def _get_amplitude_at_release(self, time_at_release: float) -> float:
        if time_at_release < self.attack:
            return time_at_release / self.attack
        time_after_attack = time_at_release - self.attack
        if time_after_attack < self.decay:
            decay_progress = time_after_attack / self.decay
            return 1.0 - (1.0 - self.sustain) * decay_progress
        return self.sustain

    def is_finished(self, time_since_release: float) -> bool:
        if time_since_release is None:
            return False
        return time_since_release >= self.release

    def generate_envelope(self, num_samples: int, sample_rate: int,
                          time_since_start: float,
                          time_since_release: float = None) -> np.ndarray:
        t = time_since_start + np.arange(num_samples, dtype=np.float32) / sample_rate

        if time_since_release is not None:
            release_t = time_since_release + np.arange(num_samples, dtype=np.float32) / sample_rate
            release_amp = np.where(
                t - release_t < self.attack,
                (t - release_t) / self.attack,
                np.where(
                    t - release_t < self.attack + self.decay,
                    1.0 - (1.0 - self.sustain) * ((t - release_t - self.attack) / self.decay),
                    self.sustain
                )
            )
            envelope = np.where(
                release_t >= self.release,
                0.0,
                release_amp * (1.0 - release_t / self.release)
            )
        else:
            envelope = np.where(
                t < self.attack,
                t / self.attack,
                np.where(
                    t < self.attack + self.decay,
                    1.0 - (1.0 - self.sustain) * ((t - self.attack) / self.decay),
                    self.sustain
                )
            )

        return envelope.astype(np.float32)
