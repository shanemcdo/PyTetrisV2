"""PyTetris is a game that is made to to be a unoffical version of tetris made with pygame"""

import pygame, sys, winsound
from pygame.locals import *
from glob import glob
from enum import Enum
from copy import deepcopy
from random import randrange
from collections import namedtuple
from pygame_tools import Point, Button, GameScreen, MenuScreen, clip_surface, ToggleButton, TrueEvery


def new_matrix(width: int, height: int = None, value = None) -> [[]]:
    """Create a 2d array with the passed width and height"""
    return [[value for j in range(width)] for i in range(height if height else width)]

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
        self.reset()

    def reset(self):
        """resets the position of the Peice to the top"""
        self.pos = Point(self.board_size.x // 2 - self.matrix_size.x // 2, 0)

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
                    result.blit(pygame.transform.scale(cells[cell.value], cell_size), (j * cell_size.x, i * cell_size.y))
        return result

    def draw(self, cells: [pygame.Surface], cell_size: Point, screen: pygame.Surface):
        """Draw the peice onto the board"""
        screen.blit(self.get_surface(cells, cell_size), (cell_size.x * self.pos.x, cell_size.y * self.pos.y))

    def draw_shadow(self, shadows: [pygame.Surface], cell_size: Point, screen: pygame.Surface, board: [[Cell]]):
        shadow_pos = self.get_fast_drop_pos(board)
        shadow_surface = self.get_surface(shadows, cell_size)
        shadow_surface.set_alpha(50)
        screen.blit(shadow_surface, (cell_size.x * shadow_pos.x, cell_size.y * shadow_pos.y))

    def fast_drop(self, board: [[Cell]]):
        while self.move_down(board): pass

    def get_fast_drop_pos(self, board: [[Cell]]) -> Point:
        point = deepcopy(self.pos)
        while self.check_valid_position(board, point):
            point = Point(point.x, point.y + 1)
        point = Point(point.x, point.y - 1)
        return point

    def move_down(self, board: [[Cell]]) -> bool:
        """Move the tetris peice down"""
        return self.move_to(board, Point(self.pos.x, self.pos.y + 1))

    def move_left(self, board: [[Cell]]) -> bool:
        """Move the tetris peice left"""
        return self.move_to(board, Point(self.pos.x - 1, self.pos.y))

    def move_right(self, board: [[Cell]]) -> bool:
        """Move the tetris peice right"""
        return self.move_to(board, Point(self.pos.x + 1, self.pos.y))

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
        :board: a 2d array of Cells the Peice cannot intersect with
        :returns: boolean of success
        """
        matrix = [[self.matrix[self.matrix_size.y - j - 1][i] for j in range(self.matrix_size.x)] for i in range(self.matrix_size.y)]
        return self.rotate_to(board, matrix)

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
        :board: a 2d array of Cells the Peice cannot intersect with
        :returns: boolean of success
        """
        matrix = [[self.matrix[j][self.matrix_size.x - i - 1] for j in range(self.matrix_size.x)] for i in range(self.matrix_size.y)]
        return self.rotate_to(board, matrix)

    #  TODO: Fix I peice edge case wall kick
    def rotate_to(self, board: [[Cell]], matrix: [[Cell]]) -> bool:
        """
        attempts to rotate the peice to the passed matrix
        :matrix: Optional. defaults to {self.matrix}. peice represented in a 2d array of type Cell
        :returns: boolean of success
        """
        rotated, pos = self.check_valid_rotate(board, peice_matrix = matrix)
        if rotated:
            self.pos = pos
            self.matrix = matrix
        return rotated

    def check_valid_rotate(self, board: [[Cell]], pos: Point = None, peice_matrix: [[Cell]] = None) -> (bool, Point):
        """
        Check if a rotated rotated position is ok and move it around slightly if it can
        :board: a 2d array of Cells the Peice cannot intersect with
        :pos: Optional. deaults to {self.pos}. the coordinates of the peice
        :matrix: Optional. defaults to {self.matrix}. peice represented in a 2d array of type Cell
        :returns: a boolean of succes and the point in ended up landing in if it succeeded
        """
        # TODO: EDGECASE WITH I PEICE NEEDING TO MOVE 2
        if not peice_matrix:
            peice_matrix = self.matrix
        if not pos:
            pos = self.pos
        directions = [
                Point(0, 0),
                Point(0, 1),
                Point(1, 1),
                Point(-1, 1),
                Point(1, 0),
                Point(-1, 0),
                Point(1, -1),
                Point(-1, -1),
                ]
        for direction in directions:
            shifted = Point(pos.x + direction.x, pos.y + direction.y)
            if self.check_valid_position(board, shifted, peice_matrix):
                return True, shifted
        return False, None

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

# TODO: Show queue, hold, and maybe grab_bag
class PyTetrisGame(MenuScreen):
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
    # TODO: check if this is actually true
    SOFT_DROP_DELAY = 2 # 1 cell per 2 frames
    DAS_INITIAL_DELAY = 16 # 1 cell per 16 frames; inital speed when holding button
    DAS_REPEAT_DELAY = 6 # 1 cell per 6 frames; speed after first iteration of holding button
    ARE_DELAY = 15 # time(frames) after a new peice is created where the peice cannot move

    def __init__(self, parent: GameScreen):
        super().__init__(parent.screen, parent.window_size, frame_rate = 60)
        self.parent = parent
        self.font_path = self.parent.font_path
        self.pause_button_font = pygame.font.Font(self.font_path, 15)
        self.pause_button_rect = Rect(10, 10, 100, 50)
        self.board_size = Point(10, 20)
        self.board = new_matrix(self.board_size.x, self.board_size.y, Cell.EMPTY)
        self.board_surface_size = Point(300, 600) # work in multiples of 10s and 20s or the bord gets wonky
        self.board_surface = pygame.Surface(self.board_surface_size, flags = SRCALPHA)
        self.cell_size = Point(self.board_surface_size.x // self.board_size.x, self.board_surface_size.y // self.board_size.y)
        board_center = self.board_surface.get_rect().center
        self.board_surface_pos = Point(self.rect.center[0] - board_center[0], self.rect.center[1] - board_center[1])
        self.hold_rect = Rect(self.board_surface_pos.x + self.board_surface_size.x + 15, 50, 120, 120)
        self.hold_surface = pygame.Surface(self.hold_rect.size)
        self.hold_padding = Point(10, 10)
        self.hold_cell_size = Point((self.hold_rect.w - self.hold_padding.x * 2) // 4, (self.hold_rect.h - self.hold_padding.y * 2) // 4)
        self.hold_text = pygame.font.Font(self.font_path, 30).render('Hold', True, (255, 255, 255))
        self.hold_text_rect = self.hold_text.get_rect()
        self.hold_text_rect.topleft = Point(self.hold_rect.centerx - self.hold_text_rect.centerx, self.hold_rect.y - self.hold_text_rect.h - self.hold_padding.y)
        self.queue_rect = Rect(self.hold_rect.x + 5, self.hold_rect.y + self.hold_rect.h + 40, self.hold_rect.w - 10, 400)
        self.queue_surface = pygame.Surface(self.queue_rect.size)
        self.queue_padding = Point(10, 10)
        self.queue_cell_size = Point((self.queue_rect.w - self.queue_padding.x * 2) // 4, (self.queue_rect.w - self.queue_padding.x * 2) // 4)
        self.queue_text = pygame.font.Font(self.font_path, 20).render('Queue', True, (255, 255, 255))
        self.queue_text_rect = self.queue_text.get_rect()
        self.queue_text_rect.topleft = Point(self.queue_rect.centerx - self.queue_text_rect.centerx, self.queue_rect.y - self.queue_text_rect.h - self.queue_padding.y)
        self.statistics_font_size = 12
        self.statistics_font = pygame.font.Font(self.font_path, self.statistics_font_size)
        self.statistics_padding = Point(10, 10 + self.pause_button_rect.bottom)
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
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        [Cell.I, Cell.I, Cell.I, Cell.I],
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                Peice(
                    [
                        [Cell.Z, Cell.Z, Cell.EMPTY],
                        [Cell.EMPTY, Cell.Z, Cell.Z],
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                Peice(
                    [
                        [Cell.EMPTY, Cell.S, Cell.S],
                        [Cell.S, Cell.S, Cell.EMPTY],
                        [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                        ],
                    self.board_size,
                    self.window_size
                    ),
                ]
        self.num_of_peices = len(self.peices)
        self.cells = self.load_cells_from_image('assets/images/peices.png')
        self.queue_size = 7 # arbitrary number
        self.reset()
        self.pause_menu = PauseMenu(self)
        self.buttons = [
                Button(self.pause_menu.run, 'Pause', self.pause_button_rect, self.pause_button_font, highlight_color = None)
                ]
        self.line_clear_sound_paths = glob('assets/audio/clear_*.wav')

    def clear_lines(self) -> int:
        """
        Clear the complete lines from the board
        :returns: number of lines cleared
        """
        lines = 0
        for i, row in enumerate(self.board):
            for cell in row:
                if cell == Cell.EMPTY:
                    break
            else:
                # create clearing lines animations
                self.board.pop(i)
                self.board.insert(0, [Cell.EMPTY for _ in range(self.board_size.x)])
                lines += 1
        return lines

    def get_from_queue(self):
        self.queue.append(self.get_from_grab_bag())
        return self.queue.pop(0)

    def reset(self):
        self.score = 0
        self.level = 0
        self.can_swap_hold = True
        self.hold = None
        self.ARE_locked = False
        self.no_pause = False
        self.lines_cleared = 0
        self.lines_cleared_since_level_up = 0
        self.delay_counters = {
                'ARE_lock': TrueEvery(self.ARE_DELAY, once = True, start_value = self.ARE_DELAY),
                'soft_drop': TrueEvery(self.SOFT_DROP_DELAY, start_value = self.SOFT_DROP_DELAY),
                'auto_drop': TrueEvery(self.LEVEL_FRAMES[self.level]),
                'DAS_fast_drop': TrueEvery(self.DAS_REPEAT_DELAY, self.DAS_INITIAL_DELAY),
                'DAS_move_left': TrueEvery(self.DAS_REPEAT_DELAY, self.DAS_INITIAL_DELAY),
                'DAS_move_right': TrueEvery(self.DAS_REPEAT_DELAY, self.DAS_INITIAL_DELAY),
                'DAS_rotate_left': TrueEvery(self.DAS_REPEAT_DELAY, self.DAS_INITIAL_DELAY),
                'DAS_rotate_right': TrueEvery(self.DAS_REPEAT_DELAY, self.DAS_INITIAL_DELAY),
                }
        self.board = new_matrix(self.board_size.x, self.board_size.y, Cell.EMPTY)
        self.queue = []
        for i in range(self.queue_size):
            self.queue.append(self.get_from_grab_bag(i == 0))
        self.player = self.get_from_queue()

    def exit(self):
        self.reset()
        self.running = False

    def get_from_grab_bag(self, new_bag: bool = False):
        if new_bag or not hasattr(self, 'grab_bag') or not self.grab_bag:
            self.grab_bag = deepcopy(self.peices)
        return self.grab_bag.pop(randrange(len(self.grab_bag)))

    def draw(self):
        """Draw Everything"""
        self.draw_board()
        self.draw_hold()
        self.draw_queue()
        self.draw_statistics()
        self.draw_buttons()

    def draw_statistics(self):
        """
        Print the games statistics
        e.g. Score, level, etc
        """
        i = 0
        for (string, skip_line) in {
            'Score:' : False,
            f'{self.score}': True,
            f'Level: {self.level}': True,
            f'Cleared: {self.lines_cleared}' : True,
            'Till next': False,
            f'level: {self.LEVEL_LINES[self.level] - self.lines_cleared_since_level_up}': True,
            }.items():
            self.screen.blit(self.statistics_font.render(string, True, (255, 255, 255)), (self.statistics_padding.x, self.statistics_padding.y + (5 + self.statistics_font_size) * i))
            i += 2 if skip_line else 1

    def draw_hold(self):
        """Draw the the hold and it's contents"""
        self.screen.blit(self.hold_text, self.hold_text_rect)
        self.hold_surface.fill((0, 0, 0))
        if self.hold:
            peice_surface = self.hold.get_surface(self.cells, self.hold_cell_size)
            self.hold_surface.blit(peice_surface, (self.hold_padding.x + self.hold_cell_size.x * (4 - self.hold.matrix_size.x) // 2, self.hold_padding.y + self.hold_cell_size.y * (4 - self.hold.matrix_size.x) // 2))
            self.screen.blit(self.hold_surface, self.hold_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), self.hold_rect, 2)

    def draw_queue(self):
        """Draw the the queue and it's contents"""
        self.screen.blit(self.queue_text, self.queue_text_rect)
        self.queue_surface.fill((0, 0, 0))
        for i, peice in enumerate(self.queue):
            self.queue_surface.blit(peice.get_surface(self.cells, self.queue_cell_size), (self.queue_padding.x + self.queue_cell_size.x * (4 - peice.matrix_size.x) // 2, self.queue_padding.y + self.queue_cell_size.y * (4 - peice.matrix_size.y) // 2 + (4 * self.queue_cell_size.y + self.queue_padding.y) * i))
        self.screen.blit(self.queue_surface, self.queue_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), self.queue_rect, 2)

    def draw_board(self):
        """Draw the the board and it's contents"""
        # make board a black screen
        self.board_surface.fill((0, 0, 0))
        # draw board lines
        for i in range(1, self.board_size.x):
            pygame.draw.line(self.board_surface, (100, 100, 100), (i * self.cell_size.x - 1, 0), (i * self.cell_size.x - 1, self.board_surface_size.y), 2)
        for i in range(1, self.board_size.y):
            pygame.draw.line(self.board_surface, (100, 100, 100), (0, i * self.cell_size.y - 1), (self.board_surface_size.y, i * self.cell_size.y - 1), 2)
        # draw the contents of the board
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell != Cell.EMPTY:
                    self.board_surface.blit(self.cells[cell.value], (j * self.cell_size.x, i * self.cell_size.y))
        # draw the player on the board
        self.player.draw_shadow(self.cells, self.cell_size, self.board_surface, self.board)
        self.player.draw(self.cells, self.cell_size, self.board_surface)
        # draw board to the screen
        self.screen.blit(self.board_surface, self.board_surface_pos)
        # draw border around board
        self.draw_board_border()

    def draw_board_border(self):
        pygame.draw.rect(self.screen, (100, 100, 100), (self.board_surface_pos, self.board_surface_size), 2)

    def load_cells_from_image(self, file_name: str) -> [pygame.Surface]:
        """Split an image into 7 surfaces to be used as tiles"""
        image = pygame.image.load(file_name)
        image_size = Point._make(image.get_size())
        cell_size = Point(image_size.x // self.num_of_peices, image_size.y)
        return [pygame.transform.scale(clip_surface(image, Rect((x, 0), cell_size)), self.cell_size) for x in range(0, image_size.x, cell_size.x)]

    def swap_hold(self):
        """"Swap the current peice with the peice in self.hold"""
        if self.can_swap_hold:
            self.can_swap_hold = False
            if not self.hold:
                self.hold = self.get_from_queue()
            temp = self.hold
            self.hold = self.player
            self.player = temp
            self.player.reset()

    def update(self):
        self.screen.fill((0, 0, 0))
        self.draw()
        if self.delay_counters['ARE_lock']():
            self.ARE_locked = False
        self.keyboard_input()
        self.auto_drop()

    def calculate_score(self, lines: int):
        if lines == 0:
            return 0
        elif lines == 1:
            return 40 * (self.level + 1)
        elif lines == 2:
            return 100 * (self.level + 1)
        elif lines == 3:
            return 300 * (self.level + 1)
        elif lines == 4:
            return 1200 * (self.level + 1)

    def level_up(self):
        self.level += 1
        self.lines_cleared_since_level_up = 0
        self.delay_counters['auto_drop'].count = self.LEVEL_FRAMES[self.level]
        winsound.PlaySound('assets/audio/level_up.wav', winsound.SND_ASYNC)

    def lock_and_get_new_peice(self):
        """Lock {self.player} in place and get a new peice from the queue"""
        self.player.lock(self.board)
        self.player = self.get_from_queue()
        lines = self.clear_lines()
        self.score += self.calculate_score(lines)
        self.lines_cleared += lines
        self.lines_cleared_since_level_up += lines
        if lines != 0:
            winsound.PlaySound(self.line_clear_sound_paths[lines - 1], winsound.SND_ASYNC)
        if self.level != 29 and self.lines_cleared_since_level_up >= self.LEVEL_LINES[self.level]:
            self.level_up()
        self.can_swap_hold = True
        self.delay_counters['ARE_lock'].reset()
        self.ARE_locked = True

    def auto_drop(self):
        """Move the peice down one and lock if it cannot go farther down"""
        if self.delay_counters['auto_drop']() and not self.ARE_locked:
            if not self.player.move_down(self.board):
                self.lock_and_get_new_peice()

    def key_up(self, event: pygame.event.Event):
        """This is triggered when a key is released"""
        if event.key == K_ESCAPE or event.key == K_p:
            self.no_pause = False

    def key_down(self, event: pygame.event.Event):
        """This function doesn't let K_SPACE into the inherited key_down function"""
        if event.key != K_SPACE:
            super().key_down(event)

    def keyboard_input(self):
        """Use pygame.key.get_pressed for input instead of keyboard events"""
        keys = pygame.key.get_pressed()
        if (keys[K_ESCAPE] or keys[K_p]) and not self.no_pause:
            self.no_pause = True
            self.pause_menu.run()
        if not self.ARE_locked:
            if self.delay_counters['soft_drop'].run_or_reset(keys[K_s]):
                self.player.move_down(self.board)
                self.delay_counters['auto_drop'].reset()
            if self.delay_counters['DAS_fast_drop'].run_or_reset(keys[K_w]):
                self.player.fast_drop(self.board)
                self.lock_and_get_new_peice()
            if self.delay_counters['DAS_move_left'].run_or_reset(keys[K_a]):
                self.player.move_left(self.board)
            if self.delay_counters['DAS_move_right'].run_or_reset(keys[K_d]):
                self.player.move_right(self.board)
            if self.delay_counters['DAS_rotate_left'].run_or_reset(keys[K_q]):
                self.player.rotate_left(self.board)
            if self.delay_counters['DAS_rotate_right'].run_or_reset(keys[K_e]):
                self.player.rotate_right(self.board)
        if keys[K_SPACE]:
            self.swap_hold()

class OptionsMenu(MenuScreen):
    """The options menu for the pytetris game"""
    # TODO: Add real options
    # TODO: Finish this

    def __init__(self, parent: GameScreen):
        super().__init__(parent.screen, parent.window_size, frame_rate = 10)
        self.parent = parent
        self.font_path = parent.font_path
        font = pygame.font.Font(self.font_path, 30)
        back_button_font = pygame.font.Font(self.font_path, 15)
        self.buttons = [
                Button(self.back, 'Back', Rect(10, 10, 100, 50), back_button_font, highlight_color = None),
                ToggleButton(None, 'Shadow On', 'Shadow Off', Rect(100, 100, 200, 100), font, (50, 200, 50), (200, 50, 50)),
                ]
        self.button_index = 1

    def update(self):
        self.screen.fill((0, 50, 100))
        super().update()

    def back(self):
        self.running = False

class ControlsMenu(MenuScreen):
    # TODO: Add ability for user to remap controls
    # TODO: Finish this

    def __init__(self, parent: GameScreen):
        super().__init__(parent.screen, parent.window_size)
        self.parent = parent
        self.font_path = parent.font_path
        self.background = pygame.image.load('assets/images/controls_background.png')
        back_button_font = pygame.font.Font(self.font_path, 15)
        self.buttons = [
                Button(self.back, 'Back', Rect(10, 10, 100, 50), back_button_font, highlight_color = None)
                ]

    def update(self):
        self.screen.blit(self.background, (0, 0))
        super().update()

    def back(self):
        self.running = False

class PauseMenu(MenuScreen):
    # TODO: Finish this

    def __init__(self, parent: GameScreen):
        super().__init__(parent.screen, parent.window_size)
        self.parent = parent
        self.font_path = parent.font_path
        self.board_rect = Rect(parent.board_surface_pos, parent.board_surface_size)
        exit_button_font = parent.pause_button_font
        exit_button_rect = parent.pause_button_rect
        self.title = pygame.font.Font(self.font_path, 40).render('Paused', True, (255, 255, 255))
        self.title_padding = Point(20, 20)
        self.title_rect = Rect((0, 0), self.title.get_size())
        self.title_rect.center = self.board_rect.centerx, self.board_rect.top + self.title_padding.y + self.title_rect.h
        center_buttons_padding = Point(40, 40)
        center_buttons_size = Point(self.board_rect.w - center_buttons_padding.x * 2, 60)
        center_buttons_pos = Point(self.board_rect.centerx - center_buttons_size.x // 2, self.board_rect.top + center_buttons_padding.y + self.title_padding.y * 2 + self.title_rect.h)
        i = 0
        self.buttons = [
                Button(self.resume, 'Resume', Rect(center_buttons_pos, center_buttons_size), exit_button_font),
                Button(self.restart, 'Reset', Rect((center_buttons_pos.x, center_buttons_pos.y + (center_buttons_size.y + center_buttons_padding.y) * (i := i + 1)), center_buttons_size), exit_button_font),
                Button(self.parent.parent.options_menu.run, 'Options', Rect((center_buttons_pos.x, center_buttons_pos.y + (center_buttons_size.y + center_buttons_padding.y) * (i := i + 1)), center_buttons_size), exit_button_font),
                Button(self.parent.parent.controls_menu.run, 'Controls', Rect((center_buttons_pos.x, center_buttons_pos.y + (center_buttons_size.y + center_buttons_padding.y) * (i := i + 1)), center_buttons_size), exit_button_font),
                Button(self.exit, 'Exit', exit_button_rect, exit_button_font),
                ]

    def update(self):
        self.screen.fill((0, 0, 0))
        self.parent.draw()
        self.screen.fill((0, 0, 0), self.board_rect)
        self.parent.draw_board_border()
        self.screen.blit(self.title, self.title_rect)
        super().update()

    def key_down(self, event: pygame.event.Event):
        if event.key == K_p or event.key == K_ESCAPE:
            self.resume()
        super().key_down(event)

    def resume(self):
        self.running = False

    def restart(self):
        self.running = False
        self.parent.reset()

    def exit(self):
        self.running = False
        self.parent.exit()


class MainMenu(MenuScreen):
    """The main menu of the pytetris game"""

    def __init__(self, screen: pygame.Surface, window_size: Point):
        super().__init__(screen, window_size, frame_rate = 10)
        # lucidaconsole, lucidasans, agencyfb, copperplategothic, dubairegualar
        # font = pygame.font.SysFont('lucidaconsole', 60)
        self.font_path = 'assets/fonts/tetris-atari.ttf'
        font = pygame.font.Font(self.font_path, 30)
        self.options_menu = OptionsMenu(self)
        self.controls_menu = ControlsMenu(self)
        self.game = PyTetrisGame(self)
        self.buttons = [
            Button(self.game.run, 'Play', Rect(40, 190, 260, 100), font, border_size = 2),
            Button(self.controls_menu.run, 'Controls', Rect(40, 300, 260, 100), font, border_size = 2),
            Button(self.options_menu.run, 'Options', Rect(40, 410, 260, 100), font, border_size = 2),
            Button(sys.exit, 'Quit', Rect(40, 520, 260, 100), font, border_size = 2),
            ]
        # TODO: Create acutally good background / title <07-01-21, ShaneMcDonough>
        self.background = pygame.image.load('assets/images/menu_background.png')
        self.background_rect = self.background.get_rect()
        self.background_rect.y = self.window_size.y - self.background_rect.h
        self.title = pygame.image.load('assets/images/Title.png')

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
