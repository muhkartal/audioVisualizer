"""
Audio Manager for switching between audio sources.
"""

from typing import Optional
import os

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from src.audio.audio_source import AudioSource
from src.audio.microphone_input import MicrophoneInput
from src.audio.file_player import FilePlayer


class AudioManager:
    """
    Manages audio sources and provides unified interface.

    Handles switching between microphone and file playback,
    maintaining state across source changes.
    """

    def __init__(self):
        """Initialize the audio manager."""
        self._current_source: Optional[AudioSource] = None
        self._mic: Optional[MicrophoneInput] = None
        self._file_player: Optional[FilePlayer] = None

        # Track source type
        self._using_mic = True

    def start_microphone(self, device: int = None) -> bool:
        """
        Start microphone input.

        Args:
            device: Input device index (None for default)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Stop current source
            self.stop()

            # Create and start microphone
            self._mic = MicrophoneInput(device=device)
            self._mic.start()

            self._current_source = self._mic
            self._using_mic = True
            return True

        except Exception as e:
            print(f"Failed to start microphone: {e}")
            return False

    def load_file(self, filepath: str) -> bool:
        """
        Load and start playing an audio file.

        Args:
            filepath: Path to audio file

        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return False

        try:
            # Stop current source
            self.stop()

            # Create and start file player
            self._file_player = FilePlayer(filepath)
            self._file_player.start()

            self._current_source = self._file_player
            self._using_mic = False
            return True

        except Exception as e:
            print(f"Failed to load file: {e}")
            return False

    def toggle_source(self) -> str:
        """
        Toggle between microphone and last loaded file.

        Returns:
            Name of the new active source
        """
        if self._using_mic and self._file_player:
            # Switch to file
            self.stop()
            self._file_player.start()
            self._current_source = self._file_player
            self._using_mic = False
        else:
            # Switch to mic
            self.start_microphone()

        return self.source_name

    def stop(self) -> None:
        """Stop the current audio source."""
        if self._current_source:
            self._current_source.stop()

    def pause(self) -> None:
        """Pause the current source."""
        if self._current_source:
            self._current_source.pause()

    def resume(self) -> None:
        """Resume the current source."""
        if self._current_source:
            self._current_source.resume()

    def toggle_pause(self) -> bool:
        """Toggle pause state."""
        if self._current_source:
            return self._current_source.toggle_pause()
        return False

    @property
    def current_source(self) -> Optional[AudioSource]:
        """Get the current audio source."""
        return self._current_source

    @property
    def source_name(self) -> str:
        """Get the name of the current source."""
        if self._current_source:
            return self._current_source.name
        return "None"

    @property
    def is_running(self) -> bool:
        """Check if audio is running."""
        return self._current_source is not None and self._current_source.is_running

    @property
    def is_paused(self) -> bool:
        """Check if audio is paused."""
        if self._current_source:
            return self._current_source.is_paused
        return False

    @property
    def is_using_microphone(self) -> bool:
        """Check if using microphone input."""
        return self._using_mic

    @property
    def file_player(self) -> Optional[FilePlayer]:
        """Get the file player (if active)."""
        return self._file_player if not self._using_mic else None
