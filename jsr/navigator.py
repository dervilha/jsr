import os, sys
import terminal as tl
from interface import Interface

MAX_WIDTH = 30
MAX_HEIGHT = 16
OS_PATHROOT = '/' if os.name != 'nt' else ''
DEFAULT_ICON_DIR = '📂'
DEFAULT_ICON_FILE = '📄'

class Navigator(Interface):
    def __init__(self):
        self.CONTROL_MAP = {
            ord('q'): self._control_exit,
            ord(' '): self._control_open,
            ord('e'): self._control_select,
            10: self._control_select, # <ENTER>
            96: self._control_exit, # <ESC>
            ord('w'): self._control_up,
            ord('s'): self._control_down,
            ord('a'): self._control_left,
            ord('d'): self._control_right,
            23: self._ctrl_w, # <Ctrl + w>
        }

        self.cwd: str = os.getcwd().replace('\\', '/')
        self.center_cursor: int = 0
        self.centered_item: str = None
        self.scroll: int = 0

        self.parent_list: list[str] = []
        self.center_list: list[str] = []
        self.child_list : list[str] = []
        self._update_lists()


    # Interface methods
    def keyboard(self, key, press, keycode):
        if key in self.CONTROL_MAP.keys() and press:
            self.CONTROL_MAP[key]()
        #print((key, keycode))

    def draw(self):
        self._update_lists()
        # len_lists = [len(self.parent_list), len(self.center_list), len(self.child_list)]
        traveled_amount = 0
        for i in range(MAX_HEIGHT):
            items = [' ' * MAX_WIDTH for _ in range(3)]
            for ii, ls in enumerate([self.parent_list, self.center_list, self.child_list]):
                index = i + self.scroll
                if index < len(ls):
                    items[ii] = ls[index]

            line = (
                tl.move_x(0)
                + items[0]
                + tl.move_x(MAX_WIDTH)
                + items[1]
                + tl.move_x(MAX_WIDTH *2)
                + items[2]
                + "   "
            )
            print(line)
            traveled_amount += 1
        print(tl.shift_y(-traveled_amount), end='')

    def cleanup(self):
        max_height = max([len(self.parent_list), len(self.center_list), len(self.child_list)])
        print(tl.shift_y(max_height))


    # Public methods
    def set_cwd(self, cwd: str):
        self.cwd = cwd


    # Private methods
    def _update_lists(self):
        dir_list = self.cwd.strip('/').split('/')
        try:
            center_list: list[str] = os.listdir(self.cwd)
        except PermissionError:
            self.cwd = os.path.dirname(self.cwd)
            self._update_lists()
            return

        center_dirs, center_files = self._format_file_list([self.cwd + '/' + item for item in center_list])
        center_list_paths = center_dirs + center_files
        self.centered_item = center_list_paths[self.center_cursor]
        self.center_list = self._highlight_cursor(
            self._fill_items(center_dirs, DEFAULT_ICON_DIR) + self._fill_items(center_files, DEFAULT_ICON_FILE)
        )

        # Parent list
        parent_list: list[str] = []
        parent_list_path = OS_PATHROOT + '/'.join(dir_list[:-1])
        if len(dir_list) > 1:
            parent_list = os.listdir(parent_list_path)
        parent_dirs, parent_files = self._format_file_list([parent_list_path + '/' + item for item in parent_list])
        self.parent_list = self._fill_items(parent_dirs, DEFAULT_ICON_DIR) + self._fill_items(parent_files, DEFAULT_ICON_FILE)

        # Child list
        child_list: list[str] = []
        child_list_path: str = center_list_paths[self.center_cursor]
        if os.path.isdir(child_list_path):
            try:
                child_list = os.listdir(child_list_path)
            except PermissionError:
                child_list = []
        child_dirs, child_files   = self._format_file_list([child_list_path + '/' + item for item in child_list])
        self.child_list  = self._fill_items(child_dirs,  DEFAULT_ICON_DIR) + self._fill_items(child_files,  DEFAULT_ICON_FILE)


    def _format_file_list(self, file_list: list[str]) -> tuple[list[str]]:
        out_dir = []
        out_file = []
        for file in file_list:
            if os.path.isdir(file):
                out_dir.append(file)
            else:
                out_file.append(file)

        return out_dir, out_file


    def _fill_items(self, item_list: list[str], default_icon: str = ".") -> list[str]:
        out = []
        for i, item in enumerate(item_list):
            name = item.split('/')[-1][:MAX_WIDTH]
            name = name + ' ' * max(0, MAX_WIDTH - len(name) - 2)
            out.append(default_icon + ' ' + name)

        return out

    def _highlight_cursor(self, full_item_list: list[str]) -> list[str]:
        if self.center_cursor >= len(full_item_list):
            return full_item_list
        full_item_list[self.center_cursor] = (
            tl.bgd(255, 255, 255) +
            tl.fgd(0, 0, 0) +
            full_item_list[self.center_cursor] +
            tl.ANSI_RESET
        )
        return full_item_list


    # Control methods
    def _control_exit(self):
        self.running = False

    def _control_open(self):
        ...

    def _control_select(self):
        ...

    def _control_up(self):
        self.center_cursor = max(self.center_cursor - 1, 0)
        if self.center_cursor < self.scroll:
            self.scroll -= 1
        
    def _control_down(self):
        self.center_cursor = min(self.center_cursor + 1, len(self.center_list) -1)
        if self.center_cursor > MAX_HEIGHT + self.scroll -1:
            self.scroll += 1

    def _control_left(self):
        self.cwd = os.path.dirname(self.cwd)
        self.center_cursor = 0 # TODO: set cursor to the previous item
        self.scroll = 0

    def _control_right(self):
        if not os.path.isdir(self.centered_item):
            return
        self.cwd = self.centered_item
        self.center_cursor = 0
        self.scroll = 0


    # Ctrl keys
    def _ctrl_w(self):
        ...





