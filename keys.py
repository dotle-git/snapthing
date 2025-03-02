from dataclasses import dataclass
from string import ascii_lowercase
from typing import final

class States:
    NOTHING = 0
    SHIFT = 1

@dataclass(frozen=True)
class KeyPress:
    key: str | None = None
    keycode: int | None = None
    state: int = States.NOTHING

    def __post_init__(self):
        assert self.key or self.keycode


def press(key: str, keycode: int | None = None):
    return KeyPress(key=key, keycode=keycode)

def keycode(code: int, key: str | None = None):
    return KeyPress(keycode=code, key=key)

def shift(key: str, keycode: int | None = None):
    return KeyPress(key=key, keycode=keycode, state=States.SHIFT)


@final
class Keys:
    ESCAPE = press('Escape', keycode=24)
    ENTER = press('Return', keycode=36)
    TAB = press('Tab', keycode=23)
    SHIFT_TAB = shift('Tab', keycode=23)
    LEFT = press('Left')
    RIGHT = press('Right')
    UP = press('Up')
    DOWN = press('Down')
    SHIFT_LEFT = shift('Left')
    SHIFT_RIGHT = shift('Right')
    SHIFT_UP = shift('Up')
    SHIFT_DOWN = shift('Down')
