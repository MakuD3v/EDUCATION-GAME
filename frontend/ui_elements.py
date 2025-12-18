import pygame

class UIElement:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        pass

    def handle_event(self, event):
        pass

class Button(UIElement):
    def __init__(self, x, y, w, h, text, callback, color=(100, 200, 100)):
        super().__init__(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        txt_surf = self.font.render(self.text, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

class Label(UIElement):
    def __init__(self, x, y, text, font_size=36, color=(255, 255, 255)):
        super().__init__(x, y, 0, 0)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, font_size)

    def set_text(self, text):
        self.text = text

    def draw(self, surface):
        txt_surf = self.font.render(self.text, True, self.color)
        surface.blit(txt_surf, (self.rect.x, self.rect.y))

class Popup(UIElement):
    def __init__(self, x, y, w, h, message, dismiss_callback):
        super().__init__(x, y, w, h)
        self.message = message
        self.dismiss_callback = dismiss_callback
        self.font = pygame.font.Font(None, 32)
        self.btn_ok = Button(x + w//2 - 50, y + h - 60, 100, 40, "OK", self.dismiss_callback)

    def draw(self, surface):
        # Background
        pygame.draw.rect(surface, (50, 50, 80), self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 3)
        
        # Text
        lines = self.message.split('\n')
        for i, line in enumerate(lines):
            txt = self.font.render(line, True, (255, 255, 255))
            rect = txt.get_rect(center=(self.rect.centerx, self.rect.y + 40 + i*30))
            surface.blit(txt, rect)
            
        self.btn_ok.draw(surface)

    def handle_event(self, event):
        self.btn_ok.handle_event(event)

class MobileKeyButton(Button):
    """Hidden button to trigger keyboard on mobile."""
    def __init__(self, callback):
        super().__init__(700, 10, 80, 40, "KBD", callback, color=(100, 100, 100))

