import pygame, sys
from pygame.locals import *
from collections import namedtuple
from game_screens import Point, Button, GameScreen, MenuScreen

if __name__ == "__main__":
    pygame.init()
    size = Point(600, 600)
    screen = pygame.display.set_mode(size)
    game = MenuScreen(screen, size)
    game.run()
