import sys
import time
import traceback
import terminal as tl
from interface import Interface
from navigator import Navigator


interface: Interface = None

def entry_standalone():
    global interface
    interface = Navigator()


def entry_args():
    ...


def run():
    global interface
    if not interface:
        raise ValueError("No interface set")

    t_width, t_height = 1, 1

    print(tl.ANSI_RESET) # no end='' to flush the buffer
    tl.set_console_flags()
    tl.hide_cursor()

    while interface.running:
        drawcall = False

        # Resize check
        _w, _h = tl.size()
        if _w != t_width or _h != t_height:
            t_width = _w
            t_height = _h
            drawcall = True

        # Input check
        while ie := tl.read_input():
            drawcall = True
            if ie['type'] == tl.INPUT_KEYBOARD:
                interface.keyboard(ie['key'], ie['press'], ie['keycode'])
            elif ie['type'] == tl.INPUT_MOUSE:
                if ie['event'] == tl.INPUT_MOUSE_MOVE:
                    interface.mouse_move(ie['x'], ie['y'])
                elif ie['event'] == tl.INPUT_MOUSE_BUTTON:
                    interface.mouse_button(ie['x'], ie['y'], ie['button'], ie['button'] != 0)
                elif ie['event'] == tl.INPUT_MOUSE_WHEEL:
                    interface.mouse_scroll(ie['x'], ie['y'], 1 if ie['button'] == tl.INPUT_MOUSE_WHEEL_DOWN else -1)

        # Draw
        if drawcall:
            interface.draw()

        # Thread sleep
        time.sleep(0.05)


def cleanup():
    global interface
    interface.cleanup()
    print(tl.ANSI_RESET)
    tl.clear_console_flags()
    tl.show_cursor()



if __name__ == "__main__":
    if len(sys.argv) > 1:
        entry_args()
    else:
        entry_standalone()

    try:
        run()
    except Exception as e:
        print(f"MAJOR ERR: {e}")
        traceback.print_exc()
    finally:
        cleanup()

