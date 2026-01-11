"""
Particle System Visualizer - Beat-reactive particle effects.
"""

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
    """Individual particle with physics properties."""
    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    ax: float = 0.0  # acceleration
    ay: float = 0.0
    lifetime: float = 0.0
    max_lifetime: float = 2.0
    size: float = 3.0
    initial_size: float = 3.0
    gray_value: float = 200.0  # Grayscale value (0-255)
    brightness: float = 100.0
    active: bool = False
    trail: bool = False


class ParticleSystem(BaseVisualizer):
    """
    Beat-reactive particle system visualization.

    Emits particles from the center on beat detection,
    with properties driven by audio features.
    """

    def __init__(self, width: int, height: int, max_particles: int = 1000):
        """
        Initialize the particle system.

        Args:
            width: Display width
            height: Display height
            max_particles: Maximum number of particles in pool
        """
        super().__init__(width, height)

        self.max_particles = max_particles
        self.center_x = width // 2
        self.center_y = (height - PANEL_HEIGHT) // 2

        # Particle pool (pre-allocated)
        self.particles: List[Particle] = [Particle() for _ in range(max_particles)]
        self.active_count = 0

        # Emission settings
        self.emit_rate = 20  # Particles per beat
        self.gravity = 50.0  # Downward acceleration
        self.drag = 0.98  # Velocity damping

        # Visual settings
        self.flash_intensity = 0.0

        # Background particles (always moving)
        self.ambient_particles: List[Particle] = [Particle() for _ in range(50)]
        self._init_ambient_particles()

        # Trail surface for motion blur effect
        self.trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def _init_ambient_particles(self) -> None:
        """Initialize ambient background particles."""
        for p in self.ambient_particles:
            p.x = np.random.uniform(0, self.width)
            p.y = np.random.uniform(0, self.height - PANEL_HEIGHT)
            p.vx = np.random.uniform(-20, 20)
            p.vy = np.random.uniform(-20, 20)
            p.size = np.random.uniform(1, 3)
            p.initial_size = p.size
            p.gray_value = np.random.uniform(60, 120)  # Dark gray ambient
            p.brightness = np.random.uniform(30, 60)
            p.active = True
            p.max_lifetime = float('inf')

    def _get_inactive_particle(self) -> Particle:
        """Get an inactive particle from the pool."""
        for p in self.particles:
            if not p.active:
                return p
        return None

    def emit(self, count: int, energy: float, spectral_centroid: float,
             bass: float) -> None:
        """
        Emit particles from center.

        Args:
            count: Number of particles to emit
            energy: Overall audio energy
            spectral_centroid: Brightness of sound (0-1)
            bass: Bass energy level
        """
        for _ in range(count):
            particle = self._get_inactive_particle()
            if particle is None:
                break

            # Random angle
            angle = np.random.uniform(0, 2 * np.pi)

            # Speed based on energy
            speed = energy * np.random.uniform(100, 400) + bass * 200

            # Initialize particle
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

            # Grayscale color - brighter with higher spectral centroid
            base_gray = 140 + spectral_centroid * 80  # Range 140-220
            particle.gray_value = base_gray + np.random.uniform(-20, 40)
            particle.gray_value = min(255, max(100, particle.gray_value))
            particle.brightness = 80 + np.random.uniform(0, 20)

            particle.active = True
            particle.trail = np.random.random() < 0.3  # 30% chance of trail

    def update(self, features: AudioFeatures) -> None:
        """Update particle system."""
        dt = 1.0 / 60.0  # Assume 60fps

        # Emit on beat
        if features.is_beat:
            emit_count = int(self.emit_rate * (1 + features.beat_strength))
            self.emit(emit_count, features.energy, features.spectral_centroid,
                     features.bass)
            self.flash_intensity = BEAT_FLASH_INTENSITY

        self.flash_intensity *= 0.9

        # Update main particles
        for p in self.particles:
            if not p.active:
                continue

            # Apply acceleration
            p.vx += p.ax * dt
            p.vy += p.ay * dt

            # Apply drag
            p.vx *= self.drag
            p.vy *= self.drag

            # Update position
            p.x += p.vx * dt
            p.y += p.vy * dt

            # Update lifetime
            p.lifetime += dt

            # Fade size over lifetime
            life_ratio = 1.0 - (p.lifetime / p.max_lifetime)
            p.size = p.initial_size * life_ratio

            # Deactivate dead particles
            if p.lifetime >= p.max_lifetime or p.size < 0.5:
                p.active = False
            elif p.y > self.height - PANEL_HEIGHT + 50:  # Below screen
                p.active = False

        # Update ambient particles
        self._update_ambient_particles(dt, features)

    def _update_ambient_particles(self, dt: float, features: AudioFeatures) -> None:
        """Update ambient background particles."""
        for p in self.ambient_particles:
            # Gentle movement influenced by audio
            p.vx += (np.random.uniform(-1, 1) + features.mid * 5) * dt * 60
            p.vy += (np.random.uniform(-1, 1) + features.treble * 3) * dt * 60

            # Damping
            p.vx *= 0.99
            p.vy *= 0.99

            # Update position
            p.x += p.vx * dt
            p.y += p.vy * dt

            # Wrap around screen
            if p.x < 0:
                p.x = self.width
            elif p.x > self.width:
                p.x = 0
            if p.y < 0:
                p.y = self.height - PANEL_HEIGHT
            elif p.y > self.height - PANEL_HEIGHT:
                p.y = 0

            # Size pulse with bass
            p.size = p.initial_size * (1 + features.bass * 0.5)

    def draw(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        """Draw the particle system."""
        # Fade trail surface
        self.trail_surface.fill((0, 0, 0, 20))

        # Draw ambient particles (dark gray)
        for p in self.ambient_particles:
            gray = int(p.gray_value)
            pygame.draw.circle(surface, (gray, gray, gray + 5),
                             (int(p.x), int(p.y)), max(1, int(p.size)))

        # Draw main particles
        for p in self.particles:
            if not p.active:
                continue

            # Calculate alpha based on lifetime
            life_ratio = 1.0 - (p.lifetime / p.max_lifetime)

            # Get grayscale color with flash boost
            flash_boost = self.flash_intensity * 50
            gray = int(min(255, p.gray_value + flash_boost))
            color = (gray, gray, min(255, gray + 8))  # Slight blue tint

            # Draw glow for larger particles
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

            # Draw particle
            pygame.draw.circle(surface, color,
                             (int(p.x), int(p.y)), max(1, int(p.size)))

        # Draw center indicator
        self._draw_center(surface, features)

    def _draw_center(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        """Draw center emission point."""
        pulse = features.bass * 20 + self.flash_intensity * 30
        radius = int(15 + pulse)

        # Glow - gray
        glow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (150, 150, 160, 40),
                          (radius * 2, radius * 2), radius * 2)
        surface.blit(glow_surface,
                    (self.center_x - radius * 2, self.center_y - radius * 2),
                    special_flags=pygame.BLEND_RGBA_ADD)

        # Core - light gray
        pygame.draw.circle(surface, (200, 200, 210),
                          (self.center_x, self.center_y), int(radius * 0.5))

    def on_resize(self, width: int, height: int) -> None:
        """Handle window resize."""
        super().on_resize(width, height)
        self.center_x = width // 2
        self.center_y = (height - PANEL_HEIGHT) // 2
        self.trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def reset(self) -> None:
        """Reset all particles."""
        for p in self.particles:
            p.active = False
        self._init_ambient_particles()

    @property
    def name(self) -> str:
        return "Particles"
