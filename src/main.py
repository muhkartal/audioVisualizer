import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from config.settings import FFT_SIZE
from src.audio.microphone_input import MicrophoneInput
from src.analysis.fft_analyzer import FFTAnalyzer
from src.analysis.beat_detector import BeatDetector
from src.analysis.audio_features import AudioFeatures
from src.visualization.renderer import Renderer
from src.synthesizer import Synthesizer
from src.synthesizer.keyboard_mapping import is_synth_key
from src.visualization.note_visualizer import NoteVisualizer


class AudioVisualizer:
    def __init__(self):
        self.audio_source = None
        self.fft_analyzer = FFTAnalyzer()
        self.beat_detector = BeatDetector()

        self.renderer = Renderer()
        self.renderer.on_quit = self.quit
        self.renderer.on_key = self.handle_key
        self.renderer.on_key_up = self.handle_key_up
        self.renderer.on_file_drop = self.handle_file_drop

        self.synthesizer = Synthesizer()
        self.note_visualizer = NoteVisualizer(
            self.renderer.width,
            self.renderer.height,
            self.synthesizer
        )
        self.renderer.note_visualizer = self.note_visualizer

        self.running = False
        self.current_features = AudioFeatures()
        self.piano_mode = False

        self.file_player = None
        self.audio_manager = None

    def start(self) -> None:
        print("Starting Audio Visualizer...")
        print()
        print("Controls (press H in app for full list):")
        print("  Audio:       O=Open  M=Mic  Space=Pause  F6=Piano Mode")
        print("  Synth:       A-L=Play notes  F7=Waveform")
        print("  Modes:       Tab=Next  1-3=Select mode")
        print("  Effects:     G=Glow  B=Bloom  V=Vignette")
        print("  Presets:     F1=Clean  F2=Subtle  F3=Vibrant  F4=Retro  F5=Dreamy")
        print("  Style:       Ctrl+S=Toggle  [ ]=Prev/Next style")
        print("  Other:       H=Help  D=Debug  ESC=Quit")
        print()

        self._start_microphone()
        self.synthesizer.start()

        self.running = True
        self._main_loop()

    def _start_microphone(self) -> None:
        try:
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
        while self.running:
            if not self.renderer.handle_events():
                self.running = False
                break

            if self.audio_source and self.audio_source.is_running:
                if not self.audio_source.is_paused:
                    samples = self.audio_source.get_samples_for_fft(FFT_SIZE)

                    self.current_features = self.fft_analyzer.analyze(samples)

                    is_beat, strength, tempo = self.beat_detector.detect(
                        self.current_features.spectrum
                    )
                    self.current_features.is_beat = is_beat
                    self.current_features.beat_strength = strength
                    self.current_features.tempo_bpm = tempo

            self.renderer.update(self.current_features)
            self.renderer.draw(
                self.current_features,
                source_name=self.audio_source.name if self.audio_source else "None",
                is_paused=self.audio_source.is_paused if self.audio_source else False,
                piano_mode=self.piano_mode
            )

    def handle_key(self, key: int, mod: int) -> None:
        if self.piano_mode and is_synth_key(key):
            self.synthesizer.note_on(key)
            return

        if key == pygame.K_F6:
            self._toggle_piano_mode()
            return

        if key == pygame.K_F7:
            waveform = self.synthesizer.cycle_waveform()
            print(f"Waveform: {waveform}")
            return

        if key == pygame.K_SPACE:
            if self.audio_source:
                paused = self.audio_source.toggle_pause()
                print("Paused" if paused else "Resumed")

        elif key == pygame.K_m:
            if self.piano_mode:
                self._toggle_piano_mode()
            else:
                self._start_microphone()

        elif key == pygame.K_o:
            if self.piano_mode:
                self._toggle_piano_mode()
            self._open_file_dialog()

    def _toggle_piano_mode(self) -> None:
        self.piano_mode = not self.piano_mode
        self.renderer.piano_mode = self.piano_mode

        if self.piano_mode:
            if self.audio_source and hasattr(self.audio_source, 'stop'):
                self.audio_source.stop()
            self.audio_source = self.synthesizer
            self.fft_analyzer.reset()
            self.beat_detector.reset()
            print("Piano Mode: ON - Visualizing synthesizer")
        else:
            self._start_microphone()
            print("Piano Mode: OFF - Visualizing microphone")

    def handle_key_up(self, key: int, mod: int) -> None:
        if self.piano_mode and is_synth_key(key):
            self.synthesizer.note_off(key)

    def handle_file_drop(self, filepath: str) -> None:
        print(f"File dropped: {filepath}")
        self._load_audio_file(filepath)

    def _open_file_dialog(self) -> None:
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
        try:
            from src.audio.file_player import FilePlayer

            if self.audio_source:
                self.audio_source.stop()

            self.audio_source = FilePlayer(filepath)
            self.audio_source.start()
            self.fft_analyzer.reset()
            self.beat_detector.reset()
            print(f"Playing: {os.path.basename(filepath)}")

        except ImportError:
            print("File player not available yet.")
        except Exception as e:
            print(f"Error loading file: {e}")
            self._start_microphone()

    def quit(self) -> None:
        print("Shutting down...")

        if self.audio_source:
            self.audio_source.stop()

        self.synthesizer.stop()
        self.renderer.quit()
        self.running = False


def main():
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