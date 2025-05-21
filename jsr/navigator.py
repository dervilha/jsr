import terminal as tl
from interface import Interface

class Navigator(Interface):


    def keyboard(self, key, press, keycode):
        if key == ord('q'):
            print("exit!")
            self.running = False

    def draw(self):
        print("draw!")


