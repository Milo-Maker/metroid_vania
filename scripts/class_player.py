import pygame
import math

class joueur(pygame.sprite.Sprite):
    def __init__(self, x, y, screen, debug_mod):
        
        self.x = x
        self.y = y
        self.vy = 0
        self.vx = 0
        self.états = 1 # 1=sol 2=en l'air
        self.direction = 1 # 1=droite -1=gauche
        self.vitesse=15
        self.jump_force = 30
        self.dash_force = 50
        self.dash_couldown = 0
        self.dash_couldown_max = 80
        self.last_y = y
        self.l = 89
        self.h = 163
        self.screen = screen
        self.animation_idle = []
        self.animation_walk = []
        self.animation_jump = []
        self.animation_dash = []
        self.animation_counter = 0
        self.animation_etat = 0 # 0=idle 1=walk 2=dash 2=jump 3=attack
        self.PATH = "img/joueur"
        for i in range(20):
            self.animation_idle.append(pygame.transform.scale(pygame.image.load(self.PATH + f"/Idle/{i}.png").convert_alpha(), (300,300)))
        for i in range(20):
            self.animation_walk.append(pygame.transform.scale(pygame.image.load(self.PATH + f"/Walk/{i}.png").convert_alpha(), (300,300)))
        for i in range(8):
            self.animation_jump.append(pygame.transform.scale(pygame.image.load(self.PATH + f"/Jump/{i}.png").convert_alpha(), (300,300)))
        for i in range(16):
            self.animation_dash.append(pygame.transform.scale(pygame.image.load(self.PATH + f"/Dash/{i}.png").convert_alpha(), (300,300)))  

        self.debug_mod_is_eanable = debug_mod  
        self.money = 0  
    
    def draw(self, xcam, ycam, resolution, resolution_base):


        if self.animation_etat == 0 and self.animation_counter > len(self.animation_idle) - 1:  
            self.animation_counter = 0
        if self.animation_etat == 1 and self.animation_counter > len(self.animation_walk) - 1:  
            self.animation_counter = 0
        if self.animation_etat == 2 and self.animation_counter > len(self.animation_jump) - 1:  
            self.animation_counter = 0  
        if self.animation_etat == 3 and self.animation_counter > len(self.animation_dash) - 1:
            self.animation_counter = 0
        scale_x = resolution[0]/resolution_base[0]
        scale_y = resolution[1]/resolution_base[1]
        screen_x = (self.x - xcam) * scale_x
        screen_y = (self.y - ycam) * scale_y
        
        #debug affichage hitbox
        if self.debug_mod_is_eanable:
            screen_l, screen_h = self.l * scale_x, self.h * scale_y
            pygame.draw.rect(self.screen, (0, 0, 255), (screen_x, screen_y, screen_l, screen_h), 2)

        if self.direction == -1:
            if self.animation_etat == 0:
                self.screen.blit(pygame.transform.flip(self.animation_idle[self.animation_counter], True, False), (screen_x - 105, screen_y - 72))
            elif self.animation_etat == 1:
                self.screen.blit(pygame.transform.flip(self.animation_walk[self.animation_counter], True, False), (screen_x - 105, screen_y - 72))
            elif self.animation_etat == 2:
                self.screen.blit(pygame.transform.flip(self.animation_jump[self.animation_counter], True, False), (screen_x - 105, screen_y - 72))
            elif self.animation_etat == 3:
                self.screen.blit(pygame.transform.flip(self.animation_dash[self.animation_counter], True, False), (screen_x - 105, screen_y - 72))
            
        else:
            if self.animation_etat == 0:
                self.screen.blit(self.animation_idle[self.animation_counter], (screen_x - 105, screen_y - 72))
            elif self.animation_etat == 1:
                self.screen.blit(self.animation_walk[self.animation_counter], (screen_x - 105, screen_y - 72))
            elif self.animation_etat == 2:
                self.screen.blit(self.animation_jump[self.animation_counter], (screen_x - 105, screen_y - 72))
            elif self.animation_etat == 3:
                self.screen.blit(self.animation_dash[self.animation_counter], (screen_x - 105, screen_y - 72))
            
    def collision_wall(self, rect_objet):
        rect_joueur = pygame.Rect(self.x, self.y, self.l, self.h)
        if rect_joueur.colliderect(rect_objet):
            return True
        return False

    def collide_items(self, rect_obj):
        rect_joueur = pygame.Rect(self.x, self.y, self.l, self.h)
        if rect_joueur.colliderect(rect_obj):
            return True
        return False

    
    def mouvementy(self, plat_collision):
        for _ in range(abs(math.ceil(self.vy))):
            if self.vy > 0:  # Descente
                self.y += 1
                self.états = 2
                for i in plat_collision:
                    if self.collision_wall(i):
                        self.y -= 1
                        self.vy = 0
                        self.états = 1
                        break
            elif self.vy < 0:  # Montée
                self.y -= 1
                for i in plat_collision:
                    if self.collision_wall(i):
                        self.y += 1
                        self.vy = 0
                        break
    
    def mouvementx(self, plat_collision):    
        for _ in range(abs(math.ceil(self.vx))):
            if self.vx > 0:  # Droite
                self.x += 1
                if not self.debug_mod_is_eanable:  
                    for i in plat_collision:
                        if self.collision_wall(i):
                            self.x -= 1
                            self.vx = 0
                            break
            elif self.vx < 0:  # Gauche
                self.x -= 1
                if not self.debug_mod_is_eanable:
                    for i in plat_collision:
                        if self.collision_wall(i):
                            self.x += 1
                            self.vx = 0
                            break