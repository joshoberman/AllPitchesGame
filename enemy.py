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
    a_notes = listdir("Notes/A")
    a_notes = ["Notes/A/{0}".format(i) for i in a_notes if not i.startswith('.')]
    aSharp_notes = listdir("Notes/A#")
    aSharp_notes = ["Notes/A#/{0}".format(i) for i in aSharp_notes if not i.startswith('.')]
    b_notes = listdir("Notes/B")
    b_notes = ["Notes/B/{0}".format(i) for i in b_notes if not i.startswith('.')]
    c_notes = listdir("Notes/C")
    c_notes = ["Notes/C/{0}".format(i) for i in c_notes if not i.startswith('.')]
    cSharp_notes = listdir("Notes/C#")
    cSharp_notes = ["Notes/C#/{0}".format(i) for i in cSharp_notes if not i.startswith('.')]
    d_notes = listdir("Notes/D")
    d_notes = ["Notes/D/{0}".format(i) for i in d_notes if not i.startswith('.')]
    dSharp_notes = listdir("Notes/D#")
    dSharp_notes = ["Notes/D#/{0}".format(i) for i in dSharp_notes if not i.startswith('.')]
    e_notes = listdir("Notes/E")
    e_notes = ["Notes/E/{0}".format(i) for i in e_notes if not i.startswith('.')]
    f_notes = listdir("Notes/F")
    f_notes = ["Notes/F/{0}".format(i) for i in f_notes if not i.startswith('.')]
    fSharp_notes = listdir("Notes/F#")
    fSharp_notes = ["Notes/F#/{0}".format(i) for i in fSharp_notes if not i.startswith('.')]
    g_notes = listdir("Notes/G")
    g_notes = ["Notes/G/{0}".format(i) for i in g_notes if not i.startswith('.')]
    gSharp_notes = listdir("Notes/G#")
    gSharp_notes = ["Notes/G#/{0}".format(i) for i in gSharp_notes if not i.startswith('.')]

    enemyA_images = listdir("Images/Enemies/EnemyA")
    enemyA_images = ["Images/Enemies/EnemyA/{0}".format(i) for i in enemyA_images if not i.startswith('.')]
    enemyB_images = listdir("Images/Enemies/EnemyB")
    enemyB_images = ["Images/Enemies/EnemyB/{0}".format(i) for i in enemyB_images if not i.startswith('.')]
    offscreen_time = 6 #seconds before appearance
    enemySightTime = []
    centerScreen = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2)
    target = centerScreen
    speed = 1
    targetReached = False

    def __init__(self, enemy_type, variance = True):
        """ Constructor, create the image of the enemy/sound for enemy. Selected from three enemy types """
        pygame.sprite.Sprite.__init__(self)
        self.targetReached = False
        self.enemy_type = enemy_type
        self.offsetTime = self.speed*FPS*self.offscreen_time #multiply by FPS for fps-->s (FPS should be 60 and in global_variables file)
        self.offset_points = [(-self.offsetTime,-self.offsetTime),(SCREEN_WIDTH+self.offsetTime,-self.offsetTime),
        (SCREEN_WIDTH+self.offsetTime,SCREEN_HEIGHT//2),(SCREEN_WIDTH+self.offsetTime, SCREEN_HEIGHT+self.offsetTime), (-self.offsetTime, SCREEN_HEIGHT+self.offsetTime), (-self.offsetTime, SCREEN_HEIGHT//2)]
        #self.env = pyo.Fader(fadein=.01,fadeout=.2, dur=0) #amplitude envelope to get rid of pops
        self.pop = pyo.SfPlayer("Sounds/kill.wav")#for when enemy dies
        self.variance = variance
        if self.variance:
            self.ind = random.randrange(0,11,1)
        else:
            self.ind = 5
        
        if self.enemy_type == 'A1':
            self.notes = [pyo.SndTable(note) for note in self.gSharp_notes]
            self.image = pygame.image.load(self.enemyA_images[0])
            self.offset_point = self.offset_points[0]
        
        elif self.enemy_type == 'A2':
            self.image = pygame.image.load(self.enemyA_images[1])
            self.notes = [pyo.SndTable(note) for note in self.a_notes]
            self.offset_point = self.offset_points[1]

        elif self.enemy_type == 'A3':
            self.image = pygame.image.load(self.enemyA_images[2])
            self.notes = [pyo.SndTable(note) for note in self.aSharp_notes]
            self.offset_point = self.offset_points[2]

        elif self.enemy_type == 'A4':
            self.image = pygame.image.load(self.enemyA_images[3])
            self.notes = [pyo.SndTable(note) for note in self.b_notes]
            self.offset_point = self.offset_points[3]
        
        elif self.enemy_type == 'A5':
            self.image = pygame.image.load(self.enemyA_images[4])
            self.notes = [pyo.SndTable(note) for note in self.fSharp_notes]
            self.offset_point = self.offset_points[4]

        elif self.enemy_type == 'A6':
            self.image = pygame.image.load(self.enemyA_images[5])
            self.notes = [pyo.SndTable(note) for note in self.g_notes]
            self.offset_point = self.offset_points[5]
        
        if self.enemy_type == 'B1':
            self.image = pygame.image.load(self.enemyB_images[0])
            self.notes = [pyo.SndTable(note) for note in self.d_notes]
            self.offset_point = self.offset_points[0]

        elif self.enemy_type == 'B2':
            self.image = pygame.image.load(self.enemyB_images[1])
            self.notes = [pyo.SndTable(note) for note in self.dSharp_notes]
            self.offset_point = self.offset_points[1]

        elif self.enemy_type == 'B3':
            self.image = pygame.image.load(self.enemyB_images[2])
            self.notes = [pyo.SndTable(note) for note in self.e_notes]
            self.offset_point = self.offset_points[2]

        elif self.enemy_type == 'B4':
            self.image = pygame.image.load(self.enemyB_images[2])
            self.notes = [pyo.SndTable(note) for note in self.f_notes]
            self.offset_point = self.offset_points[3]
        
        elif self.enemy_type == 'B5':
            self.image = pygame.image.load(self.enemyB_images[4])
            self.notes = [pyo.SndTable(note) for note in self.c_notes]
            self.offset_point = self.offset_points[4]

        elif self.enemy_type == 'B6':
            self.image = pygame.image.load(self.enemyB_images[5])
            self.notes = [pyo.SndTable(note) for note in self.cSharp_notes]
            self.offset_point = self.offset_points[5]
            
        self.image = pygame.transform.smoothscale(self.image, (40,40))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        """self._freq = pyo.midiToHz(note)
        #get min and max +-25 cents around that note
        self._minimum = self._freq * (2.**(-25./1200.))
        self._maximum = self._freq * (2.**(25./1200.))
        self._env = pyo.Adsr(attack=.1, decay=.05, sustain=.4, release=.1, dur=0.5, mul=.3)
        self._wave1 = pyo.SquareTable(order = 12).normalize()"""
        """self._wave2 = GenWaveForm(order = 10, odd  = False).normalize()
        self._mainTable = pyo.NewTable(length=8192./SR, chnls=1)
        self._lfo = pyo.Sine(.2, 0, .5, .5)
        self._mor = pyo.TableMorph(self._lfo, self._mainTable, [self._wave1,self._wave2])
        self._osc = pyo.Osc(table = self._wave1, freq = [self._freq, self._freq], mul = self._env).out()"""
        snd = self.notes[self.ind]
        freq = snd.getRate()
        if not self.variance:
            self.sound = pyo.TableRead(snd, freq=freq, mul=1)
        elif self.variance:
            self.sound = pyo.TableRead(snd, freq = freq, mul = 1)

    def set_target(self,targX,targY):
        self.target = (targX,targY)

    def generate(self):
        """ generate the enemy off screen """
        #distance for offset = desired time * velocity
        #ns.sync()
        self.offsetCoords = self.offset_point
        self.rect.x = self.offsetCoords[0]
        self.rect.y = self.offsetCoords[1]

    #this function will return an amount in cents to move up/down
    def random_walk(self):
        coinFlip = random.randrange(2) #'coin flip' to determine whether to move or stay the same
        if coinFlip == 0 and self.ind != 0 and self.ind != 10:
            self.ind += 1
        elif coinFlip == 1 and self.ind != 0 and self.ind != 10:
            self.ind -= 1
        #if at maximum or minimum, move back up or down
        elif self.ind == 0:
            self.ind += 1
        elif self.ind == 10:
            self.ind -= 1


    def playNotes(self):
        if self.variance:
            def repeat():
                """we could put another function in here to vary the notes on any dimension (e.g. harmonics, fundamental freq, amplitude)"""
                self.random_walk()
                snd = self.notes[self.ind]
                freq = snd.getRate()
                self.sound = pyo.TableRead(snd, freq = freq, mul = 1).out()
            self.pat = pyo.Pattern(function = repeat,time = 0.5).play()
        elif not self.variance:
            def repeat():
                self.sound.out()
            self.pat = pyo.Pattern(function = repeat, time = 0.5).play()

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
            if t_dist < speed*2:
                self.target = None
                self.targetReached = True
