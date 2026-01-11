"""
Control panel UI overlay for the visualizer.
"""

import pygame

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from config.settings import (
    PANEL_HEIGHT, PANEL_BG_COLOR, PANEL_TEXT_COLOR, FONT_SIZE
)
from src.analysis.audio_features import AudioFeatures


class ControlPanel:
    """
    UI control panel overlay displayed at the bottom of the window.

    Shows playback controls, audio information, and settings.
    """

    def __init__(self, width: int, height: int):
        """
        Initialize the control panel.

        Args:
            width: Window width
            height: Window height
        """
        self.width = width
        self.height = height
        self.panel_height = PANEL_HEIGHT

        # Position at bottom of window
        self.x = 0
        self.y = height - PANEL_HEIGHT

        # Font
        pygame.font.init()
        self.font = pygame.font.SysFont('consolas', FONT_SIZE)
        self.font_small = pygame.font.SysFont('consolas', FONT_SIZE - 2)

        # Create panel surface with alpha
        self.surface = pygame.Surface((width, PANEL_HEIGHT), pygame.SRCALPHA)

        # State
        self.visible = True

    def update_dimensions(self, width: int, height: int) -> None:
        """Update dimensions when window is resized."""
        self.width = width
        self.height = height
        self.y = height - PANEL_HEIGHT
        self.surface = pygame.Surface((width, PANEL_HEIGHT), pygame.SRCALPHA)

    def draw(self, screen: pygame.Surface, features: AudioFeatures,
             source_name: str = "", is_paused: bool = False,
             current_time: float = 0, duration: float = 0,
             fps: float = 0, tempo: float = 0) -> None:
        """
        Draw the control panel.

        Args:
            screen: PyGame surface to draw on
            features: Current audio features
            source_name: Name of audio source
            is_paused: Whether playback is paused
            current_time: Current playback time (for files)
            duration: Total duration (for files)
            fps: Current FPS
            tempo: Detected tempo in BPM
        """
        if not self.visible:
            return

        # Clear panel surface
        self.surface.fill(PANEL_BG_COLOR)

        # Left section: Source info
        self._draw_source_info(source_name, is_paused)

        # Center section: Playback progress (if file)
        if duration > 0:
            self._draw_progress(current_time, duration)

        # Right section: Stats
        self._draw_stats(fps, tempo, features)

        # Draw panel to screen
        screen.blit(self.surface, (self.x, self.y))

    def _draw_source_info(self, source_name: str, is_paused: bool) -> None:
        """Draw source information on the left."""
        x = 10
        y = (self.panel_height - FONT_SIZE) // 2

        # Source name
        text = source_name
        if is_paused:
            text += " [PAUSED]"

        text_surface = self.font.render(text, True, PANEL_TEXT_COLOR)
        self.surface.blit(text_surface, (x, y))

    def _draw_progress(self, current_time: float, duration: float) -> None:
        """Draw playback progress bar in center."""
        bar_width = min(300, self.width // 3)
        bar_height = 6
        x = (self.width - bar_width) // 2
        y = (self.panel_height - bar_height) // 2 - 8

        # Time display
        time_text = f"{self._format_time(current_time)} / {self._format_time(duration)}"
        time_surface = self.font_small.render(time_text, True, PANEL_TEXT_COLOR)
        time_x = x + (bar_width - time_surface.get_width()) // 2
        self.surface.blit(time_surface, (time_x, y - 14))

        # Background bar
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(self.surface, (60, 60, 60), bg_rect, border_radius=3)

        # Progress bar
        if duration > 0:
            progress = min(1.0, current_time / duration)
            progress_width = int(bar_width * progress)
            if progress_width > 0:
                progress_rect = pygame.Rect(x, y, progress_width, bar_height)
                pygame.draw.rect(self.surface, (100, 200, 150), progress_rect,
                               border_radius=3)

    def _draw_stats(self, fps: float, tempo: float, features: AudioFeatures) -> None:
        """Draw statistics on the right."""
        x = self.width - 150
        y = (self.panel_height - FONT_SIZE) // 2

        # FPS
        fps_text = f"FPS: {fps:.0f}"
        fps_surface = self.font_small.render(fps_text, True, (100, 100, 100))
        self.surface.blit(fps_surface, (x, y - 8))

        # Tempo
        if tempo > 0:
            tempo_text = f"BPM: {tempo:.0f}"
            tempo_surface = self.font_small.render(tempo_text, True, (100, 100, 100))
            self.surface.blit(tempo_surface, (x + 70, y - 8))

        # Energy level indicator
        energy = features.energy
        level_text = f"Level: {energy:.0%}"
        level_surface = self.font_small.render(level_text, True, (100, 100, 100))
        self.surface.blit(level_surface, (x, y + 8))

    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    def toggle_visibility(self) -> bool:
        """Toggle panel visibility."""
        self.visible = not self.visible
        return self.visible

    def handle_click(self, x: int, y: int) -> str:
        """
        Handle mouse click on panel.

        Args:
            x: Click x position
            y: Click y position

        Returns:
            Action string or empty if no action
        """
        # Check if click is in panel area
        if y < self.y or y > self.y + self.panel_height:
            return ""

        # Could add button handling here in the future
        return ""
