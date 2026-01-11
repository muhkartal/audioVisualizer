"""
Audio Visualizer - Main Entry Point

A real-time audio visualizer with spectrum analysis and beat detection.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from config.settings import FFT_SIZE
from src.audio.microphone_input import MicrophoneInput
from src.analysis.fft_analyzer import FFTAnalyzer
from src.analysis.beat_detector import BeatDetector
from src.analysis.audio_features import AudioFeatures
from src.visualization.renderer import Renderer


class AudioVisualizer:
    """
    Main application class for the audio visualizer.

    Coordinates audio capture, analysis, and visualization.
    """

    def __init__(self):
        """Initialize the audio visualizer."""
        # Audio components
        self.audio_source = None
        self.fft_analyzer = FFTAnalyzer()
        self.beat_detector = BeatDetector()

        # Visualization
        self.renderer = Renderer()
        self.renderer.on_quit = self.quit
        self.renderer.on_key = self.handle_key
        self.renderer.on_file_drop = self.handle_file_drop

        # State
        self.running = False
        self.current_features = AudioFeatures()

        # File player (will be imported when needed)
        self.file_player = None
        self.audio_manager = None

    def start(self) -> None:
        """Start the audio visualizer."""
        print("Starting Audio Visualizer...")
        print()
        print("Controls (press H in app for full list):")
        print("  Audio:       O=Open  M=Mic  Space=Pause")
        print("  Modes:       Tab=Next  1-3=Select mode")
        print("  Effects:     G=Glow  B=Bloom  V=Vignette")
        print("  Presets:     F1=Clean  F2=Subtle  F3=Vibrant  F4=Retro  F5=Dreamy")
        print("  Style:       Ctrl+S=Toggle  [ ]=Prev/Next style")
        print("  Other:       H=Help  D=Debug  ESC=Quit")
        print()

        # Start with microphone by default
        self._start_microphone()

        self.running = True
        self._main_loop()

    def _start_microphone(self) -> None:
        """Start microphone input."""
        try:
            # Stop current source if any
            if self.audio_source:
                self.audio_source.stop()

            self.audio_source = MicrophoneInput()
            self.audio_source.start()
            self.fft_analyzer.reset()
            self.beat_detector.reset()
            print("Microphone started")
        except Exception as e:
            print(f"Failed to start microphone: {e}")
            self.audio_source = None

    def _main_loop(self) -> None:
        """Main application loop."""
        while self.running:
            # Handle events
            if not self.renderer.handle_events():
                self.running = False
                break

            # Get audio samples and analyze
            if self.audio_source and self.audio_source.is_running:
                if not self.audio_source.is_paused:
                    # Get samples for FFT
                    samples = self.audio_source.get_samples_for_fft(FFT_SIZE)

                    # Analyze
                    self.current_features = self.fft_analyzer.analyze(samples)

                    # Beat detection
                    is_beat, strength, tempo = self.beat_detector.detect(
                        self.current_features.spectrum
                    )
                    self.current_features.is_beat = is_beat
                    self.current_features.beat_strength = strength
                    self.current_features.tempo_bpm = tempo

            # Update and draw
            self.renderer.update(self.current_features)
            self.renderer.draw(
                self.current_features,
                source_name=self.audio_source.name if self.audio_source else "None",
                is_paused=self.audio_source.is_paused if self.audio_source else False
            )

    def handle_key(self, key: int, mod: int) -> None:
        """
        Handle keyboard input.

        Args:
            key: PyGame key constant
            mod: Modifier keys state
        """
        if key == pygame.K_SPACE:
            # Toggle pause
            if self.audio_source:
                paused = self.audio_source.toggle_pause()
                print("Paused" if paused else "Resumed")

        elif key == pygame.K_m:
            # Toggle microphone
            self._start_microphone()

        elif key == pygame.K_o:
            # Open file dialog
            self._open_file_dialog()

    def handle_file_drop(self, filepath: str) -> None:
        """
        Handle file dropped onto window.

        Args:
            filepath: Path to dropped file
        """
        print(f"File dropped: {filepath}")
        self._load_audio_file(filepath)

    def _open_file_dialog(self) -> None:
        """Open file selection dialog."""
        try:
            from src.ui.file_browser import FileBrowser
            filepath = FileBrowser.open_file()
            if filepath:
                self._load_audio_file(filepath)
        except ImportError:
            print("File browser not available. Drag and drop audio files instead.")
        except Exception as e:
            print(f"Error opening file dialog: {e}")

    def _load_audio_file(self, filepath: str) -> None:
        """
        Load and play an audio file.

        Args:
            filepath: Path to audio file
        """
        try:
            from src.audio.file_player import FilePlayer

            # Stop current source
            if self.audio_source:
                self.audio_source.stop()

            # Create file player
            self.audio_source = FilePlayer(filepath)
            self.audio_source.start()
            self.fft_analyzer.reset()
            self.beat_detector.reset()
            print(f"Playing: {os.path.basename(filepath)}")

        except ImportError:
            print("File player not available yet.")
        except Exception as e:
            print(f"Error loading file: {e}")
            # Fall back to microphone
            self._start_microphone()

    def quit(self) -> None:
        """Clean up and quit the application."""
        print("Shutting down...")

        if self.audio_source:
            self.audio_source.stop()

        self.renderer.quit()
        self.running = False


def main():
    """Main entry point."""
    app = AudioVisualizer()

    try:
        app.start()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        app.quit()


if __name__ == "__main__":
    main()
