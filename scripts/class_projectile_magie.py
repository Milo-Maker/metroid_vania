import pygame 
import math

class projectile_magie():
    def __init__(self, x, y, type, degats, screen):
        
        self.pos=pygame.Vector2(x,y)
        souris = pygame.Vector2(pygame.mouse.get_pos())- self.pos
        self.vitesse = 6
        
        self.type = type #en fonction du sort : sort 1 = 1
        
        self.couleur = (150,50,175)
        self.taille = 20
        self.degats = degats
        self.screen = screen
        self.ori=math.atan2(souris[1],souris[0])
        self.mouvement=pygame.Vector2(math.cos(self.ori),math.sin(self.ori)) * self.vitesse
        
    
    def update(self):
        """Met à jour la position du projectile"""
        
        self.pos += self.mouvement
    
    def draw(self, xcam=0, ycam=0):
        """Dessine le projectile"""
        pygame.draw.circle(self.screen, self.couleur, 
                           (int(self.pos[0] - xcam), int(self.pos[1] -ycam)), 
                           int(self.taille))
    
    def get_rect(self):
        """Retourne le rectangle de collision du projectile"""
        return pygame.Rect(self.pos[0] - self.taille, self.pos[1] - self.taille, self.taille * 2, self.taille * 2)
    
    def proportion(self, a,b):
        total=a+b
        if total==0:
            return 0.5,0.5
        return a/total,b/total