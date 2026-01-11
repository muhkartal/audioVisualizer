# Audio Visualizer

A real-time audio visualizer built with Python and PyGame featuring spectrum analysis, beat detection, and multiple visualization modes.

## Features

- **Real-time spectrum analysis** - 64-band FFT with logarithmic frequency scaling
- **Beat detection** - Spectral flux-based onset detection with tempo estimation
- **Multiple audio sources** - Microphone input and audio file playback (MP3/WAV/FLAC/OGG)
- **Smooth animations** - 60fps rendering with exponential smoothing and peak decay
- **Interactive controls** - Keyboard shortcuts for all major functions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/muhkartal/audio-visualizer.git
cd audio-visualizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the visualizer:
```bash
python -m src.main
```

Or:
```bash
python src/main.py
```

## Controls

| Key | Action |
|-----|--------|
| **O** | Open audio file |
| **M** | Toggle microphone input |
| **Space** | Pause/Resume |
| **ESC** | Quit |

You can also drag and drop audio files onto the window.

## Project Structure

```
audio-visualizer/
├── config/
│   └── settings.py          # Configuration constants
├── src/
│   ├── main.py              # Application entry point
│   ├── audio/
│   │   ├── audio_buffer.py  # Thread-safe ring buffer
│   │   ├── audio_source.py  # Abstract base class
│   │   ├── microphone_input.py  # Live mic capture
│   │   ├── file_player.py   # Audio file playback
│   │   └── audio_manager.py # Source switching
│   ├── analysis/
│   │   ├── fft_analyzer.py  # FFT spectral analysis
│   │   ├── beat_detector.py # Beat/onset detection
│   │   └── audio_features.py # Feature data class
│   ├── visualization/
│   │   ├── renderer.py      # PyGame main loop
│   │   └── spectrum_bars.py # Frequency bars visualizer
│   └── ui/
│       ├── control_panel.py # UI overlay
│       └── file_browser.py  # File selection dialog
└── requirements.txt
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

## Requirements

- Python 3.8+
- sounddevice
- librosa
- numpy
- scipy
- pygame

## License

MIT License

## Author

Muhammad Ibrahim Kartal - [@muhkartal](https://github.com/muhkartal)
