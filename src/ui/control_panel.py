import pygame

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from config.settings import (
    PANEL_HEIGHT, PANEL_BG_COLOR, PANEL_TEXT_COLOR, FONT_SIZE
)
from src.analysis.audio_features import AudioFeatures


class ControlPanel:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.panel_height = PANEL_HEIGHT

        self.x = 0
        self.y = height - PANEL_HEIGHT

        pygame.font.init()
        self.font = pygame.font.SysFont('consolas', FONT_SIZE)
        self.font_small = pygame.font.SysFont('consolas', FONT_SIZE - 2)

        self.surface = pygame.Surface((width, PANEL_HEIGHT), pygame.SRCALPHA)

        self.visible = True

    def update_dimensions(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.y = height - PANEL_HEIGHT
        self.surface = pygame.Surface((width, PANEL_HEIGHT), pygame.SRCALPHA)

    def draw(self, screen: pygame.Surface, features: AudioFeatures,
             source_name: str = "", is_paused: bool = False,
             current_time: float = 0, duration: float = 0,
             fps: float = 0, tempo: float = 0) -> None:
        if not self.visible:
            return

        self.surface.fill(PANEL_BG_COLOR)

        self._draw_source_info(source_name, is_paused)

        if duration > 0:
            self._draw_progress(current_time, duration)

        self._draw_stats(fps, tempo, features)

        screen.blit(self.surface, (self.x, self.y))

    def _draw_source_info(self, source_name: str, is_paused: bool) -> None:
        x = 10
        y = (self.panel_height - FONT_SIZE) // 2

        text = source_name
        if is_paused:
            text += " [PAUSED]"

        text_surface = self.font.render(text, True, PANEL_TEXT_COLOR)
        self.surface.blit(text_surface, (x, y))

    def _draw_progress(self, current_time: float, duration: float) -> None:
        bar_width = min(300, self.width // 3)
        bar_height = 6
        x = (self.width - bar_width) // 2
        y = (self.panel_height - bar_height) // 2 - 8

        time_text = f"{self._format_time(current_time)} / {self._format_time(duration)}"
        time_surface = self.font_small.render(time_text, True, PANEL_TEXT_COLOR)
        time_x = x + (bar_width - time_surface.get_width()) // 2
        self.surface.blit(time_surface, (time_x, y - 14))

        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(self.surface, (60, 60, 60), bg_rect, border_radius=3)

        if duration > 0:
            progress = min(1.0, current_time / duration)
            progress_width = int(bar_width * progress)
            if progress_width > 0:
                progress_rect = pygame.Rect(x, y, progress_width, bar_height)
                pygame.draw.rect(self.surface, (100, 200, 150), progress_rect,
                               border_radius=3)

    def _draw_stats(self, fps: float, tempo: float, features: AudioFeatures) -> None:
        x = self.width - 150
        y = (self.panel_height - FONT_SIZE) // 2

        fps_text = f"FPS: {fps:.0f}"
        fps_surface = self.font_small.render(fps_text, True, (100, 100, 100))
        self.surface.blit(fps_surface, (x, y - 8))

        if tempo > 0:
            tempo_text = f"BPM: {tempo:.0f}"
            tempo_surface = self.font_small.render(tempo_text, True, (100, 100, 100))
            self.surface.blit(tempo_surface, (x + 70, y - 8))

        energy = features.energy
        level_text = f"Level: {energy:.0%}"
        level_surface = self.font_small.render(level_text, True, (100, 100, 100))
        self.surface.blit(level_surface, (x, y + 8))

    def _format_time(self, seconds: float) -> str:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    def toggle_visibility(self) -> bool:
        self.visible = not self.visible
        return self.visible

    def handle_click(self, x: int, y: int) -> str:
        if y < self.y or y > self.y + self.panel_height:
            return ""

        return ""