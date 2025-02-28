import tkinter as tk
from turtle import window_width
from PIL.Image import Image
import pyautogui
from io import BytesIO
from config import Shortcut, SnapConfig
from platforms import LinuxXClip
platform = LinuxXClip()
platform.assert_dependencies()

def copy_image(image: Image):
    # TODO: play the clipboard noise
    # TODO: support other formats -- png, webp, etc.
    output = BytesIO()
    image.save(output, format="PNG")
    _ = output.seek(0)
    platform.copy_image_to_clipboard(output)
    print('Copied image to clipboard.')


def screenshot(root: tk.Tk):
    w = root.winfo_width()
    h = root.winfo_height()
    y = root.winfo_y()
    x = root.winfo_x()
    
    # Capture the screenshot of the specified region
    return pyautogui.screenshot(region=(x, y, w, h))


def screenshot_and_copy_image(root: tk.Tk):
    copy_image(screenshot(root))
    root.destroy()


def open_screenshot_window(config: SnapConfig):
    root = tk.Tk()
    _ = root.attributes('-topmost', True)  # Keep the window on top
    root.wait_visibility(root)
    root.wm_attributes('-alpha',0.1)

    w, h = config.start_dimentions

    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    if config.start_position == 'center':
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
    elif config.start_position == "center-at-cursor":
        cursor = pyautogui.position()
        x = cursor.x - w/2
        y = cursor.y - h/2
    else:
        raise RuntimeError("unexpected start_position config")


    # set the dimensions of the screen 
    # and where it is placed
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))


    root.focus_force()  # Ensure the window has focus

    startx, starty, endx, endy = (0, 0, 0, 0)
    
    def exit_window(_):
        root.destroy()

    def onpress(e):
        nonlocal startx, starty
        startx, starty = (e.x, e.y)

    def onrelease(e):
        nonlocal endx, endy
        endx, endy = (e.x, e.y)

    def onmove(e):
        w = root.winfo_width()
        h = root.winfo_height()
        y = root.winfo_y()
        x = root.winfo_x()

        # absolute co-ordinates of mouse on the screen
        absx = x + e.x
        absy = y + e.y

        # position is set to the top left corner, so we need to adjust by the window size to center
        posx = absx - startx
        posy = absy - starty

        root.geometry('%dx%d+%d+%d' % (w, h, posx, posy))

    def resize(dx: int, dy: int):
        w = root.winfo_width()
        h = root.winfo_height()
        y = root.winfo_y()
        x = root.winfo_x()

        root.geometry('%dx%d+%d+%d' % (w + dx, h + dy, x - 1, y - 28))



    root.bind("<ButtonPress-1>", onpress)
    root.bind("<ButtonRelease-1>", onrelease)
    root.bind("<B1-Motion>", onmove)

    magnitude = 15
    actions = {
        'copy-image': lambda _: screenshot_and_copy_image(root),
        'close-window': exit_window,
        "resize-right": lambda _: resize(magnitude, 0),
        "resize-left": lambda _: resize(-magnitude, 0),
        "resize-down": lambda _: resize(0, magnitude),
        "resize-up": lambda _: resize(0, -magnitude),
    }

    for shortcut in config.shortcuts:
        # TODO: support more than one input key
        assert len(shortcut.press) == 1
        assert len(shortcut.hold) == 0

        action = actions[shortcut.action]
        assert action is not None
        root.bind(shortcut.press[0], action)

    root.mainloop()


    
open_screenshot_window(SnapConfig(
    start_dimentions = (800, 600),
    window_alpha = 0.1,
    start_position = "center-at-cursor",
    shortcuts=[
        Shortcut(press=["s"], action="copy-image"),
        Shortcut(press=["<Return>"], action="copy-image"),
        Shortcut(press=["<Escape>"], action="close-window"),
        Shortcut(press=["q"], action="close-window"),
        Shortcut(press=["H"], action="resize-left"),
        Shortcut(press=["L"], action="resize-right"),
        Shortcut(press=["J"], action="resize-down"),
        Shortcut(press=["K"], action="resize-up"),
    ]
))
