import pygame, sys
from pygame.locals import *
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])

def new_matrix(width: int, height: int = None, value = None):
    return [[value for j in range(width)] for i in range(height if height else width)]

class Button:
    """A button in a pygame application"""

    def __init__(self, action: callable, text: str, rect: Rect, font: pygame.font.Font, rect_color: Color = (255, 255, 255), highlight_color: Color = (255, 0, 0), font_color: Color = (0, 0, 0), width: int = 0, border_radius: int = 0, border_size: int = 0, border_color: int = (0, 0, 0)):
        self.action = action
        self.text = text
        self.rect = rect
        self.font = font
        self.rect_color = rect_color
        self.font_color = font_color
        self.highlight_color = highlight_color
        self.width = width
        self.border_radius = border_radius
        self.border_size = border_size
        self.border_color = border_color
        self.highlight = False

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.highlight_color if self.highlight else self.rect_color, self.rect, self.width, self.border_radius)
        if self.border_size > 0:
            pygame.draw.rect(screen, self.border_color, self.rect, self.border_size, self.border_radius)
        text_obj = self.font.render(self.text, True, self.font_color)
        text_size = text_obj.get_size()
        screen.blit(text_obj, (self.rect.centerx - text_size[0] / 2, self.rect.centery - text_size[1] / 2))

    def __call__(self):
        """Overwrite the () operator on the button object"""
        self.action()

class GameScreen:
    """
    A class to reperesent a screen inside a pygame application
    e.g.: menu, pause screen, or main screen

    """

    def __init__(self, screen: pygame.Surface, window_size: Point, frame_rate: int = 30):
        self.screen = screen
        self.window_size = window_size
        self.frame_rate = frame_rate
        self.running = False
        self.rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()

    def keyboard_input(self, event: pygame.event.Event):
        print(event)

    def mouse_input(self, event: pygame.event.Event):
        # maybe change this function to on mouse click because
        # this function cannot do hovering
        print(event)

    def update(self):
        self.screen.fill((0, 0, 100))

    def run(self):
        """Run the main loop"""
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                elif event.type == KEYDOWN:
                    self.keyboard_input(event)
                elif event.type == MOUSEBUTTONDOWN:
                    self.mouse_input(event)
            self.update()
            pygame.display.update()
            self.clock.tick(self.frame_rate)

class MenuScreen(GameScreen):
    """
    A class to represent a menu screen inside a pygame application
    e.g.: Main menu, Pause menu, Options
    """

    def __init__(self, screen: pygame.Surface, window_size: Point, frame_rate: int = 30):
        super().__init__(screen, window_size, frame_rate)
        self.buttons = []
        self.button_index = 0

    def keyboard_input(self, event: pygame.event.Event):
        if event.key == K_UP or event.key == K_RIGHT or event.key == K_DOWN or event.key == K_LEFT:
            self.buttons[self.button_index].highlight = False
            if event.key == K_DOWN or event.key == K_RIGHT:
                self.button_index += 1
                buttons_length = len(self.buttons)
                if self.button_index >= buttons_length:
                    self.button_index %= buttons_length
            else:
                self.button_index -= 1
                if self.button_index < 0:
                    self.button_index = len(self.buttons) - 1
            self.buttons[self.button_index].highlight = True
        elif event.key == K_RETURN or event.key == K_SPACE:
            self.buttons[self.button_index]()

    def update(self):
        for button in self.buttons:
            button.draw(self.screen)

    def mouse_input(self, event: pygame.event.Event):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            if button.rect.collidepoint(mouse_pos):
                button()
