from Widgets.base import *


class Button:
    def __init__(self, rect, **kwargs):
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2]
        self.height = rect[3]
        self.text = kwargs.get("text", "")
        self.font = kwargs.get("font", default_font)
        self.text_color = kwargs.get("text_font", (0, 0, 0))
        self.color = kwargs.get("color", [255, 255, 255])
        self.press_color = kwargs.get("press_color", (20, 20, 20))
        self.hover_color = kwargs.get("hover_color", self.color)
        self.ScaleOnHover = kwargs.get("scale_on_hover", False)
        self.scale = kwargs.get("scale", 0)

        self.max_width = self.width + self.scale

        self.normal_width = self.width
        self.normal_height = self.height
        self.normal_x = self.x
        self.normal_y = self.y
        self.normal_color = self.color

    def button(self, window):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height), 0, 3)
        if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
            if mouse_down:
                pygame.draw.rect(window, self.press_color, (self.x, self.y, self.width, self.height), 0, 3)
                return True
            else:
                pygame.draw.rect(window, self.hover_color, (self.x, self.y, self.width, self.height), 0, 3)
                if self.width < self.max_width and self.ScaleOnHover:
                    self.x -= .5
                    self.y -= .5
                    self.width += 1
                    self.height += 1
        else:
            pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height), 0, 3)
            self.x = self.normal_x
            self.y = self.normal_y
            self.width = self.normal_width
            self.height = self.normal_height

        text = self.font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        window.blit(text, text_rect)
        return False

    def show_toggled(self, window, color):
        pygame.draw.rect(window, color, (self.x, self.y, self.width, self.height), 0, 3)
