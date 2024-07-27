import pygame
import numpy as np
import VarsAPI
import Minos
from random import sample


class PlayField(VarsAPI.BaseObjImage):
    mino_type = VarsAPI.Minos.all_pieces
    mino_count = len(VarsAPI.Minos.all_pieces)

    def __init__(self, path: str, dim: tuple[int, int], x: int, y: int, init_hold: str | None = None):
        image = VarsAPI.Load_image(path, dim)
        super().__init__(image, x, y)
        self.in_game = True
        self.field_status = np.full((VarsAPI.Play_Field_Dim.H, VarsAPI.Play_Field_Dim.W),
                                    VarsAPI.Cell_Colour.NULL.value)
        self.draw_mino = Minos.Mino()
        init_mino_bag = sample(self.mino_type, self.mino_count) + sample(self.mino_type, self.mino_count)
        self.minos_info = {VarsAPI.Mino_Bag.idx: 0, VarsAPI.Mino_Bag.bag: init_mino_bag}
        self.current_mino = getattr(Minos, f"{self.Get_Mino_Id()}_Mino")(self.field_status)
        self.current_pos = self.current_mino.position
        self.hold_field = HoldField(VarsAPI.Load_Rect_From_Dim(VarsAPI.Dim.Hold_Field),
                                    self.Get_Mino(init_hold))
        self.hold_lock = False
        self.next_field = NextField(self.minos_info)
        self.controls = VarsAPI.Get_Config(args=VarsAPI.Configs.all_configs)
        for key, val in self.controls.items():
            self.controls[key] = {getattr(pygame, attr) for attr in val}

        text = VarsAPI.BaseObjWithTxt(
            "GAME OVER", VarsAPI.Dim.Game_Over.font, 60, VarsAPI.Dim.Game_Over.colour,
            (VarsAPI.Dim.Game_Over.X + VarsAPI.Dim.Game_Over.X_SHIFT,
             VarsAPI.Dim.Game_Over.Y + VarsAPI.Dim.Game_Over.Y_SHIFT)
        )
        self.end_obj = VarsAPI.RectTxtObj(
            *VarsAPI.Dim.Game_Over.COR,
            *VarsAPI.Dim.Game_Over.DIM,
            VarsAPI.Dim.Game_Over.colour_background,
            text
        )
        self.moved = False
        self.current_keys = set()
        self.buffer_keys = set()
        self.shift_status = VarsAPI.Dir.NULL
        self.shift_charged_dct = {
            VarsAPI.Dir.RIGHT: 0,
            VarsAPI.Dir.LEFT: 0,
            VarsAPI.Dir.DOWN: 0
        }
        self.gravity = self.base_gravity = 1
        self.soft_drop = False

        # For rows clearing
        self.row_nums_to_clear = []
        self.perfect_clr = False
        self.delay = 0
        self.delay_triggered = False
        self.is_cleared = False

    @property
    def mino_bag(self):
        return self.minos_info[VarsAPI.Mino_Bag.bag]

    @property
    def mino_bag_idx(self):
        return self.minos_info[VarsAPI.Mino_Bag.idx]

    @mino_bag_idx.setter
    def mino_bag_idx(self, new_idx):
        self.minos_info[VarsAPI.Mino_Bag.idx] = new_idx

    def Get_Mino(self, name: str):
        if name is None:
            return Minos.ActiveMino()
        return getattr(Minos, f"{name}_Mino")(self.field_status)

    def Get_Mino_Id(self, n: int = 0) -> str:
        return self.mino_bag[self.mino_bag_idx + n]

    def Next_Bag(self):
        self.mino_bag[:self.mino_count], self.mino_bag[self.mino_count:] = \
            self.mino_bag[self.mino_count:], sample(self.mino_type, self.mino_count)
        self.mino_bag_idx -= self.mino_count

    def Change_Mino_Init(self):
        self.current_pos = self.current_mino.position
        self.hold_lock = False
        self.moved = False
        self.shift_status = VarsAPI.Dir.NULL
        self.shift_charged_dct = {
            VarsAPI.Dir.RIGHT: 0,
            VarsAPI.Dir.LEFT: 0,
            VarsAPI.Dir.DOWN: 0
        }
        self.gravity = self.base_gravity = 1
        self.soft_drop = False

    def Next_Mino_Init(self):
        self.mino_bag_idx += 1
        if self.mino_bag_idx >= self.mino_count:
            self.Next_Bag()
        self.current_mino = self.next_field.field_lst[-1].mino
        self.current_mino.Position_Init(self.field_status)
        self.next_field.update_fields()
        if not self.current_mino.run:
            self.in_game = False
        self.Change_Mino_Init()

    def Hold_Mino(self):
        if self.hold_field.mino.is_exist:
            self.current_mino.Reset_Posture()
            self.current_mino, self.hold_field.mino = self.hold_field.mino, self.current_mino
            self.current_mino.Position_Init(self.field_status)
            self.current_pos = self.current_mino.position
        else:
            self.current_mino.Reset_Posture()
            self.hold_field.mino = self.current_mino
            self.Next_Mino_Init()

        self.hold_lock = True

    def Charge_And_Check(self, direction: VarsAPI.Dir):
        """
        Checks if charging value satisfy shift condition
        """
        self.shift_charged_dct[direction] += 1
        val_to_check = self.shift_charged_dct[direction] - VarsAPI.Delays.DAS
        return self.shift_status is direction and val_to_check >= 0 and val_to_check % VarsAPI.Delays.ARR == 0

    def Handle_Movement(self, act_return: tuple[bool, np.ndarray] | bool | None):
        """
        Updates self.in_game, self.field_status if act_return is a tuple
        Updates self.moved to True if act_return is True
        """
        if isinstance(act_return, tuple):  # Locked
            self.in_game, self.field_status = act_return
        elif act_return is True:  # Moved
            self.moved = True

    def Mino_Fall(self):
        self.shift_charged_dct[VarsAPI.Dir.DOWN] += self.gravity
        if self.shift_charged_dct[VarsAPI.Dir.DOWN] >= VarsAPI.Delays.FALL_FRAME:
            self.Handle_Movement(self.current_mino.Act_Shift_D())
            self.shift_charged_dct[VarsAPI.Dir.DOWN] %= VarsAPI.Delays.FALL_FRAME

    def Check_For_Clear(self):
        """
        Clears row when entire row is filled with minos
        """
        self.row_nums_to_clear = [row for row in range(VarsAPI.Play_Field_Dim.H)
                                  if VarsAPI.Cell_Colour.NULL not in self.field_status[row]]
        self.perfect_clr = all(
            all(self.field_status[row] == VarsAPI.Cell_Colour.NULL) for row in range(VarsAPI.Play_Field_Dim.H)
            if row not in self.row_nums_to_clear)
        clr_delay = VarsAPI.Delays.CLR_DELAY.get(len(self.row_nums_to_clear), VarsAPI.Delays.CLR_DELAY.get("default"))
        self.delay -= VarsAPI.Delays.CLR_DELAY.get("PC", clr_delay) if self.perfect_clr else clr_delay

    def Clear_Rows(self):
        """
        Clears row when entire row is filled with minos
        """
        self.field_status = np.delete(self.field_status, self.row_nums_to_clear, axis=0)
        rows_to_append = np.full((len(self.row_nums_to_clear), VarsAPI.Play_Field_Dim.W),
                                 VarsAPI.Cell_Colour.NULL.value)
        self.field_status = np.append(self.field_status, rows_to_append, axis=0)
        self.row_nums_to_clear = []
        self.perfect_clr = False
        self.is_cleared = True

    def Act_Triggered(self, key):
        match key:
            case VarsAPI.Configs.shift_left:
                self.Handle_Movement(self.current_mino.Act_Shift_L())
                if self.in_game:
                    self.shift_charged_dct[VarsAPI.Dir.LEFT] += 1
                    self.shift_status = VarsAPI.Dir.LEFT

            case VarsAPI.Configs.shift_right:
                self.Handle_Movement(self.current_mino.Act_Shift_R())
                if self.in_game:
                    self.shift_charged_dct[VarsAPI.Dir.RIGHT] += 1
                    self.shift_status = VarsAPI.Dir.RIGHT

            case VarsAPI.Configs.hard_drop:
                self.Handle_Movement(self.current_mino.Act_Hard_Drop())

            case VarsAPI.Configs.soft_drop:
                self.soft_drop = True
                self.gravity *= VarsAPI.SOFT_DROP_MULTIPLIER

            case VarsAPI.Configs.rotate_left:
                self.Handle_Movement(self.current_mino.Act_Rotate_L())

            case VarsAPI.Configs.rotate_right:
                self.Handle_Movement(self.current_mino.Act_Rotate_R())

            case VarsAPI.Configs.hold:
                if not self.hold_lock:
                    self.Hold_Mino()

    def Act_Held(self, key):
        match key:
            case VarsAPI.Configs.shift_left:
                if self.shift_status is VarsAPI.Dir.NULL:
                    self.shift_status = VarsAPI.Dir.LEFT
                if self.Charge_And_Check(VarsAPI.Dir.LEFT):
                    self.Handle_Movement(self.current_mino.Act_Shift_L())

            case VarsAPI.Configs.shift_right:
                if self.shift_status is VarsAPI.Dir.NULL:
                    self.shift_status = VarsAPI.Dir.RIGHT
                if self.Charge_And_Check(VarsAPI.Dir.RIGHT):
                    self.Handle_Movement(self.current_mino.Act_Shift_R())

            case VarsAPI.Configs.soft_drop:
                if not self.soft_drop:
                    self.soft_drop = True
                    self.gravity *= VarsAPI.SOFT_DROP_MULTIPLIER

    def Act_Inactive(self, key):
        match key:
            case VarsAPI.Configs.shift_left:
                self.shift_charged_dct[VarsAPI.Dir.LEFT] = 0
                if self.shift_status is VarsAPI.Dir.LEFT:
                    self.shift_status = VarsAPI.Dir.NULL

            case VarsAPI.Configs.shift_right:
                self.shift_charged_dct[VarsAPI.Dir.RIGHT] = 0
                if self.shift_status is VarsAPI.Dir.RIGHT:
                    self.shift_status = VarsAPI.Dir.NULL

            case VarsAPI.Configs.soft_drop:
                if self.soft_drop:
                    self.soft_drop = False
                    self.gravity = self.base_gravity

    def Act(self, surface, *current_input) -> bool:
        if self.current_mino.locked and self.in_game:
            if not self.delay_triggered:
                self.Check_For_Clear()
                self.delay_triggered = True
            elif self.delay < VarsAPI.Delays.ARE:
                self.delay += 1
                if not self.is_cleared and self.delay >= 0:
                    self.Clear_Rows()
            else:
                self.Next_Mino_Init()
                self.delay = 0
                self.delay_triggered = False
                self.is_cleared = False

        self.buffer_keys = self.current_keys
        pos, pressed, self.current_keys = current_input
        triggered_keys: set = self.current_keys - self.buffer_keys
        for mapped_action, keys_set in self.controls.items():
            if not keys_set.isdisjoint(self.current_keys):
                if not keys_set.isdisjoint(triggered_keys):
                    self.Act_Triggered(mapped_action)
                else:
                    self.Act_Held(mapped_action)
            else:
                self.Act_Inactive(mapped_action)
        self.Mino_Fall()
        self.Handle_Movement(self.current_mino.Check_Self_Lock(self.moved))

        self.moved = False
        self.Draw(surface)

        return self.in_game

    def Draw(self, surface):
        """
        Draws the play field with all existing minos visible
        """
        super().Draw(surface)
        self.hold_field.Draw(surface)
        for sub_field in self.next_field.field_lst:
            sub_field.Draw(surface)

        for y, row in enumerate(self.field_status[:VarsAPI.Play_Field_Dim.H_SHOWN + 1]):
            for x, cell in enumerate(row):
                self.draw_mino.FreeDraw(surface, *VarsAPI.Convert(y, x), cell)

        self.current_mino.Draw(surface)


class NextField:
    def __init__(self, mino_info: dict[VarsAPI.Mino_Bag, int | list]):
        self.__mino_info = mino_info
        self.total_next = VarsAPI.TOTAL_NEXT
        self.field_lst: list[PreviewField] = [
            NextFieldOther(
                VarsAPI.Load_Rect_From_Dim(
                    VarsAPI.Dim.Next_Field, x=f"X{field_id}", y=f"Y{field_id}", w="W1", h="H1"
                ),
                getattr(Minos, f"{self.Get_Mino_Id(field_id + 1)}_Mino")(None),
                field_id
            )
            for field_id in range(self.total_next - 1, 0, -1)
        ]
        self.field_lst.append(
            NextFieldText(
                VarsAPI.Load_Rect_From_Dim(
                    VarsAPI.Dim.Next_Field, x="X0", y="Y0", w="W0", h="H0"
                ),
                getattr(Minos, f"{self.Get_Mino_Id(1)}_Mino")(None)
            )
        )

    @property
    def mino_bag(self):
        return self.__mino_info[VarsAPI.Mino_Bag.bag]

    @property
    def mino_bag_idx(self):
        return self.__mino_info[VarsAPI.Mino_Bag.idx]

    def Get_Mino_Id(self, n: int = 0) -> str:
        return self.mino_bag[self.mino_bag_idx + n]

    def update_fields(self):
        next_mino = getattr(Minos, f"{self.Get_Mino_Id(self.total_next)}_Mino")()
        for field in self.field_lst:
            field.mino, next_mino = next_mino, field.mino


class PreviewField(VarsAPI.BaseObjRect):
    def __init__(self, rect: pygame.Rect, mino,
                 scale: float = VarsAPI.Dim.Show_Scale.MAIN, text: VarsAPI.BaseObjWithTxt | None = None):
        super().__init__(rect, VarsAPI.Colour.BLACK)
        self.mino = mino
        self.scale = scale
        self.text = text
        self.coordinates = self.x_cor, self.y_cor = VarsAPI.Dim.Hold_Field.COR
        self.offset = self.x_offset, self.y_offset = VarsAPI.Dim.Off_Set.MAIN

    def Draw(self, surface):
        """
        Draws the hold field and the hold mino if exist
        """
        super().Draw(surface)
        self.mino.Draw_Scale(surface, self.mino.colour, self.scale, self.coordinates, self.offset)
        if self.text is not None:
            self.text.Draw(surface)


class NextFieldText(PreviewField):
    def __init__(self, rect: pygame.Rect, mino: Minos.ActiveMino):
        next_txt_obj = VarsAPI.BaseObjWithTxt("NEXT", VarsAPI.Text.font, VarsAPI.Text.size, VarsAPI.Text.colour)
        x = VarsAPI.Dim.Next_Field.X0 + (VarsAPI.Dim.Next_Field.W0 - next_txt_obj.text.get_width()) // 2
        y = VarsAPI.Dim.Next_Field.Y0
        next_txt_obj.Update_Coordinates(x, y)
        super().__init__(rect, mino, text=next_txt_obj)
        self.coordinates = self.x_cor, self.y_cor = VarsAPI.Dim.Next_Field.COR0


class NextFieldOther(PreviewField):
    def __init__(self, rect: pygame.Rect, mino: Minos.ActiveMino, field_id: int):
        super().__init__(rect, mino, VarsAPI.Dim.Show_Scale.OTHER)
        cor = getattr(VarsAPI.Dim.Next_Field, f"COR{field_id}")
        self.coordinates = self.x_cor, self.y_cor = cor
        self.offset = self.x_offset, self.y_offset = VarsAPI.Dim.Off_Set.OTHER


class HoldField(PreviewField):
    def __init__(self, rect: pygame.Rect, mino: Minos.ActiveMino):
        hold_txt_obj = VarsAPI.BaseObjWithTxt("HOLD", VarsAPI.Text.font, VarsAPI.Text.size, VarsAPI.Text.colour)
        x = VarsAPI.Dim.Hold_Field.X + (VarsAPI.Dim.Hold_Field.W - hold_txt_obj.text.get_width()) // 2
        y = VarsAPI.Dim.Hold_Field.Y
        hold_txt_obj.Update_Coordinates(x, y)
        super().__init__(rect, mino, text=hold_txt_obj)
