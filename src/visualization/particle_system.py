import pygame
import numpy as np
import math
from dataclasses import dataclass
from typing import List

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from config.settings import PANEL_HEIGHT, BEAT_FLASH_INTENSITY
from src.analysis.audio_features import AudioFeatures
from src.visualization.base_visualizer import BaseVisualizer


@dataclass
class Particle:
    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    ax: float = 0.0
    ay: float = 0.0
    lifetime: float = 0.0
    max_lifetime: float = 2.0
    size: float = 3.0
    initial_size: float = 3.0
    gray_value: float = 200.0
    brightness: float = 100.0
    active: bool = False
    trail: bool = False


class ParticleSystem(BaseVisualizer):
    def __init__(self, width: int, height: int, max_particles: int = 1000):
        super().__init__(width, height)

        self.max_particles = max_particles
        self.center_x = width // 2
        self.center_y = (height - PANEL_HEIGHT) // 2

        self.particles: List[Particle] = [Particle() for _ in range(max_particles)]
        self.active_count = 0

        self.emit_rate = 20
        self.gravity = 50.0
        self.drag = 0.98

        self.flash_intensity = 0.0

        self.ambient_particles: List[Particle] = [Particle() for _ in range(50)]
        self._init_ambient_particles()

        self.trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def _init_ambient_particles(self) -> None:
        for p in self.ambient_particles:
            p.x = np.random.uniform(0, self.width)
            p.y = np.random.uniform(0, self.height - PANEL_HEIGHT)
            p.vx = np.random.uniform(-20, 20)
            p.vy = np.random.uniform(-20, 20)
            p.size = np.random.uniform(1, 3)
            p.initial_size = p.size
            p.gray_value = np.random.uniform(60, 120)
            p.brightness = np.random.uniform(30, 60)
            p.active = True
            p.max_lifetime = float('inf')

    def _get_inactive_particle(self) -> Particle:
        for p in self.particles:
            if not p.active:
                return p
        return None

    def emit(self, count: int, energy: float, spectral_centroid: float,
             bass: float) -> None:
        for _ in range(count):
            particle = self._get_inactive_particle()
            if particle is None:
                break

            angle = np.random.uniform(0, 2 * np.pi)

            speed = energy * np.random.uniform(100, 400) + bass * 200

            particle.x = self.center_x
            particle.y = self.center_y
            particle.vx = math.cos(angle) * speed
            particle.vy = math.sin(angle) * speed
            particle.ax = 0
            particle.ay = self.gravity * np.random.uniform(0.5, 1.5)

            particle.lifetime = 0.0
            particle.max_lifetime = np.random.uniform(1.5, 3.5)

            particle.initial_size = np.random.uniform(3, 8 + bass * 10)
            particle.size = particle.initial_size

            base_gray = 140 + spectral_centroid * 80
            particle.gray_value = base_gray + np.random.uniform(-20, 40)
            particle.gray_value = min(255, max(100, particle.gray_value))
            particle.brightness = 80 + np.random.uniform(0, 20)

            particle.active = True
            particle.trail = np.random.random() < 0.3

    def update(self, features: AudioFeatures) -> None:
        dt = 1.0 / 60.0

        if features.is_beat:
            emit_count = int(self.emit_rate * (1 + features.beat_strength))
            self.emit(emit_count, features.energy, features.spectral_centroid,
                     features.bass)
            self.flash_intensity = BEAT_FLASH_INTENSITY

        self.flash_intensity *= 0.9

        for p in self.particles:
            if not p.active:
                continue

            p.vx += p.ax * dt
            p.vy += p.ay * dt

            p.vx *= self.drag
            p.vy *= self.drag

            p.x += p.vx * dt
            p.y += p.vy * dt

            p.lifetime += dt

            life_ratio = 1.0 - (p.lifetime / p.max_lifetime)
            p.size = p.initial_size * life_ratio

            if p.lifetime >= p.max_lifetime or p.size < 0.5:
                p.active = False
            elif p.y > self.height - PANEL_HEIGHT + 50:
                p.active = False

        self._update_ambient_particles(dt, features)

    def _update_ambient_particles(self, dt: float, features: AudioFeatures) -> None:
        for p in self.ambient_particles:
            p.vx += (np.random.uniform(-1, 1) + features.mid * 5) * dt * 60
            p.vy += (np.random.uniform(-1, 1) + features.treble * 3) * dt * 60

            p.vx *= 0.99
            p.vy *= 0.99

            p.x += p.vx * dt
            p.y += p.vy * dt

            if p.x < 0:
                p.x = self.width
            elif p.x > self.width:
                p.x = 0
            if p.y < 0:
                p.y = self.height - PANEL_HEIGHT
            elif p.y > self.height - PANEL_HEIGHT:
                p.y = 0

            p.size = p.initial_size * (1 + features.bass * 0.5)

    def draw(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        self.trail_surface.fill((0, 0, 0, 20))

        for p in self.ambient_particles:
            gray = int(p.gray_value)
            pygame.draw.circle(surface, (gray, gray, gray + 5),
                             (int(p.x), int(p.y)), max(1, int(p.size)))

        for p in self.particles:
            if not p.active:
                continue

            life_ratio = 1.0 - (p.lifetime / p.max_lifetime)

            flash_boost = self.flash_intensity * 50
            gray = int(min(255, p.gray_value + flash_boost))
            color = (gray, gray, min(255, gray + 8))

            if p.size > 4:
                glow_size = int(p.size * 2)
                glow_surface = pygame.Surface((glow_size * 2, glow_size * 2),
                                             pygame.SRCALPHA)
                glow_alpha = int(life_ratio * 80)
                pygame.draw.circle(glow_surface, (gray, gray, gray, glow_alpha),
                                 (glow_size, glow_size), glow_size)
                surface.blit(glow_surface,
                           (int(p.x) - glow_size, int(p.y) - glow_size),
                           special_flags=pygame.BLEND_RGBA_ADD)

            pygame.draw.circle(surface, color,
                             (int(p.x), int(p.y)), max(1, int(p.size)))

        self._draw_center(surface, features)

    def _draw_center(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        pulse = features.bass * 20 + self.flash_intensity * 30
        radius = int(15 + pulse)

        glow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (150, 150, 160, 40),
                          (radius * 2, radius * 2), radius * 2)
        surface.blit(glow_surface,
                    (self.center_x - radius * 2, self.center_y - radius * 2),
                    special_flags=pygame.BLEND_RGBA_ADD)

        pygame.draw.circle(surface, (200, 200, 210),
                          (self.center_x, self.center_y), int(radius * 0.5))

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self.center_x = width // 2
        self.center_y = (height - PANEL_HEIGHT) // 2
        self.trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def reset(self) -> None:
        for p in self.particles:
            p.active = False
        self._init_ambient_particles()

    @property
    def name(self) -> str:
        return "Particles"