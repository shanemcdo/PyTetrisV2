import pygame, sys
from pygame.locals import *
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])

def new_matrix(width: int, height: int = None, value = None):
    return [[value for j in range(width)] for i in range(height if height else width)]

class Button:
    """A button in a pygame application"""

    def __init__(self, text: str, rect: Rect, font: pygame.font.Font, rect_color: Color = (255, 255, 255), font_color: Color = (0, 0, 0), width: int = 0, border_radius: int = 0):
        self.text = text
        self.rect = rect
        self.font = font
        self.rect_color = rect_color
        self.font_color = font_color
        self.width = width
        self.border_radius = border_radius

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.rect_color, self.rect, self.width, self.border_radius)
        text_obj = self.font.render(self.text, True, self.font_color)
        text_size = text_obj.get_size()
        screen.blit(text_obj, (self.rect.centerx - text_size[0] / 2, self.rect.centery - text_size[1] / 2))

class GameScreen:
    """
    A class to reperesent a screen inside a game
    e.g.: menu, pause screen, or main screen

    """

    def __init__(self, screen: pygame.Surface, window_size: Point, frame_rate: int = 30):
        self.screen = screen
        self.size = window_size
        self.frame_rate = frame_rate
        self.running = False
        self.clock = pygame.time.Clock()

    def keyboard_input(self, event: pygame.event.Event):
        print(event)

    def mouse_input(self, event: pygame.event.Event):
        print(event)

    def update(self):
        self.screen.fill((0, 0, 100))

    def run(self):
        """Run the main loop"""
        self.running = True
        button = Button('Button!', Rect(20, 40, 100, 50), pygame.font.SysFont('arial', 20))
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                elif event.type == KEYDOWN:
                    self.keyboard_input(event)
                elif event.type == MOUSEBUTTONDOWN:
                    self.mouse_input(event)
            self.update()
            button.draw(self.screen)
            pygame.display.update()
            self.clock.tick(self.frame_rate)

if __name__ == "__main__":
    pygame.init()
    size = Point(600, 600)
    screen = pygame.display.set_mode(size)
    gs = GameScreen(screen, size)
    gs.run()
