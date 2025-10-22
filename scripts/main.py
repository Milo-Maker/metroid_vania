import pygame
import pytmx
import pyscroll
from class_player import joueur
resolution = (2560, 1440)
resolution_base = (2560, 1440)  
ecran = pygame.display.set_mode(resolution)
pygame.display.set_caption("jeu metroidvania")
clock = pygame.time.Clock()
execution = True
img = pygame.image.load("img/dash_icon.png").convert_alpha()
img = pygame.transform.scale(img, (100 * resolution[0]/resolution_base[0], 100 * resolution[1]/resolution_base[1]))
fond_ecran = (0,110,110)
couche = 1
zone = 2
xcam = 0
ycam = 0
gravité = 1
               

         
group = None
plat_collision = []
def charge_zone():
    global group, plat_collision
    tmx_data = pytmx.load_pygame(f"map/couche1/zone{zone}.tmx")
    map_data = pyscroll.data.TiledMapData(tmx_data)
    map_layer = pyscroll.orthographic.BufferedRenderer(map_data, resolution, alpha=True)
    group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=1)
    plat_collision.clear()
    for obj in tmx_data.objects:
        if obj.type == "collision":
            plat = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            plat_collision.append(plat)


charge_zone()
joueur1 = joueur(500, 500, ecran)
frame_count = 0
# --- Boucle principale ---
while execution:
# Fermeture fenêtre 
    for i in pygame.event.get():
        if i.type == pygame.QUIT: 
            execution = False  
        if i.type == pygame.KEYDOWN:
            if i.key == pygame.K_ESCAPE:
                execution = False

# Inputs
    keys = pygame.key.get_pressed()

# Déplacement horizontal
    if abs(joueur1.vx) > joueur1.vitesse:
        joueur1.vx *= 0.9  # Diminution progressive de la vitesse du dash
    else:
        joueur1.vx = 0
        if joueur1.états == 1:
            joueur1.animation_etat = 0
        
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
            joueur1.animation_counter = 0
           
        if joueur1.états == 2 and joueur1.animation_etat != 3:
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
    if joueur1.x < 0:
        zone -= 1
        joueur1.x = 6400 - joueur1.l
        xcam = 6400 - resolution[0]
        charge_zone()
    elif joueur1.x + joueur1.l > 6400:
        zone += 1
        joueur1.x = 0
        xcam = 0
        charge_zone()

# couldown des capacités
    if joueur1.dash_couldown > 0:
        joueur1.dash_couldown -= 1
    
# Caméra
    cible_cam_x = joueur1.x + joueur1.l/2 - 2560/2
    cible_cam_y = joueur1.y + joueur1.h/2 - 1440/2
    cible_cam_x = max(0, min(6400 - resolution[0], cible_cam_x))
    cible_cam_y = max(0, min(6400 - resolution[1], cible_cam_y))
    xcam += (cible_cam_x - xcam) * 0.05
    ycam += (cible_cam_y - ycam) * 0.05

    group.center((xcam + resolution[0]//2, ycam + resolution[1]//2))

    if keys[pygame.K_1]:
        resolution = (130 * 16, 130 * 9)
        ecran = pygame.display.set_mode(resolution)
    if keys[pygame.K_2]:
        resolution = (2560, 1440)
        ecran = pygame.display.set_mode(resolution)
# Affichage
    ecran.fill(fond_ecran)
    group.draw(ecran)
    #debug affichage hitbox des plateformes
    for r in plat_collision:
       pygame.draw.rect(ecran, (255, 0, 0), (r.x - xcam, r.y - ycam, r.width, r.height), 2)
    
    joueur1.draw(xcam, ycam, resolution, resolution_base)
    ecran.blit(img, (20, 20))
   
# rafraîchissement de l'écran

    if joueur1.animation_etat == 2:  # Si en l'air
        if frame_count % 4 == 0:  # Change d'image une frame sur trois
            joueur1.animation_counter += 1
    else:
        if frame_count % 2 == 0:  # Change d'image une frame sur deux
            joueur1.animation_counter += 1
    
    frame_count += 1

    pygame.display.flip()
    clock.tick(60)

quit()