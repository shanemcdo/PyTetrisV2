"""PyTetris is a game that is made to to be a unoffical version of tetris made with pygame"""

import pygame, sys
from pygame.locals import *
from enum import Enum
from random import randrange
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

# TODO: Deal with cell_size being needed everwhere <08-01-21, Shane McDonough>
#   maybe put everything in one bigger class PyTetris?
class Cell(Enum):
    """Represents a square on the grid"""
    EMPTY = None
    RED = 0
    ORANGE = 1
    YELLOW = 2
    GREEN = 3
    CYAN = 4
    BLUE = 5
    PURPLE = 6

class Peice:
    """Represents a tetris peice or tetrimino"""

    def __init__(self, matrix: [[Cell]], board_size: Point, window_size: Point):
        self.matrix = matrix
        self.matrix_size = Point(len(matrix[0]), len(matrix))
        self.board_size = board_size
        self.window_size = window_size
        self.pos = Point(board_size.x // 2 - 2, -4)

    def get_surface(self, cells: [pygame.Surface], cell_size: Point) -> pygame.Surface:
        """Get a surface witht the given tetris peice on it"""
        # SRCALPHA allows the background to be transparent
        result = pygame.Surface((self.matrix_size.x * cell_size.x, self.matrix_size.y * cell_size.y), flags = SRCALPHA)
        result.fill((0, 0, 0, 0)) # set transparent
        for i, row in enumerate(self.matrix):
            for j, cell in enumerate(row):
                if cell != Cell.EMPTY:
                    result.blit(cells[cell.value], (j * cell_size.x, i * cell_size.y))
        return result

class PyTetrisGame(GameScreen):
    """
    The pytetris game itself.
    runs the game logic
    """

    def __init__(self, screen: pygame.Surface, window_size: Point):
        super().__init__(screen, window_size, 60)
        self.num_of_peices = len(Cell) - 1
        print(self.num_of_peices)
        self.board_size = Point(10, 20)
        self.board = new_matrix(self.board_size.x, self.board_size.y, Cell.EMPTY)
        self.cell_size = Point(30, 30)
        self.cells = self.load_cells_from_image('assets/peices.png')
        self.peices = [
                Peice(
                    [
                        [Cell.YELLOW, Cell.YELLOW],
                        [Cell.YELLOW, Cell.YELLOW],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                Peice(
                    [
                        [Cell.EMPTY, Cell.PURPLE, Cell.EMPTY],
                        [Cell.PURPLE, Cell.PURPLE, Cell.PURPLE],
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                Peice(
                    [
                        [Cell.EMPTY, Cell.ORANGE, Cell.EMPTY, Cell.EMPTY],
                        [Cell.EMPTY, Cell.ORANGE, Cell.EMPTY, Cell.EMPTY],
                        [Cell.EMPTY, Cell.ORANGE, Cell.ORANGE, Cell.EMPTY],
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                Peice(
                    [
                        [Cell.EMPTY, Cell.EMPTY, Cell.BLUE, Cell.EMPTY],
                        [Cell.EMPTY, Cell.EMPTY, Cell.BLUE, Cell.EMPTY],
                        [Cell.EMPTY, Cell.BLUE, Cell.BLUE, Cell.EMPTY],
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                Peice(
                    [
                        [Cell.EMPTY, Cell.CYAN, Cell.EMPTY, Cell.EMPTY],
                        [Cell.EMPTY, Cell.CYAN, Cell.EMPTY, Cell.EMPTY],
                        [Cell.EMPTY, Cell.CYAN, Cell.EMPTY, Cell.EMPTY],
                        [Cell.EMPTY, Cell.CYAN, Cell.EMPTY, Cell.EMPTY],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                Peice(
                    [
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        [Cell.EMPTY, Cell.RED, Cell.RED, Cell.EMPTY],
                        [Cell.EMPTY, Cell.EMPTY, Cell.RED, Cell.RED],
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                Peice(
                    [
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        [Cell.EMPTY, Cell.EMPTY, Cell.GREEN, Cell.GREEN],
                        [Cell.EMPTY, Cell.GREEN, Cell.GREEN, Cell.EMPTY],
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                ]
        self.grab_bag = []
        self.player = self.get_from_grab_bag()

    def get_from_grab_bag(self):
        if not self.grab_bag:
            self.grab_bag = self.peices.copy()
        return self.grab_bag.pop(randrange(self.num_of_peices + 1))

    def draw_board(self):
        board_screen_size = Point(self.cell_size.x * self.board_size.x,  self.cell_size.y * self.board_size.y)
        board_screen = pygame.Surface(board_screen_size)
        board_screen.fill((0, 0, 0))
        for i in range(1, self.board_size.x):
            pygame.draw.line(board_screen, (100, 100, 100), (i * self.cell_size.x, 0), (i * self.cell_size.x, board_screen_size.y))
        for i in range(1, self.board_size.y):
            pygame.draw.line(board_screen, (100, 100, 100), (0, i * self.cell_size.y), (board_screen_size.y, i * self.cell_size.x))
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell != Cell.EMPTY:
                    board_screen.blit(self.cells[cell.value], (j * self.cell_size.x, i * self.cell_size.y))
        board_center = board_screen.get_rect().center
        center = self.rect.center[0] - board_center[0], self.rect.center[1] - board_center[1]
        self.screen.blit(board_screen, center)
        pygame.draw.rect(self.screen, (100, 100, 100), (center, board_screen.get_size()), 1)

    def load_cells_from_image(self, file_name: str) -> [pygame.Surface]:
        """Split an image into 7 surfaces to be used as tiles"""
        image = pygame.image.load(file_name)
        image_size = Point._make(image.get_size())
        cell_size = Point(image_size.x // self.num_of_peices, image_size.y)
        return [pygame.transform.scale(clip_surface(image, Rect((x, 0), cell_size)), self.cell_size) for x in range(0, image_size.x, cell_size.x)]

    def update(self):
        self.screen.fill((0, 0, 0))
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
