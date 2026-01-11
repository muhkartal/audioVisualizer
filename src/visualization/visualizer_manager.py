import pygame
from typing import List, Optional

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from src.analysis.audio_features import AudioFeatures
from src.visualization.base_visualizer import BaseVisualizer
from src.visualization.spectrum_bars import SpectrumBars
from src.visualization.radial_pattern import RadialPattern
from src.visualization.waveform import Waveform


class VisualizerManager:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.visualizers: List[BaseVisualizer] = [
            SpectrumBars(width, height),
            RadialPattern(width, height),
            Waveform(width, height),
        ]

        self.current_index = 0
        self.previous_index = -1

        self.transitioning = False
        self.transition_progress = 0.0
        self.transition_speed = 3.0

        self.transition_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        self.visualizers[self.current_index].on_activate()

    @property
    def current(self) -> BaseVisualizer:
        return self.visualizers[self.current_index]

    @property
    def mode_count(self) -> int:
        return len(self.visualizers)

    @property
    def mode_names(self) -> List[str]:
        return [v.name for v in self.visualizers]

    @property
    def current_mode_name(self) -> str:
        return self.current.name

    def switch_to(self, index: int) -> None:
        if index < 0 or index >= len(self.visualizers):
            return

        if index == self.current_index:
            return

        self.previous_index = self.current_index
        self.current_index = index
        self.transitioning = True
        self.transition_progress = 0.0

        self.visualizers[self.previous_index].on_deactivate()
        self.visualizers[self.current_index].on_activate()

    def next_mode(self) -> None:
        next_index = (self.current_index + 1) % len(self.visualizers)
        self.switch_to(next_index)

    def previous_mode(self) -> None:
        prev_index = (self.current_index - 1) % len(self.visualizers)
        self.switch_to(prev_index)

    def update(self, features: AudioFeatures) -> None:
        self.current.update(features)

        if self.transitioning and self.previous_index >= 0:
            self.visualizers[self.previous_index].update(features)

            self.transition_progress += self.transition_speed / 60.0
            if self.transition_progress >= 1.0:
                self.transitioning = False
                self.transition_progress = 1.0
                self.previous_index = -1

    def draw(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        if self.transitioning and self.previous_index >= 0:
            self._draw_transition(surface, features)
        else:
            self.current.draw(surface, features)

    def _draw_transition(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        prev_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        curr_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.visualizers[self.previous_index].draw(prev_surface, features)
        self.current.draw(curr_surface, features)

        prev_alpha = int(255 * (1.0 - self.transition_progress))
        curr_alpha = int(255 * self.transition_progress)

        prev_surface.set_alpha(prev_alpha)
        curr_surface.set_alpha(curr_alpha)

        surface.blit(prev_surface, (0, 0))
        surface.blit(curr_surface, (0, 0))

    def on_resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.transition_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        for visualizer in self.visualizers:
            visualizer.on_resize(width, height)

    def draw_mode_indicator(self, surface: pygame.Surface, font: pygame.font.Font,
                           x: int, y: int) -> None:
        dot_radius = 5
        dot_spacing = 20

        for i, visualizer in enumerate(self.visualizers):
            dot_x = x + i * dot_spacing
            color = (200, 200, 200) if i == self.current_index else (60, 60, 60)
            pygame.draw.circle(surface, color, (dot_x, y), dot_radius)

        name_text = f"Mode: {self.current_mode_name}"
        text_surface = font.render(name_text, True, (150, 150, 150))
        surface.blit(text_surface, (x + len(self.visualizers) * dot_spacing + 10, y - 7))