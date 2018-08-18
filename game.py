# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 1080
WINDOWHEIGHT = 720
BOARDWIDTH = 640
BOARDHEIGHT = 480
CELLSIZE = 20
assert BOARDWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert BOARDHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(BOARDWIDTH / CELLSIZE)
CELLHEIGHT = int(BOARDHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

TEXTCOLOR = WHITE

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the dot's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('DOT-ATTACK')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    # Set a random start point for dot and NPC-dot
    dotPlayer = getRandomLocation()
    npc = getRandomLocation()

    while True: # main game loop
        direction = None

        while not direction:
            for event in pygame.event.get(): # event handling loop
                if event.type == QUIT:
                    terminate()
                elif event.type == KEYDOWN:
                    if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                        direction = LEFT
                    elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                        direction = RIGHT
                    elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                        direction = UP
                    elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                        direction = DOWN
                    elif event.key == K_ESCAPE:
                        terminate()

        # move the dot by adding a segment in the direction it is moving
        if direction == UP:
            dotPlayer['y'] -= 1
        elif direction == DOWN:
            dotPlayer['y'] += 1
        elif direction == LEFT:
            dotPlayer['x'] -= 1
        elif direction == RIGHT:
            dotPlayer['x'] += 1

        print(dotPlayer)

        # if try to move pass edges, stay at the cell
        if dotPlayer['x'] == -1:
            dotPlayer['x'] = 0

        if dotPlayer['y'] == -1:
            dotPlayer['y'] = 0

        if dotPlayer['x'] == CELLWIDTH:
            dotPlayer['x'] = CELLWIDTH - 1

        if dotPlayer['y'] == CELLHEIGHT:
            dotPlayer['y'] = CELLHEIGHT - 1

        print(dotPlayer)

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawDot(dotPlayer)
        drawNPC(npc)
        drawStatus(None, None)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (BOARDWIDTH - 200, BOARDHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('DotAtk!!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('DotAtk!!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (BOARDWIDTH / 2, BOARDHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (BOARDWIDTH / 2, BOARDHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (BOARDWIDTH / 2, 10)
    overRect.midtop = (BOARDWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawStatus(info_player, info_npc):

    # title info text
    playerSurf = BASICFONT.render('Player Info', True, TEXTCOLOR)
    playerRect = playerSurf.get_rect()
    playerRect.topleft = (BOARDWIDTH + 50, 20)
    DISPLAYSURF.blit(playerSurf, playerRect)

    # add separator
    pygame.draw.line(DISPLAYSURF,
                     DARKGRAY,
                     (BOARDWIDTH + 50, 50),
                     (BOARDWIDTH + 150, 50))

    # npc info text
    npcSurf = BASICFONT.render('NPC Info', True, TEXTCOLOR)
    npcRect = npcSurf.get_rect()
    npcRect.topleft = (BOARDWIDTH + 50, BOARDHEIGHT//2)
    DISPLAYSURF.blit(npcSurf, npcRect)

    # add separator
    pygame.draw.line(DISPLAYSURF,
                     DARKGRAY,
                     (BOARDWIDTH + 50, BOARDHEIGHT//2 + 30),
                     (BOARDWIDTH + 150, BOARDHEIGHT//2 + 30))


def drawDot(dotCoords):
    x = dotCoords['x'] * CELLSIZE
    y = dotCoords['y'] * CELLSIZE
    dotSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, DARKGREEN, dotSegmentRect)
    dotInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
    pygame.draw.rect(DISPLAYSURF, GREEN, dotInnerSegmentRect)


def drawNPC(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    npcRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, npcRect)


def drawGrid():
    for x in range(0, BOARDWIDTH + 1, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, BOARDHEIGHT))
    for y in range(0, BOARDHEIGHT + 1, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (BOARDWIDTH, y))


if __name__ == '__main__':
    main()