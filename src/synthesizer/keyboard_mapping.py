import pygame

KEYBOARD_MAP = {
    pygame.K_a: 60,   # C4 (Middle C)
    pygame.K_w: 61,   # C#4
    pygame.K_s: 62,   # D4
    pygame.K_e: 63,   # D#4
    pygame.K_d: 64,   # E4
    pygame.K_f: 65,   # F4
    pygame.K_t: 66,   # F#4
    pygame.K_g: 67,   # G4
    pygame.K_y: 68,   # G#4
    pygame.K_h: 69,   # A4
    pygame.K_u: 70,   # A#4
    pygame.K_j: 71,   # B4
    pygame.K_k: 72,   # C5
    pygame.K_o: None, # Reserved for file open
    pygame.K_l: 74,   # D5
    pygame.K_p: 75,   # D#5
    pygame.K_SEMICOLON: 76,  # E5
}

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

NOTE_COLORS = {
    0: (255, 80, 80),    # C  - Red
    1: (255, 120, 60),   # C# - Red-Orange
    2: (255, 180, 40),   # D  - Orange
    3: (255, 220, 0),    # D# - Yellow-Orange
    4: (220, 255, 0),    # E  - Yellow
    5: (100, 255, 80),   # F  - Yellow-Green
    6: (0, 255, 150),    # F# - Green
    7: (0, 220, 255),    # G  - Cyan
    8: (0, 150, 255),    # G# - Light Blue
    9: (80, 80, 255),    # A  - Blue
    10: (180, 60, 255),  # A# - Purple
    11: (255, 60, 200),  # B  - Magenta
}

def midi_to_frequency(midi_note: int) -> float:
    return 440.0 * (2 ** ((midi_note - 69) / 12))

def get_note_name(midi_note: int) -> str:
    octave = (midi_note // 12) - 1
    note = NOTE_NAMES[midi_note % 12]
    return f"{note}{octave}"

def get_note_color(midi_note: int) -> tuple:
    return NOTE_COLORS[midi_note % 12]

def is_synth_key(key: int) -> bool:
    return key in KEYBOARD_MAP and KEYBOARD_MAP[key] is not None
