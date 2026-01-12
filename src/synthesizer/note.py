from dataclasses import dataclass, field
import time

@dataclass
class Note:
    frequency: float
    midi_note: int
    key: int
    start_time: float = field(default_factory=time.time)
    release_time: float = None
    phase: float = 0.0
    velocity: float = 0.8

    @property
    def is_released(self) -> bool:
        return self.release_time is not None

    @property
    def time_since_start(self) -> float:
        return time.time() - self.start_time

    @property
    def time_since_release(self) -> float:
        if self.release_time is None:
            return None
        return time.time() - self.release_time

    def release(self) -> None:
        if self.release_time is None:
            self.release_time = time.time()
