from os import mkdir, path, listdir
import pygame 
from psychopy import core
import pyo
from bullet import Bullet
from enemy import Enemy
from player import Player
from global_variables import *
from random import shuffle, randrange, choice
import pandas as pd


"""
IMPORTANT, versions are as follows:
    1: pre-test
    2:training with congruent labels
    3:training with incongruent labels
    4:training without labels
    5: post-test

    familiarization game to be loaded seperately
"""

class Game(object):
    """ This class represents an instance of the game. If we need to
        reset the game we'd just need to create a new instance of this
        class. """
 
    def whichVersion(version):
        if int(version) > 5:
            version = raw_input("Not a valid version, please input version number 1-5: ")
            return whichVersion(version)
        else:
            return version


    # --- Class attributes. 
     
    # Sprite lists
    alienA_list = None
    alienB_list = None
    bullet_list = None
    all_sprites_list = None
    player = None
    #Time measurements
    enemy_live = False #bool to tell us if there is a live enemy
    elapsedTime = 0.0 #keep track of elapsed time via frame rate changes
    enemySpawnTime= 240.0 # of frames between enemy death and next enemy spawn

    #for transitioning from training to post test
    game_over = False

    #this is for making animated explosions
    isExplosion_center = False
    isExplosion_enemy = False
    isExplosion_player = False
    explosion_img = pygame.image.load('Images/explosion1.bmp')

    exp1 = pygame.transform.scale(explosion_img, (10,10))
    exp2 = pygame.transform.scale(explosion_img, (15,15))
    exp3 = pygame.transform.scale(explosion_img, (20,20))
    exp4 = pygame.transform.scale(explosion_img, (25,25))
    exp5 = pygame.transform.scale(explosion_img, (30,30))
    exp6 = pygame.transform.scale(explosion_img, (35,35))
    exp7 = pygame.transform.scale(explosion_img, (40,40))
    exp8 = pygame.transform.scale(explosion_img, (45,45))
    exp9 = pygame.transform.scale(explosion_img, (50,50))
    explosionDur = 0 #keep track of timing of explosion animation
    sight = False
    newBlock = False #elicit prospective assesment at each block
    AliensPerBlock = 5
    previousKill= False #helps keep track of whether previous trial was successful
    blockCount = 1
    variance = None

    #dicts that we can turn in to data frames for efficient data storage
    gameData = {'Score':[], 'EnemyType':[], 'TotalTime':[], "Success":[], "EnemyHitPlayer":[]}

    friendlyAliens = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6']
    enemyAliens = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']

    #these will be used to progress through training on only shoot and capture
    blocksShoot = 2
    blocksCapture = 2
    blocksBoth = 2
    numberAliensShootOnly = blocksShoot * AliensPerBlock
    numberAliensCaptureOnly = blocksCapture * AliensPerBlock
    numberAliensBothShootCapture = blocksBoth * AliensPerBlock
    # --- Class methods
    # Set up the game
    def __init__(self, VERSION):
        self.VERSION = VERSION
        if VERSION==1:
            self.variance = True
        elif VERSION == 2:
            self.variance = False

        self.gameData['Condition'] = VERSION

        self.shootList = []
        self.captureList = []
        self.bothList = []
        i = 1
        while(i<=self.numberAliensShootOnly):
            self.shootList.append(choice(self.friendlyAliens))
            i += 1
        i = 1
        while(i<=self.numberAliensCaptureOnly):
            self.captureList.append(choice(self.enemyAliens))
            i += 1
        i = 1
        while(i<=self.numberAliensBothShootCapture):
            self.bothList.append(choice(self.enemyAliens))
            i += 1

        self.aliens = self.shootList
        self.numberAliens = self.numberAliensShootOnly

        self.ammo = 300#(self.numberAliens/2)*3 #3 bullets per true 'enemy'
        
        shuffle(self.aliens)
        self.score = 0
        self.blockSuccesses = 0
        self.shootStart = True
        self.captureStart = False
        self.bothStart = False
        #to let us know when we're in the last phase of the game
        self.bothShootCapture = False
        #to prevent masking noise from being played at very beginning
        self.first_trial = True

        self.t = core.Clock()
         
        # Create sprite lists
        self.alienA_list = pygame.sprite.Group()
        self.alienB_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()
        self.bullet_list = pygame.sprite.Group()
         
        # Create the player
        self.player = Player()
        #shot sound
        self.shot_sound = pyo.SfPlayer("Sounds/laser_shot.aif", mul=0.4)
        #explosion sound
        self.wrong_button = pyo.SfPlayer("Sounds/wrong_hit.wav")
        self.explosionSound = pyo.SfPlayer("Sounds/explosion.wav", speed=[1,1], mul=0.5)

        #this plays the masking stuff
        t = pyo.CosTable([(0,0),(50,1), (500,0.3), (8191,0)])
        met = pyo.Metro(time=.2).play()
        amp = pyo.TrigEnv(met, table=t, dur=0.18, mul=.275)
        freq = pyo.TrigRand(met, min=400.0, max=1000.0)
        self.a = pyo.Sine(freq=[freq,freq], mul=amp)
        self.n = pyo.Noise(mul=.035).mix(2)
 
    def process_events(self):
        """ Process all of the events. Return a "True" if we need
            to close the window. """

        def shoot(color, target, degree, origin):
            #shoot to the point where the player is facing (given by target)
            if self.ammo > 0:
                self.bullet = Bullet(color, target, degree, origin)
                self.bullet.color = str(color)
                #play bullet sound
                self.shot_sound.out()
                #decrease ammo supply by 1
                self.ammo-=1
                # Add the bullet to the lists
                self.all_sprites_list.add(self.bullet)
                self.bullet_list.add(self.bullet)
            
            else:
                self.wrong_button.out()
         
        #Event handling

        self.events = pygame.event.get()

        for event in self.events:

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.turnLeft = True
                elif event.key == pygame.K_RIGHT:
                    self.player.turnRight = True
                elif event.key == pygame.K_SPACE:
                    if self.shootStart:
                        self.shootStart = False
                    elif self.captureStart:
                        self.captureStart = False
                    elif self.bothStart:
                        self.bothStart = False
                    elif self.newBlock:
                        #record then reset score, etc.
                        self.enemy_type = 'C' #cheap trick to stop label being played
                        self.newBlock = False
                        self.blockSuccesses = 0
                        self.score = 0
                        self.blockCount += 1
                        if self.blockCount == self.blocksShoot + 1:
                            self.captureStart = True
                            self.aliens = self.captureList
                            self.numberAliens = self.numberAliensCaptureOnly
                            Enemy.speed = 1
                            self.first_trial = True
                        elif self.blockCount == self.blocksShoot + self.blocksCapture + 1:
                            self.bothStart = True
                            self.aliens = self.bothList
                            self.numberAliens = self.numberAliensBothShootCapture
                            Enemy.speed = 1
                            self.bothShootCapture = True
                            self.first_trial = True
                elif event.key == pygame.K_s:
                    shoot(RED, self.player.currTarget, self.player.degree, (self.player.trueX,self.player.trueY))
                elif event.key == pygame.K_c:
                    self.player.capture()
                elif event.key == pygame.K_ESCAPE:
                    return True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.player.turnLeft = False
                elif event.key == pygame.K_RIGHT:
                    self.player.turnRight = False

        return False #for exiting game
 
    def run_logic(self):
        """
        This method is run each time through the frame. It
        updates positions, records data, and checks for collisions.
        """


        def post_mortem():
            self.enemy.stopNotes()
        
        def kill_enemy(enemy_type):
            font = pygame.font.Font(None, 25)
            RT = self.t.getTime()
            self.gameData['TotalTime'].append(RT)
            self.gameData['Success'].append(1)
            self.gameData['EnemyHitPlayer'].append(0)
            self.gameData['Score'].append(self.score)
            self.blockSuccesses += 1
            post_mortem()
            self.enemy.pop.out()
            self.score += 20
            self.elapsedTime = 0.0
            self.enemy_live = False
            self.previousKill = True

        if self.sight:
            self.t.reset()

        if not self.shootStart and not self.captureStart and not self.bothStart and not self.game_over and not self.newBlock:
            if not self.enemy_live and 30.0<self.elapsedTime<self.enemySpawnTime and not self.first_trial:
                #time to play masking noise
                self.n.out()
                self.a.out()

            if not self.enemy_live and self.elapsedTime==self.enemySpawnTime:
                print self.bullet_list
                self.a.stop()
                self.n.stop()
                if self.first_trial:
                    self.first_trial = False
                self.enemy_type = self.aliens.pop()
                self.gameData["EnemyType"].append(self.enemy_type)
                self.enemy = Enemy(self.enemy_type, variance = self.variance)
                self.enemy.generate()
                self.enemy.playNotes()
                self.all_sprites_list.add(self.enemy)
                
                if self.enemy_type[0]=='A':
                    self.alienA_list.add(self.enemy)
                
                elif self.enemy_type[0]=='B':
                    self.alienB_list.add(self.enemy)

                """for every number Aliens killed/captured that is 1/5th of total Aliens, increase speed"""

                if len(self.aliens)<(self.numberAliens-1) and self.previousKill and (sum(self.gameData['Success'])%(self.numberAliens//5)) == 0:
                    Enemy.speed+=1
                    self.player.speed+=1
                
                self.enemy_live = True
            
            if self.enemy_live:
                """ Record time right when enemy fully enters screen """
                if self.enemy.rect.y==0 or self.enemy.rect.y == SCREEN_HEIGHT or self.enemy.rect.x == 0 or self.enemy.rect.x == SCREEN_WIDTH:
                    self.sight = True
                #when enemy enters screen, decrease score
                if 0< self.enemy.rect.y<SCREEN_HEIGHT and 0 < self.enemy.rect.x <SCREEN_WIDTH:
                    self.score -= 1/float(60) # decrease score by 1 for every second that enemy is alive
                    self.sight = False
         
            
            # Move all the sprites
            self.all_sprites_list.update()
            self.player.update()
            
            #increase time for enemy spawn    
            self.elapsedTime +=1
            
            #collision detection
            for bullet in self.bullet_list:
                self.enemy_hit_list = pygame.sprite.spritecollide(bullet, self.alienA_list, True)
                for enemy in self.enemy_hit_list:
                    kill_enemy('A')
                    self.bullet_list.remove(bullet)
                    self.all_sprites_list.remove(bullet)
                    self.isExplosion_enemy = True
                    """if bullet goes off screen, remove it from sprites lists"""
                """give audio feedback if wrong sprite shot"""
                if pygame.sprite.spritecollide(bullet, self.alienB_list, True):
                    RT = self.t.getTime()
                    self.gameData['TotalTime'].append(RT)
                    self.gameData['Success'].append(0)
                    self.gameData['EnemyHitPlayer'].append(0)
                    self.gameData['Score'].append(self.score)
                    self.enemy.wrong_hit()
                    self.score -= 10
                    self.isExplosion_enemy = True
                    self.elapsedTime = 0
                    self.enemy_live = False
                    self.bullet_list.remove(bullet)
                    self.all_sprites_list.remove(bullet)
                    post_mortem()
                    self.previousKill=False
                if bullet.rect.x>SCREEN_WIDTH or bullet.rect.x<0 or bullet.rect.y>SCREEN_HEIGHT or bullet.rect.y<0:
                    self.bullet_list.remove(bullet)
                    self.all_sprites_list.remove(bullet)
            
 

            if self.player.atCenter:
                if pygame.sprite.spritecollide(self.player, self.alienB_list, True):
                    RT = self.t.getTime()
                    self.gameData['TotalTime'].append(RT)
                    self.gameData['Success'].append(0)
                    self.gameData['EnemyHitPlayer'].append(1)
                    self.gameData['Score'].append(self.score)
                    self.enemy_live = False
                    self.elapsedTime = 0
                    self.score -= 20
                    self.enemy.wrong_hit()
                    post_mortem()
                    self.previousKill=False
                
                if pygame.sprite.spritecollide(self.player, self.alienA_list, True):
                    RT = self.t.getTime()
                    self.gameData['TotalTime'].append(RT)
                    self.gameData['Success'].append(0)
                    self.gameData['EnemyHitPlayer'].append(1)
                    self.gameData['Score'].append(self.score)
                    self.enemy_live = False
                    self.elapsedTime = 0
                    self.score -= 20
                    self.isExplosion_center=True
                    self.explosionSound.out()
                    post_mortem()
                    self.previousKill=False
            
            elif not self.player.atCenter and self.enemy_live:
                
                if pygame.sprite.spritecollide(self.player, self.alienB_list, True):
                    if not self.enemy.targetReached:
                        kill_enemy('B')
                        self.player.targetReached = True
                    else:
                        RT = self.t.getTime()
                        self.gameData['TotalTime'].append(RT)
                        self.gameData['Success'].append(0)
                        self.gameData['EnemyHitPlayer'].append(1)
                        self.gameData['Score'].append(self.score)
                        self.enemy_live = False
                        self.enemy.wrong_hit()
                        self.elapsedTime = 0
                        self.score -= 20
                        post_mortem()
                        self.previousKill=False

                if pygame.sprite.spritecollide(self.player, self.alienA_list, True):
                    if not self.enemy.targetReached:
                        RT = self.t.getTime()
                        self.gameData['TotalTime'].append(RT)
                        self.gameData['Success'].append(0)
                        self.gameData['EnemyHitPlayer'].append(0)
                        self.gameData['Score'].append(self.score)      
                        self.enemy.wrong_hit()
                        self.enemy_live = False
                        self.elapsedTime = 0
                        self.score -= 10
                        self.isExplosion_enemy=True
                        self.player.targetReached=True
                        post_mortem()
                        self.previousKill=False
                    else:
                        RT = self.t.getTime()
                        self.gameData['TotalTime'].append(RT)
                        self.gameData['Success'].append(0)
                        self.gameData['EnemyHitPlayer'].append(1)
                        self.gameData['Score'].append(self.score)
                        self.explosionSound.out()
                        self.score -= 20
                        self.isExplosion_player = True
                        self.elapsedTime = 0
                        self.enemy_live = False
                        post_mortem()
                        self.previousKill=False
                      

            if not self.first_trial and (len(self.aliens)%(self.AliensPerBlock)==0) and not (self.isExplosion_player or self.isExplosion_center or self.isExplosion_enemy) and self.elapsedTime<25:
                self.newBlock = True
                self.render = False
                self.renderA = False
                self.renderB = False
                self.first_trial = True

            """define end of game"""
            if len(self.aliens)==0 and self.bothShootCapture and not self.enemy_live:
                self.game_over = True

                 
    def display_frame(self, screen):
        """ Display everything to the screen for the game. """
        def center_text(text):
            center_x = (SCREEN_WIDTH // 2) - (text.get_width() // 2)
            center_y = (SCREEN_HEIGHT // 2) - (text.get_height() // 2)
            screen.blit(text, [center_x, center_y])
        def next_line(text, spacing):
            center_x = (SCREEN_WIDTH // 2) - (text.get_width() // 2)
            center_y = (SCREEN_HEIGHT // 2) - (text.get_height() // 2) + spacing
            screen.blit(text, [center_x,center_y])

        if self.newBlock:  
            font = pygame.font.Font(None, 25)
            text2 = font.render("You successfully killed or captured a total of "+ str(self.blockSuccesses) +
                                " of the " + str(self.AliensPerBlock) + " aliens you encountered, for a score of %d."%(self.score),
                                True, GREEN)
            text3 = font.render("  Hit space to continue", True, GREEN)
            center_x = (SCREEN_WIDTH // 2) - (text2.get_width() // 2)
            center_y = (SCREEN_HEIGHT // 2) + (text2.get_height() // 2) + 2
            screen.blit(text2, [center_x, center_y])
            screen.blit(text3, [SCREEN_WIDTH//2-text3.get_width()//2, center_y + text2.get_height()+2])

        elif self.shootStart:
            font = pygame.font.Font(None, 20)
            text = font.render("Hello, thank you for participating in this experiment! For this part of the game, you will be using the 's' button to shoot the enemy aliens.",
                               True, WHITE)
            text2 = font.render ("Press the Space bar to begin", True, WHITE)
            center_text(text)
            next_line(text2, 60)


        elif self.captureStart:
            font = pygame.font.Font(None, 22)
            text = font.render("For this part of the game, you will be using the 'c' button to capture the friendly aliens.",
                               True, WHITE)
            text2 = font.render ("Press the Space bar to begin", True, WHITE)
            center_text(text)
            next_line(text2, 60)

        elif self.bothStart:
            font = pygame.font.Font(None, 22)
            text = font.render("For this part of the game, you will encounter both friendly and enemy aliens.",
                               True, WHITE)
            text2 = font.render ("Press the Space bar to begin", True, WHITE)
            center_text(text)
            next_line(text2, 60)

        elif self.game_over:  
            font = pygame.font.Font(None, 25)
            text = font.render("Game Over, you successfully completed "+ str(self.level.currentLevel) +
                               " levels", True, GREEN)
            center_text(text)
            text2 = font.render("You scored %d out of %d possible points"%(self.score, numberAliens * 20),
                                True, GREEN)
            center_x = (SCREEN_WIDTH // 2) - (text2.get_width() // 2)
            center_y = (SCREEN_HEIGHT // 2) + (text2.get_height() // 2) + 2
            screen.blit(text2, [center_x, center_y])
            
         
        else:
            #draw sprites, print score
            self.all_sprites_list.draw(screen)
            screen.blit(self.player.rotated,self.player.rect)
            font = pygame.font.Font(None, 15)
            score = font.render('Score: %s'%"{:,.0f}".format(self.score), True, RED)
            ammo = font.render('Ammo: %d'%self.ammo, True, YELLOW)
            x_pos = SCREEN_WIDTH//4
            """screen.blit(lives, [x_pos, lives.get_height()])"""
            screen.blit(score, [x_pos, (score.get_height()+ammo.get_height())])
            screen.blit(ammo, [x_pos, (ammo.get_height())])
            if self.isExplosion_center:
                """animate the explosion"""
                pos = (SCREEN_WIDTH//2-20,SCREEN_HEIGHT//2-20)
                self.explosionDur+=1
                if 1<self.explosionDur<=3:
                    screen.blit(self.exp1,pos)
                elif 3 < self.explosionDur <= 5:
                    screen.blit(self.exp2,pos)
                elif 5 < self.explosionDur <=7:
                    screen.blit(self.exp3,pos)
                elif 7 < self.explosionDur <=9:
                    screen.blit(self.exp4,pos)
                elif 9 < self.explosionDur <=11:
                    screen.blit(self.exp5,pos)
                elif 11 < self.explosionDur <=13:
                    screen.blit(self.exp6,pos)
                elif 13 < self.explosionDur <=15:
                    screen.blit(self.exp7,pos)
                elif 15 < self.explosionDur <=17:
                    screen.blit(self.exp8,pos)
                elif 20<self.explosionDur:
                    screen.blit(self.exp9,pos)

                if self.explosionDur>22:
                    self.explosionDur = 0
                    self.isExplosion_center = False

            elif self.isExplosion_enemy:
                pos = self.enemy.rect       
                self.explosionDur+=1
                if 1<self.explosionDur<=3:
                    screen.blit(self.exp1,pos)
                elif 3 < self.explosionDur <= 5:
                    screen.blit(self.exp2,pos)
                elif 5 < self.explosionDur <=7:
                    screen.blit(self.exp3,pos)
                elif 7 < self.explosionDur <=9:
                    screen.blit(self.exp4,pos)
                elif 9 < self.explosionDur <=11:
                    screen.blit(self.exp5,pos)
                elif 11 < self.explosionDur <=13:
                    screen.blit(self.exp6,pos)
                elif 13 < self.explosionDur <=15:
                    screen.blit(self.exp7,pos)
                elif 15 < self.explosionDur <=17:
                    screen.blit(self.exp8,pos)
                elif 20<self.explosionDur:
                    screen.blit(self.exp9,pos)

                if self.explosionDur>22:
                    self.explosionDur = 0
                    self.isExplosion_enemy = False


            elif self.isExplosion_player:
                pos = self.player.rect       
                self.explosionDur+=1
                if 1<self.explosionDur<=3:
                    screen.blit(self.exp1,pos)
                elif 3 < self.explosionDur <= 5:
                    screen.blit(self.exp2,pos)
                elif 5 < self.explosionDur <=7:
                    screen.blit(self.exp3,pos)
                elif 7 < self.explosionDur <=9:
                    screen.blit(self.exp4,pos)
                elif 9 < self.explosionDur <=11:
                    screen.blit(self.exp5,pos)
                elif 11 < self.explosionDur <=13:
                    screen.blit(self.exp6,pos)
                elif 13 < self.explosionDur <=15:
                    screen.blit(self.exp7,pos)
                elif 15 < self.explosionDur <=17:
                    screen.blit(self.exp8,pos)
                elif 20<self.explosionDur:
                    screen.blit(self.exp9,pos)

                if self.explosionDur>22:
                    self.explosionDur = 0
                    self.player.trueX = SCREEN_WIDTH//2
                    self.player.trueY = SCREEN_HEIGHT//2
                    self.player.target = None
                    self.isExplosion_player = False
             
        pygame.display.flip()