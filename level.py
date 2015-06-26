class Level(object):
    currentLevel = 1
    level_success = None
    ammo = None
    def __init__(self, version):
        self.live_list = []
        self.kill_list = []
        self.enemies_list = ['A1','A2','A3','A4','A5','A6','B1','B2','B3','B4','B5','B6']
        random.shuffle(self.enemies_list)
        if self.currentLevel==1 or self.currentLevel==2:
            self.ammo = 60
        elif self.currentLevel==3 or self.currentLevel==4:
            self.ammo = 50
        elif self.currentLevel==5:
            self.ammo = 40
        elif self.currentLevel==6:
            self.ammo = 45
            Enemy.y_speed = 1
            Game.stick_sensitvity = 5
        elif self.currentLevel==7 or self.currentLevel==8 or self.currentLevel==9:
            self.ammo = 35
        elif self.currentLevel==9 or self.currentLevel==10 or self.currentLevel==11 or self.currentLevel==12:
            self.ammo = 30
        
    def check_success(self):
        if len(self.kill_list)<=10:
            self.level_success = False #failed the level
        else:
            self.level_success = True
            self.increase_level()
    
    def increase_level(self):
        self.currentLevel+=1
        Enemy.speed += 1
        Bullet.bullet_speed += 1
        Game.stick_sensitivity += 0.1
        
    
    def load_level(self, version):
        self.__init__(version)