import pygame
import numpy as np
import math

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import NUM_BANDS, PANEL_HEIGHT
from src.analysis.audio_features import AudioFeatures
from src.visualization.base_visualizer import BaseVisualizer


class RadialPattern(BaseVisualizer):
    def __init__(self, width: int, height: int):
        super().__init__(width, height)

        self.center_x = width // 2
        self.center_y = (height - PANEL_HEIGHT) // 2

        self.num_segments = NUM_BANDS
        self.min_radius = 80
        self.max_radius = min(width, height - PANEL_HEIGHT) // 2 - 50

        self.rotation = 0.0
        self.pulse = 0.0
        self.glow_intensity = 0.0

        self.angles = np.linspace(0, 2 * np.pi, self.num_segments, endpoint=False)

        self.smoothed_spectrum = np.zeros(self.num_segments)

    def update(self, features: AudioFeatures) -> None:
        self.rotation += 0.005

        if features.is_beat:
            self.pulse = features.beat_strength * 0.6
            self.glow_intensity = features.beat_strength
        else:
            self.pulse *= 0.9
            self.glow_intensity *= 0.85

        self.smoothed_spectrum += (features.spectrum - self.smoothed_spectrum) * 0.25

    def draw(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        self._draw_reference_circles(surface)

        self._draw_radial_lines(surface)

        self._draw_center(surface, features)

    def _draw_reference_circles(self, surface: pygame.Surface) -> None:
        for i, radius in enumerate([self.min_radius, self.max_radius * 0.6]):
            pygame.draw.circle(
                surface, (35, 35, 40),
                (self.center_x, self.center_y),
                int(radius + self.pulse * 10), 1
            )

    def _draw_radial_lines(self, surface: pygame.Surface) -> None:
        spectrum = self.smoothed_spectrum

        for i in range(self.num_segments):
            angle = self.angles[i] + self.rotation

            magnitude = spectrum[i] if i < len(spectrum) else 0
            inner_radius = self.min_radius + self.pulse * 8
            outer_radius = inner_radius + magnitude * (self.max_radius - inner_radius)

            cos_a = math.cos(angle)
            sin_a = math.sin(angle)

            start_x = self.center_x + cos_a * inner_radius
            start_y = self.center_y + sin_a * inner_radius
            end_x = self.center_x + cos_a * outer_radius
            end_y = self.center_y + sin_a * outer_radius

            base_brightness = 90
            brightness = int(base_brightness + magnitude * (220 - base_brightness))
            brightness = min(255, brightness + int(self.glow_intensity * 25))
            color = (brightness, brightness, min(255, brightness + 5))

            thickness = max(2, int(2 + magnitude * 3))

            pygame.draw.line(surface, color,
                           (start_x, start_y), (end_x, end_y),
                           thickness)

    def _draw_center(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        if self.glow_intensity > 0.1:
            glow_radius = int(self.min_radius * 0.8 + self.pulse * 15)
            glow_surface = pygame.Surface(
                (glow_radius * 4, glow_radius * 4), pygame.SRCALPHA
            )
            glow_alpha = int(30 * self.glow_intensity)
            pygame.draw.circle(
                glow_surface, (160, 160, 170, glow_alpha),
                (glow_radius * 2, glow_radius * 2), glow_radius
            )
            surface.blit(
                glow_surface,
                (self.center_x - glow_radius * 2, self.center_y - glow_radius * 2),
                special_flags=pygame.BLEND_RGBA_ADD
            )

        ring_radius = int(self.min_radius * 0.5 + features.bass * 10 + self.pulse * 8)
        ring_brightness = 100 + int(features.bass * 60)
        pygame.draw.circle(
            surface, (ring_brightness, ring_brightness, ring_brightness + 3),
            (self.center_x, self.center_y), ring_radius, 2
        )

        inner_radius = int(ring_radius * 0.5)
        inner_brightness = 50 + int(features.bass * 40)
        pygame.draw.circle(
            surface, (inner_brightness, inner_brightness, inner_brightness + 2),
            (self.center_x, self.center_y), inner_radius
        )

        pygame.draw.circle(
            surface, (180, 180, 185),
            (self.center_x, self.center_y), 3
        )

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self.center_x = width // 2
        self.center_y = (height - PANEL_HEIGHT) // 2
        self.max_radius = min(width, height - PANEL_HEIGHT) // 2 - 50

    @property
    def name(self) -> str:
        return "Radial"