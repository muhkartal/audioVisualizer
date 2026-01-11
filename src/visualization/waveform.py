import pygame
import numpy as np

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from config.settings import PANEL_HEIGHT
from src.analysis.audio_features import AudioFeatures
from src.visualization.base_visualizer import BaseVisualizer


class Waveform(BaseVisualizer):
    def __init__(self, width: int, height: int):
        super().__init__(width, height)

        self.draw_height = height - PANEL_HEIGHT - 60
        self.center_y = (height - PANEL_HEIGHT) // 2

        self.num_points = 256
        self.line_thickness = 2

        self.waveform_data = np.zeros(self.num_points)
        self.smoothing = 0.3

        self.glow_intensity = 0.0
        self.pulse = 0.0

        self.line_color = (180, 180, 190)
        self.glow_color = (220, 220, 230)
        self.grid_color = (40, 40, 45)

    def update(self, features: AudioFeatures) -> None:
        spectrum = features.spectrum

        if len(spectrum) > 0:
            indices = np.linspace(0, len(spectrum) - 1, self.num_points).astype(int)
            new_data = spectrum[indices]

            self.waveform_data = (self.smoothing * self.waveform_data +
                                  (1 - self.smoothing) * new_data)

        if features.is_beat:
            self.glow_intensity = 0.8 * features.beat_strength
            self.pulse = 1.0
        else:
            self.glow_intensity *= 0.9
            self.pulse *= 0.92

    def draw(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        self._draw_grid(surface)

        self._draw_center_line(surface)

        self._draw_waveform(surface, features)

        self._draw_frequency_bars(surface, features)

    def _draw_grid(self, surface: pygame.Surface) -> None:
        num_h_lines = 8
        spacing = self.draw_height // num_h_lines

        for i in range(num_h_lines + 1):
            y = self.center_y - self.draw_height // 2 + i * spacing
            alpha = 30 if i == num_h_lines // 2 else 15
            pygame.draw.line(surface, (*self.grid_color[:3],),
                           (50, y), (self.width - 50, y), 1)

        num_v_lines = 16
        spacing = (self.width - 100) // num_v_lines

        for i in range(num_v_lines + 1):
            x = 50 + i * spacing
            pygame.draw.line(surface, self.grid_color,
                           (x, self.center_y - self.draw_height // 2),
                           (x, self.center_y + self.draw_height // 2), 1)

    def _draw_center_line(self, surface: pygame.Surface) -> None:
        pygame.draw.line(surface, (60, 60, 65),
                        (50, self.center_y),
                        (self.width - 50, self.center_y), 1)

    def _draw_waveform(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        if len(self.waveform_data) < 2:
            return

        x_spacing = (self.width - 100) / (self.num_points - 1)
        max_amplitude = self.draw_height * 0.4

        points_top = []
        points_bottom = []

        for i, amplitude in enumerate(self.waveform_data):
            x = 50 + i * x_spacing

            scaled_amp = amplitude * max_amplitude * (1 + self.pulse * 0.2)

            points_top.append((x, self.center_y - scaled_amp))
            points_bottom.append((x, self.center_y + scaled_amp))

        if self.glow_intensity > 0.1:
            glow_color = (
                int(self.glow_color[0] * self.glow_intensity),
                int(self.glow_color[1] * self.glow_intensity),
                int(self.glow_color[2] * self.glow_intensity)
            )
            if len(points_top) > 1:
                pygame.draw.lines(surface, glow_color, False, points_top,
                                self.line_thickness + 4)
                pygame.draw.lines(surface, glow_color, False, points_bottom,
                                self.line_thickness + 4)

        line_color = self._get_line_color(features)

        if len(points_top) > 1:
            pygame.draw.lines(surface, line_color, False, points_top,
                            self.line_thickness)
            pygame.draw.lines(surface, line_color, False, points_bottom,
                            self.line_thickness)

        if len(points_top) > 2:
            fill_points = points_top + points_bottom[::-1]
            fill_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.polygon(fill_surface, (150, 150, 160, 25), fill_points)
            surface.blit(fill_surface, (0, 0))

    def _get_line_color(self, features: AudioFeatures) -> tuple:
        brightness = 180 + int(features.energy * 60)
        brightness = min(255, brightness + int(self.glow_intensity * 40))

        return (brightness, brightness, min(255, brightness + 10))

    def _draw_frequency_bars(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        bar_area_height = 30
        bar_y = self.center_y + self.draw_height // 2 + 20

        levels = [
            ("Bass", features.bass),
            ("Mid", features.mid),
            ("High", features.treble)
        ]

        bar_width = 80
        spacing = 30
        total_width = len(levels) * bar_width + (len(levels) - 1) * spacing
        start_x = (self.width - total_width) // 2

        for i, (label, value) in enumerate(levels):
            x = start_x + i * (bar_width + spacing)

            bg_rect = pygame.Rect(x, bar_y, bar_width, 4)
            pygame.draw.rect(surface, (40, 40, 45), bg_rect)

            level_width = int(value * bar_width)
            if level_width > 0:
                brightness = 120 + int(value * 100)
                level_rect = pygame.Rect(x, bar_y, level_width, 4)
                pygame.draw.rect(surface, (brightness, brightness, brightness + 5), level_rect)

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self.draw_height = height - PANEL_HEIGHT - 60
        self.center_y = (height - PANEL_HEIGHT) // 2

    @property
    def name(self) -> str:
        return "Waveform"