import pygame
from vector import Vector
from player import Player
from global_variables import *

class Bullet(pygame.sprite.Sprite):
    bulletSpeed = 12
    def __init__(self, color, target, degree, origin):
        pygame.sprite.Sprite.__init__(self)                  
        self.image = pygame.Surface([15, 20])
        self.image.fill(color)
        self.rotated = pygame.transform.rotate(self.image, degree)
        self.rect = self.rotated.get_rect()
        self.trueX = origin[0]
        self.trueY = origin[1]
        position = Vector(self.trueX,self.trueY) # create a vector from center x,y value. This will be from player
        targ = Vector(target[0],target[1]) # and one from the target x,y
        self.dist = targ - position # get total distance between target and position
    def update(self):
        self.direction = self.dist.normalize() # normalize so its constant in all directions
        self.trueX += (self.direction[0] * self.bulletSpeed) # calculate speed from direction to move and speed constant
        self.trueY += (self.direction[1] * self.bulletSpeed)
        self.rect.center = (round(self.trueX),round(self.trueY)) # apply values to sprite.center