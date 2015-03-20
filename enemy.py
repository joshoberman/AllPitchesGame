import pygame
import pyo
import random
from os import listdir
from global_variables import *
from psychopy import core
from vector import Vector
from player import Player
from additiveSynth import GenWaveForm

class Enemy(pygame.sprite.Sprite):
    """ This class represents the enemies """
    enemyA_images = listdir("Images/Enemies/EnemyA")
    enemyA_images = ["Images/Enemies/EnemyA/{0}".format(i) for i in enemyA_images if not i.startswith('.')]
    enemyB_images = listdir("Images/Enemies/EnemyB")
    enemyB_images = ["Images/Enemies/EnemyB/{0}".format(i) for i in enemyB_images if not i.startswith('.')]
    offscreen_time = 4 #seconds before appearance
    enemySightTime = []
    centerScreen = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2)
    target = centerScreen
    speed = 1
    targetReached = False
    offsetTime = speed*FPS*offscreen_time #multiply by FPS for fps-->s (FPS should be 60 and in global_variables file)
    offset_points = [(-offsetTime,-offsetTime),(SCREEN_WIDTH+offsetTime,-offsetTime),
    (SCREEN_WIDTH+offsetTime,SCREEN_HEIGHT//2),(SCREEN_WIDTH+offsetTime, SCREEN_HEIGHT+offsetTime), (-offsetTime, SCREEN_HEIGHT+offsetTime), (-offsetTime, SCREEN_HEIGHT//2)]

    def __init__(self, enemy_type):
        """ Constructor, create the image of the enemy/sound for enemy. Selected from three enemy types """
        pygame.sprite.Sprite.__init__(self)
        self.targetReached = False
        self.enemy_type = enemy_type
        #self.env = pyo.Fader(fadein=.01,fadeout=.2, dur=0) #amplitude envelope to get rid of pops
        self.pop = pyo.SfPlayer("Sounds/kill.wav")#for when enemy dies
        if self.enemy_type == 'A1':
            self.image = pygame.image.load(self.enemyA_images[0])
            note = 60
            self.offset_point = self.offset_points[0]
        
        elif self.enemy_type == 'A2':
            self.image = pygame.image.load(self.enemyA_images[1])
            note = 62
            self.offset_point = self.offset_points[1]

        elif self.enemy_type == 'A3':
            self.image = pygame.image.load(self.enemyA_images[2])
            note = 64
            self.offset_point = self.offset_points[2]

        elif self.enemy_type == 'A4':
            self.image = pygame.image.load(self.enemyA_images[3])
            note = 66
            self.offset_point = self.offset_points[3]
        
        elif self.enemy_type == 'A5':
            self.image = pygame.image.load(self.enemyA_images[4])
            note = 68
            self.offset_point = self.offset_points[4]

        elif self.enemy_type == 'A6':
            self.image = pygame.image.load(self.enemyA_images[5])
            note = 70
            self.offset_point = self.offset_points[5]
        
        """elif self.enemy_type == 'A7':
            self.image = pygame.image.load(self.enemyA_images[6])

        elif self.enemy_type == 'A8':
            self.image = pygame.image.load(self.enemyA_images[7])
        
        elif self.enemy_type == 'A9':
            self.image = pygame.image.load(self.enemyA_images[8])

        elif self.enemy_type == 'A10':
            self.image = pygame.image.load(self.enemyA_images[9])

        elif self.enemy_type == 'A11':
            self.image = pygame.image.load(self.enemyA_images[10])

        elif self.enemy_type == 'A12':
            self.image = pygame.image.load(self.enemyA_images[11])"""

        if self.enemy_type == 'B1':
            self.image = pygame.image.load(self.enemyB_images[0])
            note = 61
            self.offset_point = self.offset_points[0]

        elif self.enemy_type == 'B2':
            self.image = pygame.image.load(self.enemyB_images[1])
            note = 63
            self.offset_point = self.offset_points[1]

        elif self.enemy_type == 'B3':
            self.image = pygame.image.load(self.enemyB_images[2])
            note = 65
            self.offset_point = self.offset_points[2]

        elif self.enemy_type == 'B4':
            self.image = pygame.image.load(self.enemyB_images[3])
            note = 67
            self.offset_point = self.offset_points[3]
        
        elif self.enemy_type == 'B5':
            self.image = pygame.image.load(self.enemyB_images[4])
            note = 69
            self.offset_point = self.offset_points[4]

        elif self.enemy_type == 'B6':
            self.image = pygame.image.load(self.enemyB_images[5])
            note = 71
            self.offset_point = self.offset_points[5]
            
        self.image = pygame.transform.smoothscale(self.image, (85,85))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self._freq = pyo.midiToHz(note)
        self._env = pyo.Adsr(attack=.1, decay=.05, sustain=.4, release=.1, dur=0.5, mul=.3)
        self._wave1 = pyo.SquareTable(order = 15).normalize()
        """self._wave2 = GenWaveForm(order = 10, odd  = False).normalize()
        self._mainTable = pyo.NewTable(length=8192./SR, chnls=1)
        self._lfo = pyo.Sine(.2, 0, .5, .5)
        self._mor = pyo.TableMorph(self._lfo, self._mainTable, [self._wave1,self._wave2])"""
        self._osc = pyo.Osc(table = self._wave1, freq = [self._freq, self._freq], mul = self._env).out()

    def set_target(self,targX,targY):
        self.target = (targX,targY)

    def generate(self):
        """ generate the enemy off screen """
        #distance for offset = desired time * velocity
        #ns.sync()
        self.offsetCoords = self.offset_point
        self.rect.x = self.offsetCoords[0]
        self.rect.y = self.offsetCoords[1]

    def playNotes(self):
        def repeat():
            self._env.play()
            #self._wave1.order-=1
        self.pat = pyo.Pattern(function = repeat,time = 1).play()

    def stopNotes(self):
        self.pat.stop()
        self.pat = None
        self._freq = None
    
    def wrong_hit(self):
        """play a sound, decrease score when wrong bullet hits enemy"""
        self.miss = pyo.SfPlayer("Sounds/buzz_alt.wav", loop=False, mul = 0.2)
        self.miss.out()
    
    def update(self):
        """ Automatically called when we need to move the enemy. """
        """ Set Vector towards player"""
        if self.target:
            position = Vector(self.rect.x, self.rect.y) # create a vector from center x,y value
            targ = Vector(self.target[0],self.target[1]) # and one from the target x,y
            dist = targ - position # get total distance between target and position
            direction = dist.normalize() # normalize so its constant in all directions
            self.rect.x += (round(direction[0]) * self.speed) # calculate speed from direction to move and speed constant, rounding debugs the diagonal vectors
            self.rect.y += (round(direction[1]) * self.speed)
            dist_x = round(abs(dist[0])) # gets absolute value of the x distance
            dist_y = round(abs(dist[1])) # gets absolute value of the y distance
            t_dist = dist_x + dist_y # gets total absolute value distance
            speed = abs(self.speed) # gets aboslute value of the speed
            if t_dist < speed*8:
                self.target = None
                self.targetReached = True
