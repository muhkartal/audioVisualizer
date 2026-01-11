"""
Audio Visualizer Configuration Settings
"""

# =============================================================================
# Audio Settings
# =============================================================================

# Sample rate in Hz (standard audio rate)
SAMPLE_RATE = 44100

# Number of samples per audio chunk (~46ms of audio at 44100Hz)
CHUNK_SIZE = 2048

# FFT size (zero-padded for smoother spectrum)
FFT_SIZE = 4096

# Audio buffer size (number of chunks to keep in ring buffer)
BUFFER_SIZE = 4

# =============================================================================
# FFT Analysis Settings
# =============================================================================

# Number of frequency bands for visualization
NUM_BANDS = 64

# Frequency range for analysis (Hz)
FREQ_MIN = 20
FREQ_MAX = 20000

# Exponential smoothing factor (higher = slower decay, 0-1)
# Lower value = more responsive to mic input
SMOOTHING_FACTOR = 0.6

# Peak hold decay rate (how fast peaks fall)
PEAK_DECAY = 0.03

# dB range for normalization (wider range = more sensitive to quiet sounds)
DB_RANGE_MIN = -80  # Minimum dB (quiet sounds)
DB_RANGE_MAX = 0    # Maximum dB (loud sounds)

# Microphone gain boost (multiplier applied to mic input)
MIC_GAIN = 3.0

# =============================================================================
# Beat Detection Settings
# =============================================================================

# Minimum time between detected beats (seconds)
MIN_BEAT_INTERVAL = 0.1

# Beat detection sensitivity (lower = more sensitive)
BEAT_THRESHOLD = 1.5

# Energy history length for beat detection (number of frames)
BEAT_HISTORY_LENGTH = 43  # ~1 second at 60fps

# =============================================================================
# Display Settings
# =============================================================================

# Window dimensions
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Target frames per second
TARGET_FPS = 60

# Window title
WINDOW_TITLE = "Audio Visualizer"

# Background color (RGB) - dark gray
BG_COLOR = (15, 15, 18)

# =============================================================================
# Visualization Settings
# =============================================================================

# Spectrum bars - gray/white theme
BAR_COLOR_LOW = (100, 100, 110)     # Dark gray for low amplitude
BAR_COLOR_HIGH = (220, 220, 230)    # Light gray/white for high amplitude
BAR_SPACING = 2                     # Pixels between bars
BAR_MIN_HEIGHT = 2                  # Minimum bar height
BAR_BORDER_RADIUS = 3               # Rounded corner radius

# Beat flash effect
BEAT_FLASH_INTENSITY = 0.4          # How much to brighten on beat (0-1)
BEAT_FLASH_DECAY = 0.85             # How fast flash fades (0-1)

# Radial pattern settings
RADIAL_RINGS = 5                    # Number of concentric rings
RADIAL_SEGMENTS = 64                # Segments per ring
RADIAL_BASE_RADIUS = 100            # Inner radius
RADIAL_RING_SPACING = 40            # Space between rings

# Particle system settings
PARTICLE_COUNT = 200                # Maximum particles
PARTICLE_LIFETIME = 3.0             # Seconds
PARTICLE_SPAWN_RATE = 10            # Particles per beat
PARTICLE_GRAVITY = 50               # Downward acceleration

# Mode transition settings
TRANSITION_SPEED = 3.0              # Transitions per second

# =============================================================================
# Post-Processing Settings
# =============================================================================

# Default post-processing preset ('clean', 'subtle', 'vibrant', 'retro', 'dreamy')
DEFAULT_POST_PRESET = 'subtle'

# Glow effect
GLOW_ENABLED = True
GLOW_INTENSITY = 0.5
GLOW_RADIUS = 2

# Bloom effect
BLOOM_ENABLED = True
BLOOM_THRESHOLD = 0.7
BLOOM_INTENSITY = 0.3

# Motion blur
MOTION_BLUR_ENABLED = False
MOTION_BLUR_AMOUNT = 0.3

# Vignette effect
VIGNETTE_ENABLED = True
VIGNETTE_INTENSITY = 0.4

# Chromatic aberration
CHROMATIC_ENABLED = False
CHROMATIC_OFFSET = 3

# Scanlines
SCANLINES_ENABLED = False
SCANLINE_INTENSITY = 0.1

# =============================================================================
# Style Transfer Settings
# =============================================================================

# Style transfer processing resolution (lower = faster)
STYLE_PROCESS_WIDTH = 320
STYLE_PROCESS_HEIGHT = 180

# Blend amount for style transfer (0-1)
STYLE_BLEND_ALPHA = 0.5

# Available styles (require ONNX models in models/pretrained/)
STYLE_PRESETS = [
    'starry_night',
    'wave',
    'mosaic',
    'candy',
    'udnie',
    'rain_princess',
]

# =============================================================================
# Color Palettes
# =============================================================================

# Named color palettes for visualizations
COLOR_PALETTES = {
    'monochrome': [
        (255, 255, 255),  # White
        (200, 200, 205),  # Light gray
        (150, 150, 158),  # Mid gray
        (100, 100, 110),  # Dark gray
        (60, 60, 68),     # Darker gray
    ],
    'silver': [
        (240, 240, 245),  # Near white
        (192, 192, 200),  # Silver
        (160, 160, 170),  # Gray
        (128, 128, 140),  # Medium gray
        (80, 80, 92),     # Charcoal
    ],
    'cool_gray': [
        (220, 225, 235),  # Cool white
        (180, 190, 205),  # Cool light gray
        (140, 150, 168),  # Cool gray
        (100, 110, 130),  # Cool dark gray
        (60, 70, 85),     # Cool charcoal
    ],
    'warm_gray': [
        (235, 230, 225),  # Warm white
        (200, 195, 188),  # Warm light gray
        (165, 158, 150),  # Warm gray
        (125, 118, 110),  # Warm dark gray
        (85, 78, 70),     # Warm charcoal
    ],
    'minimal': [
        (255, 255, 255),  # Pure white
        (220, 220, 220),  # Off white
        (180, 180, 180),  # Light gray
        (140, 140, 140),  # Mid gray
        (100, 100, 100),  # Dark gray
    ],
}

# Default palette
DEFAULT_PALETTE = 'monochrome'

# =============================================================================
# UI Settings
# =============================================================================

# Control panel
PANEL_HEIGHT = 40
PANEL_BG_COLOR = (20, 20, 25, 200)  # RGBA
PANEL_TEXT_COLOR = (200, 200, 200)
FONT_SIZE = 16

# =============================================================================
# File Types
# =============================================================================

SUPPORTED_AUDIO_FORMATS = [
    ('Audio Files', '*.mp3 *.wav *.flac *.ogg *.m4a'),
    ('MP3 Files', '*.mp3'),
    ('WAV Files', '*.wav'),
    ('All Files', '*.*')
]
