import tkinter as tk
import pyautogui
from io import BytesIO
from collections import deque
from config import SnapConfig
from keys import press, Keys, shift
from platforms import LinuxXClip
from eventhandling import ActionContext, onaction, App, action


platform = LinuxXClip()
platform.assert_dependencies()

def screenshot(root: tk.Tk):
    w = root.winfo_width()
    h = root.winfo_height()
    y = root.winfo_y()
    x = root.winfo_x()
    
    # Capture the screenshot of the specified region
    return pyautogui.screenshot(region=(x, y, w, h))


@action
def copy_image(ctx):
    image = screenshot(ctx.window)
    # TODO: play the clipboard noise
    # TODO: support other formats -- png, webp, etc.
    output = BytesIO()
    image.save(output, format="PNG")
    _ = output.seek(0)
    platform.copy_image_to_clipboard(output)
    print('Copied image to clipboard.')
    ctx.window.destroy()

@action
def copy_ocr(ctx: ActionContext):
    image = screenshot(ctx.window)
    output = BytesIO()
    image.save(output, format="PNG")
    _ = output.seek(0)
    text = platform.extract_image_text_ocr(output)
    platform.copy_text_to_clipboard(text)
    print(text)
    ctx.window.destroy()


@onaction('exit')
def exit_window(ctx: ActionContext):
    ctx.window.destroy()


def resize(root, dx: int, dy: int):
    w = root.winfo_width()
    h = root.winfo_height()
    y = root.winfo_y()
    x = root.winfo_x()

    root.geometry('%dx%d+%d+%d' % (w + dx, h + dy, x - 1, y - 28))

@onaction("resize-left")
def resize_left(ctx: ActionContext):
    resize(ctx.window, -ctx.config.resize_increment, 0)

@onaction("resize-right")
def resize_right(ctx: ActionContext):
    resize(ctx.window, ctx.config.resize_increment, 0)

@onaction("resize-down")
def resize_right(ctx: ActionContext):
    resize(ctx.window, 0, ctx.config.resize_increment)

@onaction("resize-up")
def resize_right(ctx: ActionContext):
    resize(ctx.window, 0, -ctx.config.resize_increment)

def resize_absolute(root, w, h):
    y = root.winfo_y()
    x = root.winfo_x()
    root.geometry('%dx%d+%d+%d' % (w, h, x - 1, y - 28))


def configure_window_size_quickswitch(config: SnapConfig, root: tk.Tk):
    sizes = deque(config.quick_change_dimensions)

    def next_window_size(_):
        sizes.rotate(1)
        w, h = sizes[0]
        resize_absolute(root, w, h)

    def prev_window_size(_):
        sizes.rotate(-1)
        w, h = sizes[0]
        resize_absolute(root, w, h)

    def default_window_size(_):
        w, h = config.start_dimentions
        resize_absolute(root, w, h)

    action(next_window_size)
    action(prev_window_size)
    action(default_window_size)


def translate(root: tk.Tk, dx: int, dy: int):
    w = root.winfo_width()
    h = root.winfo_height()
    y = root.winfo_y()
    x = root.winfo_x()

    root.geometry('%dx%d+%d+%d' % (w, h, x + dx - 1, y + dy - 28))

@action
def translate_right(ctx: ActionContext):
    translate(ctx.window, ctx.config.translate_increment, 0)

@action
def translate_left(ctx: ActionContext):
    translate(ctx.window, -ctx.config.translate_increment, 0)

@action
def translate_down(ctx: ActionContext):
    translate(ctx.window, 0, ctx.config.translate_increment)

@action
def translate_up(ctx: ActionContext):
    translate(ctx.window, 0, -ctx.config.translate_increment)


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

    root.bind("<ButtonPress-1>", onpress)
    root.bind("<ButtonRelease-1>", onrelease)
    root.bind("<B1-Motion>", onmove)

    configure_window_size_quickswitch(config, root)

    app = App(
        config=config,
        platform=LinuxXClip(),
        window=root
    )

    for _action, trigger in config.shortcuts:
        app.assign(_action, trigger)

    root.mainloop()

    
open_screenshot_window(SnapConfig(
    start_dimentions = (800, 600),
    window_alpha = 0.3,
    start_position = "center-at-cursor",
    shortcuts=[
        ("copy-image", press('s')),
        ("copy-image", Keys.ENTER),
        ("exit", Keys.ESCAPE),
        ("exit", press('q')),
        ("resize-left", shift('H')),
        ("resize-right", shift('L')),
        ("resize-down", shift('J')),
        ("resize-up", shift('K')),
        ("resize-left", Keys.SHIFT_LEFT),
        ("resize-right", Keys.SHIFT_RIGHT),
        ("resize-down", Keys.SHIFT_DOWN),
        ("resize-up", Keys.SHIFT_UP),
        ("translate-left", press('h')),
        ("translate-right", press('l')),
        ("translate-down", press('j')),
        ("translate-up", press('k')),
        ("translate-left", Keys.LEFT),
        ("translate-right", Keys.RIGHT),
        ("translate-down", Keys.DOWN),
        ("translate-up", Keys.UP),
        ("next-window-size", Keys.TAB),
        ("prev-window-size", Keys.SHIFT_TAB),
        ("copy-ocr", press('c'))
    ]
))
