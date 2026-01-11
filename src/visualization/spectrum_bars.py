import pygame
import numpy as np

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from config.settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, NUM_BANDS,
    BAR_COLOR_LOW, BAR_COLOR_HIGH, BAR_SPACING,
    BAR_MIN_HEIGHT, BAR_BORDER_RADIUS,
    BEAT_FLASH_INTENSITY, BEAT_FLASH_DECAY, PANEL_HEIGHT
)
from src.analysis.audio_features import AudioFeatures
from src.visualization.base_visualizer import BaseVisualizer


class SpectrumBars(BaseVisualizer):
    def __init__(self, width: int = WINDOW_WIDTH, height: int = WINDOW_HEIGHT):
        super().__init__(width, height)
        self.num_bands = NUM_BANDS

        self.update_dimensions(width, height)

        self.flash_intensity = 0.0
        self.previous_spectrum = np.zeros(NUM_BANDS)

        self._compute_color_gradient()

    def update_dimensions(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

        self.draw_height = height - PANEL_HEIGHT - 40

        total_spacing = BAR_SPACING * (self.num_bands - 1)
        available_width = width - 40
        self.bar_width = max(4, (available_width - total_spacing) // self.num_bands)

        total_bars_width = self.bar_width * self.num_bands + total_spacing
        self.start_x = (width - total_bars_width) // 2

        self.base_y = height - PANEL_HEIGHT - 20

    def _compute_color_gradient(self) -> None:
        self.colors = []
        for i in range(self.num_bands):
            t = i / (self.num_bands - 1)

            r = int(BAR_COLOR_LOW[0] + t * (BAR_COLOR_HIGH[0] - BAR_COLOR_LOW[0]))
            g = int(BAR_COLOR_LOW[1] + t * (BAR_COLOR_HIGH[1] - BAR_COLOR_LOW[1]))
            b = int(BAR_COLOR_LOW[2] + t * (BAR_COLOR_HIGH[2] - BAR_COLOR_LOW[2]))

            self.colors.append((r, g, b))

    def _apply_flash(self, color: tuple, intensity: float) -> tuple:
        if intensity <= 0:
            return color

        r = min(255, int(color[0] + intensity * (255 - color[0])))
        g = min(255, int(color[1] + intensity * (255 - color[1])))
        b = min(255, int(color[2] + intensity * (255 - color[2])))

        return (r, g, b)

    def update(self, features: AudioFeatures) -> None:
        if features.is_beat:
            self.flash_intensity = BEAT_FLASH_INTENSITY * features.beat_strength
        else:
            self.flash_intensity *= BEAT_FLASH_DECAY

        self.previous_spectrum = features.spectrum.copy()

    def draw(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        spectrum = features.spectrum
        peaks = features.spectrum_peaks

        for i in range(min(len(spectrum), self.num_bands)):
            bar_height = max(BAR_MIN_HEIGHT,
                           int(spectrum[i] * self.draw_height))
            peak_height = max(BAR_MIN_HEIGHT,
                            int(peaks[i] * self.draw_height))

            x = self.start_x + i * (self.bar_width + BAR_SPACING)
            y = self.base_y - bar_height

            color = self._apply_flash(self.colors[i], self.flash_intensity)

            bar_rect = pygame.Rect(x, y, self.bar_width, bar_height)

            if BAR_BORDER_RADIUS > 0 and bar_height > BAR_BORDER_RADIUS * 2:
                pygame.draw.rect(surface, color, bar_rect,
                               border_radius=BAR_BORDER_RADIUS)
            else:
                pygame.draw.rect(surface, color, bar_rect)

            if peak_height > bar_height + 4:
                peak_y = self.base_y - peak_height
                peak_rect = pygame.Rect(x, peak_y, self.bar_width, 3)
                peak_color = self._apply_flash((255, 255, 255), self.flash_intensity)
                pygame.draw.rect(surface, peak_color, peak_rect)

            if spectrum[i] > 0.7:
                glow_alpha = int((spectrum[i] - 0.7) * 3 * 100)
                glow_surface = pygame.Surface((self.bar_width + 10, bar_height + 10),
                                            pygame.SRCALPHA)
                glow_color = (*color, glow_alpha)
                pygame.draw.rect(glow_surface, glow_color,
                               (5, 5, self.bar_width, bar_height),
                               border_radius=BAR_BORDER_RADIUS)
                surface.blit(glow_surface, (x - 5, y - 5),
                           special_flags=pygame.BLEND_RGBA_ADD)

    def draw_frequency_labels(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        labels = [
            (0, "20"),
            (int(self.num_bands * 0.15), "100"),
            (int(self.num_bands * 0.35), "500"),
            (int(self.num_bands * 0.55), "2k"),
            (int(self.num_bands * 0.75), "8k"),
            (self.num_bands - 1, "20k")
        ]

        label_y = self.base_y + 8

        for band_idx, label_text in labels:
            if band_idx < self.num_bands:
                x = self.start_x + band_idx * (self.bar_width + BAR_SPACING)
                text = font.render(label_text, True, (100, 100, 100))
                text_x = x + self.bar_width // 2 - text.get_width() // 2
                surface.blit(text, (text_x, label_y))

    def on_resize(self, width: int, height: int) -> None:
        self.update_dimensions(width, height)