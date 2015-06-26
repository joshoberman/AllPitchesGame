import pygame, math
from pygame.locals import *
from vector import Vector
from global_variables import *

class Player(pygame.sprite.Sprite):

    def __init__(self):
        '''
        Class:
            creates a sprite
        Parameters:
            - self
        '''
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("ship.bmp") # load image
        self.image.set_colorkey(BLACK)
        #define radius for tracing circle around player
        self.radius = 500

        self.trueX = SCREEN_WIDTH//2 # created because self.rect.center does not hold
        self.trueY = SCREEN_HEIGHT//2 # decimal values but these do
        self.originPoint = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2)
        self.speed = 10 # movement speed of the player when capturing
        self.rotationSpeed = 3 #rotation speed of player
        self.turnLeft = False
        self.turnRight = False

        self.target = None # starts off with no target
        self.degree = 0

        self.targetReached = False #tells us when we've reached the target, if it's True, target returns to origin point
        self.atCenter = True #tells us if player is still in the middle (i.e. not capturing)--if enemyA collides, explodes and causes damage, if enemyB collides, no points gained

    def get_direction(self, target):
        '''
        Function:
            takes total distance from sprite.center
            to the sprites target
            (gets direction to move)
        Returns:
            a normalized vector
        Parameters:
            - self
            - target
                x,y coordinates of the sprites target
                can be any x,y coorinate pair in
                brackets [x,y]
                or parentheses (x,y)
        '''
        if self.target: # if the square has a target
            position = Vector(self.trueX,self.trueY) # create a vector from center x,y value
            target = Vector(self.target[0],self.target[1]) # and one from the target x,y
            self.dist = target - position # get total distance between target and position

            direction = self.dist.normalize() # normalize so its constant in all directions
            return direction
        
    def distance_check(self, dist):
        '''
        Function:
            tests if the total distance from the
            sprite to the target is smaller than the
            ammount of distance that would be normal
            for the sprite to travel
            (this lets the sprite know if it needs
            to slow down. we want it to slow
            down before it gets to it's target)
        Returns:
            bool
        Parameters:
            - self
            - dist
                this is the total distance from the
                sprite to the target
                can be any x,y value pair in
                brackets [x,y]
                or parentheses (x,y)
        '''
        dist_x = dist[0] ** 2 # gets absolute value of the x distance
        dist_y = dist[1] ** 2 # gets absolute value of the y distance
        t_dist = dist_x + dist_y # gets total absolute value distance
        speed = self.speed ** 2 # gets aboslute value of the speed

        if t_dist < (speed): # read function description above
            return True
            if self.target == self.originPoint:
                self.atCenter = True
        

    def update(self):
        '''
        Function:
            gets direction to move then applies
            the distance to the sprite.center
            ()
        Parameters:
            - self
        '''
        ##ROTATED
        #rotate surf by DEGREE amount degrees
        self.rotated =  pygame.transform.rotate(self.image, self.degree)

        #get the rect of the rotated surf and set it's center to the oldCenter
        self.rect = self.rotated.get_rect()
        self.rect.center = self.originPoint

        #turn right or left
        if self.turnRight:
            self.degree-=self.rotationSpeed
        if self.turnLeft:
            self.degree+=self.rotationSpeed

        if self.degree > 360:
            self.degree = 0
        if self.degree < -360:
            self.degree = 0

        #keep track of target position relative to front of player(define vector b/t front of player and point on imaginary outer circle)
        self.radian = math.radians(-(self.degree+90))
        self.targX = self.radius*math.cos(self.radian)+self.trueX
        self.targY = self.radius*math.sin(self.radian)+self.trueY
        self.currTarget = (self.targX,self.targY)

        self.dir = self.get_direction(self.target) # get direction
        if self.dir: # if there is a direction to move
            if self.distance_check(self.dist): # if we need to stop
                self.rect.center = self.target # center the sprite on the target
                if self.target == self.originPoint:
                    self.atCenter = True
                self.targetReached = True
            if self.targetReached:
                self.target = self.originPoint
                self.targetReached = False
            else: # if we need to move normal
                self.trueX += (self.dir[0] * self.speed) # calculate speed from direction to move and speed constant
                self.trueY += (self.dir[1] * self.speed)
                self.rect.center = (round(self.trueX),round(self.trueY)) # apply values to sprite.center
                self.atCenter = False

    def capture(self):
        self.target = self.currTarget
