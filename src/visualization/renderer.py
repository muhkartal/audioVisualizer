import pygame
import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TARGET_FPS,
    WINDOW_TITLE, BG_COLOR
)
from src.analysis.audio_features import AudioFeatures
from src.visualization.visualizer_manager import VisualizerManager
from src.effects.post_processing import PostProcessor
from src.effects.style_transfer import StyleTransfer


class Renderer:
    def __init__(self, width: int = WINDOW_WIDTH, height: int = WINDOW_HEIGHT):
        self.width = width
        self.height = height
        self.running = False

        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.screen = pygame.display.set_mode(
            (width, height),
            pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE
        )

        self.clock = pygame.time.Clock()
        self.fps = 0
        self.frame_count = 0
        self.fps_update_time = time.time()

        pygame.font.init()
        self.font = pygame.font.SysFont('consolas', 14)
        self.font_large = pygame.font.SysFont('consolas', 16)

        self.visualizer_manager = VisualizerManager(width, height)

        self.post_processor = PostProcessor(width, height)

        self.style_transfer = StyleTransfer(width, height)
        self.style_transfer_enabled = False
        self.current_style_index = 0

        self.show_help = False
        self.show_debug = False

        self.on_quit = None
        self.on_key = None
        self.on_key_up = None
        self.on_file_drop = None

        self.note_visualizer = None
        self.piano_mode = False

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.on_quit:
                    self.on_quit()
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.on_quit:
                        self.on_quit()
                    return False

                handled = self._handle_renderer_key(event.key, event.mod)

                if not handled and self.on_key:
                    self.on_key(event.key, event.mod)

            elif event.type == pygame.VIDEORESIZE:
                self._handle_resize(event.w, event.h)

            elif event.type == pygame.DROPFILE:
                if self.on_file_drop:
                    self.on_file_drop(event.file)

            elif event.type == pygame.KEYUP:
                if self.on_key_up:
                    self.on_key_up(event.key, event.mod)

        return True

    def _handle_renderer_key(self, key: int, mod: int) -> bool:
        if key == pygame.K_TAB:
            if mod & pygame.KMOD_SHIFT:
                self.visualizer_manager.previous_mode()
            else:
                self.visualizer_manager.next_mode()
            return True

        if key == pygame.K_1:
            self.visualizer_manager.switch_to(0)
            return True
        if key == pygame.K_2:
            self.visualizer_manager.switch_to(1)
            return True
        if key == pygame.K_3:
            self.visualizer_manager.switch_to(2)
            return True

        if not self.piano_mode:
            if key == pygame.K_g:
                enabled = self.post_processor.toggle_effect('glow')
                print(f"Glow: {'ON' if enabled else 'OFF'}")
                return True

            if key == pygame.K_b:
                enabled = self.post_processor.toggle_effect('bloom')
                print(f"Bloom: {'ON' if enabled else 'OFF'}")
                return True

            if key == pygame.K_v:
                enabled = self.post_processor.toggle_effect('vignette')
                print(f"Vignette: {'ON' if enabled else 'OFF'}")
                return True

            if key == pygame.K_c:
                enabled = self.post_processor.toggle_effect('chromatic')
                print(f"Chromatic aberration: {'ON' if enabled else 'OFF'}")
                return True

            if key == pygame.K_l:
                enabled = self.post_processor.toggle_effect('scanlines')
                print(f"Scanlines: {'ON' if enabled else 'OFF'}")
                return True

        if key == pygame.K_F1:
            self.post_processor.set_preset('clean')
            print("Preset: Clean")
            return True
        if key == pygame.K_F2:
            self.post_processor.set_preset('subtle')
            print("Preset: Subtle")
            return True
        if key == pygame.K_F3:
            self.post_processor.set_preset('vibrant')
            print("Preset: Vibrant")
            return True
        if key == pygame.K_F4:
            self.post_processor.set_preset('retro')
            print("Preset: Retro")
            return True
        if key == pygame.K_F5:
            self.post_processor.set_preset('dreamy')
            print("Preset: Dreamy")
            return True

        if key == pygame.K_s and mod & pygame.KMOD_CTRL:
            self._toggle_style_transfer()
            return True

        if key == pygame.K_LEFTBRACKET:
            self._prev_style()
            return True
        if key == pygame.K_RIGHTBRACKET:
            self._next_style()
            return True

        if key == pygame.K_h:
            self.show_help = not self.show_help
            return True

        if key == pygame.K_d:
            self.show_debug = not self.show_debug
            return True

        return False

    def _handle_resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode(
            (width, height),
            pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE
        )
        self.visualizer_manager.on_resize(width, height)
        self.post_processor.on_resize(width, height)
        self.style_transfer.on_resize(width, height)
        if self.note_visualizer:
            self.note_visualizer.on_resize(width, height)

    def _toggle_style_transfer(self) -> None:
        if not self.style_transfer.onnx_available:
            print("Style transfer unavailable (ONNX Runtime not installed)")
            return

        self.style_transfer_enabled = not self.style_transfer_enabled
        if self.style_transfer_enabled:
            styles = self.style_transfer.available_styles
            style = styles[self.current_style_index % len(styles)]
            self.style_transfer.start(style)
            print(f"Style transfer: ON ({style})")
        else:
            self.style_transfer.stop()
            print("Style transfer: OFF")

    def _next_style(self) -> None:
        if not self.style_transfer_enabled:
            return
        styles = self.style_transfer.available_styles
        self.current_style_index = (self.current_style_index + 1) % len(styles)
        style = styles[self.current_style_index]
        self.style_transfer.set_style(style)
        print(f"Style: {style}")

    def _prev_style(self) -> None:
        if not self.style_transfer_enabled:
            return
        styles = self.style_transfer.available_styles
        self.current_style_index = (self.current_style_index - 1) % len(styles)
        style = styles[self.current_style_index]
        self.style_transfer.set_style(style)
        print(f"Style: {style}")

    def update(self, features: AudioFeatures) -> None:
        self.visualizer_manager.update(features)

    def draw(self, features: AudioFeatures, source_name: str = "",
             is_paused: bool = False, piano_mode: bool = False) -> None:
        self.screen.fill(BG_COLOR)

        self.visualizer_manager.draw(self.screen, features)

        if self.note_visualizer and piano_mode:
            self.note_visualizer.draw(self.screen)

        self.post_processor.apply(self.screen, features)

        if self.style_transfer_enabled:
            self.style_transfer.submit_frame(self.screen)
            styled = self.style_transfer.get_styled_frame()
            if styled:
                styled.set_alpha(int(255 * self.style_transfer.blend_alpha))
                self.screen.blit(styled, (0, 0))

        self._draw_info_overlay(features, source_name, is_paused)

        if self.show_help:
            self._draw_help_overlay()

        pygame.display.flip()

        self._update_fps()

        self.clock.tick(TARGET_FPS)

    def _draw_info_overlay(self, features: AudioFeatures,
                          source_name: str, is_paused: bool) -> None:
        y_offset = 10

        fps_text = f"FPS: {self.fps:.0f}"
        fps_surface = self.font.render(fps_text, True, (100, 100, 100))
        self.screen.blit(fps_surface, (10, y_offset))

        source_text = f"Source: {source_name}"
        source_surface = self.font.render(source_text, True, (100, 100, 100))
        self.screen.blit(source_surface, (10, y_offset + 18))

        self.visualizer_manager.draw_mode_indicator(
            self.screen, self.font, 10, y_offset + 40
        )

        if is_paused:
            pause_text = "PAUSED"
            pause_surface = self.font_large.render(pause_text, True, (255, 200, 0))
            pause_x = self.width // 2 - pause_surface.get_width() // 2
            self.screen.blit(pause_surface, (pause_x, y_offset))

        if features.is_beat:
            beat_text = "BEAT"
            beat_surface = self.font.render(beat_text, True, (255, 100, 100))
            self.screen.blit(beat_surface, (self.width - 60, y_offset))

        if self.style_transfer_enabled:
            styles = self.style_transfer.available_styles
            style = styles[self.current_style_index % len(styles)]
            style_text = f"Style: {style}"
            style_surface = self.font.render(style_text, True, (150, 100, 200))
            self.screen.blit(style_surface, (self.width - 150, y_offset + 18))

        if self.show_debug:
            self._draw_level_meters(features)

        self._draw_controls_help()

    def _draw_level_meters(self, features: AudioFeatures) -> None:
        meter_width = 60
        meter_height = 8
        x = self.width - meter_width - 10
        y = 50

        levels = [
            ("Bass", features.bass, (255, 100, 100)),
            ("Mid", features.mid, (100, 255, 100)),
            ("Treble", features.treble, (100, 100, 255))
        ]

        for label, value, color in levels:
            label_surface = self.font.render(label, True, (100, 100, 100))
            self.screen.blit(label_surface, (x - 50, y - 2))

            bg_rect = pygame.Rect(x, y, meter_width, meter_height)
            pygame.draw.rect(self.screen, (30, 30, 30), bg_rect)

            level_width = int(value * meter_width)
            if level_width > 0:
                level_rect = pygame.Rect(x, y, level_width, meter_height)
                pygame.draw.rect(self.screen, color, level_rect)

            y += 20

    def _draw_controls_help(self) -> None:
        controls = [
            "H: Help",
            "Tab: Mode",
            "1-3: Modes",
            "F1-F5: Presets",
            "ESC: Quit"
        ]

        help_text = "  |  ".join(controls)
        help_surface = self.font.render(help_text, True, (60, 60, 60))
        help_x = self.width // 2 - help_surface.get_width() // 2
        help_y = self.height - 25
        self.screen.blit(help_surface, (help_x, help_y))

    def _draw_help_overlay(self) -> None:
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        title = "Audio Visualizer - Controls"
        sections = [
            ("Audio", [
                "O         Open audio file",
                "M         Toggle microphone",
                "Space     Pause/Resume",
            ]),
            ("Synthesizer (Piano Mode)", [
                "F6        Toggle Piano Mode",
                "A-L       Play white keys (C4-D5)",
                "W,E,T,Y,U Black keys (sharps)",
                "F7        Cycle waveform",
            ]),
            ("Visualization Modes", [
                "Tab       Next mode",
                "Shift+Tab Previous mode",
                "1-3       Select mode directly",
            ]),
            ("Effect Toggles", [
                "G         Glow",
                "B         Bloom",
                "V         Vignette",
                "C         Chromatic aberration",
                "L         Scanlines",
            ]),
            ("Effect Presets", [
                "F1        Clean (no effects)",
                "F2        Subtle",
                "F3        Vibrant",
                "F4        Retro",
                "F5        Dreamy",
            ]),
            ("Style Transfer", [
                "Ctrl+S    Toggle style transfer",
                "[         Previous style",
                "]         Next style",
            ]),
            ("Other", [
                "H         Toggle this help",
                "D         Toggle debug info",
                "ESC       Quit",
            ]),
        ]

        x_start = 50
        y = 50

        title_surface = self.font_large.render(title, True, (255, 255, 255))
        self.screen.blit(title_surface, (x_start, y))
        y += 40

        col_width = (self.width - 100) // 2
        col = 0
        col_y_start = y

        for section_title, items in sections:
            if y > self.height - 100 and col == 0:
                col = 1
                y = col_y_start

            x = x_start + col * col_width

            section_surface = self.font.render(section_title, True, (150, 200, 255))
            self.screen.blit(section_surface, (x, y))
            y += 22

            for item in items:
                item_surface = self.font.render(item, True, (180, 180, 180))
                self.screen.blit(item_surface, (x + 10, y))
                y += 18

            y += 10

    def _update_fps(self) -> None:
        self.frame_count += 1
        current_time = time.time()

        if current_time - self.fps_update_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.fps_update_time)
            self.frame_count = 0
            self.fps_update_time = current_time

    def quit(self) -> None:
        if self.style_transfer_enabled:
            self.style_transfer.stop()
        pygame.quit()