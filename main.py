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


    def move_up(self,paddle):
        """
        Takes in a paddle object and moves it up by the paddle velocity
        Returns None
        """
        velocity = (0,-self.paddle_vel)
        paddle.move_ip(velocity)
    def move_down(self,paddle):
        """
        Takes in a paddle object and moves it down by the paddle velocity
        Returns None
        """
        velocity = (0, self.paddle_vel)
        paddle.move_ip(velocity) 
    def play_game(self,genome,config):
        net = neat.nn.FeedForwardNetwork.create(genome,config)
        active = True
        self.genome = genome
        left_score = 0
        right_score = 0

        pygame.init()
        pygame.display.set_caption("Pong")
        clock = pygame.time.Clock()
        ai_paddle = Rect(self.starting_paddle_pos+(self.paddle_width,self.paddle_height))
        print(self.starting_paddle_pos+(self.paddle_width,self.paddle_height))
        player_paddle = Rect(self.screen_width-60, self.center[1]+self.paddle_height, self.paddle_width, self.paddle_height)
        ballx,bally = self.center
        score = [0,0]
        font = pygame.font.Font('bit5x3.ttf',60)
        while active == True:
            #sets the game fps
            clock.tick(60)

            #renders score to the screen
            text = font.render('{} : {}'.format(score[0],score[1]), True, self.white, self.black)
            textObj = text.get_rect()
            textObj.center = (self.screen_width//2, self.screen_height//8)
            self.screen.blit(text,textObj)
            #Allows you to quit the game and gets input for player paddle
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting")
                    pygame.quit() 
            # checking if keydown event happened or not
            if event.type == pygame.KEYDOWN:     
                # checking if key "A" was pressed
                if event.key == pygame.K_UP:
                    self.move_up(player_paddle)
               
                # checking if key "J" was pressed
                if event.key == pygame.K_DOWN:
                    self.move_down(player_paddle)
                
                if event.key == pygame.K_ESCAPE:
                    print("Quitting")
                    pygame.quit() 

            #Creates the paddle
            pygame.draw.rect(surface=self.screen,color=self.white,rect=ai_paddle)
            pygame.draw.rect(surface=self.screen,color=self.white,rect=player_paddle)

            #Creates the Ball
            pygame.draw.circle(surface=self.screen,color=self.white,center=(ballx,bally),radius=self.ball_radius)

            #Feeds in the current paddle y pos, ball y pos, and x distances between the paddle and ball
            #Returns a decicion based on the current game state
            output = net.activate((ai_paddle.y,bally,abs(ai_paddle.x-ballx)))
            decision=output.index(max(output))

           
            #Depending on the decision, move it up or down accordingly
            #Punish it for moving out of bounds
            if decision == 1:
                self.move_up(ai_paddle)
            else:
                self.move_down(ai_paddle)
            
            #player paddle movement
            
            #gameloop--------------------------------------------------
            pygame.display.flip()
            

            #check right wall collision for ball
            if ballx+(self.ball_radius/2) >= self.screen_width:
                ballx,bally = self.center
                score[0]+=1
            
            #Check left wall collision for ball
            if ballx-(self.ball_radius/2)<=0:
                ballx,bally = self.center
                score[1]+=1
        
            #check ai paddle collision for ball
            if ballx-(self.ball_radius/2)<=ai_paddle.x+self.paddle_width:
                if bally-(self.ball_radius/2)>=ai_paddle.y:
                    if bally+(self.ball_radius/2)<=ai_paddle.y+self.paddle_height:
                        if self.ballxvel<0:
                            self.ballxvel*=-1
            #check player paddle collision for ball
            if ballx-(self.ball_radius)>=player_paddle.x-self.paddle_width/2:
                if bally-(self.ball_radius/2)>=player_paddle.y:
                    if bally+(self.ball_radius/2)<=player_paddle.y+self.paddle_height:
                        if self.ballxvel>0:
                            self.ballxvel*=-1

            #check top and bottom collision for balls
            if bally+(self.ball_radius/2)>=self.screen_height or bally-(self.ball_radius/2)<=0:
                self.ballyvel *= -1

            #update ball position
            ballx+=self.ballxvel
            bally+=self.ballyvel
            # print(player_paddle)
            #reset the screen
            self.screen.fill(self.black)


        
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
            #Creates the paddle
            pygame.draw.rect(surface=self.screen,color=self.white,rect=paddle)

            #wall
            if self.wall == True:
                pygame.draw.rect(surface=self.screen,color=self.white,rect=(self.screen_width-self.paddle_width,0,self.paddle_width,self.screen_height))

            #Creates the Ball
            pygame.draw.circle(surface=self.screen,color=self.white,center=(ballx,bally),radius=self.ball_radius)

            #Feeds in the current paddle y pos, ball y pos, and x distances between the paddle and ball
            #Returns a decicion based on the current game state
            output = net.activate((paddle.y,bally,abs(paddle.x-ballx)))
            decision=output.index(max(output))

            #If the model decides not to move, punish it slightly
            if decision == 0:
                genome.fitness -=.01
            
            #Depending on the decision, move it up or down accordingly
            #Punish it for moving out of bounds
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
            

            #check right wall collision for ball
            if ballx+(self.ball_radius/2) >= self.screen_width-self.paddle_width:
                self.ballxvel *= -1
            
            #Check left wall collision for ball
            if ballx-(self.ball_radius/2)<=0:
                ballx,bally = self.center
                fails += 1
        
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

            #reset the screen
            self.screen.fill(self.black)


            duration = time.time() - start_time
            if fails>0 or hits>= max_hits:
                self.calculate_fitness(hits,duration)
                break
    def calculate_fitness(self,hits,duration):
        """
        Takes in the hits and duration of a genome and updates it's fitness value
        Returns None
        """
        self.genome.fitness+=hits+duration

localdir = os.path.dirname(__file__)
configpath = os.path.join(localdir, "config.txt")
def eval_genomes(genomes, config):
    """
    Takes in a collection of genomes and runs the neat training model on them
    """
    width, height = 900,600
    screen = pygame.display.set_mode((width,height))
    pygame.display.set_caption("Pong")
    for genome_id,genome in genomes:
        genome.fitness = 0
        pong = PongGame(screen,width,height)
        force_quit = pong.train_ai(genome,config)
        if force_quit:
            quit()

def run_neat(config, checkpoint = None):
    """
    Runs the eval_genomes function
    Returns the strongest genome after 20 generations
    """
    #if provided a checkpoint, load it, otherwise use the config settings
    if checkpoint:
       p = neat.Checkpointer.restore_checkpoint(checkpoint)
    else:
        p = neat.Population(config)
    
    #add reporters for stats of the genome
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    winner = p.run(eval_genomes, 1)
    with open("best.pickle","wb") as f:
        pickle.dump(winner,f)


config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, configpath)
#run_neat(config, 'checkpoints/neat-checkpoint-20')
width, height = 900,600
screen = pygame.display.set_mode((width,height))
pong = PongGame(screen,width,height)
with open('best.pickle', "rb") as f:
        genome = pickle.load(f)
print(type(genome))
pong.play_game(genome,config)