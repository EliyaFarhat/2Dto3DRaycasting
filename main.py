
import pygame
import math
import sys
from pygame.locals import *
pygame.init()

# constants
SCREEN_H = 480
SCREEN_W = SCREEN_H * 2
MAP_W = 8
TILE_SIZE = int((SCREEN_W/2)/ MAP_W)
FOV = math.pi/3
HALF_FOV = FOV/2
maxDepth = int(MAP_W * TILE_SIZE) # 480
# global var
playerX = (SCREEN_W/2) / 2
playerY = (SCREEN_W/2) / 2
playerAngle = math.pi
castedRays = 120 # 1/4 of width
stepAngle = FOV / castedRays
SPEED = 2.2
SCALE = (SCREEN_W/2) / castedRays
sens = 0.06

# map

MAP = (
    '########'
    '# #    #'
    '#      #'
    '###    #'
    '#    # #'
    '#      #'
    '##   # #'
    '########'
)






win = pygame.display.set_mode((SCREEN_W, SCREEN_H))

# set window title

pygame.display.set_caption('Raycaster 2D to 3D')

# timer

clock = pygame.time.Clock()

# drawMap

def drawMap():
    # loop over map rows
    for row in range(MAP_W):
        for col in range(MAP_W):
            # calc square index
            square = row * MAP_W + col

            # draw map in the window
            pygame.draw.rect(
                win,
                (202,165,165) if MAP[square] == '#' else (100, 100, 100),
                (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE - 2, TILE_SIZE - 2)
            )
    # draw player on 2D board
    pygame.draw.circle(win, (255, 0, 0), (int(playerX), int(playerY)), 8)

    # direction of player
    pygame.draw.line(win, (0,255,0), (playerX, playerY), (playerX - math.sin(playerAngle) * 50,
                                                          playerY + math.cos(playerAngle)* 50), 3)
    # draw FOV
    pygame.draw.line(win, (0, 255, 0), (playerX, playerY), (playerX - math.sin(playerAngle - HALF_FOV) * 50,
                                                            playerY + math.cos(playerAngle - HALF_FOV) * 50), 3)

    pygame.draw.line(win, (0, 255, 0), (playerX, playerY), (playerX - math.sin(playerAngle + HALF_FOV) * 50,
                                                            playerY + math.cos(playerAngle + HALF_FOV) * 50), 3)


# raycast algo
def castRays():
    # left most angle of FOV
    startAngle = playerAngle - HALF_FOV
    # loop over rays
    for ray in range(castedRays):
        # cast ray step by step
        for depth in range(maxDepth):
            # get ray target coords
            targetX = playerX - math.sin(startAngle) * depth
            targetY = playerY + math.cos(startAngle) * depth

            # convert target X, Y coords to map col, row
            col = int(targetX / TILE_SIZE)
            row = int(targetY / TILE_SIZE)
            # calculate map square index
            square = row * MAP_W + col

            # draw casted ray and highlight wall
            if MAP[square] == '#':
                pygame.draw.rect(win, (0,255,0), (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE - 2, TILE_SIZE - 2))
                pygame.draw.line(win, (255, 255, 0), (playerX, playerY), (targetX, targetY))

                # wall shading
                colour1 = 202 / (1 +depth * depth * 0.00003)
                colour2 = 165 / (1 +depth * depth * 0.00003)

                # fix fish eye
                depth *= math.cos(playerAngle - startAngle)

                # calc wall height
                wallHeight = 21000 / (depth + 0.0001)

                # fix stuck on a wall
                if wallHeight > SCREEN_H:
                    wallHeight = SCREEN_H

                # draw 3D projection(rect by rect)
                pygame.draw.rect(win, (colour1,colour2,colour2), (SCREEN_H + ray * SCALE, (SCREEN_H/2)
                                                   - wallHeight/2, SCALE, wallHeight))
                break

        # increment angle by single step
        startAngle += stepAngle


# moving direction, fixes phase thru wall backwards
forward = True

# game loop
while True:
    # escape condition/how to exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

    # convert target X, Y coords to map col, row
    col = int(playerX / TILE_SIZE)
    row = int(playerY / TILE_SIZE)

    # calculate map square index
    square = row * MAP_W + col

    # player hits wall/coll detection
    if MAP[square] == '#':
        if forward:
            # when forward is true and u hit a wall, stop
            playerX -= -math.sin(playerAngle) * SPEED
            playerY -= math.cos(playerAngle) * SPEED
        else:
            # when forward is false and u hit a wall, stop
            playerX += -math.sin(playerAngle) * SPEED
            playerY += math.cos(playerAngle) * SPEED


    # fix green lines update 2D background
    pygame.draw.rect(win, (0, 0, 0), (0, 0, SCREEN_H, SCREEN_H))

    # update 3D background
    pygame.draw.rect(win, (100, 100, 100), (480, SCREEN_H/2, SCREEN_H, SCREEN_H))
    pygame.draw.rect(win, (70, 70, 170), (480, -SCREEN_H / 2, SCREEN_H, SCREEN_H))
    # draw the map
    drawMap()

    # ray casting
    castRays()



    # user controls
    keys = pygame.key.get_pressed()

    # handle user input
    if keys[pygame.K_LEFT]: playerAngle -= sens
    if keys[pygame.K_RIGHT]: playerAngle += sens
    if keys[pygame.K_UP]:
        forward = True
        playerX += -math.sin(playerAngle) * SPEED
        playerY += math.cos(playerAngle) * SPEED
    if keys[pygame.K_DOWN]:
        forward = False
        playerX -= -math.sin(playerAngle) * SPEED
        playerY -= math.cos(playerAngle) * SPEED

    # set FPS
    clock.tick(60)

    # get FPS/display it
    fps = str(int(clock.get_fps()))

    # get font
    font = pygame.font.SysFont('Comic Sans', 25)

    # create font surface
    textsurface = font.render(fps, True, (255,255,0))

    # print fps to screen
    win.blit(textsurface, (SCREEN_H + 1,-5))

    # update display
    pygame.display.flip()
