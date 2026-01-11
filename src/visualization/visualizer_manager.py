"""
Visualizer Manager - Handles multiple visualization modes with transitions.
"""

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
    """
    Manages multiple visualization modes with smooth transitions.

    Handles mode switching, crossfade effects, and unified
    update/draw interface.
    """

    def __init__(self, width: int, height: int):
        """
        Initialize the visualizer manager.

        Args:
            width: Display width
            height: Display height
        """
        self.width = width
        self.height = height

        # Create all visualizers
        self.visualizers: List[BaseVisualizer] = [
            SpectrumBars(width, height),
            RadialPattern(width, height),
            Waveform(width, height),
        ]

        # Current state
        self.current_index = 0
        self.previous_index = -1

        # Transition state
        self.transitioning = False
        self.transition_progress = 0.0
        self.transition_speed = 3.0  # Transitions per second

        # Transition surface for crossfade
        self.transition_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Activate first visualizer
        self.visualizers[self.current_index].on_activate()

    @property
    def current(self) -> BaseVisualizer:
        """Get the current active visualizer."""
        return self.visualizers[self.current_index]

    @property
    def mode_count(self) -> int:
        """Get the number of visualization modes."""
        return len(self.visualizers)

    @property
    def mode_names(self) -> List[str]:
        """Get names of all visualization modes."""
        return [v.name for v in self.visualizers]

    @property
    def current_mode_name(self) -> str:
        """Get name of current mode."""
        return self.current.name

    def switch_to(self, index: int) -> None:
        """
        Switch to a specific visualization mode.

        Args:
            index: Mode index to switch to
        """
        if index < 0 or index >= len(self.visualizers):
            return

        if index == self.current_index:
            return

        # Start transition
        self.previous_index = self.current_index
        self.current_index = index
        self.transitioning = True
        self.transition_progress = 0.0

        # Notify visualizers
        self.visualizers[self.previous_index].on_deactivate()
        self.visualizers[self.current_index].on_activate()

    def next_mode(self) -> None:
        """Switch to the next visualization mode."""
        next_index = (self.current_index + 1) % len(self.visualizers)
        self.switch_to(next_index)

    def previous_mode(self) -> None:
        """Switch to the previous visualization mode."""
        prev_index = (self.current_index - 1) % len(self.visualizers)
        self.switch_to(prev_index)

    def update(self, features: AudioFeatures) -> None:
        """
        Update all active visualizers.

        Args:
            features: Current audio features
        """
        # Update current visualizer
        self.current.update(features)

        # Update previous during transition
        if self.transitioning and self.previous_index >= 0:
            self.visualizers[self.previous_index].update(features)

            # Update transition progress
            self.transition_progress += self.transition_speed / 60.0  # Assuming 60fps
            if self.transition_progress >= 1.0:
                self.transitioning = False
                self.transition_progress = 1.0
                self.previous_index = -1

    def draw(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        """
        Draw the current visualization (with transition if active).

        Args:
            surface: PyGame surface to draw on
            features: Current audio features
        """
        if self.transitioning and self.previous_index >= 0:
            # Crossfade transition
            self._draw_transition(surface, features)
        else:
            # Draw current only
            self.current.draw(surface, features)

    def _draw_transition(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        """Draw crossfade transition between modes."""
        # Create temporary surfaces
        prev_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        curr_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw both visualizers
        self.visualizers[self.previous_index].draw(prev_surface, features)
        self.current.draw(curr_surface, features)

        # Calculate alpha values
        prev_alpha = int(255 * (1.0 - self.transition_progress))
        curr_alpha = int(255 * self.transition_progress)

        # Apply alpha
        prev_surface.set_alpha(prev_alpha)
        curr_surface.set_alpha(curr_alpha)

        # Composite to main surface
        surface.blit(prev_surface, (0, 0))
        surface.blit(curr_surface, (0, 0))

    def on_resize(self, width: int, height: int) -> None:
        """Handle window resize."""
        self.width = width
        self.height = height
        self.transition_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        for visualizer in self.visualizers:
            visualizer.on_resize(width, height)

    def draw_mode_indicator(self, surface: pygame.Surface, font: pygame.font.Font,
                           x: int, y: int) -> None:
        """
        Draw mode indicator showing current mode.

        Args:
            surface: Surface to draw on
            font: Font to use
            x: X position
            y: Y position
        """
        # Draw mode indicator dots
        dot_radius = 5
        dot_spacing = 20

        for i, visualizer in enumerate(self.visualizers):
            dot_x = x + i * dot_spacing
            color = (200, 200, 200) if i == self.current_index else (60, 60, 60)
            pygame.draw.circle(surface, color, (dot_x, y), dot_radius)

        # Draw mode name
        name_text = f"Mode: {self.current_mode_name}"
        text_surface = font.render(name_text, True, (150, 150, 150))
        surface.blit(text_surface, (x + len(self.visualizers) * dot_spacing + 10, y - 7))
