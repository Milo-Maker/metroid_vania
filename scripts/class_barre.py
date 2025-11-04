import pygame

class barre:
    def __init__(self, x, y, largeur, hauteur, couleur_fond, couleur_barre, avec_bordure=True, avec_brillance=True, avec_texte=True):
        self.x = x
        self.y = y
        self.largeur = largeur
        self.hauteur = hauteur
        self.couleur_fond = couleur_fond  # Ex: (50, 50, 50)
        self.couleur_barre = couleur_barre  # Ex: [(200, 20, 20), (150, 50, 20)] pour dégradé
        self.avec_bordure = avec_bordure
        self.avec_brillance = avec_brillance
        self.avec_texte = avec_texte
    
    def draw(self, screen, valeur_actuelle, valeur_max, texte="", scale=1.0):
        """
        Dessine la barre
        - valeur_actuelle/valeur_max : pour calculer le pourcentage
        - texte : optionnel, ex "HP: 80/100"
        - scale : pour s'adapter aux différentes résolutions
        """
        # Calculer les dimensions avec le scale
        x = int(self.x * scale)
        y = int(self.y * scale)
        largeur = int(self.largeur * scale)
        hauteur = int(self.hauteur * scale)
        
        # Calculer le pourcentage
        pourcentage = max(0, min(1, valeur_actuelle / valeur_max))
        largeur_actuelle = int(largeur * pourcentage)
        
        # Fond noir semi-transparent (optionnel)
        fond = pygame.Surface((largeur + 10, hauteur + 10), pygame.SRCALPHA)
        pygame.draw.rect(fond, (0, 0, 0, 180), fond.get_rect(), border_radius=int(10 * scale))
        screen.blit(fond, (x - 5, y - 5))
        
        # Barre de fond (gris foncé)
        pygame.draw.rect(screen, self.couleur_fond, 
                        (x, y, largeur, hauteur), 
                        border_radius=int(8 * scale))
        
        # Barre de progression avec dégradé
        if largeur_actuelle > 0:
            if isinstance(self.couleur_barre, list) and len(self.couleur_barre) == 2:
                # Dégradé entre 2 couleurs
                for i in range(largeur_actuelle):
                    ratio = i / largeur
                    r = int(self.couleur_barre[0][0] + (self.couleur_barre[1][0] - self.couleur_barre[0][0]) * ratio)
                    g = int(self.couleur_barre[0][1] + (self.couleur_barre[1][1] - self.couleur_barre[0][1]) * ratio)
                    b = int(self.couleur_barre[0][2] + (self.couleur_barre[1][2] - self.couleur_barre[0][2]) * ratio)
                    pygame.draw.line(screen, (r, g, b), 
                                   (x + i, y), 
                                   (x + i, y + hauteur))
            else:
                # Couleur unie
                pygame.draw.rect(screen, self.couleur_barre, 
                               (x, y, largeur_actuelle, hauteur))
        
        # Effet de brillance
        if self.avec_brillance and pourcentage > 0:
            brillance = pygame.Surface((largeur_actuelle, hauteur // 3), pygame.SRCALPHA)
            pygame.draw.rect(brillance, (255, 255, 255, 60), 
                           brillance.get_rect(), 
                           border_radius=int(5 * scale))
            screen.blit(brillance, (x, y + int(5 * scale)))
        
        # Bordure
        if self.avec_bordure:
            pygame.draw.rect(screen, (255, 255, 255), 
                           (x, y, largeur, hauteur), 
                           int(3 * scale), 
                           border_radius=int(8 * scale))
        
        # Texte
        if self.avec_texte and texte:
            font = pygame.font.Font(None, int(28 * scale))
            texte_ombre = font.render(texte, True, (0, 0, 0))
            texte_surface = font.render(texte, True, (255, 255, 255))
            
            texte_x = x + largeur // 2 - texte_surface.get_width() // 2
            texte_y = y + hauteur // 2 - texte_surface.get_height() // 2
            
            screen.blit(texte_ombre, (texte_x + 2, texte_y + 2))
            screen.blit(texte_surface, (texte_x, texte_y))