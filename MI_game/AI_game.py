# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 13:39:10 2024

@author: zoltan
"""

import pygame #játékfejlesztéshez
import neat #AI support
import os #fájlműveletek
import random



#alapértelmezett ablakméret
WIN_WIDTH = 550
WIN_HEIGHT = 800
FPS = 60


#pontok, generációk, populációk
score = 0
generation = 0
population = 0
pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 40)


#képek
sBirdPath1 = os.path.join("img","bird1.png")
sBirdPath2 = os.path.join("img","bird2.png")
sBirdPath3 = os.path.join("img","bird3.png")
sBasePath = os.path.join("img","base.png")
sBgPath = os.path.join("img","bg.png")
sPipePath = os.path.join("img","pipe.png")


screen_size = (WIN_WIDTH, WIN_HEIGHT)


#lista a madár képeinek, méretnövelés
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(sBirdPath1)),
             pygame.transform.scale2x(pygame.image.load(sBirdPath2)),
             pygame.transform.scale2x(pygame.image.load(sBirdPath3))]

BASE_IMG = pygame.transform.scale2x(pygame.image.load(sBasePath))
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(sPipePath))
BG_IMG = pygame.transform.scale2x(pygame.image.load(sBgPath))



class Bird:
    IMGS = BIRD_IMGS
    ANIMATION_TIME = 3
    
    def __init__(self, x, y):
        self.x = x #madár X koordinátája
        self.y = y #madár Y koordinátája
        #self.tilt = 0 
        self.tick_count = 0 #movement counter
        self.vel = 0 #gyorsaság
        self.height = self.y 
        self.img_count = 0
        self.img = self.IMGS[0]
    
    
    #ugrás; ezt a függvényt az AI fogja meghívni, amikor úgy dönt, hogy ugrani kell
    def jump(self):
        self.vel = -9
        self.tick_count = 0
        self.height = self.y
        
    
    
    #mozgás; ekkor esik a madár lefelé, majd a 'jump' meghívása miatt ismét ugrik
    def move(self):
        self.tick_count += 1
        
        delta = self.vel * self.tick_count + 1.5 * self.tick_count**2
        
        if delta >= 16:
            delta = 16
        if delta < 0:
            delta -= 2
        
        self.y = self.y + delta
    
    
    #madár megjelenítése
    def draw(self, win):
        self.img_count += 1
        if self.img_count == self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        if self.img_count == (self.ANIMATION_TIME * 2):
            self.img = self.IMGS[1]
        if self.img_count == (self.ANIMATION_TIME * 3):
            self.img = self.IMGS[2]
            self.img_count = 0
            
            
        win.blit(self.img,(self.x, self.y)) #a madár képét adott pozícióra helyezi
        
        
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
        



class Pipe:
    GAP = 200
    VEL = 7
    
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        
        #cső tükrözése
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        
        self.passed = False
        self.set_height()
        
        
    #cső méreteinek változtatása
    def set_height(self):
        self.height = random.randrange(30, 550)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
        
        
    def move(self):
        self.x -= self.VEL
        
        
    #a két cső kirajzolása
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
        
        
    #ütközésvizsgálat
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        #távolságvizsgálat
        top_offset = (self.x - bird.x, self.top - bird.y)
        bottom_offset = (self.x - bird.x, self.bottom - bird.y)
        
        #volt ütközés?
        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        
        #ha igen:
        if t_point or b_point:
            return True
        
        return False
        
    
    
#képernyő alja
class Base:
    VEL = 7;
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        
        
    #ha kifutott a képernyőből:    
    def move(self):
        self.x1 = self.VEL
        self.x2 = self.VEL
        
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
            
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
        
    #kirajzoljuk az alsó elemeket
    def draw(self, win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))
        
        
        
#kirajzolunk mindent az ablakra
def draw_window(win, birds, pipes, base):
    win.blit(BG_IMG, (0,0)) #háttér
    #csövek:
    for pipe in pipes:
        pipe.draw(win)
        
    #pontszámok:
    pipe_passed = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(pipe_passed,(5,5))
    
    
    
    generation_counter = STAT_FONT.render("Generáció: " + str(generation),1,(255,255,255))
    win.blit(generation_counter,(5,45))
    
    
    genom_counter = STAT_FONT.render("Populáció: " +str(population) + "/" + str(len(birds)),1,(255,255,255))
    win.blit(genom_counter,(5,90))
    
    base.draw(win)
    
    
    for bird in birds:
        bird.draw(win)
    pygame.display.update()
   

#mozgatás
def object_mover(win, birds, pipes, base, gen, nets):
    trash = []
    global score
    
    #ugorjunk vagy ne
    pipe_ind = 0
    if len(birds) > 0:
        if len(pipes) > 1 and birds[0].x>pipes[0].x + pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1
    else:
        return False
    
    #madárvizsgálat
    for count, bird in enumerate(birds):
        bird.move() #a madár lejjebb jön
        gen[count].fitness += 0.1
        
        #az AI döntést hoz az adatok alapján
        data_to_evaluate = (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom))
   
        result = nets[count].activate(data_to_evaluate)
        
        
        if result[0] > 0.5:
            bird.jump()
            
    
    
    #bird.move()
    
    for pipe in pipes:
        
        #madár ütközik-e a csővel
#        if pipe.collide(bird):
#            score -= 1
#            pass

        pipe.move()
        
        for count,bird in enumerate(birds):
            if pipe.collide(bird):
                gen[count].fitness -= 1
                birds.remove(bird)
                nets.pop(count)
                gen.pop(count)
                
            if pipe.passed == False and pipe.x < bird.x:
                pipe.passed  = True
                score += 1
                
                for g in gen:
                    g.fitness += 5
                pipes.append(Pipe(WIN_WIDTH+100))

        #cső helyzetének vizsgálata
        if pipe.x + pipe.PIPE_TOP.get_width() < 0:
            trash.append(pipe)
            
#        if pipe.passed == False and pipe.x < bird.x: 
#            pipe.passed = True
#            score += 1
#            pipes.append(Pipe(WIN_WIDTH+100))
        
        
        
    for r in trash:
        pipes.remove(r)
        

    for count, bird in enumerate(birds):
        if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
            gen[count].fitness -= 1
            birds.remove(bird)
            nets.pop(count)
            gen.pop(count)
            
        
            
#    if bird.y + bird.img.get_height() >= 730:
#        score -= 1
#        pass
    base.move()
    
def run_game(genomes,config):
    
    gen = []
    nets = []
    birds = []
    global generation
    global population
    
    generation += 1
    population = len(genomes)
    
    #genomok
    for ID, g in genomes:
        #neurális háló
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)        
        birds.append(Bird(random.randrange(100,230),350))
        g.fitness = 0 #0 tudás
        gen.append(g) #genomokat gyűjtjük
    
    pygame.init()
    pygame.display.set_caption("MI beadandó")
    
    base = Base(730)
    #bird = Bird(230, 350)
    pipes = [Pipe(700)]
    
    win = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()
    
    run = True

    #main ciklus
    while run:
        clock.tick(60) #FPS
                    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
           # if event.type == pygame.KEYDOWN:
            #    if event.key == pygame.K_SPACE:
            #        bird.jump()
            
        if object_mover(win,birds,pipes,base,gen,nets) == False:
            run = False
            break
    
        draw_window(win,birds,pipes,base)
    

    
    
#run függvény:
def run(config_path):
    try:
        config = neat.config.Config(neat.DefaultGenome,
                                    neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet,
                                    neat.DefaultStagnation,
                                    config_path)
    except:
        print("Fájl hiba")
        return
    
    
    population = neat.Population(config)
    
    population.run(run_game,50)
    pygame.quit()
    quit()

if __name__ == "__main__":
    
    local_dir = os.path.dirname((__file__))
    config_path = os.path.join(local_dir, "config-mi_beadando.txt")
    run(config_path)
    
    

