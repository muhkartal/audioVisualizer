from abc import ABC, abstractmethod
import pygame

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from src.analysis.audio_features import AudioFeatures


class BaseVisualizer(ABC):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.active = False
        self.alpha = 1.0

    @abstractmethod
    def update(self, features: AudioFeatures) -> None:
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        pass

    def on_resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def on_activate(self) -> None:
        self.active = True
        self.alpha = 1.0

    def on_deactivate(self) -> None:
        self.active = False

    def reset(self) -> None:
        pass

    @property
    def name(self) -> str:
        return self.__class__.__name__