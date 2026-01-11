import pygame
import numpy as np
import threading
import queue
from typing import Optional, Tuple
import os

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])


class StyleTransfer:
    STYLES = {
        'starry_night': 'Van Gogh Starry Night',
        'wave': 'Hokusai Great Wave',
        'mosaic': 'Mosaic Pattern',
        'candy': 'Candy Colors',
        'udnie': 'Udnie Abstract',
        'rain_princess': 'Rain Princess',
    }

    def __init__(self, width: int, height: int, model_dir: str = None):
        self.display_width = width
        self.display_height = height

        self.process_width = 320
        self.process_height = 180

        if model_dir is None:
            model_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'models', 'pretrained'
            )
        self.model_dir = model_dir

        self.enabled = False
        self.current_style = None
        self.session = None
        self.blend_alpha = 0.5

        self.running = False
        self.input_queue = queue.Queue(maxsize=1)
        self.output_queue = queue.Queue(maxsize=2)
        self.thread = None

        self.styled_surface = None
        self.onnx_available = self._check_onnx()

    def _check_onnx(self) -> bool:
        try:
            import onnxruntime
            return True
        except ImportError:
            print("ONNX Runtime not available. Style transfer disabled.")
            print("Install with: pip install onnxruntime")
            return False

    def start(self, style_name: str = 'starry_night') -> bool:
        if not self.onnx_available:
            return False

        if self.running:
            self.stop()

        if not self._load_model(style_name):
            print(f"Could not load style model: {style_name}")
            print("Style transfer will use placeholder effect.")

        self.current_style = style_name
        self.enabled = True
        self.running = True

        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()

        return True

    def stop(self) -> None:
        self.running = False
        self.enabled = False

        if self.thread is not None:
            try:
                self.input_queue.put_nowait(None)
            except queue.Full:
                pass
            self.thread.join(timeout=1.0)
            self.thread = None

        self.session = None

    def _load_model(self, style_name: str) -> bool:
        try:
            import onnxruntime as ort

            model_path = os.path.join(self.model_dir, f"{style_name}.onnx")

            if os.path.exists(model_path):
                self.session = ort.InferenceSession(model_path)
                print(f"Loaded style model: {style_name}")
                return True
            else:
                self.session = None
                return False

        except Exception as e:
            print(f"Error loading model: {e}")
            self.session = None
            return False

    def submit_frame(self, surface: pygame.Surface) -> None:
        if not self.enabled or not self.running:
            return

        small = pygame.transform.smoothscale(
            surface,
            (self.process_width, self.process_height)
        )

        array = pygame.surfarray.array3d(small)
        array = np.transpose(array, (1, 0, 2))

        try:
            self.input_queue.put_nowait(array)
        except queue.Full:
            pass

    def get_styled_frame(self) -> Optional[pygame.Surface]:
        try:
            styled_array = self.output_queue.get_nowait()

            styled_array = np.transpose(styled_array, (1, 0, 2))
            surface = pygame.surfarray.make_surface(styled_array)

            self.styled_surface = pygame.transform.smoothscale(
                surface,
                (self.display_width, self.display_height)
            )

            return self.styled_surface

        except queue.Empty:
            return self.styled_surface

    def _process_loop(self) -> None:
        while self.running:
            try:
                frame = self.input_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if frame is None:
                break

            styled = self._apply_style(frame)

            try:
                self.output_queue.put_nowait(styled)
            except queue.Full:
                try:
                    self.output_queue.get_nowait()
                    self.output_queue.put_nowait(styled)
                except:
                    pass

    def _apply_style(self, frame: np.ndarray) -> np.ndarray:
        if self.session is not None:
            try:
                input_tensor = self._preprocess(frame)

                input_name = self.session.get_inputs()[0].name
                output = self.session.run(None, {input_name: input_tensor})[0]

                return self._postprocess(output)

            except Exception as e:
                print(f"Style transfer error: {e}")
                return self._apply_placeholder_style(frame)
        else:
            return self._apply_placeholder_style(frame)

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        tensor = frame.astype(np.float32) / 255.0

        tensor = np.transpose(tensor, (2, 0, 1))
        tensor = np.expand_dims(tensor, 0)

        return tensor

    def _postprocess(self, output: np.ndarray) -> np.ndarray:
        output = output[0]

        output = np.transpose(output, (1, 2, 0))

        output = np.clip(output * 255, 0, 255).astype(np.uint8)

        return output

    def _apply_placeholder_style(self, frame: np.ndarray) -> np.ndarray:
        levels = 8
        quantized = (frame // (256 // levels)) * (256 // levels)

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
        if degrees > 0:
            return np.roll(frame, 1, axis=2)
        else:
            return np.roll(frame, -1, axis=2)

    def _add_blue_tint(self, frame: np.ndarray) -> np.ndarray:
        result = frame.copy().astype(np.float32)
        result[:, :, 2] = np.clip(result[:, :, 2] * 1.3, 0, 255)
        result[:, :, 0] = result[:, :, 0] * 0.8
        return result.astype(np.uint8)

    def _add_cyan_tint(self, frame: np.ndarray) -> np.ndarray:
        result = frame.copy().astype(np.float32)
        result[:, :, 1] = np.clip(result[:, :, 1] * 1.2, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 1.2, 0, 255)
        return result.astype(np.uint8)

    def _saturate(self, frame: np.ndarray, factor: float) -> np.ndarray:
        gray = np.mean(frame, axis=2, keepdims=True)
        result = gray + (frame - gray) * factor
        return np.clip(result, 0, 255).astype(np.uint8)

    def _pixelate(self, frame: np.ndarray, block_size: int) -> np.ndarray:
        h, w = frame.shape[:2]
        small = frame[::block_size, ::block_size]

        result = np.repeat(np.repeat(small, block_size, axis=0), block_size, axis=1)
        return result[:h, :w]

    def set_style(self, style_name: str) -> bool:
        if style_name == self.current_style:
            return True

        if self.running:
            self.stop()
            return self.start(style_name)

        self.current_style = style_name
        return True

    def set_blend(self, alpha: float) -> None:
        self.blend_alpha = max(0.0, min(1.0, alpha))

    def on_resize(self, width: int, height: int) -> None:
        self.display_width = width
        self.display_height = height
        self.styled_surface = None

    @property
    def available_styles(self) -> list:
        return list(self.STYLES.keys())

    @property
    def style_descriptions(self) -> dict:
        return self.STYLES.copy()