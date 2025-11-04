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
        scale = resolution[0] / resolution_base[0]
        screen_x = (self.x - xcam) * scale
        screen_y = (self.y - ycam) * scale
        
        
        # Ajuster les offsets
        offset_x = int(49 * scale)
        offset_y = int(89 * scale)
        
        if self.debug_mod:
            rect_x = int((self.rect[0] * scale) + screen_x)
            rect_y = int((self.rect[1] * scale) + screen_y)
            rect_w = int(self.rect[2] * scale)
            rect_h = int(self.rect[3] * scale)
            pygame.draw.rect(self.screen, (255, 0, 255), (rect_x, rect_y, rect_w, rect_h), 2)
           
    
        self.screen.blit(self.img, (screen_x - offset_x, screen_y - offset_y))

    
    def return_rect(self):
        rect = pygame.Rect(self.rect[0] + self.x, self.rect[1] + self.y, self.rect[2], self.rect[3])
        return rect