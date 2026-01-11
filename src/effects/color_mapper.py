"""
Color Mapper - Color utilities and palette generation.
"""

import pygame
import numpy as np
from typing import List, Tuple
import colorsys


class ColorMapper:
    """
    Utilities for color manipulation and palette generation.

    Provides methods for creating gradients, mapping audio
    features to colors, and generating color schemes.
    """

    # Pre-defined color palettes
    PALETTES = {
        'neon': [
            (255, 0, 128),    # Hot pink
            (0, 255, 255),    # Cyan
            (255, 255, 0),    # Yellow
            (128, 0, 255),    # Purple
            (0, 255, 128),    # Mint
        ],
        'fire': [
            (255, 0, 0),      # Red
            (255, 100, 0),    # Orange
            (255, 200, 0),    # Yellow
            (255, 255, 100),  # Light yellow
            (255, 255, 255),  # White (hottest)
        ],
        'ocean': [
            (0, 20, 60),      # Deep blue
            (0, 50, 100),     # Navy
            (0, 100, 150),    # Blue
            (50, 150, 200),   # Light blue
            (150, 220, 255),  # Pale blue
        ],
        'forest': [
            (20, 60, 20),     # Dark green
            (40, 100, 40),    # Forest
            (60, 150, 60),    # Green
            (100, 200, 100),  # Light green
            (180, 230, 150),  # Pale green
        ],
        'synthwave': [
            (255, 0, 100),    # Pink
            (200, 0, 200),    # Magenta
            (100, 0, 255),    # Purple
            (0, 100, 255),    # Blue
            (0, 200, 255),    # Cyan
        ],
        'rainbow': [
            (255, 0, 0),      # Red
            (255, 127, 0),    # Orange
            (255, 255, 0),    # Yellow
            (0, 255, 0),      # Green
            (0, 0, 255),      # Blue
            (75, 0, 130),     # Indigo
            (148, 0, 211),    # Violet
        ],
    }

    def __init__(self, palette_name: str = 'neon'):
        """
        Initialize the color mapper.

        Args:
            palette_name: Name of the color palette to use
        """
        self.set_palette(palette_name)
        self.hue_offset = 0.0

    def set_palette(self, palette_name: str) -> None:
        """Set the active color palette."""
        if palette_name in self.PALETTES:
            self.palette = self.PALETTES[palette_name]
            self.palette_name = palette_name
        else:
            self.palette = self.PALETTES['neon']
            self.palette_name = 'neon'

    @staticmethod
    def lerp_color(color1: Tuple[int, int, int], color2: Tuple[int, int, int],
                   t: float) -> Tuple[int, int, int]:
        """
        Linear interpolation between two colors.

        Args:
            color1: First color (RGB)
            color2: Second color (RGB)
            t: Interpolation factor (0-1)

        Returns:
            Interpolated color
        """
        t = max(0.0, min(1.0, t))
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        return (r, g, b)

    def get_gradient_color(self, t: float) -> Tuple[int, int, int]:
        """
        Get a color from the palette gradient.

        Args:
            t: Position in gradient (0-1)

        Returns:
            Color at that position
        """
        t = max(0.0, min(1.0, t))
        n = len(self.palette)

        if n == 1:
            return self.palette[0]

        # Find segment
        segment = t * (n - 1)
        i = int(segment)
        if i >= n - 1:
            return self.palette[-1]

        local_t = segment - i
        return self.lerp_color(self.palette[i], self.palette[i + 1], local_t)

    @staticmethod
    def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        """
        Convert HSV to RGB.

        Args:
            h: Hue (0-360)
            s: Saturation (0-100)
            v: Value/Brightness (0-100)

        Returns:
            RGB color tuple
        """
        h = h / 360.0
        s = s / 100.0
        v = v / 100.0

        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))

    @staticmethod
    def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
        """
        Convert RGB to HSV.

        Args:
            r: Red (0-255)
            g: Green (0-255)
            b: Blue (0-255)

        Returns:
            HSV tuple (h: 0-360, s: 0-100, v: 0-100)
        """
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        return (h * 360, s * 100, v * 100)

    def map_frequency_to_color(self, frequency_index: int, num_bands: int) -> Tuple[int, int, int]:
        """
        Map a frequency band index to a color.

        Args:
            frequency_index: Index of the frequency band
            num_bands: Total number of bands

        Returns:
            Color for that frequency
        """
        t = frequency_index / max(1, num_bands - 1)
        return self.get_gradient_color(t)

    def map_energy_to_brightness(self, color: Tuple[int, int, int],
                                  energy: float) -> Tuple[int, int, int]:
        """
        Adjust color brightness based on energy level.

        Args:
            color: Base color
            energy: Energy level (0-1)

        Returns:
            Brightness-adjusted color
        """
        factor = 0.3 + energy * 0.7  # 30% base brightness + up to 70% from energy
        r = int(color[0] * factor)
        g = int(color[1] * factor)
        b = int(color[2] * factor)
        return (min(255, r), min(255, g), min(255, b))

    def generate_spectrum_colors(self, num_bands: int) -> List[Tuple[int, int, int]]:
        """
        Generate colors for spectrum visualization.

        Args:
            num_bands: Number of frequency bands

        Returns:
            List of colors for each band
        """
        return [self.map_frequency_to_color(i, num_bands) for i in range(num_bands)]

    def apply_flash(self, color: Tuple[int, int, int],
                    intensity: float) -> Tuple[int, int, int]:
        """
        Apply a flash/brightening effect to a color.

        Args:
            color: Base color
            intensity: Flash intensity (0-1)

        Returns:
            Flashed color
        """
        r = min(255, int(color[0] + intensity * (255 - color[0])))
        g = min(255, int(color[1] + intensity * (255 - color[1])))
        b = min(255, int(color[2] + intensity * (255 - color[2])))
        return (r, g, b)

    def shift_hue(self, color: Tuple[int, int, int],
                  degrees: float) -> Tuple[int, int, int]:
        """
        Shift the hue of a color.

        Args:
            color: Input color
            degrees: Degrees to shift hue (0-360)

        Returns:
            Hue-shifted color
        """
        h, s, v = self.rgb_to_hsv(*color)
        h = (h + degrees) % 360
        return self.hsv_to_rgb(h, s, v)

    def update(self, dt: float = 1/60) -> None:
        """Update animated color effects."""
        self.hue_offset = (self.hue_offset + dt * 30) % 360

    @property
    def available_palettes(self) -> List[str]:
        """Get list of available palette names."""
        return list(self.PALETTES.keys())
