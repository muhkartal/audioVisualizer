# Contributing to Audio Visualizer

Thank you for your interest in contributing to Audio Visualizer! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A working audio input device (microphone) for testing

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/muhkartal/audio-visualizer.git
   cd audio-visualizer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Run the application**
   ```bash
   python -m src.main
   ```

## Development Workflow

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Formatting

We use `black` for code formatting and `isort` for import sorting:

```bash
# Format code
black src/ config/

# Sort imports
isort src/ config/
```

### Linting

Run `flake8` to check for code issues:

```bash
flake8 src/ config/
```

### Type Checking

Run `mypy` for static type analysis:

```bash
mypy src/
```

## Making Changes

### Branch Naming

- `feature/` - New features (e.g., `feature/add-waveform-visualizer`)
- `fix/` - Bug fixes (e.g., `fix/audio-buffer-overflow`)
- `docs/` - Documentation updates (e.g., `docs/update-readme`)
- `refactor/` - Code refactoring (e.g., `refactor/improve-fft-performance`)

### Commit Messages

Write clear, concise commit messages:

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line should be 50 characters or less
- Reference issues when applicable

**Examples:**
```
Add particle system visualization mode

Fix audio buffer overflow on high sample rates

Update README with Docker instructions
```

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and ensure:
   - Code passes linting (`flake8`)
   - Code is formatted (`black`, `isort`)
   - Type hints are added for new code
   - Documentation is updated if needed

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request** with:
   - Clear description of changes
   - Screenshots/GIFs for visual changes
   - Reference to related issues

## Project Structure

```
audio-visualizer/
├── config/
│   └── settings.py          # Configuration constants
├── src/
│   ├── main.py              # Application entry point
│   ├── audio/               # Audio input/output
│   │   ├── audio_source.py  # Abstract base class
│   │   ├── microphone_input.py
│   │   └── file_player.py
│   ├── analysis/            # Audio analysis
│   │   ├── fft_analyzer.py  # Spectrum analysis
│   │   ├── beat_detector.py # Beat detection
│   │   └── audio_features.py
│   ├── visualization/       # Visualizers
│   │   ├── renderer.py      # Main renderer
│   │   ├── spectrum_bars.py
│   │   ├── radial_pattern.py
│   │   └── particle_system.py
│   ├── effects/             # Post-processing
│   │   ├── post_processing.py
│   │   └── style_transfer.py
│   ├── synthesizer/         # Piano synthesizer
│   │   ├── synthesizer.py
│   │   ├── oscillator.py
│   │   └── envelope.py
│   └── ui/                  # User interface
│       ├── control_panel.py
│       └── file_browser.py
├── tests/                   # Unit tests (TODO)
├── Dockerfile
├── requirements.txt
└── pyproject.toml
```

## Adding New Features

### Adding a New Visualizer

1. Create a new file in `src/visualization/`
2. Inherit from `BaseVisualizer`
3. Implement `update()` and `draw()` methods
4. Register in `VisualizerManager`

```python
from src.visualization.base_visualizer import BaseVisualizer

class MyVisualizer(BaseVisualizer):
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        # Initialize your visualizer

    def update(self, features: AudioFeatures) -> None:
        # Update state based on audio features
        pass

    def draw(self, surface: pygame.Surface, features: AudioFeatures) -> None:
        # Draw visualization
        pass
```

### Adding a New Effect

1. Add effect toggle in `PostProcessor`
2. Implement effect in `apply()` method
3. Add keyboard shortcut in `Renderer._handle_renderer_key()`

## Reporting Issues

When reporting bugs, please include:

- Python version (`python --version`)
- Operating system and version
- Audio device information
- Steps to reproduce
- Expected vs actual behavior
- Error messages/tracebacks

## Questions?

Feel free to open an issue for questions or discussions about the project.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
