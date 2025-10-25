import pygame

class bouton(pygame.sprite.Sprite):
    def __init__(self, x, y, l, h, text, text_color, color, screen):
        
        self.rect=pygame.Rect(x,y,l,h)
        self.color=color
        self.screen=screen
        self.font=pygame.font.SysFont("comicsans", 50)
        self.text_surface=self.font.render(text, True, text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
        self.screen.blit(self.text_surface, self.text_rect)

    def is_pressed(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self.rect.collidepoint(event.pos)
            return False