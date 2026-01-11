"""
Neural Style Transfer - Async ONNX-based style transfer.

Note: This module requires onnxruntime and pre-trained style models.
The style transfer runs asynchronously to avoid blocking the main render loop.
"""

import pygame
import numpy as np
import threading
import queue
from typing import Optional, Tuple
import os

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])


class StyleTransfer:
    """
    Asynchronous neural style transfer using ONNX Runtime.

    Processes frames in a background thread at reduced resolution
    to maintain real-time performance.
    """

    # Available style presets (would need actual ONNX models)
    STYLES = {
        'starry_night': 'Van Gogh Starry Night',
        'wave': 'Hokusai Great Wave',
        'mosaic': 'Mosaic Pattern',
        'candy': 'Candy Colors',
        'udnie': 'Udnie Abstract',
        'rain_princess': 'Rain Princess',
    }

    def __init__(self, width: int, height: int, model_dir: str = None):
        """
        Initialize the style transfer system.

        Args:
            width: Display width
            height: Display height
            model_dir: Directory containing ONNX models
        """
        self.display_width = width
        self.display_height = height

        # Processing resolution (lower for performance)
        self.process_width = 320
        self.process_height = 180

        # Model directory
        if model_dir is None:
            model_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'models', 'pretrained'
            )
        self.model_dir = model_dir

        # State
        self.enabled = False
        self.current_style = None
        self.session = None
        self.blend_alpha = 0.5

        # Threading
        self.running = False
        self.input_queue = queue.Queue(maxsize=1)
        self.output_queue = queue.Queue(maxsize=2)
        self.thread = None

        # Output
        self.styled_surface = None
        self.onnx_available = self._check_onnx()

    def _check_onnx(self) -> bool:
        """Check if ONNX Runtime is available."""
        try:
            import onnxruntime
            return True
        except ImportError:
            print("ONNX Runtime not available. Style transfer disabled.")
            print("Install with: pip install onnxruntime")
            return False

    def start(self, style_name: str = 'starry_night') -> bool:
        """
        Start the style transfer system.

        Args:
            style_name: Name of style to use

        Returns:
            True if started successfully
        """
        if not self.onnx_available:
            return False

        if self.running:
            self.stop()

        # Load model
        if not self._load_model(style_name):
            print(f"Could not load style model: {style_name}")
            print("Style transfer will use placeholder effect.")

        self.current_style = style_name
        self.enabled = True
        self.running = True

        # Start processing thread
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()

        return True

    def stop(self) -> None:
        """Stop the style transfer system."""
        self.running = False
        self.enabled = False

        if self.thread is not None:
            # Send stop signal
            try:
                self.input_queue.put_nowait(None)
            except queue.Full:
                pass
            self.thread.join(timeout=1.0)
            self.thread = None

        self.session = None

    def _load_model(self, style_name: str) -> bool:
        """Load an ONNX style transfer model."""
        try:
            import onnxruntime as ort

            model_path = os.path.join(self.model_dir, f"{style_name}.onnx")

            if os.path.exists(model_path):
                self.session = ort.InferenceSession(model_path)
                print(f"Loaded style model: {style_name}")
                return True
            else:
                # Model doesn't exist - will use placeholder effect
                self.session = None
                return False

        except Exception as e:
            print(f"Error loading model: {e}")
            self.session = None
            return False

    def submit_frame(self, surface: pygame.Surface) -> None:
        """
        Submit a frame for style transfer processing.

        Args:
            surface: PyGame surface to process
        """
        if not self.enabled or not self.running:
            return

        # Downscale for processing
        small = pygame.transform.smoothscale(
            surface,
            (self.process_width, self.process_height)
        )

        # Convert to array
        array = pygame.surfarray.array3d(small)
        array = np.transpose(array, (1, 0, 2))  # HWC format

        # Non-blocking put (drop frame if queue full)
        try:
            self.input_queue.put_nowait(array)
        except queue.Full:
            pass

    def get_styled_frame(self) -> Optional[pygame.Surface]:
        """
        Get the latest styled frame.

        Returns:
            Styled surface or None if not available
        """
        try:
            styled_array = self.output_queue.get_nowait()

            # Convert to surface
            styled_array = np.transpose(styled_array, (1, 0, 2))  # WxHxC for pygame
            surface = pygame.surfarray.make_surface(styled_array)

            # Upscale to display size
            self.styled_surface = pygame.transform.smoothscale(
                surface,
                (self.display_width, self.display_height)
            )

            return self.styled_surface

        except queue.Empty:
            # Return cached surface if available
            return self.styled_surface

    def _process_loop(self) -> None:
        """Background processing loop for style transfer."""
        while self.running:
            try:
                frame = self.input_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if frame is None:  # Stop signal
                break

            # Process frame
            styled = self._apply_style(frame)

            # Put result (non-blocking, replace old if full)
            try:
                self.output_queue.put_nowait(styled)
            except queue.Full:
                try:
                    self.output_queue.get_nowait()
                    self.output_queue.put_nowait(styled)
                except:
                    pass

    def _apply_style(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply style transfer to a frame.

        Args:
            frame: Input frame as HWC numpy array

        Returns:
            Styled frame
        """
        if self.session is not None:
            # Real ONNX inference
            try:
                # Preprocess
                input_tensor = self._preprocess(frame)

                # Run inference
                input_name = self.session.get_inputs()[0].name
                output = self.session.run(None, {input_name: input_tensor})[0]

                # Postprocess
                return self._postprocess(output)

            except Exception as e:
                print(f"Style transfer error: {e}")
                return self._apply_placeholder_style(frame)
        else:
            # Placeholder style effect
            return self._apply_placeholder_style(frame)

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for ONNX model."""
        # Normalize to [0, 1]
        tensor = frame.astype(np.float32) / 255.0

        # Add batch dimension and transpose to NCHW
        tensor = np.transpose(tensor, (2, 0, 1))
        tensor = np.expand_dims(tensor, 0)

        return tensor

    def _postprocess(self, output: np.ndarray) -> np.ndarray:
        """Postprocess ONNX model output."""
        # Remove batch dimension
        output = output[0]

        # Transpose from CHW to HWC
        output = np.transpose(output, (1, 2, 0))

        # Denormalize to [0, 255]
        output = np.clip(output * 255, 0, 255).astype(np.uint8)

        return output

    def _apply_placeholder_style(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply a placeholder style effect when no model is available.

        This creates a painterly/posterized effect.
        """
        # Simple posterization effect
        levels = 8
        quantized = (frame // (256 // levels)) * (256 // levels)

        # Add some color shift based on style name
        style_effects = {
            'starry_night': lambda f: self._shift_hue(f, 30),
            'wave': lambda f: self._add_blue_tint(f),
            'mosaic': lambda f: self._pixelate(f, 8),
            'candy': lambda f: self._saturate(f, 1.5),
            'udnie': lambda f: self._shift_hue(f, -20),
            'rain_princess': lambda f: self._add_cyan_tint(f),
        }

        effect = style_effects.get(self.current_style, lambda f: f)
        styled = effect(quantized)

        return styled.astype(np.uint8)

    def _shift_hue(self, frame: np.ndarray, degrees: float) -> np.ndarray:
        """Shift hue of the image."""
        # Simplified hue shift using channel rotation
        if degrees > 0:
            return np.roll(frame, 1, axis=2)
        else:
            return np.roll(frame, -1, axis=2)

    def _add_blue_tint(self, frame: np.ndarray) -> np.ndarray:
        """Add blue tint to image."""
        result = frame.copy().astype(np.float32)
        result[:, :, 2] = np.clip(result[:, :, 2] * 1.3, 0, 255)
        result[:, :, 0] = result[:, :, 0] * 0.8
        return result.astype(np.uint8)

    def _add_cyan_tint(self, frame: np.ndarray) -> np.ndarray:
        """Add cyan tint to image."""
        result = frame.copy().astype(np.float32)
        result[:, :, 1] = np.clip(result[:, :, 1] * 1.2, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 1.2, 0, 255)
        return result.astype(np.uint8)

    def _saturate(self, frame: np.ndarray, factor: float) -> np.ndarray:
        """Increase color saturation."""
        gray = np.mean(frame, axis=2, keepdims=True)
        result = gray + (frame - gray) * factor
        return np.clip(result, 0, 255).astype(np.uint8)

    def _pixelate(self, frame: np.ndarray, block_size: int) -> np.ndarray:
        """Apply pixelation effect."""
        h, w = frame.shape[:2]
        small = frame[::block_size, ::block_size]

        # Resize back using numpy
        result = np.repeat(np.repeat(small, block_size, axis=0), block_size, axis=1)
        return result[:h, :w]

    def set_style(self, style_name: str) -> bool:
        """Change the current style."""
        if style_name == self.current_style:
            return True

        if self.running:
            self.stop()
            return self.start(style_name)

        self.current_style = style_name
        return True

    def set_blend(self, alpha: float) -> None:
        """Set the blend amount for styled output."""
        self.blend_alpha = max(0.0, min(1.0, alpha))

    def on_resize(self, width: int, height: int) -> None:
        """Handle window resize."""
        self.display_width = width
        self.display_height = height
        self.styled_surface = None

    @property
    def available_styles(self) -> list:
        """Get list of available styles."""
        return list(self.STYLES.keys())

    @property
    def style_descriptions(self) -> dict:
        """Get style name to description mapping."""
        return self.STYLES.copy()
