from os import mkdir, path
import pygame
from game import Game
import pyo
from global_variables import *
from psychopy import core
from sys import platform
import pandas as pd
    
         
def main():
    def checkData(subj):
        if VERSION==1:
            if path.exists("Subject %s/Variance/"%subj):
                subj = raw_input("Data already exists for that subject, Please choose a different subject number: ")
                return checkData(subj)
        elif VERSION==2:
            if path.exists("Subject %s/NoVariance/"%subj):
                subj = raw_input("Data already exists for that subject, Please choose a different subject number: ")
                return checkData(subj)
        return subj
    
    VERSION = int(raw_input("Condition (1 or 2): "))
    SUBJECT = checkData(subj = raw_input("Subject Number: "))
    if not path.exists("Subject %s"%SUBJECT):
        mkdir("Subject %s"%SUBJECT)
        print "Making subject directory"

    """ Main program function. """
    # Initialize Pygame and set up the window
    pygame.display.init()
    pygame.font.init()
    #start pyo sound, use lowest latency output
    if platform == "linux2":
        s = pyo.Server(sr = SR, buffersize=256, audio = 'jack', duplex = 0)
    elif platform == "win64" or platform == "win32":
        s = pyo.Server(sr = SR, duplex=0)
        s.setOutputDevice(14)
    else:
        s = pyo.Server(sr = SR, duplex = 0)
    s.boot()
    s.start()
    
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    bgimage = pygame.image.load("Images/planet.bmp")
    bgimage = pygame.transform.scale(bgimage, (SCREEN_WIDTH, SCREEN_HEIGHT))
     
    # Create our objects and set the data
    done = False
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    
    # Create an instance of the Game class
    game = Game(VERSION = VERSION)
    # Main game loop
    while not done:
        # Process events (keystrokes, mouse clicks, etc)
        done = game.process_events()
        #draw bg image
        screen.blit(bgimage, [0,0])

        # Update object positions, check for collisions
        game.run_logic()
         
        # Draw the current frame
        game.display_frame(screen)
         
        # Pause for the next frame
        clock.tick(FPS)

    if VERSION==1:
        directory="Subject %s/Variance/"%SUBJECT
        if not path.exists(directory):
            mkdir(directory)
    elif VERSION==2:
        directory = "Subject %s/NoVariance/"%SUBJECT
        if not path.exists(directory):
            mkdir(directory)

    print Game.gameData
    general = pd.DataFrame(Game.gameData)
    general.to_csv(directory+'generalData.csv')

    #shut down pyo server
    s.stop()
    # Close window and exit
    pygame.quit()
    core.quit()

 
# Call the main function, start up the game
if __name__ == "__main__":
    main()