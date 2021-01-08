import pygame, sys
from pygame.locals import *
from collections import namedtuple
from game_screens import Point, Button, GameScreen, MenuScreen

class MainMenu(MenuScreen):
    """The main menu of a pygame application"""

    def __init__(self, screen: pygame.Surface, window_size: Point, frame_rate: int = 30):
        super().__init__(screen, window_size, frame_rate)
        # lucidaconsole, lucidasans, agencyfb, copperplategothic, dubairegualar
        self.button_font = pygame.font.SysFont('lucidaconsole', 60)
        self.buttons = [
            Button(lambda: print('Play'), 'Play', Rect(20, 40, 260, 100), self.button_font),
            Button(lambda: print('Options'), 'Options', Rect(20, 150, 260, 100), self.button_font),
            Button(sys.exit, 'Quit', Rect(20, 260, 260, 100), self.button_font),
            ]

if __name__ == "__main__":
    pygame.init()
    size = Point(600, 700)
    screen = pygame.display.set_mode(size)
    menu = MainMenu(screen, size)
    menu.run()
