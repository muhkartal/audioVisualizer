"""
File browser dialog using tkinter.
"""

import os
from typing import Optional

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 3)[0])
from config.settings import SUPPORTED_AUDIO_FORMATS


class FileBrowser:
    """
    Simple file browser dialog using tkinter.

    Opens a native file dialog for selecting audio files.
    """

    @staticmethod
    def open_file(initial_dir: str = None) -> Optional[str]:
        """
        Open a file selection dialog.

        Args:
            initial_dir: Initial directory to open (None for user's home)

        Returns:
            Selected file path, or None if cancelled
        """
        try:
            # Import tkinter (hide root window)
            import tkinter as tk
            from tkinter import filedialog

            # Create hidden root window
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)

            # Set initial directory
            if initial_dir is None:
                initial_dir = os.path.expanduser("~")

            # Convert format list for tkinter
            filetypes = [
                ("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a"),
                ("MP3 Files", "*.mp3"),
                ("WAV Files", "*.wav"),
                ("FLAC Files", "*.flac"),
                ("OGG Files", "*.ogg"),
                ("All Files", "*.*")
            ]

            # Open dialog
            filepath = filedialog.askopenfilename(
                title="Select Audio File",
                initialdir=initial_dir,
                filetypes=filetypes
            )

            # Clean up
            root.destroy()

            return filepath if filepath else None

        except ImportError:
            print("tkinter not available for file dialog")
            return None
        except Exception as e:
            print(f"Error opening file dialog: {e}")
            return None

    @staticmethod
    def open_folder(initial_dir: str = None) -> Optional[str]:
        """
        Open a folder selection dialog.

        Args:
            initial_dir: Initial directory to open

        Returns:
            Selected folder path, or None if cancelled
        """
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)

            if initial_dir is None:
                initial_dir = os.path.expanduser("~")

            folder = filedialog.askdirectory(
                title="Select Folder",
                initialdir=initial_dir
            )

            root.destroy()

            return folder if folder else None

        except ImportError:
            print("tkinter not available for folder dialog")
            return None
        except Exception as e:
            print(f"Error opening folder dialog: {e}")
            return None

    @staticmethod
    def is_supported_audio(filepath: str) -> bool:
        """
        Check if a file is a supported audio format.

        Args:
            filepath: Path to check

        Returns:
            True if supported audio format
        """
        if not filepath:
            return False

        ext = os.path.splitext(filepath)[1].lower()
        supported = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']
        return ext in supported
