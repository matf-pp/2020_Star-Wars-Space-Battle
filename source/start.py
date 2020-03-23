import time as TIME
from source import cls
from source import gui
from source import glob
from pygame import mixer
import pygame
import math
import random

def check_menu_events():
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            exit()
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                exit()

        #Ukoliko smo kliknuli na pauzu, otvaramo pause_meni i zaustavljamo muziku
        if e.type == pygame.MOUSEBUTTONDOWN and gui.pause_menu.is_disabled():
            if glob.pause_img.get_rect(topleft=glob.PAUSE_ONE_PLAYER_POS).collidepoint(pygame.mouse.get_pos()):
                gui.pause_menu.enable()

    #ako su ukljuceni meniji, prikupljamo dogadjaje u njima
    if gui.main_menu.is_enabled():
        gui.main_menu.mainloop(events)
    elif gui.pause_menu.is_enabled():
        gui.pause_menu.mainloop(events)

def check_player_events(player, burst_fire):
    cont = cls.Controler()
    movement = 4
    left_margin = 0 + 10
    right_margin = glob.WINDOW_SIZE[0] - 70
    pressed = pygame.key.get_pressed()

    if pressed[cont.get_control('Left')] and player.position_x > left_margin:
        player.position_x -= movement

    if pressed[cont.get_control('Right')] and player.position_x < right_margin:
        player.position_x += movement

    if pressed[cont.get_control('Fire')]:
        # Metak se ispaljuje u svakom 50-tom ciklusu
        if burst_fire % 50 is 0:
            #Zvuk pri ispaljivanju metaka
            rocket_sound = mixer.Sound('sounds/laser.wav')
            rocket_sound.play()

            rocket = cls.Rocket()
            rocket.rect.x = player.position_x + 26  # razlika u velicina slika
            rocket.rect.y = player.position_y

            glob.all_sprites_list.add(rocket)
            glob.rockets_list.add(rocket)
        burst_fire += 1
    else:
        burst_fire = 0

    return burst_fire

def make_enemies(number):
    for n in range(number):
        enm = cls.Enemy()
        enm.rect.y = 0
        distance = glob.WINDOW_SIZE[0]/number
        enm.rect.x = n * distance   
        glob.enemies_list.add(enm)
        glob.all_sprites_list.add(enm)

def draw_player(player): 
    if player.score > 0:
        player.show()
    else:
        if player.lifes_number > 0:
            player.lifes_number -= 1
            player.score = 100
            player.show_score()
            pygame.display.update()
            TIME.sleep(0.5)

def draw_destroyer(destroyer, timer_destroyer):
    timer_destroyer += 3
    destroyer.rect.x = glob.WINDOW_SIZE[0] / 2 - 64
    destroyer.rect.y = (int(timer_destroyer / 5) - 240 if timer_destroyer < 1400 else 40)
    
    if destroyer.health > 0:
        destroyer.show()
        if timer_destroyer > 1000:
            pygame.draw.rect(gui.screen, (200, 10, 10), (150, 10, destroyer.health * 10, 20))
            destroyer.is_ready = True
    
    return timer_destroyer

def enemies_fire_to_player(player, game_timer):
    
    if game_timer < 1200:
        return

    rand_enm = random.choice(glob.enemies_list.sprites())
    num_enemies = len(glob.enemies_list.sprites())

    if game_timer % int(200/num_enemies) == 0: #Napad neprijatelja: 160 ucestalost paljbe
        bul = cls.BulletEnemy()
        bul.rect.x = rand_enm.rect.x + 20
        bul.rect.y = rand_enm.rect.y + 20
        seanse = math.sqrt( (bul.rect.x - player.position_x)**2 + (bul.rect.y - player.position_y)**2)
        bul.direction[0] = (player.position_x - bul.rect.x) / seanse + 0.1
        bul.direction[1] = (player.position_y - bul.rect.y) / seanse + 0.1
        glob.bullets_enm_list.add(bul)
        glob.all_sprites_list.add(bul)

    glob.bullets_enm_list.draw(gui.screen)

def check_bullets_player_collide(player):

    for bullet in glob.bullets_enm_list:
        if bullet.rect.x in range(player.position_x, player.position_x + 64):
            if bullet.rect.y in range(player.position_y+20, player.position_y + 64):
                glob.bullets_enm_list.remove(bullet)
                player.score -= 20


        if bullet.rect.y > 1000:
            glob.bullets_enm_list.remove(bullet)


def check_rocket_to_enemise_colide(destroyer):
     for r in glob.rockets_list:
         r.show_rocket()

         # Obrada kolizije player vs enemies
         enemy_hit_list = pygame.sprite.spritecollide(r, glob.enemies_list, True)

         for enm in enemy_hit_list:
             glob.rockets_list.remove(r)
             glob.all_sprites_list.remove(r)
             glob.enemies_list.remove(enm)

         #ako je destroyer spreman onda mozemo da pucamo na njega i da mu skidamo health-e
         if destroyer.is_ready:
             # Obrada kolizije player vs destroyer
             if r.rect.x in range(destroyer.rect.x, destroyer.rect.x + 120):
                 dist = 120 - r.rect.x + destroyer.rect.x
                 dist = dist if dist < 64 else 120 - dist
                 if r.rect.y < destroyer.rect.y + 3*dist + 40:
                     glob.rockets_list.remove(r)
                     glob.all_sprites_list.remove(r)

                     #Zvuk eksplozije kada metak pogodi protivnika
                     explosion_sound = mixer.Sound('sounds/explosion.wav')
                     explosion_sound.play()

                     destroyer.health -= 10  

         if r.rect.y < -20:
             glob.rockets_list.remove(r)
             glob.all_sprites_list.remove(r)

def move_enemies(game_timer):
    # Primer kretanja neprijatelja
    i = 0
    for enm in glob.enemies_list:
        i += 1
        if game_timer < 1000:
            enm.rect.x += 0
            enm.rect.y = int(game_timer/10) - 80
            if i % 2 == 0 : 
                enm.rect.y += 100

        if game_timer > 3000:
            enm.rect.y = 100 + 100 * math.cos(game_timer/100+i*30)
            enm.rect.x = math.sin(game_timer/100)*400 + 100 * math.sin(game_timer/100+i*30) + 600

def start_game_one_player():

    player = cls.Player()
    destroyer = cls.Destroyer()
    make_enemies(15)
    
    game_timer = 0  # Tajmer igrice
    timer_destroyer = 0 # Tajmer postavljanja destrojera
    burst_fire = 0 # Tajmer rafala
    next_level = True # da znamo da li igramo igricu ili isrctavamo prelazak nivoa

    while True:
        game_timer += 3
        gui.screen.blit(glob.game_background, (0, 0))
        gui.screen.blit(glob.pause_img, glob.PAUSE_ONE_PLAYER_POS)

        if next_level:
            #ako smo presli nivo, iscratavamo prelazak i presakcemo sve ostale funckije
            #jedino moramo da pozovemo update() da bi se postavile slike
            next_level = False
            gui.screen.blit(pygame.image.load('images/up-level.png'), (50, 225))
            gui.screen.blit(pygame.image.load(glob.LEVEL_IMAGES[glob.LEVEL]), (50+256, 225))
            pygame.display.update()
            TIME.sleep(2)
            continue

        # Funkcija koja pravi animaciju kretanja
        move_enemies(game_timer)

        # Iscrtaj EMI figter-e
        for enm in glob.enemies_list:
            enm.show()

        # Ako ima nepriajtelja, neka ispaljuju metkove
        num_enemies = len(glob.enemies_list.sprites())
        if num_enemies > 0:
            # Ispaljivanje metkova od strane nepriajtelja
            enemies_fire_to_player(player, game_timer)

        else:
            timer_destroyer = draw_destroyer(destroyer, timer_destroyer)
            
            if destroyer.health <= 0:
                #DODATA cela else grana, ako je destroyer.health = 0, onda prelazimo na veci nivo
                #i brisemo sve iz listi kako ne bi ostali upamceni metkovi
                #ponovo pozivamo start_game_one_player
                if glob.LEVEL == 3:
                    exit()
                glob.LEVEL += 1
                for r in glob.rockets_list:
                    glob.rockets_list.remove(r)
                    glob.all_sprites_list.remove(r)

                glob.all_sprites_list.update()
                start_game_one_player()

        # Funkcija koja proverava da li je pogodjen player
        check_bullets_player_collide(player)
    
        # Funkcija za proveru dogadjaja u meniju
        check_menu_events()

        # Funkcija za proveru dogadjaja nad player-om
        burst_fire = check_player_events(player, burst_fire)

        # Funkcija za proveru pogotka u (sve) neprijatelje
        check_rocket_to_enemise_colide(destroyer)

        # Funkcija za iscrtavanje player-a  ( X-Wing )  
        draw_player(player)


        glob.all_sprites_list.update()
        pygame.display.update()


def start_game_two_player():

    gui.background = pygame.image.load('images/game_background.jpg')
    player_img = pygame.image.load('images/player.png')
    pause_img = pygame.image.load('images/pause.png')

    while True:
        gui.screen.blit(gui.background, (0, 0))
        pygame.draw.line(gui.screen, glob.BLACK_COLOR, glob.WALL_START_POS, glob.WALL_END_POS, glob.WALL_WIDTH)
        gui.screen.blit(player_img, (280, 600))
        gui.screen.blit(player_img, (950, 600))
        gui.screen.blit(pause_img, glob.PAUSE_TWO_PLAYERS_POS)

        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    exit()

            #Ukoliko smo kliknuli na pauzu, otvaramo pause_meni i zaustavljamo muziku
            if e.type == pygame.MOUSEBUTTONDOWN and gui.pause_menu.is_disabled():
                if pause_img.get_rect(topleft=glob.PAUSE_TWO_PLAYERS_POS).collidepoint(pygame.mouse.get_pos()):
                    gui.pause_menu.enable()

        if gui.main_menu.is_enabled():
            gui.main_menu.mainloop(events)
        elif gui.pause_menu.is_enabled():
            gui.pause_menu.mainloop(events)

        pygame.display.update()


def start_game():

    if glob.NUM_PLAYERS == 'ONE_PLAYER':
        mixer.music.stop() #zaustavljamo muziku menija
        gui.main_menu.disable()
        mixer.music.load('sounds/background.wav')
        mixer.music.play(-1) #pustamo muziku igrice
        mixer.music.set_volume(glob.GAME_VOLUME)
        start_game_one_player()
    else:
        mixer.music.stop() #zaustavljamo muziku menija
        gui.main_menu.disable()
        mixer.music.load('sounds/background.wav')
        mixer.music.play(-1) #pustamo muziku igrice
        mixer.music.set_volume(glob.GAME_VOLUME)
        start_game_two_player()
