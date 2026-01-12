import pygame
import random
import time
from typing import List
from dataclasses import dataclass, field

from config.settings import (
    PIANO_KEY_HEIGHT, PIANO_WHITE_KEY_WIDTH,
    PIANO_BLACK_KEY_WIDTH, PIANO_BLACK_KEY_HEIGHT,
    PARTICLE_DT
)
from src.synthesizer.keyboard_mapping import (
    KEYBOARD_MAP, get_note_name, get_note_color, NOTE_NAMES
)

@dataclass
class NoteParticle:
    x: float
    y: float
    vx: float
    vy: float
    color: tuple
    size: float
    alpha: float = 255
    lifetime: float = 2.0
    created: float = field(default_factory=time.time)

    @property
    def age(self) -> float:
        return time.time() - self.created

    @property
    def is_dead(self) -> bool:
        return self.age >= self.lifetime


class NoteVisualizer:
    WHITE_KEYS = [
        (pygame.K_a, 60),   # C4
        (pygame.K_s, 62),   # D4
        (pygame.K_d, 64),   # E4
        (pygame.K_f, 65),   # F4
        (pygame.K_g, 67),   # G4
        (pygame.K_h, 69),   # A4
        (pygame.K_j, 71),   # B4
        (pygame.K_k, 72),   # C5
        (pygame.K_l, 74),   # D5
        (pygame.K_SEMICOLON, 76),  # E5
    ]

    BLACK_KEYS = [
        (pygame.K_w, 61, 0),   # C#4 - after white key index 0
        (pygame.K_e, 63, 1),   # D#4 - after white key index 1
        (pygame.K_t, 66, 3),   # F#4 - after white key index 3
        (pygame.K_y, 68, 4),   # G#4 - after white key index 4
        (pygame.K_u, 70, 5),   # A#4 - after white key index 5
        (pygame.K_p, 75, 8),   # D#5 - after white key index 8
    ]

    def __init__(self, width: int, height: int, synthesizer):
        self.width = width
        self.height = height
        self.synthesizer = synthesizer
        self.particles: List[NoteParticle] = []
        self.key_rects = {}
        self._calculate_key_positions()
        self.font = pygame.font.SysFont('consolas', 14)
        self.font_small = pygame.font.SysFont('consolas', 11)

    def _calculate_key_positions(self):
        num_white = len(self.WHITE_KEYS)
        total_width = num_white * PIANO_WHITE_KEY_WIDTH
        start_x = (self.width - total_width) // 2
        y = self.height - PIANO_KEY_HEIGHT - 30

        self.key_rects = {}

        for i, (key, midi) in enumerate(self.WHITE_KEYS):
            x = start_x + i * PIANO_WHITE_KEY_WIDTH
            self.key_rects[key] = pygame.Rect(
                x, y, PIANO_WHITE_KEY_WIDTH - 2, PIANO_KEY_HEIGHT
            )

        for key, midi, after_index in self.BLACK_KEYS:
            white_x = start_x + after_index * PIANO_WHITE_KEY_WIDTH
            x = white_x + PIANO_WHITE_KEY_WIDTH - PIANO_BLACK_KEY_WIDTH // 2
            self.key_rects[key] = pygame.Rect(
                x, y, PIANO_BLACK_KEY_WIDTH, PIANO_BLACK_KEY_HEIGHT
            )

    def on_resize(self, width: int, height: int):
        self.width = width
        self.height = height
        self._calculate_key_positions()

    def _spawn_particles(self, key: int, midi_note: int):
        if key not in self.key_rects:
            return

        rect = self.key_rects[key]
        color = get_note_color(midi_note)
        center_x = rect.centerx
        top_y = rect.top

        for _ in range(5):
            particle = NoteParticle(
                x=center_x + random.uniform(-10, 10),
                y=top_y,
                vx=random.uniform(-30, 30),
                vy=random.uniform(-150, -80),
                color=color,
                size=random.uniform(4, 8),
                lifetime=random.uniform(1.0, 2.0)
            )
            self.particles.append(particle)

    def _update_particles(self, dt: float):
        for particle in self.particles:
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.vy += 50 * dt
            progress = particle.age / particle.lifetime
            particle.alpha = int(255 * (1 - progress))
            particle.size = max(1, particle.size * (1 - progress * 0.3))

        self.particles = [p for p in self.particles if not p.is_dead]

    def draw(self, surface: pygame.Surface):
        active_notes = self.synthesizer.get_active_notes()
        active_keys = {note.key for note in active_notes}

        for note in active_notes:
            if note.key in self.key_rects:
                if random.random() < 0.3:
                    self._spawn_particles(note.key, note.midi_note)

        self._update_particles(PARTICLE_DT)

        for particle in self.particles:
            if particle.alpha > 0:
                color = (*particle.color, int(particle.alpha))
                size = int(particle.size)
                if size > 0:
                    glow_surf = pygame.Surface((size*4, size*4), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*particle.color, int(particle.alpha * 0.3)),
                                     (size*2, size*2), size*2)
                    pygame.draw.circle(glow_surf, color,
                                     (size*2, size*2), size)
                    surface.blit(glow_surf,
                               (int(particle.x - size*2), int(particle.y - size*2)))

        for key, midi in self.WHITE_KEYS:
            if key not in self.key_rects:
                continue
            rect = self.key_rects[key]
            is_active = key in active_keys

            if is_active:
                color = get_note_color(midi)
                pygame.draw.rect(surface, color, rect, border_radius=3)
                glow_rect = rect.inflate(6, 6)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*color, 100), glow_surf.get_rect(), border_radius=5)
                surface.blit(glow_surf, glow_rect.topleft)
                pygame.draw.rect(surface, color, rect, border_radius=3)
            else:
                pygame.draw.rect(surface, (240, 240, 245), rect, border_radius=3)
                pygame.draw.rect(surface, (100, 100, 110), rect, 1, border_radius=3)

        for key, midi, _ in self.BLACK_KEYS:
            if key not in self.key_rects:
                continue
            rect = self.key_rects[key]
            is_active = key in active_keys

            if is_active:
                color = get_note_color(midi)
                pygame.draw.rect(surface, color, rect, border_radius=2)
                glow_rect = rect.inflate(4, 4)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*color, 100), glow_surf.get_rect(), border_radius=3)
                surface.blit(glow_surf, glow_rect.topleft)
                pygame.draw.rect(surface, color, rect, border_radius=2)
            else:
                pygame.draw.rect(surface, (30, 30, 35), rect, border_radius=2)

        if active_notes:
            note_names = [get_note_name(n.midi_note) for n in active_notes]
            text = "Playing: " + ", ".join(note_names)
            text_surface = self.font.render(text, True, (200, 200, 220))
            x = self.width // 2 - text_surface.get_width() // 2
            y = self.height - PIANO_KEY_HEIGHT - 55
            surface.blit(text_surface, (x, y))

        waveform_text = f"[{self.synthesizer.waveform}]"
        if not self.synthesizer.enabled:
            waveform_text += " (OFF)"
        wf_surface = self.font_small.render(waveform_text, True, (100, 100, 110))
        x = self.width // 2 - wf_surface.get_width() // 2
        y = self.height - 20
        surface.blit(wf_surface, (x, y))
