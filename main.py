import pygame
from pygame.locals import *

#window setup
pygame.init()
screen_width = 900
screen_height = 600
screen = pygame.display.set_mode((screen_width,screen_height))
clock = pygame.time.Clock()
active = True

#consts
center = (screen_width/2,screen_height/2)
print(center)
player = False
starting_paddle_pos = (30,center[1])
white = (255,255,255)
black = (0,0,0)
paddle_width = 30
paddle_height = 100
wall = True
paddle = Rect(starting_paddle_pos+(paddle_width,paddle_height))
ball_radius = 10
ballx,bally = center
ballxvel = 5
ballyvel = 5
paddle_vel = 5

#functions
def move_up(paddle):
    velocity = (0,-paddle_vel)
    paddle.move_ip(velocity)
def move_down(paddle):
    velocity = (0, paddle_vel)
    paddle.move_ip(velocity)  

while active == True:
    #sets the game fps
    clock.tick(60)
    #Allows you to quit the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            active = False
    #paddle
    pygame.draw.rect(surface=screen,color=white,rect=paddle)

    #wall
    if wall == True:
        pygame.draw.rect(surface=screen,color=white,rect=(screen_width-paddle_width,0,paddle_width,screen_height))
    
    #ball
    pygame.draw.circle(surface=screen,color=white,center=(ballx,bally),radius=ball_radius)

    #gameloop
    pygame.display.flip()
    if paddle.y > 0:
        move_up(paddle)
    #update ball position
    if ballx+(ball_radius/2) == screen_width-paddle_width or ballx+(ball_radius/2)>screen_width-paddle_width or ballx-(ball_radius/2)==0 or ballx-(ball_radius/2)<0:
        ballxvel *= -1
        print("collidex",ballxvel,ballx)
    if bally+(ball_radius/2) == screen_height or bally+(ball_radius/2)>screen_height or bally-(ball_radius/2)==0 or bally-(ball_radius/2)<0:
        ballyvel *= -1
        print("collidey",ballyvel,bally)
    
    ballx+=ballxvel
    bally+=ballyvel 
    screen.fill(black)
