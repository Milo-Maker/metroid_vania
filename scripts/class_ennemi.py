import pygame
import math

class ennemi(pygame.sprite.Sprite):
    def __init__(self, type, x, y, screen, debug_mod):
        self.type = type
        self.x = x
        self.y = y - 45
        self.screen = screen
        self.debug_mod = debug_mod
        
        # Stats
        self.vie = 100
        self.vie_max = 100
        self.vitesse = 3
        self.degats = 10
        self.vx = 0
        self.vy = 0
        self.direction = 1  # 1=droite, -1=gauche
        
        # Hitbox
        if self.type == "slime_1":
            self.l = 55  # largeur
            self.h = 45  # hauteur
            self.sprite_extra = 15  # pour le dessin du sprite
        # Animation
        self.animation_counter = 0
        self.animation = []
        
        # Barre de vie au-dessus de la tête
        from scripts.class_barre import barre
        self.barre_vie = barre(0, -20, 80, 15, (50, 50, 50), (200, 50, 50), avec_brillance=False, avec_texte=False)
        
        # Charger les animations selon le type
        self.charger_animations()
        self.hit_timer = 0
                
    def charger_animations(self):
        """Charge les sprites selon le type d'ennemi"""
        if self.type == "slime_1":
            for i in range(30):
                self.animation.append(pygame.image.load(f"img/ennemis/slime_1/{i}.png").convert_alpha())
    
    def draw(self, xcam, ycam, resolution, resolution_base):
        scale = resolution[0] / resolution_base[0]
        screen_x = (self.x - xcam) * scale
        screen_y = (self.y - ycam) * scale
        
        # Décrémenter le hit timer
        if self.hit_timer > 0:
            self.hit_timer -= 1
            
        # Clignotement si touché (1 frame sur 3 masquée)
        if self.hit_timer > 0 and (self.hit_timer // 3) % 2 == 0:
            # Dessiner seulement la barre de vie
            barre_x = screen_x - 10
            barre_y = screen_y - 25
            self.barre_vie.x = barre_x
            self.barre_vie.y = barre_y
            self.barre_vie.draw(self.screen, self.vie, self.vie_max, "", scale)
            return

        # Debug hitbox
        if self.debug_mod:
            rect_w = int(self.l * scale)
            rect_h = int(self.h * scale)
            pygame.draw.rect(self.screen, (255, 0, 255), (screen_x, screen_y, rect_w, rect_h), 2)

        # Afficher le sprite
        
        scaled_sprite = pygame.transform.scale(self.animation[self.animation_counter], (int((self.l+self.sprite_extra) * scale), int((self.h+self.sprite_extra) * scale)))
        if self.direction == -1:
            scaled_sprite = pygame.transform.flip(scaled_sprite, True, False)
        self.screen.blit(scaled_sprite, (screen_x-8*scale, screen_y-8*scale))

        # Barre de vie au-dessus de la tête
        barre_x = screen_x - 10  # Centré au-dessus de l'ennemi
        barre_y = screen_y - 25
        
        # On ajuste la position de la barre pour la caméra
        self.barre_vie.x = barre_x
        self.barre_vie.y = barre_y
        self.barre_vie.draw(self.screen, self.vie, self.vie_max, "", scale)
    
    def update(self, plat_collision):
        """IA basique : patrouille gauche-droite"""
        # Déplacement
        self.vx = self.vitesse * self.direction
        
        # Gravité
        self.vy += 1
        
        # Mouvement (tu peux réutiliser la logique du joueur)
        self.mouvementx(plat_collision)
        self.mouvementy(plat_collision)
        self.animation_counter += 1
        if self.animation_counter >= len(self.animation):
            self.animation_counter = 0
        
    
    def collision_wall(self, rect_objet, get_fall=False):
        if get_fall:
            rect_ennemi = pygame.Rect(self.x+self.l*self.direction, self.y + 1, self.l, self.h)
        else :
            rect_ennemi = pygame.Rect(self.x, self.y, self.l, self.h)
        return rect_ennemi.colliderect(rect_objet)
    
    def mouvementx(self, plat_collision):
        # Copie de ta logique du joueur
        for _ in range(abs(math.ceil(self.vx))):
            if self.vx > 0:
                self.x += 1
                for i in plat_collision:
                    
                    if self.collision_wall(i):
                        print("collision droite")
                        self.x -= 1
                        self.direction = -1  # Change de direction
                        break
                    if self.direction == -1:
                        break  # Sort de la boucle si la direction a changé
                        

            elif self.vx < 0:
                self.x -= 1
                for i in plat_collision:
                    if self.collision_wall(i):
                        print("collision gauche")
                        self.x += 1
                        self.direction = 1
                        break
                    
                        
                if self.direction == 1:
                    break  # Sort de la boucle si la direction a changé
        
        # Vérifie si le sol est présent devant l'ennemi
        a=False
        for i in plat_collision:
            if self.collision_wall(i, get_fall=True):
                a=True
                break
        
        if not a:
            self.direction *= -1  # Change de direction s'il n'y a pas de sol
                
        
    def mouvementy(self, plat_collision):
        # Pareil que le joueur
        for _ in range(abs(math.ceil(self.vy))):
            if self.vy > 0:
                self.y += 1
                for i in plat_collision:
                    if self.collision_wall(i):
                        self.y -= 1
                        self.vy = 0
                        break
            elif self.vy < 0:
                self.y -= 1
                for i in plat_collision:
                    if self.collision_wall(i):
                        self.y += 1
                        self.vy = 0
                        break
    
    def prendre_degats(self, degats):
        """Réduit la vie de l'ennemi"""
        self.vie -= degats
        self.hit_timer = 15  # Active le clignotement pour 15 frames
        if self.vie <= 0:
            return True  # Ennemi mort
        return False