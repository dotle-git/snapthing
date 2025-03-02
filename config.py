from dataclasses import dataclass, field
from typing import Literal

type StartPositionOption = Literal[
        "center",
        "center-at-cursor"
]

type ScreenshotActionOption = Literal[
        "copy-image",
        "close-window",
        "resize-left",
        "resize-right",
        "resize-up",
        "resize-down",
        "translate-left",
        "translate-right",
        "translate-up",
        "translate-down",
]

type Key = str

@dataclass(frozen=True)
class Shortcut:
    action: ScreenshotActionOption
    press: list[Key] = field(default_factory=list)
    hold: list[Key] = field(default_factory=list)
    # TODO: Can it support key sequences?

    
# TODO: refine the types, enable good autocomplete
type KeyPress = list[str]
type KeyHold = list[str]

def default_actions():
    return [
        Shortcut(
            action='copy-image',
            press=['s']
        ),
        Shortcut(
            action='close-window',
            press=['q']
        ),
        Shortcut(
            action='close-window',
            press=['<Escape>']
        )
    ]

@dataclass
class SnapConfig:
    start_dimentions: tuple[int, int]
    shortcuts: list[Shortcut] = field(default_factory=default_actions)
    window_alpha: float = 0.1
    start_position: StartPositionOption = "center-at-cursor"
    resize_increment: int = 20
    translate_increment: int = 20

    def __post_init__(self):
        if not (0 <= self.window_alpha <= 1):
            raise ValueError("window_alpha must be set between 0 and 1")
