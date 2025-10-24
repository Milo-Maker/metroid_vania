import pygame
class collectible(pygame.sprite.Sprite):
    def __init__(self, type, x,y, img, screen, ID, quantity=0, debug_mod = False):
        self.type = type
        self.x = x
        self.y = y
        self.screen = screen
        self.img = img
        self.quantity = quantity
        self.debug_mod=debug_mod
        self.ID= ID
        if self.type == "cash_bag":
            self.rect = (-29,-82,62,85)
    def draw(self, xcam, ycam, resolution, resolution_base):
        scale_x = resolution[0]/resolution_base[0]
        scale_y = resolution[1]/resolution_base[1]
        screen_x = (self.x - xcam) * scale_x
        screen_y = (self.y - ycam) * scale_y
        
        if self.debug_mod:
            pygame.draw.rect(self.screen, (255,0,255), (screen_x + self.rect[0],screen_y + self.rect[1],self.rect[2],self.rect[3]), 2)
        self.screen.blit(self.img, (screen_x-49, screen_y-89))
    
    def return_rect(self):
        rect = pygame.Rect(self.rect[0] + self.x, self.rect[1] + self.y, self.rect[2], self.rect[3])
        return rect