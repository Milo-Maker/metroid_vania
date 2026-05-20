import pygame
import random
import math

class particule():
    def __init__(self, x, y, vx, vy, couleur, taille, type, duree_vie=None):
        self.x = x
        self.y = y
        self.vx = vx  # Vitesse X
        self.vy = vy  # Vitesse Y
        self.couleur = couleur
        self.type = type # "flottante" ou autre
        self.taille = taille
        self.taille_initiale = taille
        self.duree_vie = duree_vie  # Frames avant disparition, ne disparait jamais si pas de duré de vie
        self.age = 0
        self.alpha = 255
    
    def update(self):
        """Met à jour la position et l'âge"""
        if self.type == "flottante":
            self.vy += random.random() - 0.5  # renvoi un nombre entre 0.5 et -0.5
            self.vx += random.random() - 0.5  
            self.vy=max(min(self.vy,2),-1)  # limite la vitesse verticale
            self.vx=max(min(self.vx,1),-1)  # limite la vitesse horizontale
            self.x += self.vx
            self.y += self.vy
        if self.duree_vie:
            self.age += 1
        
            # Réduction progressive de la taille et de l'alpha
            ratio_vie = 1 - (self.age / self.duree_vie)
            self.taille = max(self.taille_initiale * ratio_vie,1)
            self.alpha = int(255 * ratio_vie)

        
    
    def draw(self, screen, xcam=0, ycam=0):
        """Dessine la particule"""
        if self.taille > 0 and self.alpha > 0:
            # Surface avec transparence
            surface = pygame.Surface((int(self.taille * 2), int(self.taille * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.couleur, self.alpha), 
                             (int(self.taille), int(self.taille)), 
                             int(self.taille))
            screen.blit(surface, (int(self.x - xcam - self.taille), 
                                 int(self.y - ycam - self.taille)))
    
    def est_morte(self):
        """Vérifie si la particule doit être supprimée"""
        if self.duree_vie is None:
            return False
        return self.age >= self.duree_vie


class systemeParticules():
    def __init__(self):
        self.particules = []
    
    def creer_explosion(self, x, y, nombre=20, couleur=(255, 200, 50)):
        """Crée une explosion de particules"""
        for _ in range(nombre):
            angle = random.uniform(0, 2 * math.pi)
            vitesse = random.uniform(2, 8)
            vx = math.cos(angle) * vitesse
            vy = math.sin(angle) * vitesse
            taille = random.uniform(2, 6)
            duree = random.randint(20, 50)
            
            self.particules.append(particule(x, y, vx, vy, couleur, taille, "explosion", duree))
    
    def creer_trainee_dash(self, x, y, direction, couleur=(100, 200, 255)):
        """Crée une traînée de particules"""
        for _ in range(15):
            vx = random.uniform(-2, 2) - direction * 3
            vy = random.uniform(-1, 1)
            taille = random.uniform(2, 4)
            duree = random.randint(10, 17)
            yp=y + random.uniform(-60,60)
            xp= x + random.uniform(-20,20) + 10 * direction

            self.particules.append(particule(xp, yp, vx, vy, couleur, taille, "trainé",duree))
    
    def creer_etoiles_menu(self, largeur_ecran, hauteur_ecran, nombre=100):
        """Crée des étoiles flottantes pour le menu"""
        for _ in range(nombre):
            x = random.uniform(0, largeur_ecran)
            y = random.uniform(0, hauteur_ecran)
            taille = random.uniform(1, 3)
            vitesse_y = random.uniform(0.5, 2)
            couleur = (200, 200, 255)
            duree = random.randint(300, 500)
            p = particule(x, y, 0, vitesse_y, couleur, taille, "flottante", duree)
            self.particules.append(p)
        
    def update(self, largeur_ecran=None, hauteur_ecran=None):
        """Met à jour toutes les particules"""
        for i in self.particules[:]:  # Copie pour pouvoir supprimer
            i.update()
            
            # Supprimer les particules mortes
            if i.est_morte():
                if i.type == "flottante":
                    x = random.uniform(0, largeur_ecran)
                    y = random.uniform(0, hauteur_ecran)
                    taille = random.uniform(1, 3)
                    vitesse_y = random.uniform(0.5, 2)
                    couleur = (200, 200, 255)
                    duree = random.randint(300, 500)
                    p = particule(x, y, 0, vitesse_y, couleur, taille, "flottante", duree)
                    self.particules.append(p)
                    
                self.particules.remove(i)
    
    def draw(self, screen, xcam=0, ycam=0):
        """Dessine toutes les particules"""
        for i in self.particules:
            i.draw(screen, xcam, ycam)
    
    def clear(self):
        """Vide toutes les particules"""
        self.particules.clear()