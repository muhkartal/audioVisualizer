"""
Abstract base class for all visualizers.
"""

from abc import ABC, abstractmethod
import pygame

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from src.analysis.audio_features import AudioFeatures


class BaseVisualizer(ABC):
    """
    Abstract base class for visualization modes.

    All visualizers must implement update() and draw() methods.
    """

    def __init__(self, width: int, height: int):
        """
        Initialize the visualizer.

        Args:
            width: Display width in pixels
            height: Display height in pixels
        """
        self.width = width
        self.height = height
        self.active = False
        self.alpha = 1.0  # For fade transitions

    @abstractmethod
    def update(self, features: AudioFeatures) -> None:
        """
        Update visualizer state based on audio features.

        Args:
            features: Current audio features from analyzer
        """
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        """
        Draw the visualization.

        Args:
            surface: PyGame surface to draw on
            features: Current audio features
        """
        pass

    def on_resize(self, width: int, height: int) -> None:
        """
        Handle window resize.

        Args:
            width: New width
            height: New height
        """
        self.width = width
        self.height = height

    def on_activate(self) -> None:
        """Called when this visualizer becomes active."""
        self.active = True
        self.alpha = 1.0

    def on_deactivate(self) -> None:
        """Called when this visualizer is deactivated."""
        self.active = False

    def reset(self) -> None:
        """Reset visualizer state."""
        pass

    @property
    def name(self) -> str:
        """Get the name of this visualizer."""
        return self.__class__.__name__
