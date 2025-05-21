import time
import terminal as tl
from interface import Interface
from navigator import Navigator

interface: Interface = None

def entry_standalone():
    global interface
    interface = Navigator()
    interface.running = True

def run():
    global interface
    if not interface:
        raise ValueError("No interface set")
    
    print(tl.ANSI_RESET) # no end='' to flush the buffer
    tl.set_console_flags()
    tl.hide_cursor()

    while interface.running:
        drawcall = True
        while ie := tl.read_input():
            if ie['type'] == tl.INPUT_KEYBOARD:
                interface.keyboard(ie['key'], ie['press'], ie['keycode'])
            elif ie['type'] == tl.INPUT_MOUSE:
                if ie['event'] == tl.INPUT_MOUSE_MOVE:
                    interface.mouse_move(ie['x'], ie['y'])
                elif ie['event'] == tl.INPUT_MOUSE_BUTTON:
                    interface.mouse_button(ie['x'], ie['y'], ie['button'], ie['button'] != 0)
                elif ie['event'] == tl.INPUT_MOUSE_WHEEL:
                    interface.mouse_scroll(ie['x'], ie['y'], 1 if ie['button'] == tl.INPUT_MOUSE_WHEEL_DOWN else -1)
            else:
                drawcall = False

        if drawcall:
            interface.draw()

        time.sleep(0.05)

    print(tl.ANSI_RESET)
    tl.clear_console_flags()
    tl.show_cursor()

if __name__ == "__main__":
    entry_standalone()
    run()