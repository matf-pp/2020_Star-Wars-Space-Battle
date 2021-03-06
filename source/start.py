from source import gui
from source import glob
from source import two_players as two
from source import one_player as one
from pygame import mixer


def start_game():

    if glob.NUM_PLAYERS == 'ONE_PLAYER':
        mixer.music.stop() #zaustavljamo muziku menija
        gui.main_menu.disable()
        mixer.music.load('sounds/background.mp3')
        mixer.music.play(-1) #pustamo muziku igrice
        mixer.music.set_volume(glob.GAME_VOLUME)
        one.start_game_one_player()
    else:
        mixer.music.stop() #zaustavljamo muziku menija
        gui.main_menu.disable()
        mixer.music.load('sounds/background.mp3')
        mixer.music.play(-1) #pustamo muziku igrice
        mixer.music.set_volume(glob.GAME_VOLUME)
        two.start_game_two_player()
