import time
import terminal as tl

if __name__ == "__main__":
    print(tl.ANSI_RESET) # no end='' to flush the buffer
    tl.set_console_flags()
    tl.hide_cursor()

    running = True
    while running:
        while ie := tl.read_input():
            print(ie)
            if ie['type'] == tl.INPUT_KEYBOARD and ie['key'] == ord('q'):
                running = False
                break
        
        time.sleep(0.1)

    print(tl.ANSI_RESET)
    tl.clear_console_flags()
    tl.show_cursor()
