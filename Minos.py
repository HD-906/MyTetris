import pygame
import numpy as np
import VarsAPI
from random import sample


class Mino:
    def __init__(self):
        self.DIM = VarsAPI.Play_Field_Dim.MINO_DIM
        self.Get_Image = VarsAPI.Get_Image_Func()

    def FreeDraw(self, surface, x, y, cell_colour, *, ghost: bool = False) -> bool:
        """
        Draws the mino with cell_cond colour on x, y and returns true without updating the play field
        if cell_cond is null, does not draw anything and returns false
        """
        if cell_colour == VarsAPI.Cell_Colour.NULL:
            return False

        block_img = self.Get_Image(cell_colour, ghost=ghost)
        surface.blit(block_img, (x, y))
        return True


class ActiveMino(Mino):
    spawn_position = VarsAPI.SPAWN

    def __init__(self, field_status=None):
        super().__init__()
        self.run = False
        self.in_game = True
        self.field_status = field_status
        self.id = VarsAPI.Minos.NULL_Piece
        self.__position = self.__y, self.__x = 0, 0
        self.y_lowest = self.__y
        self.orient = VarsAPI.Orient.UP
        self.occupy_init = self.occupy = ()  # ((int, int), (int, int), (int, int))
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.colour = VarsAPI.Cell_Colour.NULL
        self.width = VarsAPI.Play_Field_Dim.MINO_W
        self.height = VarsAPI.Play_Field_Dim.MINO_H
        self.is_exist = False
        self.lockable = False
        self.locked = False
        self.all_clr = False
        self.delay = VarsAPI.Delays.ARE
        self.lock_charged_value = 0
        self.movement = 0

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, new_position):
        self.__position = self.__y, self.__x = new_position

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, new_y):
        self.__y = new_y
        self.__position = self.__y, self.__x

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, new_x):
        self.__x = new_x
        self.__position = self.__y, self.__x

    def Reset_Posture(self):
        self.orient = VarsAPI.Orient.INIT
        self.occupy = self.occupy_init

    def Occupied(self) -> bool:
        border = VarsAPI.Play_Field_Dim.DIM[::-1]
        if not VarsAPI.In_Square(self.position, border) or \
                any(not VarsAPI.In_Square(VarsAPI.Add_Pos(self.position, position), border)
                    for position in self.occupy):
            return True

        if self.field_status[self.position] != VarsAPI.Cell_Colour.NULL or \
                any(self.field_status[VarsAPI.Add_Pos(self.position, position)] != VarsAPI.Cell_Colour.NULL
                    for position in self.occupy):
            return True

        return False

    def Position_Init(self, field_status=None) -> None:
        """
        Set the position of current mino to spawn and return True. If not possible, returns False
        """
        if field_status is not None:
            self.field_status = field_status
        elif self.field_status is None:
            return

        for position in self.spawn_position:
            self.position = position
            if not self.Occupied():
                self.y_lowest = self.y
                self.run = True
                return

        self.run = False

    def Check_Grounded(self):
        """
        Check if mino is grounded and sets self.lockable accordingly
        """
        old_position = self.position
        self.position = VarsAPI.Add_Pos(old_position, (-1, 0))
        self.lockable = self.Occupied()
        self.position = old_position

    def Check_Lock(self) -> tuple[bool, np.ndarray] | bool:
        """
        Updates movement count of piece and lock if needed
        Returns a tuple of self.in_game, self.field_status if locked, returns True if not locked
        """
        self.movement += 1
        self.Check_Grounded()
        if self.movement >= VarsAPI.MAX_MOVEMENT and self.lockable:
            self.Lock_Piece()
            return self.in_game, self.field_status
        return True

    def Check_Self_Lock(self, moved) -> tuple[bool, np.ndarray] | None:
        """
        Updates or clears lock delay based on whether mino is moved
        Returns a tuple of self.in_game, self.field_status if locked, returns None otherwise
        """
        if self.locked:
            return

        self.Check_Grounded()
        if not moved and self.lockable:
            self.lock_charged_value += 1
        else:
            self.lock_charged_value = 0

        if self.lock_charged_value >= VarsAPI.Delays.LOCK_DELAY:
            self.Lock_Piece()
            return self.in_game, self.field_status

    def Lock_Piece(self):
        """
        Updates the play field with the mino by its current state
        """
        if self.locked:
            return

        row_locked = {self.y}
        self.field_status[self.position] = self.colour
        for position in self.occupy:
            pos_y, pos_x = VarsAPI.Add_Pos(self.position, position)
            self.field_status[pos_y, pos_x] = self.colour
            row_locked.add(pos_y)

        self.in_game = any(row < 20 for row in row_locked)
        self.locked = True

    def Reset_Movement(self) -> tuple[bool, np.ndarray] | bool:
        self.Check_Grounded()
        if self.y_lowest > self.y:
            self.y_lowest = self.y
            self.movement = 0
        elif self.movement >= VarsAPI.MAX_MOVEMENT and self.lockable:
            self.Lock_Piece()
            return self.in_game, self.field_status
        return True

    def Act_Shift_R(self) -> tuple[bool, np.ndarray] | None | bool:
        """
        Sets occupy after shifting right 1 grid
        Returns a tuple of self.in_game, self.field_status if locked, True if not locked or None if not moved
        """
        if self.locked:
            return

        old_position = self.position
        self.position = VarsAPI.Add_Pos(old_position, (0, 1))
        if not self.Occupied():
            return self.Check_Lock()

        self.position = old_position

    def Act_Shift_L(self) -> tuple[bool, np.ndarray] | None | bool:
        """
        Sets occupy after shifting left 1 grid
        Returns a tuple of self.in_game, self.field_status if locked, True if not locked or None if not moved
        """
        if self.locked:
            return

        old_position = self.position
        self.position = VarsAPI.Add_Pos(old_position, (0, -1))
        if not self.Occupied():
            return self.Check_Lock()

        self.position = old_position

    def Act_Shift_D(self) -> tuple[bool, np.ndarray] | None | bool:
        """
        Sets occupy after falling down 1 grid
        Returns a tuple of self.in_game, self.field_status if locked, True if not locked or None if not moved
        """
        if self.locked:
            return

        old_position = self.position
        self.position = VarsAPI.Add_Pos(old_position, (-1, 0))
        if not self.Occupied():
            return self.Reset_Movement()

        self.position = old_position

    def Act_Hard_Drop(self) -> tuple[bool, np.ndarray] | None:
        """
        Sets orient and occupy after rotation left
        """
        if self.locked:
            return

        last_position = self.position
        while not self.Occupied():
            last_position = self.position
            self.position = VarsAPI.Add_Pos(last_position, (-1, 0))
        self.position = last_position
        self.Lock_Piece()
        return self.in_game, self.field_status

    def Check_Rotation(self, direction: VarsAPI.Dir) -> bool:
        """
        Checks on legal locations with wall-kick
        """
        check_lst = getattr(VarsAPI.Rotation_Test,
                            VarsAPI.Rotation_Test.status_dct[self.orient][direction])
        old_position, old_occupy = self.position, self.occupy
        self.occupy = tuple((-x, y) if direction is VarsAPI.Dir.RIGHT else (x, -y)
                            for y, x in old_occupy)
        for offset in check_lst:
            self.position = VarsAPI.Add_Pos(old_position, offset)
            if not self.Occupied():
                return True

        self.position, self.occupy = old_position, old_occupy
        return False

    def Act_Rotate_R(self) -> tuple[bool, np.ndarray] | None | bool:
        """
        Sets orient and occupy after rotation right
        Returns a tuple of self.in_game, self.field_status if locked, True if not locked or None if not moved
        """
        if self.locked:
            return

        if self.Check_Rotation(VarsAPI.Dir.RIGHT):
            self.orient = VarsAPI.Orient((self.orient.value + 1) % 4)
            self.y_lowest = min(self.y, self.y_lowest)
            return self.Check_Lock()

    def Act_Rotate_L(self) -> tuple[bool, np.ndarray] | None | bool:
        """
        Sets orient and occupy after rotation left
        Returns a tuple of self.in_game, self.field_status if locked, True if not locked or None if not moved
        """
        if self.locked:
            return

        if self.Check_Rotation(VarsAPI.Dir.LEFT):
            self.orient = VarsAPI.Orient((self.orient.value - 1) % 4)
            self.y_lowest = min(self.y, self.y_lowest)
            return self.Check_Lock()

    def Draw(self, surface):
        """
        Draws the mino to the play field by its current state without updating the play field
        """
        if self.locked:
            return

        if self.colour == VarsAPI.Cell_Colour.NULL:
            return

        cor = VarsAPI.Convert(*self.position)
        drawn_temp = {cor}
        super().FreeDraw(surface, *cor, self.colour)
        for y, x in self.occupy:
            x_cor = VarsAPI.Convert_x(self.x + x)
            y_cor = VarsAPI.Convert_y(self.y + y)
            drawn_temp.add((x_cor, y_cor))
            super().FreeDraw(surface, x_cor, y_cor, self.colour)

        # Draws ghost pieces
        old_position = last_position = self.position
        while not self.Occupied():
            last_position = self.position
            self.position = VarsAPI.Add_Pos(last_position, (-1, 0))
        self.position = last_position

        cor = VarsAPI.Convert(*self.position)
        if cor not in drawn_temp:
            super().FreeDraw(surface, *cor, self.colour, ghost=True)
        for y, x in self.occupy:
            x_cor = VarsAPI.Convert_x(self.x + x)
            y_cor = VarsAPI.Convert_y(self.y + y)
            if (x_cor, y_cor) not in drawn_temp:
                super().FreeDraw(surface, x_cor, y_cor, self.colour, ghost=True)

        self.position = old_position

    def Draw_Scale(self, surface, cell_colour, scale: float,
                   coordinates: tuple[int, int], offset: tuple[int, int]):
        """
        Draws the mino to the play field by its current state without updating the play field
        """
        if cell_colour == VarsAPI.Cell_Colour.NULL:
            return

        x_offset = self.x_offset * self.width * scale
        y_offset = self.y_offset * self.height * scale
        cor_x, cor_y = VarsAPI.Add_Pos(coordinates, offset)

        block_img = self.Get_Image(cell_colour)
        width = block_img.get_width()
        height = block_img.get_height()
        block_img = pygame.transform.scale(block_img, (int(width * scale), int(height * scale)))

        surface.blit(block_img, (cor_x + x_offset, cor_y + y_offset))

        for pos_y, pos_x in self.occupy:
            other_cor_x = int(cor_x + pos_x * self.width * scale + x_offset)
            other_cor_y = int(cor_y - pos_y * self.height * scale + y_offset)
            surface.blit(block_img, (other_cor_x, other_cor_y))


class S_Mino(ActiveMino):
    def __init__(self, field_status=None):
        super().__init__(field_status)
        self.is_exist = True
        self.id = VarsAPI.Minos.S_Piece
        self.occupy_init = self.occupy = ((0, -1), (1, 0), (1, 1))
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.colour = VarsAPI.Cell_Colour.GREEN
        self.Position_Init()


class Z_Mino(ActiveMino):
    def __init__(self, field_status=None):
        super().__init__(field_status)
        self.is_exist = True
        self.id = VarsAPI.Minos.Z_Piece
        self.occupy_init = self.occupy = ((0, 1), (1, 0), (1, -1))
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.colour = VarsAPI.Cell_Colour.RED
        self.Position_Init()


class L_Mino(ActiveMino):
    def __init__(self, field_status=None):
        super().__init__(field_status)
        self.is_exist = True
        self.id = VarsAPI.Minos.L_Piece
        self.occupy_init = self.occupy = ((0, -1), (0, 1), (1, 1))
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.colour = VarsAPI.Cell_Colour.ORANGE
        self.Position_Init()


class J_Mino(ActiveMino):
    def __init__(self, field_status=None):
        super().__init__(field_status)
        self.is_exist = True
        self.id = VarsAPI.Minos.J_Piece
        self.occupy_init = self.occupy = ((0, 1), (0, -1), (1, -1))
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.colour = VarsAPI.Cell_Colour.BLUE
        self.Position_Init()


class I_Mino(ActiveMino):
    def __init__(self, field_status=None):
        super().__init__(field_status)
        self.is_exist = True
        self.id = VarsAPI.Minos.I_Piece
        self.occupy_init = self.occupy = ((0, -1), (0, 1), (0, 2))
        self.x_offset = -0.5
        self.y_offset = -0.5
        self.colour = VarsAPI.Cell_Colour.CYAN
        self.Position_Init()

    def Check_Rotation(self, direction: VarsAPI.Dir) -> bool:
        """
        Checks on legal locations with wall-kick
        """
        check_lst = getattr(VarsAPI.Rotation_Test.I_mino,
                            VarsAPI.Rotation_Test.status_dct[self.orient][direction])
        old_position, old_occupy = self.position, self.occupy
        self.occupy = tuple((-x, y) if direction is VarsAPI.Dir.RIGHT else (x, -y)
                            for y, x in old_occupy)
        for offset in check_lst:
            self.position = VarsAPI.Add_Pos(old_position, offset)
            if not self.Occupied():
                return True

        self.position, self.occupy = old_position, old_occupy
        return False


class O_Mino(ActiveMino):
    def __init__(self, field_status=None):
        super().__init__(field_status)
        self.is_exist = True
        self.id = VarsAPI.Minos.O_Piece
        self.occupy_init = self.occupy = ((0, 1), (1, 0), (1, 1))
        self.x_offset = -0.5
        self.y_offset = 0.0
        self.colour = VarsAPI.Cell_Colour.YELLOW
        self.Position_Init()

    def Act_Rotate_R(self) -> tuple[bool, np.ndarray] | None | bool:
        """
        Sets orient and occupy after rotation right
        Returns a tuple of self.in_game, self.field_status if locked, True if not locked or None if not moved
        """
        if self.locked:
            return

        self.orient = VarsAPI.Orient((self.orient.value + 1) % 4)
        return self.Check_Lock()

    def Act_Rotate_L(self) -> tuple[bool, np.ndarray] | None | bool:
        """
        Sets orient and occupy after rotation left
        Returns a tuple of self.in_game, self.field_status if locked, True if not locked or None if not moved
        """
        if self.locked:
            return

        self.orient = VarsAPI.Orient((self.orient.value - 1) % 4)
        return self.Check_Lock()


class T_Mino(ActiveMino):
    def __init__(self, field_status=None):
        super().__init__(field_status)
        self.is_exist = True
        self.id = VarsAPI.Minos.T_Piece
        self.occupy_init = self.occupy = ((0, -1), (0, 1), (1, 0))
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.colour = VarsAPI.Cell_Colour.PURPLE
        self.Position_Init()
