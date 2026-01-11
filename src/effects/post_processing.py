import pygame
import numpy as np
from typing import Tuple, Optional

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from src.analysis.audio_features import AudioFeatures


class PostProcessor:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.glow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.blur_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.vignette_surface = self._create_vignette(width, height)
        self.previous_frame = None

        self.glow_enabled = True
        self.glow_intensity = 0.5
        self.glow_radius = 2

        self.bloom_enabled = True
        self.bloom_threshold = 0.7
        self.bloom_intensity = 0.3

        self.motion_blur_enabled = False
        self.motion_blur_amount = 0.3

        self.vignette_enabled = True
        self.vignette_intensity = 0.4

        self.chromatic_enabled = False
        self.chromatic_offset = 3

        self.scanlines_enabled = False
        self.scanline_intensity = 0.1

    def _create_vignette(self, width: int, height: int) -> pygame.Surface:
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        center_x, center_y = width // 2, height // 2
        max_distance = np.sqrt(center_x ** 2 + center_y ** 2)

        for y in range(height):
            for x in range(width):
                distance = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                alpha = int(255 * (distance / max_distance) ** 2)
                surface.set_at((x, y), (0, 0, 0, alpha))

        return surface

    def _create_vignette_fast(self, width: int, height: int) -> pygame.Surface:
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        scale = 4
        small_w, small_h = width // scale, height // scale
        small_surface = pygame.Surface((small_w, small_h), pygame.SRCALPHA)

        center_x, center_y = small_w // 2, small_h // 2
        max_distance = np.sqrt(center_x ** 2 + center_y ** 2)

        for y in range(small_h):
            for x in range(small_w):
                distance = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                alpha = int(255 * (distance / max_distance) ** 1.5)
                small_surface.set_at((x, y), (0, 0, 0, min(200, alpha)))

        return pygame.transform.smoothscale(small_surface, (width, height))

    def apply(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        if self.motion_blur_enabled:
            self._apply_motion_blur(surface)

        if self.glow_enabled:
            self._apply_glow(surface, features)

        if self.bloom_enabled:
            self._apply_bloom(surface, features)

        if self.chromatic_enabled:
            self._apply_chromatic_aberration(surface, features)

        if self.scanlines_enabled:
            self._apply_scanlines(surface)

        if self.vignette_enabled:
            self._apply_vignette(surface, features)

        if self.motion_blur_enabled:
            self.previous_frame = surface.copy()

    def _apply_glow(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        scale = 4
        small_size = (self.width // scale, self.height // scale)

        small = pygame.transform.smoothscale(surface, small_size)

        blurred = pygame.transform.smoothscale(small, (self.width, self.height))

        intensity = self.glow_intensity * (0.5 + features.energy * 0.5)

        blurred.set_alpha(int(255 * intensity))
        surface.blit(blurred, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def _apply_bloom(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        if features.is_beat:
            intensity = self.bloom_intensity * features.beat_strength

            bloom_surface = pygame.Surface((self.width, self.height))
            bloom_surface.fill((int(255 * intensity * 0.3),
                               int(255 * intensity * 0.3),
                               int(255 * intensity * 0.4)))
            surface.blit(bloom_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def _apply_motion_blur(self, surface: pygame.Surface) -> None:
        if self.previous_frame is not None:
            alpha = int(255 * self.motion_blur_amount)
            self.previous_frame.set_alpha(alpha)
            surface.blit(self.previous_frame, (0, 0))

    def _apply_vignette(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        intensity = self.vignette_intensity * (0.8 + features.bass * 0.2)

        vignette = self.vignette_surface.copy()
        vignette.set_alpha(int(255 * intensity))
        surface.blit(vignette, (0, 0))

    def _apply_chromatic_aberration(self, surface: pygame.Surface,
                                     features: AudioFeatures) -> None:
        offset = int(self.chromatic_offset * (1 + features.bass))

        if offset < 1:
            return

        tint_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        pygame.draw.rect(tint_surface, (30, 0, 0, 50), (0, 0, offset * 2, self.height))

        pygame.draw.rect(tint_surface, (0, 20, 30, 50),
                        (self.width - offset * 2, 0, offset * 2, self.height))

        surface.blit(tint_surface, (0, 0))

    def _apply_scanlines(self, surface: pygame.Surface) -> None:
        scanline_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        alpha = int(255 * self.scanline_intensity)
        for y in range(0, self.height, 3):
            pygame.draw.line(scanline_surface, (0, 0, 0, alpha),
                           (0, y), (self.width, y))

        surface.blit(scanline_surface, (0, 0))

    def on_resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.glow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.blur_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.vignette_surface = self._create_vignette_fast(width, height)
        self.previous_frame = None

    def toggle_effect(self, effect_name: str) -> bool:
        attr_name = f"{effect_name}_enabled"
        if hasattr(self, attr_name):
            current = getattr(self, attr_name)
            setattr(self, attr_name, not current)
            return not current
        return False

    def set_preset(self, preset_name: str) -> None:
        presets = {
            'clean': {
                'glow_enabled': False,
                'bloom_enabled': False,
                'motion_blur_enabled': False,
                'vignette_enabled': False,
                'chromatic_enabled': False,
                'scanlines_enabled': False,
            },
            'subtle': {
                'glow_enabled': True,
                'glow_intensity': 0.3,
                'bloom_enabled': False,
                'motion_blur_enabled': False,
                'vignette_enabled': True,
                'vignette_intensity': 0.3,
                'chromatic_enabled': False,
                'scanlines_enabled': False,
            },
            'vibrant': {
                'glow_enabled': True,
                'glow_intensity': 0.6,
                'bloom_enabled': True,
                'bloom_intensity': 0.4,
                'motion_blur_enabled': False,
                'vignette_enabled': True,
                'vignette_intensity': 0.4,
                'chromatic_enabled': False,
                'scanlines_enabled': False,
            },
            'retro': {
                'glow_enabled': True,
                'glow_intensity': 0.4,
                'bloom_enabled': False,
                'motion_blur_enabled': False,
                'vignette_enabled': True,
                'vignette_intensity': 0.5,
                'chromatic_enabled': True,
                'chromatic_offset': 2,
                'scanlines_enabled': True,
                'scanline_intensity': 0.15,
            },
            'dreamy': {
                'glow_enabled': True,
                'glow_intensity': 0.8,
                'bloom_enabled': True,
                'bloom_intensity': 0.5,
                'motion_blur_enabled': True,
                'motion_blur_amount': 0.2,
                'vignette_enabled': True,
                'vignette_intensity': 0.5,
                'chromatic_enabled': False,
                'scanlines_enabled': False,
            },
        }

        if preset_name in presets:
            for key, value in presets[preset_name].items():
                setattr(self, key, value)