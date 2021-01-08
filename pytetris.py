import pygame, sys
from pygame.locals import *
from collections import namedtuple
from game_screens import Point, Button, GameScreen, MenuScreen

class PyTetrisMenu(MenuScreen):
    """The main menu of the pytetris game"""

    def __init__(self, screen: pygame.Surface, window_size: Point):
        super().__init__(screen, window_size, 10)
        # lucidaconsole, lucidasans, agencyfb, copperplategothic, dubairegualar
        font = pygame.font.SysFont('lucidaconsole', 60)
        self.buttons = [
            Button(lambda: print('Play'), 'Play', Rect(20, 240, 260, 100), font, border_size = 2),
            Button(lambda: print('Options'), 'Options', Rect(20, 350, 260, 100), font, border_size = 2),
            Button(sys.exit, 'Quit', Rect(20, 460, 260, 100), font, border_size = 2),
            ]
        background = pygame.image.load('assets/menu_background.png')
        background_rect = background.get_rect()
        background_rect.y = window_size.y - background_rect.h
        screen.blit(background, background_rect)

if __name__ == "__main__":
    pygame.init()
    size = Point(600, 700)
    screen = pygame.display.set_mode(size)
    menu = PyTetrisMenu(screen, size)
    menu.run()
