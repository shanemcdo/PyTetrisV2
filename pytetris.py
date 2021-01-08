"""PyTetris is a game that is made to to be a unoffical version of tetris made with pygame"""

import pygame, sys
from pygame.locals import *
from collections import namedtuple
from game_screens import Point, Button, GameScreen, MenuScreen

def new_matrix(width: int, height: int = None, value = None) -> [[]]:
    """Create a 2d array with the passed width and height"""
    return [[value for j in range(width)] for i in range(height if height else width)]

def clip_surface(surface: pygame.Surface, rect: Rect) -> pygame.Surface:
    """Copy part of a pygame.Surface"""
    cropped = pygame.Surface(rect.size)
    cropped.blit(surface, (0, 0), rect)
    return cropped

def load_cells_from_image(file_name: str, peice_count: int = 7, real_cell_size: Point = None) -> [pygame.Surface]:
    """Split an image into 7 surfaces to be used as tiles"""
    image = pygame.image.load(file_name)
    image_size = Point._make(image.get_size())
    cell_size = Point(image_size.x // peice_count, image_size.y)
    if not real_cell_size:
        real_cell_size = cell_size
    return [pygame.transform.scale(clip_surface(image, Rect((x, 0), cell_size)), real_cell_size) for x in range(0, image_size.x, cell_size.x)]

class Cell:
    """Represents a square on the grid"""
    CELLS = load_cells_from_image('assets/peices.png')
    EMPTY = None
    RED = CELLS[0]
    ORANGE = CELLS[1]
    YELLOW = CELLS[2]
    GREEN = CELLS[3]
    CYAN = CELLS[4]
    BLUE = CELLS[5]
    PURPLE = CELLS[6]

class Peice:

    def __init__(self, matrix: [[Cell]], board_size: Point, window_size: Point):
        self.matrix = matrix
        self.board_size = board_size
        self.window_size = window_size
        self.pos = Point(board_size // 2 - 2, -4)

class PyTetrisGame(GameScreen):
    """
    The pytetris game itself.
    runs the game logic
    """

    def __init__(self, screen: pygame.Surface, window_size: Point):
        super().__init__(screen, window_size, 60)
        self.board_size = Point(10, 20)
        self.board = new_matrix(self.board_size.x, self.board_size.y, ' ')
        self.cell_size = Point(30, 30)

    def draw_board(self):
        board_screen_size = Point(self.cell_size.x * self.board_size.x,  self.cell_size.y * self.board_size.y)
        board_screen = pygame.Surface(board_screen_size)
        board_screen.fill((0, 0, 0))
        for i in range(self.board_size.x):
            pygame.draw.line(board_screen, (255, 255, 255), (i * self.cell_size.x, 0), (i * self.cell_size.x, board_screen_size.y))
        for i in range(self.board_size.y):
            pygame.draw.line(board_screen, (255, 255, 255), (0, i * self.cell_size.y), (board_screen_size.y, i * self.cell_size.x))
        board_center = board_screen.get_rect().center
        center = self.rect.center[0] - board_center[0], self.rect.center[1] - board_center[1]
        self.screen.blit(board_screen, center)

    def update(self):
        self.screen.fill((255, 255, 255))
        self.draw_board()

    def key_down(self, event: pygame.event.Event):
        if event.key == K_ESCAPE:
            self.running = False


class MainMenu(MenuScreen):
    """The main menu of the pytetris game"""

    def __init__(self, screen: pygame.Surface, window_size: Point):
        super().__init__(screen, window_size, 10)
        # lucidaconsole, lucidasans, agencyfb, copperplategothic, dubairegualar
        # font = pygame.font.SysFont('lucidaconsole', 60)
        font = pygame.font.Font('assets/tetris-atari.ttf', 30)
        game = PyTetrisGame(screen, window_size)
        self.buttons = [
            Button(game.run, 'Play', Rect(40, 190, 260, 100), font, border_size = 2),
            Button(lambda: print('Controls'), 'Controls', Rect(40, 300, 260, 100), font, border_size = 2),
            Button(lambda: print('Options'), 'Options', Rect(40, 410, 260, 100), font, border_size = 2),
            Button(sys.exit, 'Quit', Rect(40, 520, 260, 100), font, border_size = 2),
            ]
        # TODO: Create acutally good background / title <07-01-21, ShaneMcDonough>
        self.background = pygame.image.load('assets/menu_background.png')
        self.background_rect = self.background.get_rect()
        self.background_rect.y = self.window_size.y - self.background_rect.h
        self.title = pygame.image.load('assets/Title.png')

    def update(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background, self.background_rect)
        self.screen.blit(self.title, (50, 50))
        super().update()

if __name__ == "__main__":
    pygame.init()
    size = Point(600, 700)
    screen = pygame.display.set_mode(size)
    menu = MainMenu(screen, size)
    menu.run()
