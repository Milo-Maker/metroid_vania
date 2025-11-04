import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
import pygame
import pytmx
import pyscroll
from scripts.class_player import joueur
from scripts.class_collectible import collectible
from scripts.class_bouton import bouton
from scripts.class_ennemi import ennemi 
from scripts.class_barre import barre
pygame.init()
debug_mod_is_eanable=False

# fenètre
resolution_base = (2560, 1440)
resolution = (2560, 1440)
#resolution = (1920, 1080)
resolutions_disponibles = [
    (1280, 720),    # 16:9 - HD
    (1920, 1080),   # 16:9 - Full HD
    (2560, 1440),   # 16:9 - QHD
    (3840, 2160),   # 16:9 - 4K
] 
barre_vie = barre(20, 20, 300, 35, (50, 50, 50), [(200, 20, 20), (150, 50, 20)])
barre_mana = barre(20, 75, 300, 35, (50, 50, 50), [(20, 100, 200), (100, 200, 255)])

ecran = pygame.display.set_mode(resolution)
pygame.display.set_caption("jeu metroidvania")
fond_ecran = (0,110,110)

# boucle principal
clock = pygame.time.Clock()
execution = True
frame_count = 0 

# chargement des images : 
icon_dash = pygame.transform.scale(pygame.image.load("img/dash_icon.png").convert_alpha(), (100 * resolution[0]/resolution_base[0], 100 * resolution[1]/resolution_base[1]))
icon_money = pygame.transform.scale(pygame.image.load("img/argent_icon.png").convert_alpha(), (100 * resolution[0]/resolution_base[0], 100 * resolution[1]/resolution_base[1]))
icon_interdiction = pygame.transform.scale(pygame.image.load("img/interdiction.png").convert_alpha(), (110 * resolution[0]/resolution_base[0], 110 * resolution[1]/resolution_base[1]))
cash_bag = pygame.transform.scale(pygame.image.load("img/cash_bag.png").convert_alpha(), (100 * resolution[0]/resolution_base[0], 100 * resolution[1]/resolution_base[1]))


couche = 1
zone = 2
xcam = 0
ycam = 0
gravité = 1
joueur1 = joueur(500, 500, ecran, debug_mod_is_eanable)
        
group = None
plat_collision = []
items = []
items_recovered= []
ennemis = [] 

map_surface = None
font = pygame.font.SysFont("comicsans",40)
col_bouton= (0,200,0)

class graphisme_map:
    def __init__(self, filename, scale=1.0):
        self.tmx_data = pytmx.load_pygame(filename)
        self.scale = scale
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight
        
    def render(self, surface):
        # Parcourir toutes les couches
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        # Redimensionner chaque tuile
                        scaled_tile = pygame.transform.scale(
                            tile,
                            (int(self.tmx_data.tilewidth * self.scale),
                             int(self.tmx_data.tileheight * self.scale))
                        )
                        surface.blit(
                            scaled_tile,
                            (x * self.tmx_data.tilewidth * self.scale,
                             y * self.tmx_data.tileheight * self.scale)
                        )
    
    def make_map(self):
        """Créer une surface avec la carte complète"""
        temp_surface = pygame.Surface((int(self.width), int(self.height)), pygame.SRCALPHA)
        self.render(temp_surface)
        return temp_surface
    
def changer_resolution(nouvelle_resolution):
    global resolution, ecran, icon_dash, icon_money, icon_interdiction, cash_bag, group
    
    resolution = nouvelle_resolution
    ecran = pygame.display.set_mode(resolution)
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)

    # Recharger les images avec la nouvelle résolution
    icon_dash = pygame.transform.scale(
        pygame.image.load("img/dash_icon.png").convert_alpha(), 
        (int(100 * resolution[0]/resolution_base[0]), int(100 * resolution[1]/resolution_base[1]))
    )
    icon_money = pygame.transform.scale(
        pygame.image.load("img/argent_icon.png").convert_alpha(), 
        (int(100 * resolution[0]/resolution_base[0]), int(100 * resolution[1]/resolution_base[1]))
    )
    icon_interdiction = pygame.transform.scale(
        pygame.image.load("img/interdiction.png").convert_alpha(), 
        (int(110 * resolution[0]/resolution_base[0]), int(110 * resolution[1]/resolution_base[1]))
    )
    cash_bag = pygame.transform.scale(
        pygame.image.load("img/cash_bag.png").convert_alpha(), 
        (int(100 * resolution[0]/resolution_base[0]), int(100 * resolution[1]/resolution_base[1]))
    )
    
    # IMPORTANT : Recharger la carte avec la nouvelle résolution
    charge_zone(zone, couche)
    
    # Mettre à jour la référence de l'écran pour tous les objets
    joueur1.screen = ecran
    for item in items:
        item.screen = ecran
        # Mettre à jour l'image du collectible avec la nouvelle résolution
        if item.type == "cash_bag":
            item.img = cash_bag
        

def charge_zone(zone, couche):
    global group, plat_collision, map_surface, items, ennemis
    tiled_map = graphisme_map(f"map/couche{couche}/zone{zone}.tmx", scale=resolution[0]/resolution_base[0])
    map_surface = tiled_map.make_map()

    tmx_data = pytmx.load_pygame(f"map/couche{couche}/zone{zone}.tmx")
    #map_data = pyscroll.data.TiledMapData(tmx_data)
    
    
    plat_collision.clear()
    items.clear()
    ennemis.clear()
    # Récupérer TOUS les colliders d'un coup
    all_colliders = {}
    for gid, colliders in tmx_data.get_tile_colliders():
        all_colliders[gid] = colliders
    
    # Parcourir les layers pour placer les colliders aux bonnes positions
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if gid == 0:
                    continue

                # Vérifier si ce GID a des colliders
                if gid in all_colliders:
                    for collision_obj in all_colliders[gid]:
                        # Calculer la position absolue du rectangle de collision
                        abs_rect = pygame.Rect(
                            (x * tmx_data.tilewidth + collision_obj.x),
                            (y * tmx_data.tileheight + collision_obj.y),
                            (collision_obj.width),
                            (collision_obj.height)
                        )
                        plat_collision.append(abs_rect)

    # Charger les items et les ennemis
    for obj in tmx_data.objects: 
        if obj.name == "cash_bag":
            if not obj.number in items_recovered:
                items.append(collectible(obj.name, obj.x, obj.y, cash_bag, ecran, obj.number, obj.quantity, debug_mod_is_eanable))
        if obj.type == "ennemi":
            if obj.name == "slime_1":
                ennemis.append(ennemi(obj.name, obj.x, obj.y, ecran, debug_mod_is_eanable))
def changement_zone(xcam, ycam, zone, couche):
    if joueur1.x < 0:
        zone -= 1
        joueur1.x = 6400 - joueur1.l
        xcam = 6400 - resolution[0]
        charge_zone(zone, couche)
        
                
    elif joueur1.x + joueur1.l > 6400:
        zone += 1
        joueur1.x = 0
        xcam = 0
        charge_zone(zone, couche)

    return xcam, ycam, zone, couche

def draw():
    scale = resolution[0] / resolution_base[0]
    # Map
    ecran.fill(fond_ecran)
    ecran.blit(map_surface, (-int(xcam * scale), -int(ycam * scale))) 
    

    # Debug affichage hitbox des plateformes
    if debug_mod_is_eanable:
        for r in plat_collision:
            screen_rect = pygame.Rect(
                int((r.x - xcam) * scale),
                int((r.y - ycam) * scale),
                int(r.width * scale),
                int(r.height * scale)
            )
            pygame.draw.rect(ecran, (255, 0, 0), screen_rect, 2)
    
    # Joueur
    joueur1.draw(xcam, ycam, resolution, resolution_base)
    # Ennemis
    for e in ennemis:
        e.draw(xcam, ycam, resolution, resolution_base)
    # Items
    for i in items:
        i.draw(xcam, ycam, resolution, resolution_base)
    
    # Barres de vie et mana
    scale = resolution[0] / resolution_base[0]
    barre_vie.draw(ecran, joueur1.vie, joueur1.vie_max, f"HP: {int(joueur1.vie)}/{int(joueur1.vie_max)}", scale)
    barre_mana.draw(ecran, joueur1.mana, joueur1.mana_max, f"MP: {int(joueur1.mana)}/{int(joueur1.mana_max)}", scale)
    
    # Money icon and text
    ecran.blit(icon_money, (int(20 * scale), int(100 * scale)))
    
    font_scaled = pygame.font.SysFont("comicsans", int(40 * scale))
    text_surface = font_scaled.render(str(joueur1.money), True, (255, 255, 255))
    ecran.blit(text_surface, (int(140 * scale), int(120 * scale)))
  
    # Dash icon
    ecran.blit(icon_dash, (int(20 * scale), int(220 * scale)))
    if joueur1.dash_couldown > 0:
        ecran.blit(icon_interdiction, (int(15 * scale), int(214 * scale)))  
def touch_items():
    for i in items:
        if joueur1.collide_items(i.return_rect()):
            if i.type == "cash_bag":
                joueur1.money+=i.quantity
                items_recovered.append(i.ID)
                items.remove(i)
def menu_options():
    global execution, resolution, debug_mod_is_eanable
    
    # Index de la résolution actuelle
    current_res_index = resolutions_disponibles.index(resolution) if resolution in resolutions_disponibles else 2
    
    # Créer les boutons
    bouton_resolution_moins = bouton(
        resolution[0]//2 - 250,
        350,
        80,
        60,
        "<",
        (255, 255, 255),
        (50, 100, 150),
        ecran
    )
    
    bouton_resolution_plus = bouton(
        resolution[0]//2 + 170,
        350,
        80,
        60,
        ">",
        (255, 255, 255),
        (50, 100, 150),
        ecran
    )
    
    bouton_debug = bouton(
        resolution[0]//2 - 150,
        480,
        300,
        60,
        "DEBUG: " + ("ON" if debug_mod_is_eanable else "OFF"),
        (255, 255, 255),
        (150, 100, 50),
        ecran
    )
    
    bouton_appliquer = bouton(
        resolution[0]//2 - 150,
        600,
        300,
        70,
        "APPLIQUER",
        (255, 255, 255),
        (50, 150, 50),
        ecran
    )
    
    bouton_retour = bouton(
        resolution[0]//2 - 150,
        700,
        300,
        70,
        "RETOUR",
        (255, 255, 255),
        (150, 50, 50),
        ecran
    )
    
    # Variables pour animation
    alpha_fond = 0
    alpha_max = 180
    temp_resolution_index = current_res_index
    temp_debug = debug_mod_is_eanable
    changes_made = False
    
    in_options = True
    while in_options:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                execution = False
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Bouton résolution -
                if bouton_resolution_moins.rect.collidepoint(event.pos):
                    if temp_resolution_index > 0:
                        temp_resolution_index -= 1
                        changes_made = True
                
                # Bouton résolution +
                if bouton_resolution_plus.rect.collidepoint(event.pos):
                    if temp_resolution_index < len(resolutions_disponibles) - 1:
                        temp_resolution_index += 1
                        changes_made = True
                
                # Bouton debug toggle
                if bouton_debug.rect.collidepoint(event.pos):
                    temp_debug = not temp_debug
                    changes_made = True
                    # Mettre à jour le texte du bouton
                    bouton_debug.text_surface = bouton_debug.font.render(
                        "DEBUG: " + ("ON" if temp_debug else "OFF"), 
                        True, 
                        (255, 255, 255)
                    )
                    bouton_debug.text_rect = bouton_debug.text_surface.get_rect(center=bouton_debug.rect.center)
                
                # Bouton appliquer
                if bouton_appliquer.rect.collidepoint(event.pos):
                    if changes_made:
                        # Appliquer les changements
                        nouvelle_resolution = resolutions_disponibles[temp_resolution_index]
                        if nouvelle_resolution != resolution:
                            changer_resolution(nouvelle_resolution)
                        
                        debug_mod_is_eanable = temp_debug
                        joueur1.debug_mod_is_eanable = temp_debug
                        for item in items:
                            item.debug_mod = temp_debug
                        
                        changes_made = False
                        
                        # Recréer les boutons avec la nouvelle résolution
                        bouton_resolution_moins.rect.x = resolution[0]//2 - 250
                        bouton_resolution_moins.rect.y = 350
                        
                        bouton_resolution_plus.rect.x = resolution[0]//2 + 170
                        bouton_resolution_plus.rect.y = 350
                        
                        bouton_debug.rect.x = resolution[0]//2 - 150
                        bouton_debug.rect.y = 480
                        
                        bouton_appliquer.rect.x = resolution[0]//2 - 150
                        bouton_appliquer.rect.y = 600
                        
                        bouton_retour.rect.x = resolution[0]//2 - 150
                        bouton_retour.rect.y = 700
                        
                        # Recalculer les positions de texte
                        for btn in [bouton_resolution_moins, bouton_resolution_plus, bouton_debug, bouton_appliquer, bouton_retour]:
                            btn.text_rect = btn.text_surface.get_rect(center=btn.rect.center)
                
                # Bouton retour
                if bouton_retour.rect.collidepoint(event.pos):
                    return
        
        # Animation du fond
        if alpha_fond < alpha_max:
            alpha_fond = min(alpha_max, alpha_fond + 5)
        
        # === AFFICHAGE ===
        
        # Fond dégradé
        for i in range(resolution[1]):
            couleur = (
                20 + int(i / resolution[1] * 20),
                20 + int(i / resolution[1] * 30),
                40 + int(i / resolution[1] * 60)
            )
            pygame.draw.line(ecran, couleur, (0, i), (resolution[0], i))
        
        # Overlay semi-transparent
        overlay = pygame.Surface(resolution)
        overlay.set_alpha(alpha_fond)
        overlay.fill((0, 0, 20))
        ecran.blit(overlay, (0, 0))
        
        # Titre
        font_titre = pygame.font.Font(None, 100)
        titre = font_titre.render("OPTIONS", True, (255, 200, 50))
        titre_rect = titre.get_rect(center=(resolution[0]//2, 150))
        
        # Ombre du titre
        titre_ombre = font_titre.render("OPTIONS", True, (0, 0, 0))
        titre_ombre_rect = titre_ombre.get_rect(center=(resolution[0]//2 + 3, 153))
        ecran.blit(titre_ombre, titre_ombre_rect)
        ecran.blit(titre, titre_rect)
        
        # Ligne décorative
        pygame.draw.line(ecran, (150, 150, 200), 
                        (resolution[0]//2 - 200, 220),
                        (resolution[0]//2 + 200, 220), 3)
        
        # === SECTION RÉSOLUTION ===
        font_label = pygame.font.Font(None, 45)
        label_res = font_label.render("RESOLUTION", True, (200, 200, 200))
        ecran.blit(label_res, (resolution[0]//2 - label_res.get_width()//2, 280))
        
        # Afficher la résolution actuelle sélectionnée
        current_res = resolutions_disponibles[temp_resolution_index]
        font_res = pygame.font.Font(None, 55)
        res_text = font_res.render(f"{current_res[0]} x {current_res[1]}", True, (255, 255, 255))
        res_text_rect = res_text.get_rect(center=(resolution[0]//2, 365))
        
        # Fond pour le texte de résolution
        res_bg = pygame.Rect(resolution[0]//2 - 160, 340, 320, 50)
        pygame.draw.rect(ecran, (50, 50, 70), res_bg, border_radius=5)
        ecran.blit(res_text, res_text_rect)
        
        # Dessiner les boutons avec effet de survol
        for btn in [bouton_resolution_moins, bouton_resolution_plus, bouton_debug, bouton_appliquer, bouton_retour]:
            if btn.rect.collidepoint(mouse_pos):
                halo_rect = btn.rect.inflate(10, 10)
                pygame.draw.rect(ecran, (255, 255, 255), halo_rect, 3, border_radius=5)
        
        bouton_resolution_moins.draw()
        bouton_resolution_plus.draw()
        
        # === SECTION DEBUG ===
        label_debug = font_label.render("MODE DEBUG", True, (200, 200, 200))
        ecran.blit(label_debug, (resolution[0]//2 - label_debug.get_width()//2, 430))
        
        bouton_debug.draw()
        
        # Indicateur de changements non appliqués
        if changes_made:
            font_warning = pygame.font.Font(None, 35)
            warning = font_warning.render("* Changements non appliqués", True, (255, 200, 100))
            warning.set_alpha(200 + int(55 * abs((pygame.time.get_ticks() % 1000) / 500 - 1)))
            ecran.blit(warning, (resolution[0]//2 - warning.get_width()//2, 550))
        
        bouton_appliquer.draw()
        bouton_retour.draw()
        
        # Instructions
        font_instructions = pygame.font.Font(None, 30)
        instructions = font_instructions.render("ESC pour retour", True, (150, 150, 150))
        instructions.set_alpha(200)
        ecran.blit(instructions, (20, resolution[1] - 40))
        
        pygame.display.flip()
        clock.tick(60)
def pause():
    global execution
    
    # Créer les boutons
    bouton_reprendre = bouton(
        resolution[0]//2 - 150, 
        400, 
        300, 
        70, 
        "REPRENDRE",
        (255, 255, 255),
        (50, 150, 50),
        ecran
    )
    
    bouton_menu = bouton(
        resolution[0]//2 - 150, 
        500, 
        300, 
        70, 
        "MENU",
        (255, 255, 255),
        (50, 100, 150),
        ecran
    )
    
    bouton_quitter = bouton(
        resolution[0]//2 - 150, 
        600, 
        300, 
        70, 
        "QUITTER",
        (255, 255, 255),
        (150, 50, 50),
        ecran
    )
    
    # Variables pour les animations
    alpha_fond = 0
    alpha_max = 180
    scale = 0.5
    scale_target = 1.0
    
    # Particules flottantes
    particules = []
    for i in range(30):
        x = (i * 234) % resolution[0]
        y = (i * 567) % resolution[1]
        size = (i % 4) + 2
        vitesse_x = ((i % 5) - 2) * 0.3
        vitesse_y = ((i % 3) - 1) * 0.2
        particules.append([x, y, size, vitesse_x, vitesse_y])
    
    paused = True
    while paused:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                execution = False
                paused = False
                return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                    return "resume"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if bouton_reprendre.rect.collidepoint(event.pos):
                    paused = False
                    return "resume"
                
                if bouton_menu.rect.collidepoint(event.pos):
                    return "menu"
                
                if bouton_quitter.rect.collidepoint(event.pos):
                    execution = False
                    paused = False
                    return "quit"
                
                        
        
        # Animation du fond (fade in)
        if alpha_fond < alpha_max:
            alpha_fond = min(alpha_max, alpha_fond + 5)
        
        # Animation du scale (zoom)
        if scale < scale_target:
            scale = min(scale_target, scale + 0.02)
        
        # Animation des particules
        for particule in particules:
            particule[0] += particule[3]
            particule[1] += particule[4]
            
            # Rebond sur les bords
            if particule[0] < 0 or particule[0] > resolution[0]:
                particule[3] *= -1
            if particule[1] < 0 or particule[1] > resolution[1]:
                particule[4] *= -1
        
        # === AFFICHAGE ===
        
        # Fond semi-transparent assombri
        overlay = pygame.Surface(resolution)
        overlay.set_alpha(alpha_fond)
        overlay.fill((0, 0, 20))
        ecran.blit(overlay, (0, 0))
        
        # Dessiner les particules flottantes
        for particule in particules:
            alpha_particule = int(100 + 50 * ((particule[1] / resolution[1])))
            color = (100, 150, 200)
            
            # Créer une surface pour la particule avec alpha
            particle_surface = pygame.Surface((particule[2]*2, particule[2]*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*color, alpha_particule), 
                             (particule[2], particule[2]), particule[2])
            ecran.blit(particle_surface, (int(particule[0]), int(particule[1])))
        
        # Cadre décoratif autour du titre
        cadre_rect = pygame.Rect(
            resolution[0]//2 - 250,
            150,
            500,
            120
        )
        pygame.draw.rect(ecran, (100, 100, 150), cadre_rect, 3, border_radius=10)
        
        # Titre PAUSE avec effet de scale et ombre
        font_titre = pygame.font.Font(None, int(120 * scale))
        
        # Ombre du titre
        titre_ombre = font_titre.render("PAUSE", True, (0, 0, 0))
        titre_ombre_rect = titre_ombre.get_rect(center=(resolution[0]//2 + 4, 210 + 4))
        ecran.blit(titre_ombre, titre_ombre_rect)
        
        # Titre principal avec pulsation
        pulsation = abs((pygame.time.get_ticks() % 1500) / 750 - 1)
        color_r = int(200 + 55 * pulsation)
        color_g = int(200 + 55 * pulsation)
        color_b = int(255)
        
        titre = font_titre.render("PAUSE", True, (color_r, color_g, color_b))
        titre_rect = titre.get_rect(center=(resolution[0]//2, 210))
        ecran.blit(titre, titre_rect)
        
        # Ligne décorative sous le titre
        ligne_y = 280
        ligne_length = int(400 * scale)
        pygame.draw.line(ecran, (150, 150, 200), 
                        (resolution[0]//2 - ligne_length//2, ligne_y),
                        (resolution[0]//2 + ligne_length//2, ligne_y), 3)
        
        # Dessiner les boutons avec effet de survol
        for btn in [bouton_reprendre, bouton_menu, bouton_quitter]:
            if btn.rect.collidepoint(mouse_pos):
                # Halo lumineux autour du bouton survolé
                halo_rect = btn.rect.inflate(15, 15)
                
                # Animation de pulsation du halo
                halo_alpha = int(100 + 50 * abs((pygame.time.get_ticks() % 1000) / 500 - 1))
                halo_surface = pygame.Surface((halo_rect.width, halo_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(halo_surface, (255, 255, 255, halo_alpha), 
                               halo_surface.get_rect(), 4, border_radius=5)
                ecran.blit(halo_surface, halo_rect.topleft)
        
        bouton_reprendre.draw()
        bouton_menu.draw()
        bouton_quitter.draw()
        
        # Instructions en bas avec icônes
        font_instructions = pygame.font.Font(None, 35)
        
        # Icône ESC stylisée
        esc_surface = pygame.Surface((80, 40), pygame.SRCALPHA)
        pygame.draw.rect(esc_surface, (100, 100, 150, 200), esc_surface.get_rect(), border_radius=5)
        esc_text = pygame.font.Font(None, 30).render("ESC", True, (255, 255, 255))
        esc_text_rect = esc_text.get_rect(center=(40, 20))
        esc_surface.blit(esc_text, esc_text_rect)
        
        ecran.blit(esc_surface, (20, resolution[1] - 60))
        
        instructions = font_instructions.render("pour reprendre", True, (200, 200, 200))
        instructions.set_alpha(220)
        ecran.blit(instructions, (110, resolution[1] - 50))
        
        pygame.display.flip()
        clock.tick(60)
    
    return "resume"
def menu():
    
    global execution
    
    # Créer les boutons
    bouton_jouer = bouton(
        resolution[0]//2 - 150, 
        400, 
        300, 
        70, 
        "JOUER",
        (255, 255, 255),  # Couleur du texte
        (50, 150, 50),     # Couleur du bouton
        ecran
    )
    
    bouton_options = bouton(
        resolution[0]//2 - 150, 
        500, 
        300, 
        70, 
        "OPTIONS",
        (255, 255, 255),
        (50, 100, 150),
        ecran
    )
    
    bouton_quitter = bouton(
        resolution[0]//2 - 150, 
        600, 
        300, 
        70, 
        "QUITTER",
        (255, 255, 255),
        (150, 50, 50),
        ecran
    )
    
    # Variables pour les animations
    titre_y = -100
    titre_target = 200
    alpha = 0
    boutons_visible = False
    
    # Étoiles pour le fond
    etoiles = []
    for i in range(100):
        x = (i * 123) % resolution[0]
        y = (i * 456) % resolution[1]
        size = (i % 3) + 1
        vitesse = (i % 3) + 0.5
        etoiles.append([x, y, size, vitesse])
    
    in_menu = True
    while in_menu:
        # Gestion des événements
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                execution = False
                in_menu = False
                return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    execution = False
                    in_menu = False
                    return "quit"
                if event.key == pygame.K_SPACE and boutons_visible:
                    in_menu = False
                    return "play"
            
            # Vérifier les clics sur les boutons (seulement si visibles)
            if boutons_visible:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if bouton_jouer.rect.collidepoint(event.pos):
                        in_menu = False
                        return "play"
                    
                    if bouton_options.rect.collidepoint(event.pos):
                        menu_options()  # ← Appeler le menu d'options
                        # Recréer les boutons du menu après retour des options
                        bouton_jouer = bouton(
                            resolution[0]//2 - 150, 
                            400, 
                            300, 
                            70, 
                            "JOUER",
                            (255, 255, 255),
                            (50, 150, 50),
                            ecran
                        )
                        bouton_options = bouton(
                            resolution[0]//2 - 150, 
                            500, 
                            300, 
                            70, 
                            "OPTIONS",
                            (255, 255, 255),
                            (50, 100, 150),
                            ecran
                        )
                        bouton_quitter = bouton(
                            resolution[0]//2 - 150, 
                            600, 
                            300, 
                            70, 
                            "QUITTER",
                            (255, 255, 255),
                            (150, 50, 50),
                            ecran
                        )
                    
                    if bouton_quitter.rect.collidepoint(event.pos):
                        execution = False
                        in_menu = False
                        return "quit"
        
        # Animation du titre (descente progressive)
        if titre_y < titre_target:
            titre_y += 5
        elif not boutons_visible:
            boutons_visible = True  # Afficher les boutons après l'animation
        
        # Fade in
        if alpha < 255:
            alpha = min(255, alpha + 3)
        
        # Animation des étoiles
        for etoile in etoiles:
            etoile[1] += etoile[3]  # Déplacement vertical
            if etoile[1] > resolution[1]:
                etoile[1] = 0
                etoile[0] = (etoile[0] + 50) % resolution[0]
        
        # === AFFICHAGE ===
        
        # Fond dégradé
        for i in range(resolution[1]):
            couleur = (
                20 + int(i / resolution[1] * 20),
                20 + int(i / resolution[1] * 30),
                40 + int(i / resolution[1] * 60)
            )
            pygame.draw.line(ecran, couleur, (0, i), (resolution[0], i))
        
        # Dessiner les étoiles
        for etoile in etoiles:
            brightness = int(150 + 105 * ((etoile[1] / resolution[1])))
            blue = min(255, brightness + 50)
            pygame.draw.circle(ecran, (brightness, brightness, blue), (int(etoile[0]), int(etoile[1])), etoile[2],)
        
        # Titre du jeu avec effet d'ombre
        font_titre = pygame.font.Font(None, 120)
        
        # Ombre du titre
        titre_ombre = font_titre.render("METROIDVANIA", True, (0, 0, 0))
        titre_ombre_rect = titre_ombre.get_rect(center=(resolution[0]//2 + 5, int(titre_y) + 5))
        ecran.blit(titre_ombre, titre_ombre_rect)
        
        # Titre principal
        titre = font_titre.render("METROIDVANIA", True, (255, 200, 50))
        titre.set_alpha(alpha)
        titre_rect = titre.get_rect(center=(resolution[0]//2, int(titre_y)))
        ecran.blit(titre, titre_rect)
        
        # Sous-titre avec effet de pulsation
        if titre_y >= titre_target:
            pulsation = abs((pygame.time.get_ticks() % 2000) / 1000 - 1)  # 0 à 1 à 0
            alpha_sous_titre = int(150 + 105 * pulsation)
            
            font_sous_titre = pygame.font.Font(None, 50)
            sous_titre = font_sous_titre.render("Appuyez sur ESPACE pour commencer", True, (200, 200, 200))
            sous_titre.set_alpha(alpha_sous_titre)
            sous_titre_rect = sous_titre.get_rect(center=(resolution[0]//2, 300))
            ecran.blit(sous_titre, sous_titre_rect)
        
        # Dessiner les boutons avec effet de survol (seulement si visibles)
        if boutons_visible:
            # Effet de survol pour chaque bouton
            for btn in [bouton_jouer, bouton_options, bouton_quitter]:
                if btn.rect.collidepoint(mouse_pos):
                    # Dessiner un halo autour du bouton survolé
                    halo_rect = btn.rect.inflate(10, 10)
                    pygame.draw.rect(ecran, (255, 255, 255), halo_rect, 3)
            
            bouton_jouer.draw()
            bouton_options.draw()
            bouton_quitter.draw()
        
        # Instructions en bas avec transparence
        font_instructions = pygame.font.Font(None, 35)
        instructions = font_instructions.render("ESC pour quitter", True, (150, 150, 150))
        instructions.set_alpha(200)
        ecran.blit(instructions, (20, resolution[1] - 50))
        
        pygame.display.flip()
        clock.tick(60)
    
    return "play"


def main():
    global couche, zone, xcam, ycam, execution, frame_count

    result = menu()
    
    if result == "quit":
        return
    charge_zone(zone, couche)

#       --- Boucle principale ---
    while execution:
    # Fermeture fenêtre 
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                execution = False  
            if i.type == pygame.KEYDOWN:
                if i.key == pygame.K_ESCAPE:
                    result = pause()  # ← Appeler le menu pause
                    
                    if result == "quit":
                        execution = False
                    elif result == "menu":
                        # Retourner au menu principal
                        result = menu()
                        if result == "quit":
                            execution = False

    # Inputs
        keys = pygame.key.get_pressed()

    # Déplacement horizontal
        if abs(joueur1.vx) > joueur1.vitesse: # Si en dash
            joueur1.vx *= 0.9  # Diminution progressive de la vitesse du dash
            joueur1.états = 3
        else:
            joueur1.vx = 0
            if joueur1.états == 1:
                joueur1.animation_etat = 0
            if joueur1.états == 3:
                joueur1.états = 2
                joueur1.animation_etat = 2
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                joueur1.direction = 1
                joueur1.vx = joueur1.vitesse
                joueur1.animation_etat = 1
                if joueur1.états == 1:
                    joueur1.animation_etat = 1
            if keys[pygame.K_LEFT] or keys[pygame.K_q]:
                joueur1.direction = -1
                joueur1.vx = -joueur1.vitesse
                if joueur1.états == 1:
                    joueur1.animation_etat = 1
            
            if keys[pygame.K_SPACE] and joueur1.dash_couldown == 0:
                joueur1.vx = joueur1.dash_force * joueur1.direction
                joueur1.dash_couldown = joueur1.dash_couldown_max
                joueur1.vy = 0  # Annule la vitesse verticale lors du dash
                joueur1.animation_etat = 3
                joueur1.états = 3
                joueur1.animation_counter = 0
            
            if joueur1.états == 2:
            #and joueur1.animation_etat != 3:
                joueur1.animation_etat = 2
    # saut
            if (keys[pygame.K_z] or keys[pygame.K_UP]) and joueur1.états == 1:
                joueur1.vy = -joueur1.jump_force
                joueur1.états = 2

    # Appliquer la gravité 
            joueur1.vy += gravité
            
    # collision et mouvement

            joueur1.mouvementy(plat_collision)
        joueur1.mouvementx(plat_collision)
        touch_items()

        xcam, ycam, zone, couche=changement_zone(xcam, ycam, zone, couche)
            

    # couldown des capacités
        if joueur1.dash_couldown > 0:
            joueur1.dash_couldown -= 1

    # ennemis :
        for e in ennemis:
            e.update(plat_collision)
        
    # Caméra
        cible_cam_x = joueur1.x + joueur1.l/2 - resolution_base[0]/2
        cible_cam_y = joueur1.y + joueur1.h/2 - resolution_base[1]/2
        cible_cam_x = max(0, min(6400 - resolution_base[0], cible_cam_x))
        cible_cam_y = max(0, min(6400 - resolution_base[1], cible_cam_y))
        xcam += (cible_cam_x - xcam) * 0.05
        ycam += (cible_cam_y - ycam) * 0.05

    
    
    # rafraîchissement de l'écran

        if joueur1.animation_etat == 2:  # Si en l'air
            if frame_count % 4 == 0:  # Change d'image une frame sur trois
                joueur1.animation_counter += 1
        else:
            if frame_count % 2 == 0:  # Change d'image une frame sur deux
                joueur1.animation_counter += 1
        
        frame_count += 1
    # Affichage
        
        draw()
        pygame.display.flip()
        clock.tick(60)
    
main()
quit()

# TODO faire ce ptn de changement de resolution