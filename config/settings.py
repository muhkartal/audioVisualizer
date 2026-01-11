SAMPLE_RATE = 44100
CHUNK_SIZE = 2048
FFT_SIZE = 4096
BUFFER_SIZE = 4
NUM_BANDS = 64
FREQ_MIN = 20
FREQ_MAX = 20000
SMOOTHING_FACTOR = 0.6
PEAK_DECAY = 0.03
DB_RANGE_MIN = -80
DB_RANGE_MAX = 0
MIC_GAIN = 3.0
MIN_BEAT_INTERVAL = 0.1
BEAT_THRESHOLD = 1.5
BEAT_HISTORY_LENGTH = 43
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TARGET_FPS = 60
WINDOW_TITLE = "Audio Visualizer"
BG_COLOR = (15, 15, 18)
BAR_COLOR_LOW = (100, 100, 110)
BAR_COLOR_HIGH = (220, 220, 230)
BAR_SPACING = 2
BAR_MIN_HEIGHT = 2
BAR_BORDER_RADIUS = 3
BEAT_FLASH_INTENSITY = 0.4
BEAT_FLASH_DECAY = 0.85
RADIAL_RINGS = 5
RADIAL_SEGMENTS = 64
RADIAL_BASE_RADIUS = 100
RADIAL_RING_SPACING = 40
PARTICLE_COUNT = 200
PARTICLE_LIFETIME = 3.0
PARTICLE_SPAWN_RATE = 10
PARTICLE_GRAVITY = 50
TRANSITION_SPEED = 3.0
DEFAULT_POST_PRESET = 'subtle'
GLOW_ENABLED = True
GLOW_INTENSITY = 0.5
GLOW_RADIUS = 2
BLOOM_ENABLED = True
BLOOM_THRESHOLD = 0.7
BLOOM_INTENSITY = 0.3
MOTION_BLUR_ENABLED = False
MOTION_BLUR_AMOUNT = 0.3
VIGNETTE_ENABLED = True
VIGNETTE_INTENSITY = 0.4
CHROMATIC_ENABLED = False
CHROMATIC_OFFSET = 3
SCANLINES_ENABLED = False
SCANLINE_INTENSITY = 0.1
STYLE_PROCESS_WIDTH = 320
STYLE_PROCESS_HEIGHT = 180
STYLE_BLEND_ALPHA = 0.5
STYLE_PRESETS = [
    'starry_night',
    'wave',
    'mosaic',
    'candy',
    'udnie',
    'rain_princess',
]
COLOR_PALETTES = {
    'monochrome': [
        (255, 255, 255),
        (200, 200, 205),
        (150, 150, 158),
        (100, 100, 110),
        (60, 60, 68),
    ],
    'silver': [
        (240, 240, 245),
        (192, 192, 200),
        (160, 160, 170),
        (128, 128, 140),
        (80, 80, 92),
    ],
    'cool_gray': [
        (220, 225, 235),
        (180, 190, 205),
        (140, 150, 168),
        (100, 110, 130),
        (60, 70, 85),
    ],
    'warm_gray': [
        (235, 230, 225),
        (200, 195, 188),
        (165, 158, 150),
        (125, 118, 110),
        (85, 78, 70),
    ],
    'minimal': [
        (255, 255, 255),
        (220, 220, 220),
        (180, 180, 180),
        (140, 140, 140),
        (100, 100, 100),
    ],
}
DEFAULT_PALETTE = 'monochrome'
PANEL_HEIGHT = 40
PANEL_BG_COLOR = (20, 20, 25, 200)
PANEL_TEXT_COLOR = (200, 200, 200)
FONT_SIZE = 16
SUPPORTED_AUDIO_FORMATS = [
    ('Audio Files', '*.mp3 *.wav *.flac *.ogg *.m4a'),
    ('MP3 Files', '*.mp3'),
    ('WAV Files', '*.wav'),
    ('All Files', '*.*')
]