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
    Z = 0
    L = 1
    O = 2
    S = 3
    I = 4
    J = 5
    T = 6

class Peice:
    """Represents a tetris peice or tetrimino"""

    def __init__(self, matrix: [[Cell]], board_size: Point, window_size: Point):
        self.matrix = matrix
        self.matrix_size = Point(len(matrix[0]), len(matrix))
        self.board_size = board_size
        self.window_size = window_size
        self.pos = Point(board_size.x // 2 - self.matrix_size.x // 2, 0)

    def get_cell_type(self) -> Cell:
        """Find the first cell in the matrix and return it"""
        for row in self.matrix:
            for cell in row:
                if cell != Cell.EMPTY:
                    return cell
        return Cell.EMPTY

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

    def draw(self, cells: [pygame.Surface], cell_size: Point, screen: pygame.Surface):
        """Draw the peice onto the board"""
        screen.blit(self.get_surface(cells, cell_size), (cell_size.x * self.pos.x, cell_size.y * self.pos.y))

    def move_down(self, board: [[Cell]]) -> bool:
        """Move the tetris peice down"""
        if not self.move_to(board, Point(self.pos.x, self.pos.y + 1)):
            self.lock(board)

    def move_left(self, board: [[Cell]]) -> bool:
        """Move the tetris peice left"""
        self.move_to(board, Point(self.pos.x - 1, self.pos.y))

    def move_right(self, board: [[Cell]]) -> bool:
        """Move the tetris peice right"""
        self.move_to(board, Point(self.pos.x + 1, self.pos.y))

    def move_to(self, board: [[Cell]], pos: Point) -> bool:
        """Try to move to a new position"""
        if valid := self.check_valid_position(board, pos):
            self.pos = pos
        return valid

    def rotate_right(self, board: [[Cell]]) -> bool:
        """
        Rotate a peice's matrix 90 degrees to the right
        matrix can be any size as long and width and height are the same
            ^^^^ make it work with other sizes
        e.g.:
            Matrix:
                +--+--+--+--+      +--+--+--+--+
                |00|01|02|03|      |30|20|10|00|
                +--+--+--+--+      +--+--+--+--+
                |10|11|12|13|      |31|21|11|01|
                +--+--+--+--+ ---> +--+--+--+--+
                |20|21|22|23|      |32|22|12|02|
                +--+--+--+--+      +--+--+--+--+
                |30|31|32|33|      |33|23|13|03|
                +--+--+--+--+      +--+--+--+--+
        """
        matrix = [[self.matrix[self.matrix_size.y - j - 1][i] for j in range(self.matrix_size.x)] for i in range(self.matrix_size.y)]
        if rotated := self.check_valid_position(board, peice_matrix = matrix):
            self.matrix = matrix
        return rotated

    def rotate_left(self, board: [[Cell]]):
        """
        Rotate a peice's matrix 90 degrees to the left
        matrix can be any size as long and width and height are the same
        e.g.:
            Matrix:
                +--+--+--+--+      +--+--+--+--+
                |00|01|02|03|      |03|13|23|33|
                +--+--+--+--+      +--+--+--+--+
                |10|11|12|13|      |02|12|22|22|
                +--+--+--+--+ ---> +--+--+--+--+
                |20|21|22|23|      |01|11|21|31|
                +--+--+--+--+      +--+--+--+--+
                |30|31|32|33|      |00|10|20|30|
                +--+--+--+--+      +--+--+--+--+
        """
        matrix = [[self.matrix[j][self.matrix_size.x - i - 1] for j in range(self.matrix_size.x)] for i in range(self.matrix_size.y)]
        if rotated := self.check_valid_position(board, peice_matrix = matrix):
            self.matrix = matrix
        # TODO: Push the matrix around if it can't rotate <08-01-21, Shane McDonough> #
        return rotated

    def check_valid_position(self, board: [[Cell]], pos: Point = None, peice_matrix: [[Cell]] = None) -> bool:
        """Check if the position passed is avaliale for the this object"""
        if not peice_matrix:
            peice_matrix = self.matrix
        if not pos:
            pos = self.pos
        for i, row in enumerate(peice_matrix):
            for j, cell in enumerate(row):
                if cell != Cell.EMPTY and not (pos.x + j >= 0 and pos.x + j < self.board_size.x and pos.y + i < self.board_size.y and board[i + pos.y][j + pos.x] == Cell.EMPTY):
                    return False
        return True

    def lock(self, board: [[Cell]]):
        """Lock the peice in place on the board"""
        for i, row in enumerate(self.matrix):
            for j, cell in enumerate(row):
                if cell != Cell.EMPTY:
                    board[i + self.pos.y][j + self.pos.x] = cell

class PyTetrisGame(GameScreen):
    """
    The pytetris game itself.
    runs the game logic
    """
    SCORE_DICT = {
            # TODO
            }
    LEVEL_FRAMES = { # 1 cell per {value} at level {key}
            0: 48,
            1: 43,
            2: 38,
            3: 33,
            4: 28,
            5: 23,
            6: 18,
            7: 13,
            8: 8,
            9: 6,
            10: 5,
            11: 5,
            12: 5,
            13: 4,
            14: 4,
            15: 4,
            16: 3,
            17: 3,
            18: 3,
            19: 2,
            20: 2,
            21: 2,
            22: 2,
            23: 2,
            24: 2,
            25: 2,
            26: 2,
            27: 2,
            28: 2,
            29: 1,
            }
    LEVEL_LINES = { # how many lines it takes to reach the next level
            0: 10,
            1: 20,
            2: 30,
            3: 40,
            4: 50,
            5: 60,
            6: 70,
            7: 80,
            8: 90,
            9: 100,
            10: 100,
            11: 100,
            12: 100,
            13: 100,
            14: 100,
            15: 100,
            16: 110,
            17: 120,
            18: 130,
            19: 140,
            20: 150,
            21: 160,
            22: 170,
            23: 180,
            24: 190,
            25: 200,
            26: 200,
            27: 200,
            28: 200,
            }
    SOFT_DROP_SPEED = 2 # 1 cell per 2 frames; speed of fall
    DAS_INITIAL_DELAY = 16 # 1 cell per 16 frames; inital speed when holding button
    DAS_REPEAT_DELAY = 6 # 1 cell per 6 frames; speed after first iteration of holding button
    ARE_DELAY = 15 # time(frames) after a new peice is created where the peice cannot move

    def __init__(self, screen: pygame.Surface, window_size: Point):
        super().__init__(screen, window_size, 60)
        pygame.key.set_repeat(1)
        self.cell_size = Point(30, 30)
        self.board_size = Point(10, 20)
        self.board = new_matrix(self.board_size.x, self.board_size.y, Cell.EMPTY)
        self.board_surface_size = Point(self.cell_size.x * self.board_size.x,  self.cell_size.y * self.board_size.y)
        self.board_surface = pygame.Surface(self.board_surface_size)
        board_center = self.board_surface.get_rect().center
        self.board_surface_pos = self.rect.center[0] - board_center[0], self.rect.center[1] - board_center[1]
        self.peices = [
                Peice(
                    [
                        [Cell.O, Cell.O],
                        [Cell.O, Cell.O],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                Peice(
                    [
                        [Cell.EMPTY, Cell.T, Cell.EMPTY],
                        [Cell.T, Cell.T, Cell.T],
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                Peice(
                    [
                        [Cell.EMPTY, Cell.L, Cell.EMPTY],
                        [Cell.EMPTY, Cell.L, Cell.EMPTY],
                        [Cell.EMPTY, Cell.L, Cell.L],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                Peice(
                    [
                        [Cell.EMPTY, Cell.J, Cell.EMPTY],
                        [Cell.EMPTY, Cell.J, Cell.EMPTY],
                        [Cell.J, Cell.J, Cell.EMPTY],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                Peice(
                    [
                        [Cell.EMPTY, Cell.I, Cell.EMPTY, Cell.EMPTY],
                        [Cell.EMPTY, Cell.I, Cell.EMPTY, Cell.EMPTY],
                        [Cell.EMPTY, Cell.I, Cell.EMPTY, Cell.EMPTY],
                        [Cell.EMPTY, Cell.I, Cell.EMPTY, Cell.EMPTY],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                Peice(
                    [
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        [Cell.Z, Cell.Z, Cell.EMPTY],
                        [Cell.EMPTY, Cell.Z, Cell.Z],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                Peice(
                    [
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        [Cell.EMPTY, Cell.S, Cell.S],
                        [Cell.S, Cell.S, Cell.EMPTY],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                ]
        self.num_of_peices = len(self.peices)
        self.cells = self.load_cells_from_image('assets/peices.png')
        self.reset()

    def reset(self):
        self.player = self.get_from_grab_bag(True)
        self.level = 0

    def exit(self):
        self.reset()
        self.running = False

    def get_from_grab_bag(self, new_bag: bool = False):
        if new_bag or not hasattr(self, 'grab_bag') or not self.grab_bag:
            self.grab_bag = self.peices.copy()
        return self.grab_bag.pop(randrange(len(self.grab_bag)))

    def draw_board(self):
        # make board a black screen
        self.board_surface.fill((0, 0, 0))
        # draw board lines
        for i in range(1, self.board_size.x):
            pygame.draw.line(self.board_surface, (100, 100, 100), (i * self.cell_size.x, 0), (i * self.cell_size.x, self.board_surface_size.y))
        for i in range(1, self.board_size.y):
            pygame.draw.line(self.board_surface, (100, 100, 100), (0, i * self.cell_size.y), (self.board_surface_size.y, i * self.cell_size.x))
        # draw the contents of the board
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell != Cell.EMPTY:
                    self.board_surface.blit(self.cells[cell.value], (j * self.cell_size.x, i * self.cell_size.y))
        # draw the player on the board
        self.player.draw(self.cells, self.cell_size, self.board_surface)
        # draw board to the screen
        self.screen.blit(self.board_surface, self.board_surface_pos)
        # draw border around board
        pygame.draw.rect(self.screen, (100, 100, 100), (self.board_surface_pos, self.board_surface_size), 1)

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
            self.exit()
        elif event.key == K_s:
            self.player.move_down(self.board)
        elif event.key == K_a:
            self.player.move_left(self.board)
        elif event.key == K_d:
            self.player.move_right(self.board)
        elif event.key == K_w:
            self.player.lock(self.board)
        elif event.key == K_e:
            self.player.rotate_right(self.board)
        elif event.key == K_q:
            self.player.rotate_left(self.board)
        elif event.key == K_r:
            self.player = self.get_from_grab_bag()

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
