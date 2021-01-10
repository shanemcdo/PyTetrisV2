"""Basic classes for creating a pygame application"""

import pygame, sys
from pygame.locals import *
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])

def clip_surface(surface: pygame.Surface, rect: Rect) -> pygame.Surface:
    """Copy part of a pygame.Surface"""
    cropped = pygame.Surface(rect.size)
    cropped.blit(surface, (0, 0), rect)
    return cropped

class Button:
    """A button in a pygame application"""

    def __init__(
            self,
            action: callable,
            text: str,
            rect: Rect,
            font: pygame.font.Font,
            rect_color: Color = (255, 255, 255),
            highlight_color: Color = (150, 150, 150),
            font_color: Color = (0, 0, 0),
            width: int = 0,
            border_radius: int = 0,
            border_size: int = 0,
            border_color: Color = (0, 0, 0),
            clicked_color: Color = (100, 100, 100)
            ):
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
        self.clicked_color = clicked_color
        self.clicked = False
        self.highlight = False

    def draw(self, screen: pygame.Surface, overridde_highlight: bool = None):
        pygame.draw.rect(screen, self.clicked_color if self.clicked else self.highlight_color if (overridde_highlight == None and self.highlight) or overridde_highlight else self.rect_color, self.rect, self.width, self.border_radius)
        self.clicked = False
        if self.border_size > 0:
            pygame.draw.rect(screen, self.border_color, self.rect, self.border_size, self.border_radius)
        text_obj = self.font.render(self.text, True, self.font_color)
        text_size = text_obj.get_size()
        screen.blit(text_obj, (self.rect.centerx - text_size[0] / 2, self.rect.centery - text_size[1] / 2))

    def __call__(self):
        """Overwrite the () operator on the button object"""
        self.action()
        self.clicked = True

class GameScreen:
    """
    A class to reperesent a screen inside a pygame application
    e.g.: menu, pause screen, or main screen

    """

    def __init__(self, screen: pygame.Surface, real_window_size: Point, window_size: Point = None, frame_rate: int = 30):
        """
        :screen: The pygame surface that will be drawn onto
        :real_window_size: The height and width of the screen in real computer pixels
        :window_size: The height and width of the screen in game pixels pixels
            if this is smaller than real_window_size the pixels become larger
            if this is larger than real_window_size the pixels become smaller
        :frame_rate: The desired frame rate of the current screen
        """
        self.scaled = bool(window_size) and window_size != real_window_size
        self.real_screen = screen
        self.screen = screen if not self.scaled else pygame.Surface(window_size)
        self.real_window_size = real_window_size
        self.window_size = window_size if self.scaled else real_window_size
        self.frame_rate = frame_rate
        self.running = False
        self.rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.game_ticks = 0

    def tick(self):
        self.clock.tick(self.frame_rate)
        self.game_ticks += 1
        if self.game_ticks > 999999999999999999999:
            self.game_ticks = 0

    def key_down(self, event: pygame.event.Event):
        """Function called when a pygame KEYDOWN event is triggered"""

    def key_up(self, event: pygame.event.Event):
        """Function called when a pygame KEYUP event is triggered"""

    def mouse_button_down(self, event: pygame.event.Event):
        """Function called when a pygame MOUSEBUTTONDOWN event is triggered"""

    def mouse_button_up(self, event: pygame.event.Event):
        """Function called when a pygame key_down MOUSEBUTTONDOWN is triggered"""

    def handle_event(self, event: pygame.event.Event):
        """Handle a pygame events"""
        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            self.key_down(event)
        elif event.type == KEYUP:
            self.key_up(event)
        elif event.type == MOUSEBUTTONDOWN:
            self.mouse_button_down(event)
        elif event.type == MOUSEBUTTONUP:
            self.mouse_button_up(event)

    def update(self):
        """Run every frame, meant for drawing and update logic"""
        self.screen.fill((0, 0, 100))

    def run(self):
        """Run the main loop"""
        self.running = True
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            pygame.display.update()
            self.tick()

class MenuScreen(GameScreen):
    """
    A class to represent a menu screen inside a pygame application
    e.g.: Main menu, Pause menu, Options
    """

    def __init__(self, screen: pygame.Surface, real_window_size: Point, window_size: Point = None, frame_rate: int = 30):
        super().__init__(screen, real_window_size, window_size, frame_rate)
        self.buttons = []
        self.button_index = 0

    def key_down(self, event: pygame.event.Event):
        if event.key == K_UP or event.key == K_RIGHT or event.key == K_DOWN or event.key == K_LEFT:
            if event.key == K_DOWN or event.key == K_RIGHT:
                self.button_index += 1
                buttons_length = len(self.buttons)
                if self.button_index >= buttons_length:
                    self.button_index %= buttons_length
            else:
                self.button_index -= 1
                if self.button_index < 0:
                    self.button_index = len(self.buttons) - 1
        elif event.key == K_RETURN or event.key == K_SPACE:
            self.buttons[self.button_index]()

    def update(self):
        for i, button in enumerate(self.buttons):
            button.draw(self.screen, True if i == self.button_index else None)

    def mouse_button_down(self, event: pygame.event.Event):
        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for i, button in enumerate(self.buttons):
                if button.rect.collidepoint(mouse_pos):
                    self.button_index = i
                    button()
