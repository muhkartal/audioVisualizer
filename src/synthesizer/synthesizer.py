import numpy as np
import sounddevice as sd
import threading
from typing import Dict, List
from collections import deque

from config.settings import (
    SYNTH_SAMPLE_RATE, SYNTH_CHUNK_SIZE, SYNTH_MASTER_VOLUME,
    SYNTH_VIZ_SCALE, SYNTH_MAX_POLYPHONY,
    SYNTH_ATTACK, SYNTH_DECAY, SYNTH_SUSTAIN, SYNTH_RELEASE
)
from src.synthesizer.oscillator import Oscillator
from src.synthesizer.envelope import ADSREnvelope
from src.synthesizer.note import Note
from src.synthesizer.keyboard_mapping import (
    KEYBOARD_MAP, midi_to_frequency, get_note_name, is_synth_key
)

class Synthesizer:
    VIZ_BUFFER_SIZE = 8

    def __init__(self, sample_rate: int = SYNTH_SAMPLE_RATE, chunk_size: int = SYNTH_CHUNK_SIZE):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.oscillator = Oscillator(sample_rate)
        self.envelope = ADSREnvelope(
            attack=SYNTH_ATTACK,
            decay=SYNTH_DECAY,
            sustain=SYNTH_SUSTAIN,
            release=SYNTH_RELEASE
        )
        self.active_notes: Dict[int, Note] = {}
        self._lock = threading.Lock()
        self._stream: sd.OutputStream = None
        self.waveform = 'sine'
        self.waveform_index = 0
        self.master_volume = SYNTH_MASTER_VOLUME
        self.viz_scale = SYNTH_VIZ_SCALE
        self.enabled = True
        self._running = False
        self._paused = False
        self._mix_buffer = np.zeros(chunk_size, dtype=np.float32)
        self._viz_buffer: deque = deque(maxlen=self.VIZ_BUFFER_SIZE)
        self._viz_lock = threading.Lock()

    def start(self) -> None:
        if self._stream is not None:
            return
        self._stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32,
            blocksize=self.chunk_size,
            latency='low',
            callback=self._audio_callback
        )
        self._stream.start()
        self._running = True

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self._running = False
        with self._lock:
            self.active_notes.clear()
        with self._viz_lock:
            self._viz_buffer.clear()

    def note_on(self, key: int) -> None:
        if not self.enabled or not is_synth_key(key):
            return

        midi_note = KEYBOARD_MAP[key]
        if midi_note is None:
            return

        with self._lock:
            if key in self.active_notes:
                return

            if len(self.active_notes) >= SYNTH_MAX_POLYPHONY:
                oldest_key = min(self.active_notes.keys(),
                               key=lambda k: self.active_notes[k].start_time)
                del self.active_notes[oldest_key]

            frequency = midi_to_frequency(midi_note)
            note = Note(
                frequency=frequency,
                midi_note=midi_note,
                key=key
            )
            self.active_notes[key] = note

    def note_off(self, key: int) -> None:
        with self._lock:
            if key in self.active_notes:
                self.active_notes[key].release()

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        if not self.enabled:
            with self._lock:
                self.active_notes.clear()
        return self.enabled

    def cycle_waveform(self) -> str:
        self.waveform_index = (self.waveform_index + 1) % len(Oscillator.WAVEFORMS)
        self.waveform = Oscillator.WAVEFORMS[self.waveform_index]
        return self.waveform

    def get_active_notes(self) -> List[Note]:
        with self._lock:
            return list(self.active_notes.values())

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def name(self) -> str:
        return f"Piano [{self.waveform}]"

    def toggle_pause(self) -> bool:
        self._paused = not self._paused
        return self._paused

    def get_samples_for_fft(self, num_samples: int) -> np.ndarray:
        with self._viz_lock:
            if not self._viz_buffer:
                return np.zeros(num_samples, dtype=np.float32)

            all_samples = np.concatenate(list(self._viz_buffer))

            if len(all_samples) >= num_samples:
                return all_samples[-num_samples:]
            else:
                result = np.zeros(num_samples, dtype=np.float32)
                result[-len(all_samples):] = all_samples
                return result

    def _audio_callback(self, outdata, frames, time_info, status):
        with self._lock:
            notes = list(self.active_notes.items())

        self._mix_buffer.fill(0)
        finished_keys = []

        for key, note in notes:
            samples, new_phase = self.oscillator.generate(
                note.frequency,
                frames,
                note.phase,
                self.waveform
            )

            envelope = self.envelope.generate_envelope(
                frames,
                self.sample_rate,
                note.time_since_start,
                note.time_since_release
            )

            self._mix_buffer += samples * envelope * note.velocity

            with self._lock:
                if key in self.active_notes:
                    self.active_notes[key].phase = new_phase

            if self.envelope.is_finished(note.time_since_release):
                finished_keys.append(key)

        if finished_keys:
            with self._lock:
                for key in finished_keys:
                    self.active_notes.pop(key, None)

        if len(notes) > 1:
            self._mix_buffer /= np.sqrt(len(notes))

        output = self._mix_buffer * self.master_volume
        outdata[:, 0] = output

        with self._viz_lock:
            self._viz_buffer.append(output.copy() * self.viz_scale)
