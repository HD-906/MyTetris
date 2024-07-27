import numpy as np
import pygame
import Button
import VarsAPI


class Config(VarsAPI.MenuObj):
    def __init__(self):
        super().__init__()
        self.background_colour = VarsAPI.Colour.BLUE

        self.config_btn = self.Get_Button("ConfigTitle", False, new_name="Config")
        self.controls = VarsAPI.Get_Config(args=VarsAPI.Configs.all_configs)
        self.new_controls = {key: val.copy() for key, val in self.controls.items()}
        self.button_dct: dict[int, str] = {}
        self.name_button_dct: dict[str, Button.Button] = {}
        self.name_list = []
        self.key_list = []
        dummy_btn = self.Get_Button("Dummy", False)
        self.button_array = np.full((len(self.controls), VarsAPI.MAX_KEY_ASSIGN), dummy_btn)
        self.__current_select = self.__current_select_h = 0

        for i, (name, k_list) in enumerate(self.controls.items()):
            self.name_list.append(name)
            btn = self.Get_Button(VarsAPI.Cap_Str(name), False)
            self.key_list.append(btn)
            # j = 0
            # for j, k_name in enumerate(k_list):
            #     show_name = k_name.lstrip('K').lstrip('_')
            #     new_btn = self.Get_Button(VarsAPI.Cap_Str(name), offset=(190 + 150 * j, 0), new_name=show_name)
            #     self.button_array[i, j] = new_btn
            #     self.button_dct.update({new_btn.id: name})
                # self.name_button_dct.update({show_name: new_btn})

            for j in range(VarsAPI.MAX_KEY_ASSIGN):
                new_btn = self.Get_Button(VarsAPI.Cap_Str(name), offset=(190 + 150 * j, 0))#, new_name=VarsAPI.Keys.NULL)
                self.button_array[i, j] = new_btn
                self.button_dct.update({new_btn.id: name})

        self.max_select = VarsAPI.MAX_KEY_ASSIGN
        self.max_select_h = len(self.controls)

        self.button_array[self.__current_select, self.__current_select_h].selected = True

        text = VarsAPI.BaseObjWithTxt(
            "PRESS A KEY TO SET", VarsAPI.Dim.Set_Key_Window.font, 60, VarsAPI.Dim.Set_Key_Window.colour,
            (VarsAPI.Dim.Set_Key_Window.X + VarsAPI.Dim.Set_Key_Window.X_SHIFT,
             VarsAPI.Dim.Set_Key_Window.Y + VarsAPI.Dim.Set_Key_Window.Y_SHIFT)
        )
        self.set_obj = VarsAPI.RectTxtObj(
            *VarsAPI.Dim.Set_Key_Window.COR,
            *VarsAPI.Dim.Set_Key_Window.DIM,
            VarsAPI.Dim.Set_Key_Window.colour_background,
            text
        )
        self.btn_chosen = None
        self.setting = False
        self.apply_btn = self.Get_Button("Apply")
        self.reset_btn = self.Get_Button("Reset")
        self.action_btns = [self.apply_btn, self.reset_btn]
        self.action_max_select = len(self.action_btns)

    @property
    def current_select(self):
        return self.__current_select

    @current_select.setter
    def current_select(self, new_select):
        if self.__current_select_h >= 0:
            self.button_array[self.__current_select_h, self.__current_select].selected = False
            self.__current_select = new_select % self.max_select
            self.button_array[self.__current_select_h, self.__current_select].selected = True
        else:
            self.action_btns[self.__current_select].selected = False
            self.__current_select = new_select % self.action_max_select
            self.action_btns[self.__current_select].selected = True

    @property
    def current_select_h(self):
        return self.__current_select_h

    @current_select_h.setter
    def current_select_h(self, new_select_h):
        if self.__current_select_h >= 0:
            self.button_array[self.__current_select_h, self.__current_select].selected = False
        else:
            self.action_btns[self.__current_select].selected = False
        self.__current_select_h = VarsAPI.Select_with_Negative(new_select_h, self.max_select_h)
        if self.__current_select_h >= 0:
            self.button_array[self.__current_select_h, self.__current_select].selected = True
        else:
            self.__current_select = min(self.__current_select, self.action_max_select - 1)
            self.action_btns[self.__current_select].selected = True

    def Fill_Background(self, surface, colour=None):
        """
        Fills background with given colour and updates background colour
        if colour is not given, saved background colour will be used
        """
        if colour is not None:
            self.background_colour = colour
        surface.fill(self.background_colour)

    def Init_Config_Menu(self):
        self.name_button_dct.clear()
        self.new_controls = {key: val.copy() for key, val in self.controls.items()}
        for i, (name, k_list) in enumerate(self.controls.items()):
            j = 0
            for j, k_name in enumerate(k_list):
                show_name: str = k_name.lstrip('K').lstrip('_')
                # show_name = VarsAPI.SHOW_DIR.get(show_name, show_name)
                btn = self.button_array[i, j]
                btn.text.Edit_Text(show_name.upper())
                btn.text_selected.Edit_Text(show_name.upper())
                self.name_button_dct.update({show_name: btn})
            for j in range(j + 1, VarsAPI.MAX_KEY_ASSIGN):
                btn = self.button_array[i, j]
                btn.text.Edit_Text(VarsAPI.Keys.NULL)
                btn.text_selected.Edit_Text(VarsAPI.Keys.NULL)

    def Reset_Config_Menu(self):
        pass

    def Act_Config_Menu(self, surface):
        self.config_btn.Draw(surface)

        if self.Key_Triggered(VarsAPI.Keys.right):
            self.current_select += 1

        if self.Key_Triggered(VarsAPI.Keys.left):
            self.current_select -= 1

        if self.Key_Triggered(VarsAPI.Keys.down):
            self.current_select_h += 1

        if self.Key_Triggered(VarsAPI.Keys.up):
            self.current_select_h -= 1

        for key in self.key_list:
            key.Draw(surface)

        for button_row in self.button_array:
            self.Pass_Input(*button_row)
            for button in button_row:
                if button.Act(surface):
                    self.setting = True
                    self.btn_chosen = button

        self.Pass_Input(self.apply_btn)
        if self.apply_btn.Act(surface):
            self.controls = {key: val.copy() for key, val in self.new_controls.items()}
            VarsAPI.Set_Config(**self.controls)

        self.Pass_Input(self.reset_btn)
        if self.reset_btn.Act(surface):
            VarsAPI.Init_Config()
            self.controls = VarsAPI.Get_Config(args=VarsAPI.Configs.all_configs)
            self.new_controls = {key: val.copy() for key, val in self.controls.items()}
            self.Init_Config_Menu()

    def Act_Setting(self, surface) -> int | None:
        self.set_obj.Draw(surface)
        if self.Key_Triggered(VarsAPI.Keys.quit):
            self.setting = False
            self.Fill_Background(surface)
        elif self.triggered_keys:
            self.setting = False
            return self.triggered_keys.pop()

    def Assign_Key(self, key: str):
        old_key: str = self.btn_chosen.text.text_str
        if len(old_key) == 1:
            old_key = old_key.lower()
        self.btn_chosen.text.Edit_Text(key)
        self.btn_chosen.text_selected.Edit_Text(key)
        if len(key) == 1:
            key = key.lower()
        name: str = self.button_dct.get(self.btn_chosen.id)
        if old_key != VarsAPI.Keys.NULL:
            self.new_controls[name].remove(f"K_{old_key}")
        for val_lst in self.new_controls.values():
            if f"K_{key}" in val_lst:
                val_lst.remove(f"K_{key}")
                btn_to_null = self.name_button_dct.get(key)
                btn_to_null.text.Edit_Text(VarsAPI.Keys.NULL)
                btn_to_null.text_selected.Edit_Text(VarsAPI.Keys.NULL)
                break

        self.new_controls[name].append(f"K_{key}")
        self.name_button_dct[key] = self.btn_chosen

    def Act_Frame(self, surface):
        if self.setting:
            key: int | None = self.Act_Setting(surface)
            if key is not None:
                self.Assign_Key(VarsAPI.Keys.name_dct.get(key).upper())
                self.Fill_Background(surface)
        else:
            self.Act_Config_Menu(surface)

