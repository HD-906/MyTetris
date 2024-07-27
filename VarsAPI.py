from os import getcwd, path
import pygame
from configparser import RawConfigParser
from enum import Enum, IntEnum

pygame.font.init()
pygame.mixer.init()

os_Getcwd, os_Path = getcwd, path
FPS = 60
SOFT_DROP_MULTIPLIER = 20
MAX_MOVEMENT = 15
MINO_COLOURS = ("RED", "GREEN", "BLUE", "YELLOW", "PURPLE", "CYAN", "ORANGE", "GREY")
SPAWN = ((19, 4), (20, 4))
TOTAL_NEXT = 5
CONFIG_TITLE = "key_bindings"
REN_ATK = (0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 5)
BUTTONS = ("start", "config", "quit")
MAX_KEY_ASSIGN = 3
SHOW_DIR = {"LEFT": '←',
            "RIGHT": '→',
            "UP": '↑',
            "DOWN": '↓'
            }


class Colour:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)  # Z
    GREEN = (0, 255, 0)  # S
    BLUE = (0, 0, 255)  # J
    YELLOW = (255, 255, 0)  # O
    MAGENTA = (255, 0, 255)  # T
    CYAN = (0, 255, 255)  # I
    ORANGE = (255, 102, 0)  # L

    @staticmethod
    def Code(colour_code: str) -> tuple[int, int, int]:
        colour_code = colour_code.replace('#', '')
        return int(colour_code[:2], 16), int(colour_code[2:4], 16), int(colour_code[4:], 16)


class Text:
    font = "Berlin Sans FB"
    size = 40
    colour = Colour.WHITE
    colour_selected = Colour.YELLOW


class Dim:
    Selected_Scale = 1.2

    class Main:
        DIM = W, H = 750, 850

    class Play_Field:
        DIM = W, H = 401, 810
        COR = X, Y = 170, 25

    class Hold_Field:
        DIM = W, H = 140, 140
        COR = X, Y = 28, 35

    class Next_Field:
        DIM0 = W0, H0 = 140, 140
        COR0 = X0, Y0 = 573, 5

        DIM1 = W1, H1 = 116, 75
        COR1 = X1, Y1 = 573, 167
        COR2 = X2, Y2 = 573, 274
        COR3 = X3, Y3 = 573, 381
        COR4 = X4, Y4 = 573, 488

    class Game_Over:
        DIM = W, H = 340, 90
        COR = X, Y = 200, 400
        X_SHIFT, Y_SHIFT = 10, 10
        font = Text.font
        size = Text.size
        colour = Colour.RED
        colour_background = Colour.WHITE

    class Off_Set:
        MAIN = X_MAIN, Y_MAIN = 55, 85
        OTHER = X_OTR, Y_OTR = 45, 35

    class Show_Scale:
        MAIN = 0.8
        OTHER = 0.6

    class Start_Btn:
        DIM = W, H = 200, 100
        COR = X, Y = 275, 163
        X_SHIFT, Y_SHIFT = 45, 25
        font = Text.font
        size = 40
        colour = Colour.WHITE
        colour_selected = Colour.YELLOW

    class Config_Btn:
        DIM = W, H = 200, 100
        COR = X, Y = 275, 375
        X_SHIFT, Y_SHIFT = 30, 25
        font = Text.font
        size = 40
        colour = Colour.WHITE
        colour_selected = Colour.YELLOW

    class Quit_Btn:
        DIM = W, H = 200, 100
        COR = X, Y = 275, 588
        X_SHIFT, Y_SHIFT = 55, 25
        font = Text.font
        size = 40
        colour = Colour.WHITE
        colour_selected = Colour.YELLOW

    class Set_Key_Window:
        DIM = W, H = 340, 90
        COR = X, Y = 200, 400
        X_SHIFT, Y_SHIFT = 10, 10
        font = Text.font
        size = Text.size
        colour = Colour.BLACK
        colour_background = Colour.WHITE

    class Shift_Left_Btn:
        DIM = W, H = 150, 50
        COR = X, Y = 60, 165
        X_SHIFT, Y_SHIFT = 15, 15
        font = Text.font
        size = 16
        colour = Colour.WHITE
        colour_selected = Colour.YELLOW

    class Shift_Right_Btn:
        DIM = W, H = 150, 50
        COR = X, Y = 60, 245
        X_SHIFT, Y_SHIFT = 15, 15
        font = Text.font
        size = 16
        colour = Colour.WHITE
        colour_selected = Colour.YELLOW

    class Hard_Drop_Btn:
        DIM = W, H = 150, 50
        COR = X, Y = 60, 325
        X_SHIFT, Y_SHIFT = 15, 15
        font = Text.font
        size = 16
        colour = Colour.WHITE
        colour_selected = Colour.YELLOW

    class Soft_Drop_Btn:
        DIM = W, H = 150, 50
        COR = X, Y = 60, 405
        X_SHIFT, Y_SHIFT = 15, 15
        font = Text.font
        size = 16
        colour = Colour.WHITE
        colour_selected = Colour.YELLOW

    class Rotate_Left_Btn:
        DIM = W, H = 150, 50
        COR = X, Y = 60, 485
        X_SHIFT, Y_SHIFT = 15, 15
        font = Text.font
        size = 16
        colour = Colour.WHITE
        colour_selected = Colour.YELLOW

    class Rotate_Right_Btn:
        DIM = W, H = 150, 50
        COR = X, Y = 60, 565
        X_SHIFT, Y_SHIFT = 15, 15
        font = Text.font
        size = 16
        colour = Colour.WHITE
        colour_selected = Colour.YELLOW

    class Hold_Btn:
        DIM = W, H = 150, 50
        COR = X, Y = 60, 645
        X_SHIFT, Y_SHIFT = 15, 15
        font = Text.font
        size = 16
        colour = Colour.WHITE
        colour_selected = Colour.YELLOW

    class Dummy_Btn:
        DIM = W, H = 1, 1
        COR = X, Y = 0, 0
        X_SHIFT, Y_SHIFT = 0, 0
        font = Text.font
        size = 1
        colour = Colour.BLACK
        colour_selected = Colour.BLACK

    class ConfigTitle_Btn:
        DIM = W, H = 250, 80
        COR = X, Y = 250, 25
        X_SHIFT, Y_SHIFT = 55, 17
        font = Text.font
        size = 40
        colour = Colour.WHITE
        colour_selected = Colour.YELLOW

    class Apply_Btn:
        DIM = W, H = 250, 80
        COR = X, Y = 110, 725
        X_SHIFT, Y_SHIFT = 70, 17
        font = Text.font
        size = 40
        colour = Colour.WHITE
        colour_selected = Colour.YELLOW

    class Reset_Btn:
        DIM = W, H = 250, 80
        COR = X, Y = 400, 725
        X_SHIFT, Y_SHIFT = 75, 17
        font = Text.font
        size = 40
        colour = Colour.WHITE
        colour_selected = Colour.YELLOW


class Play_Field_Dim:
    DIM = W, H = 10, 25
    H_MAX = 20
    H_SHOWN = 20
    H_SHOWN_F = 20.25
    MINO_DIM = MINO_W, MINO_H = Dim.Play_Field.W // W, int(Dim.Play_Field.H // H_SHOWN_F)


class Path:
    current = os_Getcwd()

    play_field = os_Path.join(current, "img", "play_field.png")
    blank_btn = os_Path.join(current, "img", "blank_btn.png")
    start_btn = os_Path.join(current, "img", "start_btn.png")
    config_btn = os_Path.join(current, "img", "config_btn.png")
    quit_btn = os_Path.join(current, "img", "quit_btn.png")
    mino_f = os_Path.join(current, "img", "mino_{}.png")
    mino_ghost_f = os_Path.join(current, "img", "mino_{}_ghost.png")

    config = os_Path.join(current, "Config.cfg")


class Delays:
    FPS = 60
    FALL_FRAME = 60
    CLR_DELAY = {0: 0,
                 1: 35,
                 2: 40,
                 3: 40,
                 4: 45,
                 "PC": 1,
                 "default": 45}
    DAS = 10  # delay before continuous shift
    ARR = 2  # continuous shift delay
    ARE = 6  # delay between lock and spawn
    LOCK_DELAY = 30  # delay before lock


class Menu(Enum):
    start = 0
    in_game = 1
    config = 2
    quit = 3


class Cell_Colour(IntEnum):
    NULL = 0
    RED = 1  # Z
    GREEN = 2  # S
    BLUE = 3  # J
    ORANGE = 4  # L
    YELLOW = 5  # O
    PURPLE = 6  # T
    CYAN = 7  # I
    GREY = 8


class Minos:
    NULL_Piece = ''
    S_Piece = 'S'
    Z_Piece = 'Z'
    L_Piece = 'L'
    J_Piece = 'J'
    I_Piece = 'I'
    O_Piece = 'O'
    T_Piece = 'T'
    all_pieces = tuple(char for piece, char in locals().items() if piece[:1] != '_' and char)


class Orient(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    INIT = UP


class Dir(Enum):
    NULL = 0
    LEFT = 1
    RIGHT = 2
    DOWN = 3


class Configs:
    shift_left = "shift_left"
    shift_right = "shift_right"
    hard_drop = "hard_drop"
    soft_drop = "soft_drop"
    rotate_left = "rotate_left"
    rotate_right = "rotate_right"
    hold = "hold"
    all_configs = tuple(config for config in locals() if config[:1] != '_')


class Rotation_Test:
    U_R = ((0, 0), (0, -1), (1, -1), (-2, 0), (-2, -1))
    D_R = ((0, 0), (0, -1), (1, -1), (-2, 0), (-2, -1))
    U_L = ((0, 0), (0, 1), (1, 1), (-2, 0), (-2, 1))
    D_L = ((0, 0), (0, 1), (1, 1), (-2, 0), (-2, 1))
    R_U = ((0, 0), (0, 1), (-1, 1), (2, 0), (2, 1))
    R_D = ((0, 0), (0, 1), (-1, 1), (2, 0), (2, 1))
    L_U = ((0, 0), (0, -1), (-1, -1), (2, 0), (2, -1))
    L_D = ((0, 0), (0, -1), (-1, -1), (2, 0), (2, -1))

    class I_mino:
        U_R = ((0, 1), (0, -1), (0, 2), (-1, -1), (2, 2))
        L_D = ((0, 1), (0, -1), (0, 2), (-1, -1), (2, 2))
        R_U = ((0, -1), (0, 1), (0, -2), (1, 1), (-2, -2))
        D_L = ((0, -1), (0, 1), (0, -2), (1, 1), (-2, -2))
        D_R = ((1, 0), (1, 1), (1, -2), (-1, 1), (2, -2))
        L_U = ((1, 0), (1, 1), (1, -2), (-1, 1), (2, -2))
        R_D = ((-1, 0), (-1, -1), (-1, 2), (1, -1), (-2, 2))
        U_L = ((-1, 0), (-1, -1), (-1, 2), (1, -1), (-2, 2))

    status_dct = {
        Orient.UP: {Dir.RIGHT: "U_R",
                    Dir.LEFT: "U_L"},
        Orient.DOWN: {Dir.RIGHT: "D_L",
                      Dir.LEFT: "D_R"},
        Orient.LEFT: {Dir.RIGHT: "L_U",
                      Dir.LEFT: "L_D"},
        Orient.RIGHT: {Dir.RIGHT: "R_D",
                       Dir.LEFT: "R_U"}
    }


class Mino_Bag(Enum):
    idx = 0
    bag = 1


class InputObj:
    def __init__(self, *args, **kwargs):
        self.pos = None
        self.pressed = None
        self.clicked = self.pressed
        self.current_input = None, None, set()
        self.__current_keys = set()
        self.__buffer_keys = set()
        self.__triggered_keys = set()
        super().__init__(*args, **kwargs)

    @property
    def current_keys(self):
        return self.__current_keys

    @current_keys.setter
    def current_keys(self, new_keys):
        self.__current_keys = new_keys
        self.__triggered_keys = self.__current_keys - self.__buffer_keys

    @property
    def buffer_keys(self):
        return self.__buffer_keys

    @buffer_keys.setter
    def buffer_keys(self, new_keys):
        self.__buffer_keys = new_keys
        self.__triggered_keys = self.__current_keys - self.__buffer_keys

    @property
    def triggered_keys(self):
        return self.__triggered_keys

    def Key_Pressed(self, pygame_keys: set) -> bool:
        """
        checks and returns if any of the given keys are just pressed
        """
        return not pygame_keys.isdisjoint(self.current_keys)

    def Key_Triggered(self, pygame_keys: set) -> bool:
        """
        checks and returns if any of the given keys are just pressed
        """
        return not pygame_keys.isdisjoint(self.triggered_keys)


class MenuObj(InputObj):
    def __init__(self):
        super().__init__()
        self.background_colour = Colour.BLACK
        self.button_list = []
        self.__current_select = 0
        self.max_select = 0

    @property
    def current_select(self):
        return self.__current_select

    @current_select.setter
    def current_select(self, new_select):
        self.button_list[self.__current_select].selected = False
        self.__current_select = new_select % self.max_select
        self.button_list[self.__current_select].selected = True

    @staticmethod
    def Get_Button(name: str, interact: bool = True, *,
                   offset: tuple[int, int] | None = None, new_name: str = None):
        """
        Creates a Button object with name
        """
        if offset is None:
            x, y = 0, 0
        else:
            x, y = offset

        if new_name is None:
            new_name = name

        btn = getattr(Dim, f"{name}_Btn")
        btn_path = Path.blank_btn
        txt_x, txt_y = btn.X + btn.X_SHIFT + x, btn.Y + btn.Y_SHIFT + y
        text_obj = BaseObjWithTxt(
            new_name.upper(), btn.font, btn.size, btn.colour, (txt_x, txt_y))
        text_obj_selected = BaseObjWithTxt(
            new_name.upper(), btn.font, btn.size, btn.colour_selected, (txt_x, txt_y))
        from Button import NonInteractButton, Button
        if interact:
            return Button(
                btn_path, btn.DIM, btn.X + x, btn.Y + y, text_obj, text_obj_selected
            )
        else:
            return NonInteractButton(
                btn_path, btn.DIM, btn.X + x, btn.Y + y, text_obj, text_obj_selected
            )

    def Pass_Input(self, *attrs: str | object):
        """
        Pass current mouse and keyboard input status to attribute named attr
        """
        for attr in attrs:
            if isinstance(attr, str):
                attr = getattr(self, attr)
            attr.pos = self.pos
            attr.pressed = self.pressed
            attr.clicked = self.clicked
            attr.current_keys = self.current_keys
            attr.buffer_keys = self.buffer_keys
            attr.current_input = self.current_input


class BaseObjRect:
    def __init__(self, rect: pygame.Rect, colour: tuple[int, int, int]):
        self.rect = rect
        self.colour = colour

    def Update_Coordinates(self, x, y):
        self.rect.topleft = (x, y)

    def Draw(self, surface):
        pygame.draw.rect(surface, self.colour, self.rect)


class BaseObjImage:
    def __init__(self, image: pygame.Surface, x: int, y: int):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def Update_Coordinates(self, x, y):
        self.rect.topleft = (x, y)

    def Draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))


class BaseObjWithTxt:
    def __init__(self, text: str, font: str, size: int, colour: tuple[int, int, int],
                 coordinates: tuple[int, int] | None = None):
        self.text_str = text
        self.font = font
        self.size = size
        self.colour = colour
        self.text = self.Load_Text(text, font, size, colour)
        self.rect = self.text.get_rect()
        if coordinates is not None:
            self.rect.topleft = coordinates

    @staticmethod
    def Load_Text(text: str, font: str, size: int, colour: tuple[int, int, int]) -> pygame.Surface:
        return pygame.font.SysFont(font, size).render(text, 1, colour)

    def Edit_Text(self, text: str | None = None, font: str | None = None, size: int | None = None,
                  colour: tuple[int, int, int] | None = None):
        if text is not None:
            self.text_str = text
        if font is not None:
            self.font = font
        if size is not None:
            self.size = size
        if colour is not None:
            self.colour = colour
        self.text = self.Load_Text(self.text_str, self.font, self.size, self.colour)
        topleft = self.rect.topleft
        self.rect = self.text.get_rect()
        self.rect.topleft = topleft

    def Update_Coordinates(self, x, y):
        self.rect.topleft = (x, y)

    def Draw(self, surface):
        surface.blit(self.text, self.rect.topleft)

    def __str__(self):
        return self.text_str


class RectTxtObj(BaseObjRect):
    def __init__(self, left, top, width, height, colour,
                 text: BaseObjWithTxt):
        rect = pygame.rect.Rect(left, top, width, height)
        super().__init__(rect, colour)
        self.text = text

    def Draw(self, surface):
        super().Draw(surface)
        self.text.Draw(surface)


class Keys:
    names: list[str] = [
               "LEFT",
               "RIGHT",
               "UP",
               "DOWN",
               "RETURN",
               "KP_ENTER",
               "SPACE",
               "LSHIFT",
               "LCTRL",
               "LALT",
               "RSHIFT",
               "RCTRL",
               "RALT",
               "BACKQUOTE",
               "TAB",
               "ESCAPE",
               "BACKSPACE",
               "MINUS",
               "EQUALS",
               "LEFTBRACKET",
               "RIGHTBRACKET",
               "BACKSLASH",
               "SEMICOLON",
               "QUOTE",
               "COMMA",
               "PERIOD",
               "SLASH"
           ] + [  # includes all alphabet keys from a to z
               chr(alp) for alp in range(ord('a'), ord('z') + 1)
           ] + [  # includes all number keys from 0 to 9
               str(num) for num in range(10)
           ] + [  # includes all number keys from 0 to 9 on keypad
               f"KP_{num}" for num in range(10)
           ] + [  # includes all function keys from F1 to F12
               f"F{num}" for num in range(1, 13)
           ]

    keys: list[int] = [getattr(pygame, f"K_{name}") for name in names]
    name_dct: dict[int, str] = {key: val for key, val in zip(keys, names)}

    confirm = {pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE}
    left = {pygame.K_LEFT, pygame.K_a, pygame.K_KP_4}
    right = {pygame.K_RIGHT, pygame.K_d, pygame.K_KP_6}
    up = {pygame.K_UP, pygame.K_w, pygame.K_KP_8}
    down = {pygame.K_DOWN, pygame.K_s, pygame.K_KP_5}
    quit = {pygame.K_ESCAPE}

    NULL = "NULL"


def Get_Delay(interval: int) -> int:
    """
    Converts intervals in frames to milliseconds
    """
    return 1000 * interval // Delays.FPS


def Cap_Str(string: str) -> str:
    str_lst: list[str] = [str_single[0].upper() + str_single[1:] if str_single else str_single
                          for str_single in string.split('_')]
    return '_'.join(str_lst)


def Convert_x(x: int) -> int:
    """
    Converts x-coordinate of play field to x-coordinate of game window
    """
    return int(Dim.Play_Field.X + Dim.Play_Field.W * x / Play_Field_Dim.W)


def Convert_y(y: int) -> int:
    """
    Converts y-coordinate of play field to y-coordinate of game window
    """
    return int(Dim.Play_Field.Y + Dim.Play_Field.H - Dim.Play_Field.H * (y + 1) / Play_Field_Dim.H_SHOWN_F)


def Convert(y: int, x: int) -> tuple[int, int]:
    """
    Converts coordinate of play field to coordinate of game window, order reverted
    """
    return Convert_x(x), Convert_y(y)


def Add_Pos(*pos: tuple[int, int]) -> tuple:
    """
    Sums up all tuples by dimension
    """
    return tuple(map(lambda *x: sum(x), *pos))


def In_Square(pos_in: tuple[int, int], pos_upper_bound: tuple[int, int], pos_lower_bound: tuple[int, int] = (0, 0)):
    """
    Checks if coordinate pos_in is in the square bounded by pos_lower_bound and pos_upper_bound
    """
    x_set, y_set = zip(pos_lower_bound, pos_upper_bound)
    lower_x, lower_y, upper_x, upper_y = min(x_set), min(y_set), max(x_set), max(y_set)
    x, y = pos_in

    return lower_x <= x < upper_x and lower_y <= y < upper_y


def Select_with_Negative(number: int, total: int):
    return {
        total: -1,
        -2: total - 1
    }.get(number, number)


def Load_image(path_str: str, scale: float | tuple[int, int] = 1, rotation: int = 0) -> pygame.Surface:
    """
    :path: A string containing the path
    :scale: A float representing the scale, or a tuple representing the width and height to resize to
    :rotation: An integer representing the angle in degree to rotate image clockwise
    :return: pygame image object
    """
    image = pygame.image.load(path_str).convert_alpha()
    if isinstance(scale, tuple):
        image = pygame.transform.scale(image, scale)
    elif scale != 1:
        width = image.get_width()
        height = image.get_height()
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))

    if rotation:
        image = pygame.transform.rotate(image, rotation)
    return image


def Get_Image_Func():
    image_dct = {
        getattr(Cell_Colour, colour):
            Load_image(Path.mino_f.format(colour.lower()), Play_Field_Dim.MINO_DIM)
        for colour in MINO_COLOURS
    }
    image_dct_ghost = {
        getattr(Cell_Colour, colour):
            Load_image(Path.mino_ghost_f.format(colour.lower()), Play_Field_Dim.MINO_DIM)
        for colour in MINO_COLOURS[:-1]
    }

    def Inner_Get_Image(colour, *, ghost=False):
        return (image_dct_ghost if ghost else image_dct).get(colour)

    return Inner_Get_Image


def Load_Rect_From_Dim(class_name, *, x='X', y='Y', w='W', h='H') -> pygame.Rect:
    x, y, w, h = map(lambda attr: getattr(class_name, attr), (x, y, w, h))
    return pygame.rect.Rect(x, y, w, h)


def Confirmed(keys) -> bool:
    return keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER] or keys[pygame.K_SPACE]


def Get_Keys_Pressed(keys) -> set:
    """
    returns a list of keys pressed. Only keys in self.check_list will be checked
    """
    return {key for key in Keys.keys if keys[key]}


def Set_Config(category=CONFIG_TITLE, **kwargs):
    """
    Sets configs under category with keys and values from kwargs
    """
    config_parser = RawConfigParser()
    config_parser.read(Path.config)
    if not config_parser.has_section(category):
        config_parser.add_section(category)
    for key, val in kwargs.items():
        config_parser.set(category, key, val)

    with open(Path.config, 'w') as configfile:
        config_parser.write(configfile)


def Get_Config(category=CONFIG_TITLE, args: tuple[str, ...] = Configs.all_configs) -> dict[str, list[str, ...]]:
    """
    Gets configs under category as dictionary
    """
    config_parser = RawConfigParser()
    config_parser.read(Path.config)
    config_dct = {config: config_parser.get(category, config) for config in args}
    config_dct.update({key: [item.strip("'\"") for item in val.strip("[]").split(", ")]
                       for key, val in config_dct.items()
                       })
    return config_dct


def Init_Config():
    """
    Initialize config values
    """
    Set_Config(shift_left=["K_LEFT", "K_KP_4"],
               shift_right=["K_RIGHT", "K_KP_6"],
               hard_drop=["K_UP", "K_KP_8"],
               soft_drop=["K_DOWN", "K_KP_5"],
               rotate_left=["K_q", "K_a", "K_z"],
               rotate_right=["K_w", "K_s", "K_x"],
               hold=["K_SPACE"]
               )
    # Set_Config(shift_left=["K_a"],
    #            shift_right=["K_d"],
    #            hard_drop=["K_w"],
    #            soft_drop=["K_s"],
    #            rotate_left=["K_j"],
    #            rotate_right=["K_k"],
    #            hold=["K_SPACE"]
    #            )
