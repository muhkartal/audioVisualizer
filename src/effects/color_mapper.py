import pygame
import numpy as np
from typing import List, Tuple
import colorsys


class ColorMapper:
    PALETTES = {
        'neon': [
            (255, 0, 128),
            (0, 255, 255),
            (255, 255, 0),
            (128, 0, 255),
            (0, 255, 128),
        ],
        'fire': [
            (255, 0, 0),
            (255, 100, 0),
            (255, 200, 0),
            (255, 255, 100),
            (255, 255, 255),
        ],
        'ocean': [
            (0, 20, 60),
            (0, 50, 100),
            (0, 100, 150),
            (50, 150, 200),
            (150, 220, 255),
        ],
        'forest': [
            (20, 60, 20),
            (40, 100, 40),
            (60, 150, 60),
            (100, 200, 100),
            (180, 230, 150),
        ],
        'synthwave': [
            (255, 0, 100),
            (200, 0, 200),
            (100, 0, 255),
            (0, 100, 255),
            (0, 200, 255),
        ],
        'rainbow': [
            (255, 0, 0),
            (255, 127, 0),
            (255, 255, 0),
            (0, 255, 0),
            (0, 0, 255),
            (75, 0, 130),
            (148, 0, 211),
        ],
    }

    def __init__(self, palette_name: str = 'neon'):
        self.set_palette(palette_name)
        self.hue_offset = 0.0

    def set_palette(self, palette_name: str) -> None:
        if palette_name in self.PALETTES:
            self.palette = self.PALETTES[palette_name]
            self.palette_name = palette_name
        else:
            self.palette = self.PALETTES['neon']
            self.palette_name = 'neon'

    @staticmethod
    def lerp_color(color1: Tuple[int, int, int], color2: Tuple[int, int, int],
                   t: float) -> Tuple[int, int, int]:
        t = max(0.0, min(1.0, t))
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        return (r, g, b)

    def get_gradient_color(self, t: float) -> Tuple[int, int, int]:
        t = max(0.0, min(1.0, t))
        n = len(self.palette)

        if n == 1:
            return self.palette[0]

        segment = t * (n - 1)
        i = int(segment)
        if i >= n - 1:
            return self.palette[-1]

        local_t = segment - i
        return self.lerp_color(self.palette[i], self.palette[i + 1], local_t)

    @staticmethod
    def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        h = h / 360.0
        s = s / 100.0
        v = v / 100.0

        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))

    @staticmethod
    def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        return (h * 360, s * 100, v * 100)

    def map_frequency_to_color(self, frequency_index: int, num_bands: int) -> Tuple[int, int, int]:
        t = frequency_index / max(1, num_bands - 1)
        return self.get_gradient_color(t)

    def map_energy_to_brightness(self, color: Tuple[int, int, int],
                                  energy: float) -> Tuple[int, int, int]:
        factor = 0.3 + energy * 0.7
        r = int(color[0] * factor)
        g = int(color[1] * factor)
        b = int(color[2] * factor)
        return (min(255, r), min(255, g), min(255, b))

    def generate_spectrum_colors(self, num_bands: int) -> List[Tuple[int, int, int]]:
        return [self.map_frequency_to_color(i, num_bands) for i in range(num_bands)]

    def apply_flash(self, color: Tuple[int, int, int],
                    intensity: float) -> Tuple[int, int, int]:
        r = min(255, int(color[0] + intensity * (255 - color[0])))
        g = min(255, int(color[1] + intensity * (255 - color[1])))
        b = min(255, int(color[2] + intensity * (255 - color[2])))
        return (r, g, b)

    def shift_hue(self, color: Tuple[int, int, int],
                  degrees: float) -> Tuple[int, int, int]:
        h, s, v = self.rgb_to_hsv(*color)
        h = (h + degrees) % 360
        return self.hsv_to_rgb(h, s, v)

    def update(self, dt: float = 1/60) -> None:
        self.hue_offset = (self.hue_offset + dt * 30) % 360

    @property
    def available_palettes(self) -> List[str]:
        return list(self.PALETTES.keys())