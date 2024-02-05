import pygame
from pygame.locals import *
import neat
import os
import time
import pickle

class PongGame:
    def __init__(self,screen,screen_width,screen_height):
        #consts
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.white = (255,255,255)
        self.black = (0,0,0)
        self.center = (screen_width/2,screen_height/2)
        self.paddle_width = 30
        self.paddle_height = 100
        self.starting_paddle_pos = (30,self.center[1]+100)
        self.wall = True
        self.ball_radius = 10
        self.ballyvel = 5
        self.ballxvel = 5
        self.paddle_vel = 5
        #functions

    def move_up(self,paddle):
        velocity = (0,-self.paddle_vel)
        paddle.move_ip(velocity)
    def move_down(self,paddle):
        velocity = (0, self.paddle_vel)
        paddle.move_ip(velocity) 

    def train_ai(self,genome,config):
        net = neat.nn.FeedForwardNetwork.create(genome,config)
        active = True
        start_time = time.time()
        self.genome = genome
        max_hits = 50
        #window setup
        pygame.init()
        clock = pygame.time.Clock()
        fails = 0
        hits = 0
        paddle = Rect(self.starting_paddle_pos+(self.paddle_width,self.paddle_height))
        ballx,bally = self.center 

        while active == True:
            #sets the game fps
            clock.tick(60)
            #Allows you to quit the game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    active = False
            #paddle
            pygame.draw.rect(surface=self.screen,color=self.white,rect=paddle)

            #wall
            if self.wall == True:
                pygame.draw.rect(surface=self.screen,color=self.white,rect=(self.screen_width-self.paddle_width,0,self.paddle_width,self.screen_height))

            #ball
            pygame.draw.circle(surface=self.screen,color=self.white,center=(ballx,bally),radius=self.ball_radius)
            output = net.activate((paddle.y,bally,abs(paddle.x-ballx)))
            decision=output.index(max(output))
            if decision == 0:
                genome.fitness -=.01
            if decision == 1:
                if paddle.y <= 0:
                    genome.fitness-=1
                self.move_up(paddle)
            else:
                if paddle.y >= self.screen_height:
                    genome.fitness-=1
                self.move_down(paddle)
            
            #gameloop--------------------------------------------------
            pygame.display.flip()
            #if paddle.y > 0:
                #move_up(paddle)

            #check right wall collision for ball
            if ballx+(self.ball_radius/2) == self.screen_width-self.paddle_width or ballx+(self.ball_radius/2)>self.screen_width-self.paddle_width:
                self.ballxvel *= -1
                #print("collidex",ballxvel,ballx)
            if ballx-(self.ball_radius/2)==0 or ballx-(self.ball_radius/2)<0:
                ballx,bally = self.center
                fails += 1
                #print('{} fails'.format(fails))
            #check paddle collision for ball
            if ballx-(self.ball_radius/2)<=paddle.x+self.paddle_width:
                if bally-(self.ball_radius/2)>=paddle.y:
                    if bally+(self.ball_radius/2)<=paddle.y+self.paddle_height:
                        if self.ballxvel<0:
                            self.ballxvel*=-1
                            hits+=1

            #check top and bottom collision for balls
            if bally+(self.ball_radius/2)>=self.screen_height or bally-(self.ball_radius/2)<=0:
                self.ballyvel *= -1

            #update ball position
            ballx+=self.ballxvel
            bally+=self.ballyvel 
            self.screen.fill(self.black)

            duration = time.time() - start_time
            if fails>0 or hits>= max_hits:
                self.calculate_fitness(hits,duration)
                break
    def calculate_fitness(self,hits,duration):
        self.genome.fitness+=hits+duration
localdir = os.path.dirname(__file__)
configpath = os.path.join(localdir, "config.txt")
def eval_genomes(genomes, config):
    width, height = 900,600
    screen = pygame.display.set_mode((width,height))
    pygame.display.set_caption("Pong")
    for genome_id,genome in genomes:
        genome.fitness = 0
        pong = PongGame(screen,width,height)
        force_quit = pong.train_ai(genome,config)
        if force_quit:
            quit()
def run_neat(config):
    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-20')
    #p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))
    winner = p.run(eval_genomes, 20)
    with open("best.pickle","wb") as f:
        pickle.dump(winner,f)


config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, configpath)
run_neat(config)