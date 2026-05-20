import pygame 
import math

class projectile_magie():
    def __init__(self, x, y, type, degats, screen, xcam=0, ycam=0, scale=1.0):
        self.pos = pygame.Vector2(x, y)
        
        # Obtenir la position de la souris dans le monde en inversant la projection écran
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        mouse_world_x = mouse_pos.x / scale + xcam
        mouse_world_y = mouse_pos.y / scale + ycam
        souris = pygame.Vector2(mouse_world_x, mouse_world_y) - self.pos
        
        self.vitesse = 12  # Vitesse de 12 pour un feeling plus réactif
        self.type = type # en fonction du sort : sort 1 = 1
        
        self.couleur = (150, 50, 175)
        self.taille = 20
        self.degats = degats
        self.screen = screen
        self.ori = math.atan2(souris[1], souris[0])
        self.mouvement = pygame.Vector2(math.cos(self.ori), math.sin(self.ori)) * self.vitesse
        
    def update(self):
        """Met à jour la position du projectile dans le monde"""
        self.pos += self.mouvement
    
    def draw(self, xcam=0, ycam=0, scale=1.0):
        """Dessine le projectile en appliquant la caméra et l'échelle"""
        screen_x = (self.pos[0] - xcam) * scale
        screen_y = (self.pos[1] - ycam) * scale
        scaled_taille = self.taille * scale
        pygame.draw.circle(self.screen, self.couleur, 
                           (int(screen_x), int(screen_y)), 
                           int(scaled_taille))
    
    def get_rect(self):
        """Retourne le rectangle de collision du projectile (coordonnées monde)"""
        return pygame.Rect(self.pos[0] - self.taille, self.pos[1] - self.taille, self.taille * 2, self.taille * 2)
    
    def proportion(self, a,b):
        total=a+b
        if total==0:
            return 0.5,0.5
        return a/total,b/total