import os

# ----------------------------------------------------------------------------------------------------------------------
# ANSI characters
ANSI_RESET: str = "\033[0m"
ANSI_BOLD: str = "\033[1m"
ANSI_UNDERLINE: str = "\033[4m"
ANSI_INVERSE: str = "\033[7m"


# ----------------------------------------------------------------------------------------------------------------------
# ANSI control characters
def move(x: int, y: int):
    return f"\033[{y +1};{x +1}H"

def bgd(r: int, g: int, b: int):
    return f"\033[48;2;{r};{g};{b}m"

def fgd(r: int, g: int, b: int):
    return f"\033[38;2;{r};{g};{b}m"


# ----------------------------------------------------------------------------------------------------------------------
# ANSI methods
def clear_line():
    print("\033[2K", end='')

def clear_screen():
    print("\033[2J", end='')


# ----------------------------------------------------------------------------------------------------------------------
# General methods
def size() -> tuple[int, int]:
    _ts = os.get_terminal_size()
    return _ts.columns, _ts.lines


# ----------------------------------------------------------------------------------------------------------------------
# Draw calls
def draw_box(x: int, y: int, width: int, height: int, name: str = None, rounded: bool = True, dotted: bool = False):
    corner = '╭╮╰╯' if rounded else '┌┐└┘'
    edge = '╴╵' if dotted else '─│'

    _hline = (edge[0] *(width -2))
    out = move(x, y) + corner[0] + _hline + corner[1]
    for i in range(1, height -1):
        out += move(x, y +i) + edge[1] + move(x + width -1, y +i) + edge[1]
    out += move(x, y + height -1) + corner[2] + _hline  + corner[3]

    if name:
        out += f'{move(x +1, y)} {name[:width -3]} '

    print(out, end='')


INPUT_KEYBOARD = 1
INPUT_MOUSE = 2

INPUT_MOUSE_BUTTON = 0
INPUT_MOUSE_MOVE = 1
INPUT_MOUSE_WHEEL = 4
INPUT_MOUSE_BUTTON_LEFT = 1
INPUT_MOUSE_BUTTON_RIGHT = 2
INPUT_MOUSE_BUTTON_MIDDLE = 4
INPUT_MOUSE_WHEEL_UP = 8388608
INPUT_MOUSE_WHEEL_DOWN = 4286578688


# ----------------------------------------------------------------------------------------------------------------------
# OS specific handling
if os.name == 'nt': # Windows
    import ctypes
    import ctypes.wintypes as wintypes

    # Constants from Windows API
    _STD_INPUT_HANDLE = -10
    _STD_OUTPUT_HANDLE = -11
    _ENABLE_MOUSE_INPUT = 0x0010
    _ENABLE_EXTENDED_FLAGS = 0x0080
    _ENABLE_WINDOW_INPUT = 0x0008

    # Structs from Windows API
    class COORD(ctypes.Structure):
        _fields_ = [("X", wintypes.SHORT), ("Y", wintypes.SHORT)]

    class KEY_EVENT_RECORD(ctypes.Structure):
        _fields_ = [
            ("bKeyDown", wintypes.BOOL),
            ("wRepeatCount", wintypes.WORD),
            ("wVirtualKeyCode", wintypes.WORD),
            ("wVirtualScanCode", wintypes.WORD),
            ("uChar", wintypes.WCHAR),
            ("dwControlKeyState", wintypes.DWORD),
        ]

    class MOUSE_EVENT_RECORD(ctypes.Structure):
        _fields_ = [
            ("dwMousePosition", COORD),
            ("dwButtonState", wintypes.DWORD),
            ("dwControlKeyState", wintypes.DWORD),
            ("dwEventFlags", wintypes.DWORD),
        ]

    class EVENT_UNION(ctypes.Union):
        _fields_ = [
            ("KeyEvent", KEY_EVENT_RECORD),
            ("MouseEvent", MOUSE_EVENT_RECORD),
        ]

    class INPUT_RECORD(ctypes.Structure):
        _fields_ = [
            ("EventType", wintypes.WORD),
            ("Event", EVENT_UNION),
        ]

    # kernel32 config
    kernel32 = ctypes.windll.kernel32
    stdin_handle = kernel32.GetStdHandle(_STD_INPUT_HANDLE)
    console_flags_enabled = False

    # Set console mode to enable mouse input and extended flags
    def set_console_flags():
        global kernel32, console_flags_enabled
        console_flags_enabled = True
        kernel32.SetConsoleMode(
            stdin_handle,
            _ENABLE_EXTENDED_FLAGS | _ENABLE_MOUSE_INPUT | _ENABLE_WINDOW_INPUT
        )

    def clear_console_flags():
        ...

    # Input
    _forced_input_stack = []
    def force_input(event: dict[str, int]):
        _forced_input_stack.append(event)

    def read_input() -> dict[str, int]:
        global console_flags_enabled
        global _forced_input_stack
        if _forced_input_stack:
            return _forced_input_stack.pop()
        
        if not console_flags_enabled:
            set_console_flags()

        record = INPUT_RECORD()
        count = wintypes.DWORD()

        kernel32.PeekConsoleInputW(stdin_handle, ctypes.byref(record), 1, ctypes.byref(count))
        if not count.value:
            return None

        kernel32.ReadConsoleInputW(stdin_handle, ctypes.byref(record), 1, ctypes.byref(count))
        if record.EventType == INPUT_KEYBOARD:
            key = record.Event.KeyEvent
            return {
                'type': INPUT_KEYBOARD,
                'key': ord(key.uChar),
                'press': key.bKeyDown,
                'keycode': key.wVirtualKeyCode,
                'scancode': key.wVirtualScanCode
            }

        if record.EventType == INPUT_MOUSE:
            mouse = record.Event.MouseEvent
            return {
                'type': INPUT_MOUSE,
                'event': mouse.dwEventFlags,
                'button': mouse.dwButtonState,
                'x': mouse.dwMousePosition.X,
                'y': mouse.dwMousePosition.Y,
            }

    # Window title
    def set_title(title: str):
        kernel32.SetConsoleTitleW(title)
        # os.system(f"title {title}") # closed alternative

    # Cursor
    def hide_cursor():
        class CONSOLE_CURSOR_INFO(ctypes.Structure):
            _fields_ = [
                ("dwSize", ctypes.c_int),
                ("bVisible", ctypes.c_bool)
            ]
        cursor_info = CONSOLE_CURSOR_INFO()
            
        stdout_handle = ctypes.windll.kernel32.GetStdHandle(_STD_OUTPUT_HANDLE)
        ctypes.windll.kernel32.GetConsoleCursorInfo(stdout_handle, ctypes.byref(cursor_info))
        cursor_info.bVisible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(stdout_handle, ctypes.byref(cursor_info))

    def show_cursor():
        class CONSOLE_CURSOR_INFO(ctypes.Structure):
            _fields_ = [
                ("dwSize", ctypes.c_int),
                ("bVisible", ctypes.c_bool)
            ]
        cursor_info = CONSOLE_CURSOR_INFO()
            
        stdout_handle = ctypes.windll.kernel32.GetStdHandle(_STD_OUTPUT_HANDLE)
        ctypes.windll.kernel32.GetConsoleCursorInfo(stdout_handle, ctypes.byref(cursor_info))
        cursor_info.bVisible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(stdout_handle, ctypes.byref(cursor_info))
else: # UNIX
    import tty
    import signal
    import termios
    import select, struct
    import fcntl

    _forced_input_stack = []
    _orig_termios = None

    def set_console_flags():
        global _orig_termios
        if _orig_termios is None:
            fd = sys.stdin.fileno()
            _orig_termios = termios.tcgetattr(fd)
            tty.setcbreak(fd)
            fcntl.fcntl(fd, fcntl.F_SETFL)
            # fcntl.fcntl(fd, fcntl.F_SETFL, os.O_NONBLOCK)

    def clear_console_flags():
        global _orig_termios
        if _orig_termios is None:
            return
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _orig_termios)

    def force_input(event: dict[str, int]):
        _forced_input_stack.append(event)

    def read_input() -> dict[str, int]:
        global _forced_input_stack
        if _forced_input_stack:
            return _forced_input_stack.pop()

        if not _orig_termios:
            set_console_flags()

        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if not rlist:
            return None

        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
            if ch == '\x1b[<':
                ch += sys.stdin.read(1)
                return {
                    'type': INPUT_MOUSE,
                    'event': INPUT_MOUSE_MOVE,
                    'button': 0,
                    'x': ord(ch[3]) - 32,
                    'y': ord(ch[4]) - 32
                }
            else:
                return {
                    'type': INPUT_KEYBOARD,
                    'key': ord(ch),
                    'press': True,
                    'keycode': 0,
                    'scancode': 0
                }
        else:
            return {
                'type': INPUT_KEYBOARD,
                'key': ord(ch),
                'press': True,
                'keycode': 0,
                'scancode': 0
            }
        
    def set_title(title: str):
        sys.stdout.write(f"\033]0;{title}\007", end='')
        sys.stdout.flush()
    
    def hide_cursor():
        sys.stdout.write("\033[?25l", end='')
        sys.stdout.flush()

    def show_cursor():
        sys.stdout.write("\033[?25h", end='')
        sys.stdout.flush()

