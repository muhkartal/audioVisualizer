# Audio Visualizer

A real-time audio visualizer built with Python and PyGame featuring spectrum analysis, beat detection, and multiple visualization modes.

## Features

- **Real-time spectrum analysis** - 64-band FFT with logarithmic frequency scaling
- **Beat detection** - Spectral flux-based onset detection with tempo estimation
- **Multiple audio sources** - Microphone input and audio file playback (MP3/WAV/FLAC/OGG)
- **Piano synthesizer** - Built-in piano with keyboard input, ADSR envelope, and multiple waveforms (sine, square, saw, triangle)
- **Multiple visualization modes** - Spectrum Bars, Radial Pattern, and Waveform with smooth transitions
- **Post-processing effects** - Glow, bloom, vignette, chromatic aberration, and scanlines
- **Effect presets** - Clean, Subtle, Vibrant, Retro, and Dreamy presets
- **AI Style Transfer** - Real-time neural style transfer with multiple artistic styles (requires ONNX Runtime)
- **Smooth animations** - 60fps rendering with exponential smoothing and peak decay
- **Interactive controls** - Keyboard shortcuts for all major functions
- **Drag and drop** - Drop audio files directly onto the window

## Installation

### Option 1: Standard Installation

1. Clone the repository:
```bash
git clone https://github.com/muhkartal/audio-visualizer.git
cd audio-visualizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the visualizer:
```bash
python -m src.main
```

### Option 2: Docker Installation (Linux)

1. Build the Docker image:
```bash
docker build -t audio-visualizer .
```

2. Allow X11 access and run:
```bash
# Allow Docker to access display
xhost +local:docker

# Run with audio and display support
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -e PULSE_SERVER=unix:/run/user/1000/pulse/native \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $XDG_RUNTIME_DIR/pulse/native:/run/user/1000/pulse/native \
  -v ~/.config/pulse/cookie:/home/visualizer/.config/pulse/cookie:ro \
  --device /dev/snd \
  audio-visualizer

# Revoke X11 access after use
xhost -local:docker
```

Or use Docker Compose:
```bash
xhost +local:docker
docker-compose up --build
```

### Option 3: Install as Package

```bash
pip install -e .
audio-visualizer
```

## Usage

Run the visualizer:
```bash
python -m src.main
```

## Controls

### Audio
| Key | Action |
|-----|--------|
| **O** | Open audio file |
| **M** | Toggle microphone input |
| **Space** | Pause/Resume |
| **ESC** | Quit |

### Piano Synthesizer
| Key | Action |
|-----|--------|
| **F6** | Toggle piano mode |
| **A-L** | Play white keys (C4-D5) |
| **W, E, T, Y, U** | Play black keys (sharps) |
| **F7** | Cycle waveform (sine/square/saw/triangle) |

### Visualization
| Key | Action |
|-----|--------|
| **Tab** | Next visualization mode |
| **Shift+Tab** | Previous visualization mode |
| **1-3** | Select mode directly |

### Effects
| Key | Action |
|-----|--------|
| **G** | Toggle glow |
| **B** | Toggle bloom |
| **V** | Toggle vignette |
| **C** | Toggle chromatic aberration |
| **L** | Toggle scanlines |

### Presets
| Key | Action |
|-----|--------|
| **F1** | Clean (no effects) |
| **F2** | Subtle |
| **F3** | Vibrant |
| **F4** | Retro |
| **F5** | Dreamy |

### Style Transfer
| Key | Action |
|-----|--------|
| **Ctrl+S** | Toggle style transfer |
| **[** | Previous style |
| **]** | Next style |

### Other
| Key | Action |
|-----|--------|
| **H** | Toggle help overlay |
| **D** | Toggle debug info |

You can also drag and drop audio files onto the window.

## Project Structure

```
audio-visualizer/
├── config/
│   └── settings.py              # Configuration constants
├── src/
│   ├── main.py                  # Application entry point
│   ├── audio/
│   │   ├── audio_buffer.py      # Thread-safe ring buffer
│   │   ├── audio_source.py      # Abstract base class
│   │   ├── microphone_input.py  # Live mic capture
│   │   ├── file_player.py       # Audio file playback
│   │   └── audio_manager.py     # Source switching
│   ├── analysis/
│   │   ├── fft_analyzer.py      # FFT spectral analysis
│   │   ├── beat_detector.py     # Beat/onset detection
│   │   └── audio_features.py    # Feature data class
│   ├── visualization/
│   │   ├── renderer.py          # PyGame main loop
│   │   ├── base_visualizer.py   # Abstract visualizer base
│   │   ├── visualizer_manager.py # Mode switching & transitions
│   │   ├── spectrum_bars.py     # Frequency bars visualizer
│   │   ├── radial_pattern.py    # Circular visualizer
│   │   ├── waveform.py          # Waveform visualizer
│   │   ├── particle_system.py   # Particle effects
│   │   └── note_visualizer.py   # Piano keyboard display
│   ├── effects/
│   │   ├── post_processing.py   # Glow, bloom, vignette, etc.
│   │   ├── style_transfer.py    # AI neural style transfer
│   │   └── color_mapper.py      # Color utilities
│   ├── synthesizer/
│   │   ├── synthesizer.py       # Main synth engine
│   │   ├── oscillator.py        # Waveform generation
│   │   ├── envelope.py          # ADSR envelope
│   │   ├── note.py              # Note data structure
│   │   └── keyboard_mapping.py  # Key-to-note mapping
│   └── ui/
│       ├── control_panel.py     # UI overlay
│       └── file_browser.py      # File selection dialog
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker Compose config
├── pyproject.toml               # Project metadata & tools config
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
└── CONTRIBUTING.md              # Contribution guidelines
```

## Technical Details

### Audio Processing
- Sample rate: 44100 Hz
- FFT size: 4096 samples
- Chunk size: 2048 samples (~46ms latency)
- 64 logarithmic frequency bands (20Hz - 20kHz)

### Beat Detection
- Spectral flux onset detection
- Adaptive threshold with local mean normalization
- Minimum inter-onset interval: 100ms
- Real-time tempo estimation via autocorrelation

### Visualization
- 60fps target with double buffering
- Exponential smoothing (factor: 0.85)
- Peak hold with gradual decay
- Beat-reactive flash effects
- Bass/Mid/Treble energy meters
- Smooth crossfade transitions between modes

### Piano Synthesizer
- Polyphonic synthesis (up to 8 voices)
- ADSR envelope (Attack/Decay/Sustain/Release)
- Multiple waveforms: sine, square, sawtooth, triangle
- Real-time keyboard input mapping
- Low-latency audio output

### Post-Processing Effects
- **Glow**: Soft light bloom based on audio energy
- **Bloom**: Beat-reactive flash on transients
- **Vignette**: Dynamic edge darkening
- **Chromatic aberration**: Bass-reactive color fringing
- **Scanlines**: Retro CRT effect

### Style Transfer
- Real-time neural style transfer using ONNX Runtime
- Available styles: Starry Night, Great Wave, Mosaic, Candy, Udnie, Rain Princess
- Asynchronous processing to maintain frame rate

## Requirements

- Python 3.8+
- sounddevice
- librosa
- numpy
- scipy
- pygame

### Optional Dependencies

```bash
# For AI style transfer
pip install onnxruntime
```

## Development

### Setup

```bash
# Clone and install
git clone https://github.com/muhkartal/audio-visualizer.git
cd audio-visualizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Code Quality

```bash
# Format code
black src/ config/
isort src/ config/

# Lint
flake8 src/ config/

# Type check
mypy src/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## License

MIT License

## Author

Muhammad Ibrahim Kartal - [@muhkartal](https://github.com/muhkartal)
