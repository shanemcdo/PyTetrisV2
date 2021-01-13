"""Basic classes for creating a pygame application"""

import pygame, sys
from glob import glob
from pygame.locals import *
from recordclass import RecordClass

class TrueEvery:
    """This is a functor that creates a function that returns true once every {self.count} calls"""

    def __init__(self, count: int, initial_count: int = None, once: bool = False, start_value: int = 0):
        """
        :count: the number of times {self.__call__} must be called to return true once
        :initial_count: Optional. defaults to {self.count}. the number of times {self._call__} must be called to return True after the first call
        :once: Optional. defaults to False. the value
        :start_value: Optional. defaults to 0. the value that the offset starts at before the current call
        """
        self.count = count
        self.initial_count = initial_count if initial_count != None else count
        self.once = once
        self.calls = self.start_value = start_value
        self.first_call = True

    def __call__(self) -> bool:
        """
        Override () operator
        :returns: true once every {self.count} calls
            always returns true first time run unless start_value is set to something different
        """
        # TODO: refactor this
        if not self.first_call and self.once:
            return False
        self.calls -= 1
        if self.calls <= 0:
            self.calls = self.initial_count if self.first_call else self.count
            self.first_call = False
            return True

    def reset(self, override_start_value: int = None):
        """
        reset {self.calls}, and {self.first_call}
        :override_start_value: Optional. Defaults to self.start_value. set a new start value instead of the one in the constructor
        """
        self.calls = override_start_value if override_start_value != None else self.start_value
        self.first_call = True

    def run_or_reset(self, boolean: bool) -> bool:
        """
        :boolean: the boolean to be evaluated. If this boolean is True the {self.__call__} is called.
            If the boolean is False it calls {self.reset}
        :returns: a bool. It returns the result of call if {boolean} is True. or it returns False if {boolean} is False
        """
        if boolean:
            return self()
        self.reset()
        return False

class Point(RecordClass):
    x: float
    y: float

def clip_surface(surface: pygame.Surface, rect: Rect) -> pygame.Surface:
    """Copy part of a pygame.Surface"""
    cropped = pygame.Surface(rect.size)
    cropped.blit(surface, (0, 0), rect)
    return cropped

class Animation:
    """
    Represents a object that has multiple frames each with diffrent length
    :example:

        # assets/animations has files 0.png, 1.png, 2.png, and 3.png
        a = Animation('assets/animations/*', [30, 7, 7, 7]) # create animation
        class Example(GameScreen):
            def __init__(self):
                pygame.init()
                size = Point(300, 300)
                real_size = Point(size.x * 2, size.y * 2)
                screen = pygame.display.set_mode(real_size)
                super().__init__(screen, real_size, size)

            def update(self):
                super().update()
                self.screen.blit(a.get_surface(), (self.window_size.x / 2, self.window_size.y / 2))
                a.update()

        Example().run()
    """
    def __init__(self, glob_path: str, frame_data: [int], repititions: int = None):
        """
        :glob_path: the path that glob is called on.
            e.g.: 'assets/animations/*' to get every file in assets/animations
        :frame_data: how long a frame of the animation should be displayed in game frames
            e.g.: [7, 8, 9] first image found in glob_path lasts 7, the next lasts 8, and the third lasts 9
            this must be the same length as the number of items from glob_path
        :repititions: Optional. defaults to None. if repititions is none, it repeats forever.
            if this number is an int, it decrements every time update is called until it is zero
        """
        self.glob_path = glob_path
        self.frame_data = frame_data
        self.repititions = repititions
        self.finished = True if self.repititions == 0 else False
        self.load(glob_path, frame_data)

    def update(self):
        """
        Indicate a frame has passed
        """
        if not self.finished:
            self.frames_until_next -= 1
            if self.frames_until_next == 0:
                self.frame_index = (self.frame_index + 1) % self.frame_count
                self.frames_until_next += self.frames[self.frame_index][1]
                if self.frame_index == 0 and self.repititions != None:
                    self.repititions -= 1
                    if self.repititions == 0:
                        self.finished = True

    def get_surface(self) -> pygame.Surface:
        """return the frame of the current index"""
        return self.frames[self.frame_index][0]

    def reset(self):
        """Restart the animation to the start of the loop"""
        self.frame_index = 0
        self.frames_until_next = self.frames[0][1]

    def load(self, glob_path: str, frame_data):
        """
        Load animations from a glob path
        :glob_path: the path that glob is called on.
            e.g.: 'assets/animations/*' to get every file in assets/animations
        :frame_data: how long a frame of the animation should be displayed in game frames
            e.g.: [7, 8, 9] first image found in glob_path lasts 7, the next lasts 8, and the third lasts 9
            this must be the same length as the number of items from glob_path
        """
        file_names = glob(glob_path)
        if len(file_names) != len(frame_data):
            raise ValueError('Length of frame_data and the number of files must be the same')
        self.frames = [(pygame.image.load(file_name), frame_data[i]) for i, file_name in enumerate(file_names)]
        self.frame_count = len(self.frames)
        self.frame_index = 0
        self.frames_until_next = self.frames[0][1]

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
            rect_line_width: int = 0,
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
        self.highlight_color = highlight_color if highlight_color else rect_color
        self.rect_line_width = rect_line_width
        self.border_radius = border_radius
        self.border_size = border_size
        self.border_color = border_color
        self.clicked_color = clicked_color
        self.clicked = False
        self.highlight = False

    def draw(self, screen: pygame.Surface, override_highlight: bool = None):
        pygame.draw.rect(screen, self.clicked_color if self.clicked else self.highlight_color if (override_highlight == None and self.highlight) or override_highlight else self.rect_color, self.rect, self.rect_line_width, self.border_radius)
        self.clicked = False
        if self.border_size > 0:
            pygame.draw.rect(screen, self.border_color, self.rect, self.border_size, self.border_radius)
        text_obj = self.font.render(self.text, True, self.font_color)
        text_size = text_obj.get_size()
        screen.blit(text_obj, (self.rect.centerx - text_size[0] / 2, self.rect.centery - text_size[1] / 2))

    def __call__(self):
        """Overwrite the () operator on the button object"""
        if self.action:
            self.action()
        self.clicked = True

class ToggleButton:
    """When clickd this button will change its color, text, and also call target"""

    def __init__(
            self,
            action: callable,
            on_text: str,
            off_text: str,
            rect: Rect,
            font: pygame.font.Font,
            on_rect_color: Color = (255, 255, 255),
            off_rect_color: Color = None,
            on_highlight_color: Color = (150, 150, 150),
            off_highlight_color: Color = (150, 150, 150),
            on_font_color: Color = (0, 0, 0),
            off_font_color: Color = (0, 0, 0),
            rect_line_width: int = 0,
            border_radius: int = 0,
            border_size: int = 0,
            on_border_color: Color = (0, 0, 0),
            off_border_color: Color = None,
            toggled: bool = False,
            ):
        self.action = action
        self.on_text = on_text
        self.off_text = off_text
        self.rect = rect
        self.font = font
        self.on_rect_color = on_rect_color
        self.off_rect_color = off_rect_color if off_rect_color else on_rect_color
        self.on_highlight_color = on_highlight_color
        self.off_highlight_color = off_highlight_color
        self.on_font_color = on_font_color
        self.off_font_color = off_font_color
        self.rect_line_width = rect_line_width
        self.border_radius = border_radius
        self.border_size = border_size
        self.on_border_color = on_border_color
        self.off_border_color = off_border_color if off_border_color else on_border_color
        self.highlight = False
        self.toggled = toggled

    def draw(self, screen: pygame.Surface, override_highlight: bool = None):
        if self.toggled:
            pygame.draw.rect(screen, self.on_highlight_color if (override_highlight == None and self.highlight) or override_highlight else self.on_rect_color, self.rect, self.rect_line_width, self.border_radius)
            if self.border_size > 0:
                pygame.draw.rect(screen, self.on_border_color, self.rect, self.border_size, self.border_radius)
            text_obj = self.font.render(self.on_text, True, self.on_font_color)
            text_size = text_obj.get_size()
            screen.blit(text_obj, (self.rect.centerx - text_size[0] / 2, self.rect.centery - text_size[1] / 2))
        else:
            pygame.draw.rect(screen, self.off_highlight_color if (override_highlight == None and self.highlight) or override_highlight else self.on_rect_color, self.rect, self.rect_line_width, self.border_radius)
            if self.border_size > 0:
                pygame.draw.rect(screen, self.off_border_color, self.rect, self.border_size, self.border_radius)
            text_obj = self.font.render(self.off_text, True, self.on_font_color)
            text_size = text_obj.get_size()
            screen.blit(text_obj, (self.rect.centerx - text_size[0] / 2, self.rect.centery - text_size[1] / 2))

    def __call__(self):
        """override the ()"""
        if self.action:
            self.action()
        self.toggled = not self.toggled

class GameScreen:
    """
    A class to reperesent a screen inside a pygame application
    e.g.: menu, pause screen, or main screen
    to use this class, inherit it and overwrite some/all of its functions
    :example:

        class Example(GameScreen):
            def __init__(self):
                pygame.init()
                real_size = Point(600, 600) # size of window itself
                size = Point(real_size.x / 40, real_size.y / 40) # 1 pixel for every 40
                super().__init__(pygame.display.set_mode(real_size), real_size, size)

            def update(self):
                pygame.draw.line(self.screen, (255, 255, 255), (0, self.window_size.y / 2), (self.window_size.x, self.window_size.y / 2))

        example = Example()
        example.run()
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
        self.window_scaled = bool(window_size) and window_size != real_window_size
        self.real_screen = screen
        self.screen = screen if not self.window_scaled else pygame.Surface(window_size)
        self.real_window_size = Point._make(real_window_size)
        self.window_size = Point._make(window_size if self.window_scaled else real_window_size)
        self.window_scale = Point(self.real_window_size.x // self.window_size.x, self.real_window_size.y // self.window_size.y)
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
            if self.window_scaled:
                self.real_screen.blit(pygame.transform.scale(self.screen, self.real_window_size), (0, 0))
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

    def draw_buttons(self, screen: pygame.Surface = None):
        """Draw the buttons"""
        if not screen:
            screen = self.screen
        for i, button in enumerate(self.buttons):
            button.draw(screen, True if i == self.button_index else None)

    def update(self):
        self.draw_buttons()

    def mouse_button_down(self, event: pygame.event.Event):
        if event.button == 1:
            mouse_pos = Point._make(pygame.mouse.get_pos())
            if self.window_scaled:
                mouse_pos = Point(mouse_pos.x // self.window_scale.x, mouse_pos.y // self.window_scale.y)
            for i, button in enumerate(self.buttons):
                if button.rect.collidepoint(mouse_pos):
                    self.button_index = i
                    button()
