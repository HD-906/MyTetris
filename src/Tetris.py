import random

import pygame
import Config
import Button
import PlayField
import VarsAPI

INIT_CONFIG = False
Play_Field = VarsAPI.Dim.Play_Field


# Button.Button.Write(surface, text, x, y)

# SOUND = pygame.mixer.Sound(VarsAPI.Path)
# SOUND.play()
# SOUND.stop()

# SOME_EVENT = pygame.USEREVENT + 1
# ELSE_EVENT = pygame.USEREVENT + 2
# pygame.event.post(pygame.event.Event(SOME_EVENT))
# for event in pygame.event.get():
#     if event.type == SOME_EVENT:
#         pass
#     if event.type == ELSE_EVENT:
#         pass


class Game(VarsAPI.MenuObj):
    def __init__(self, name: str = "Tetris"):
        super().__init__()
        self.run = True
        self.screen = pygame.display.set_mode(VarsAPI.Dim.Main.DIM)
        self.__name = name
        self.__menu_status = VarsAPI.Menu.start
        self.__menu_changed = True
        pygame.display.set_caption(self.__name)
        # load button images

        self.start_button = self.Get_Button("Start")
        self.config_button = self.Get_Button("Config")
        self.quit_button = self.Get_Button("Quit")
        self.button_list = [self.start_button, self.config_button, self.quit_button]
        self.__current_select = 0
        self.max_select = len(self.button_list)
        self.clicked = False

        self.config = Config.Config()

        self.play_field = None
        self.Init_Play_Field()

        self.button_list[self.__current_select].selected = True

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_name):
        self.__name = new_name
        pygame.display.set_caption(self.__name)

    @property
    def menu_status(self):
        return self.__menu_status

    @menu_status.setter
    def menu_status(self, new_status):
        self.__menu_status, self.__menu_changed = new_status, True

    def Fill_Background(self, colour=None):
        """
        Fills background with given colour and updates background colour
        if colour is not given, saved background colour will be used
        """
        if colour is not None:
            self.background_colour = colour
        self.screen.fill(self.background_colour)

    def Update_Input(self):
        """
        Updates current mouse and keyboard input
        """
        self.pos = pygame.mouse.get_pos()
        last_pressed, self.pressed = self.pressed, pygame.mouse.get_pressed()
        self.clicked = self.pressed if last_pressed is None \
            else tuple(press and not last for press, last in zip(self.pressed, last_pressed))
        self.current_keys = VarsAPI.Get_Keys_Pressed(pygame.key.get_pressed())
        self.current_input = (self.pos, self.pressed, self.current_keys)

    def Init_Play_Field(self):
        """
        Initialize an empty playfield
        """
        self.play_field = PlayField.PlayField(
            VarsAPI.Path.play_field, Play_Field.DIM, Play_Field.X, Play_Field.Y,
            # add a piece in hold for DPC practice
            # VarsAPI.Minos.S_Piece
        )

    def Main_Menu_frame(self):
        """
        action within 1 frame in start of menu
        """
        if self.__menu_changed:
            self.Fill_Background(VarsAPI.Colour.BLUE)
            self.__menu_changed = False

        if self.Key_Triggered(VarsAPI.Keys.right | VarsAPI.Keys.down):
            self.current_select += 1

        if self.Key_Triggered(VarsAPI.Keys.left | VarsAPI.Keys.up):
            self.current_select -= 1

        self.Pass_Input("start_button", "config_button", "quit_button")
        if self.start_button.Act(self.screen):
            self.menu_status = VarsAPI.Menu.in_game

        if self.config_button.Act(self.screen):
            self.menu_status = VarsAPI.Menu.config

        elif self.quit_button.Act(self.screen) or self.Key_Triggered(VarsAPI.Keys.quit):
            self.run = False

    def Config_frame(self):
        """
        action within 1 frame in config
        """
        if self.__menu_changed:
            self.config.Fill_Background(self.screen)
            self.__menu_changed = False
            self.config.Init_Config_Menu()

        if self.Key_Triggered(VarsAPI.Keys.quit) and not self.config.setting:
            self.menu_status = VarsAPI.Menu.start
            return

        self.Pass_Input("config")
        self.config.Act_Frame(self.screen)

    def Play_Screen_frame(self):
        """
        action within 1 frame in game
        """
        if self.__menu_changed:
            self.Init_Play_Field()
            self.Fill_Background(VarsAPI.Colour.YELLOW)
            self.__menu_changed = False

        if self.play_field.in_game:
            self.play_field.Act(self.screen, *self.current_input)
        else:
            self.play_field.end_obj.Draw(self.screen)

        # Erase 3/4 of the 21st row
        erase_field = pygame.rect.Rect(VarsAPI.Dim.Play_Field.X, 0, VarsAPI.Dim.Play_Field.W, VarsAPI.Dim.Play_Field.Y)
        pygame.draw.rect(self.screen, self.background_colour, erase_field)

        if self.Key_Triggered(VarsAPI.Keys.quit):
            self.menu_status = VarsAPI.Menu.start
            return

        if self.Key_Triggered({pygame.K_r}):
            self.Init_Play_Field()

    def Run(self, *, fps=VarsAPI.Delays.FPS):
        """
        Main run method
        """
        if not self.run:
            self.__init__(self.name)

        clock = pygame.time.Clock()
        self.screen.fill(self.background_colour)
        # run loop
        while self.run:
            clock.tick(fps)
            self.Update_Input()
            match self.menu_status:
                case VarsAPI.Menu.start:
                    self.Main_Menu_frame()
                case VarsAPI.Menu.config:
                    self.Config_frame()
                case VarsAPI.Menu.in_game:
                    self.Play_Screen_frame()

            # event handler
            for event in pygame.event.get():
                # X is clicked
                if event.type == pygame.QUIT:
                    self.run = False

            pygame.display.update()
            self.buffer_keys = self.current_keys

        pygame.quit()
        self.run = False


if __name__ == "__main__":
    if INIT_CONFIG:
        VarsAPI.Init_Config()
        print("Settings Initialized")

    Game().Run()
