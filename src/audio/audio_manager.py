from typing import Optional
import os

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.audio.audio_source import AudioSource
from src.audio.microphone_input import MicrophoneInput
from src.audio.file_player import FilePlayer


class AudioManager:
    def __init__(self):
        self._current_source: Optional[AudioSource] = None
        self._mic: Optional[MicrophoneInput] = None
        self._file_player: Optional[FilePlayer] = None

        self._using_mic = True

    def start_microphone(self, device: int = None) -> bool:
        try:
            self.stop()

            self._mic = MicrophoneInput(device=device)
            self._mic.start()

            self._current_source = self._mic
            self._using_mic = True
            return True

        except Exception as e:
            print(f"Failed to start microphone: {e}")
            return False

    def load_file(self, filepath: str) -> bool:
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return False

        try:
            self.stop()

            self._file_player = FilePlayer(filepath)
            self._file_player.start()

            self._current_source = self._file_player
            self._using_mic = False
            return True

        except Exception as e:
            print(f"Failed to load file: {e}")
            return False

    def toggle_source(self) -> str:
        if self._using_mic and self._file_player:
            self.stop()
            self._file_player.start()
            self._current_source = self._file_player
            self._using_mic = False
        else:
            self.start_microphone()

        return self.source_name

    def stop(self) -> None:
        if self._current_source:
            self._current_source.stop()

    def pause(self) -> None:
        if self._current_source:
            self._current_source.pause()

    def resume(self) -> None:
        if self._current_source:
            self._current_source.resume()

    def toggle_pause(self) -> bool:
        if self._current_source:
            return self._current_source.toggle_pause()
        return False

    @property
    def current_source(self) -> Optional[AudioSource]:
        return self._current_source

    @property
    def source_name(self) -> str:
        if self._current_source:
            return self._current_source.name
        return "None"

    @property
    def is_running(self) -> bool:
        return self._current_source is not None and self._current_source.is_running

    @property
    def is_paused(self) -> bool:
        if self._current_source:
            return self._current_source.is_paused
        return False

    @property
    def is_using_microphone(self) -> bool:
        return self._using_mic

    @property
    def file_player(self) -> Optional[FilePlayer]:
        return self._file_player if not self._using_mic else None