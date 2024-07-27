import pygame
import VarsAPI


class NonInteractButton(VarsAPI.BaseObjImage):
    ID = 0

    def __init__(self, path: str, dim: tuple[int, int], x: int, y: int,
                 text: VarsAPI.BaseObjWithTxt, text_selected: VarsAPI.BaseObjWithTxt):
        image = VarsAPI.Load_image(path, dim)
        super().__init__(image, x, y)
        self.text = text
        self.text_selected = text_selected
        self.selected = False

        self.__id = self.ID
        Button.ID += 1

    @property
    def id(self):
        return self.__id

    @staticmethod
    def Write(surface, text, x, y):
        surface.blit(text, (x, y))

    def Draw(self, surface):
        super().Draw(surface)
        if self.selected and self.text_selected is not None:
            self.text_selected.Draw(surface)
        elif not self.selected and self.text is not None:
            self.text.Draw(surface)

    def __str__(self):
        return self.text.__str__()


class Button(VarsAPI.InputObj, NonInteractButton):
    def Act(self, surface):
        action = False

        if self.rect.collidepoint(self.pos) and self.clicked[0] or \
                self.selected and self.Key_Triggered(VarsAPI.Keys.confirm):
            action = True

        self.Draw(surface)

        return action


class PreviewField(VarsAPI.BaseObjRect):
    def __init__(self, rect: pygame.Rect, text: VarsAPI.BaseObjWithTxt | None = None):
        super().__init__(rect, VarsAPI.Colour.BLACK)
        self.text = text
        self.coordinates = self.x_cor, self.y_cor = VarsAPI.Dim.Hold_Field.COR
        self.offset = self.x_offset, self.y_offset = VarsAPI.Dim.Off_Set.MAIN

    def Draw(self, surface):
        """
        Draws the hold field and the hold mino if exist
        """
        super().Draw(surface)
        if self.text is not None:
            self.text.Draw(surface)
