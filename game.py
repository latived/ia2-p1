# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from pygame.locals import *

from player import Player

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

TILECOLOR = RED
TEXTCOLOR = WHITE

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the dot's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, STATUSFONT
    global RESET_SURF, RESET_RECT, QUIT_SURF, QUIT_RECT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('DOT-ATTACK')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    STATUSFONT = pygame.font.Font('freesansbold.ttf', 14)

    # store options
    RESET_SURF, RESET_RECT = makeText(BASICFONT, 'Reset game', TEXTCOLOR, TILECOLOR, BOARDWIDTH + 50, BOARDHEIGHT + 50)
    QUIT_SURF, QUIT_RECT = makeText(BASICFONT, 'Quit game', TEXTCOLOR, TILECOLOR, BOARDWIDTH + 50, BOARDHEIGHT + 80)

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    # Set a random start point for dot and NPC-dot
    dotPlayer = Player('latived', getRandomLocation(), 100, 50, None)
    npcPlayer = Player('npc_01', getRandomLocation(), 100, 50, None)

    gameStarted = False  # inhibit necessity for one move before the game starts

    dotTurn = True # control if dot or npc can move

    while True: # main game loop
        direction = None  # inhibit continuous movement

        while gameStarted and not direction:
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

        if gameStarted:
            # TODO: put this print below in a log section at game window
            # TODO: move again if the chosen move wasn't valid (ie, would pass the board edges)
            if dotTurn:
                # move the dot in the direction it is moving, obviously
                if move(direction, dotPlayer.position):  # only false at first game start
                    dotPlayer.movement_points -= 1
                print("{}: ({}, {})".format(dotPlayer.name, dotPlayer.position['x'], dotPlayer.position['y']))
            else:
                move(getRandomDirection(), npcPlayer.position)
                npcPlayer.movement_points -= 1
                print("{}: ({}, {})".format(npcPlayer.name, npcPlayer.position['x'], npcPlayer.position['y']))

            # change turn
            dotTurn = not dotTurn

        gameStarted = True  # not necessary anymore after the game starts

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawDot(dotPlayer.position)
        drawNPC(npcPlayer.position)
        drawStatus(dotPlayer, npcPlayer)
        drawOptions()
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def getRandomDirection():
    directions = [UP, DOWN, LEFT, RIGHT]
    return random.choice(directions)


def move(direction, dotPosition):

    if not direction:
        return False

    if direction == UP:
        dotPosition['y'] -= 1
    elif direction == DOWN:
        dotPosition['y'] += 1
    elif direction == LEFT:
        dotPosition['x'] -= 1
    elif direction == RIGHT:
        dotPosition['x'] += 1

    # if try to move pass edges, stay at the actual cell
    if dotPosition['x'] == -1:
        dotPosition['x'] = 0

    if dotPosition['y'] == -1:
        dotPosition['y'] = 0

    if dotPosition['x'] == CELLWIDTH:
        dotPosition['x'] = CELLWIDTH - 1

    if dotPosition['y'] == CELLHEIGHT:
        dotPosition['y'] = CELLHEIGHT - 1

    return True


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


def makeText(font, text, color, bgcolor, top, left):
    # create the surface and rect objects for some text
    textSurf = font.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)

def drawStatus(dotPlayer, dotNpc):

    playerName = "Player {}"

    # title info text
    playerSurf, playerRect = makeText(BASICFONT, playerName.format(dotPlayer.name), TEXTCOLOR, None, BOARDWIDTH + 50, 20)
    DISPLAYSURF.blit(playerSurf, playerRect)

    # add separator
    pygame.draw.line(DISPLAYSURF, DARKGRAY, (BOARDWIDTH + 50, 50), (BOARDWIDTH + 150, 50))

    # add attributes (ap, mp, atks, ...)
    mpSurf, mpRect = makeText(STATUSFONT,
                              'Movement points: {}'.format(dotPlayer.movement_points),
                              TEXTCOLOR,
                              None,
                              BOARDWIDTH  + 60,
                              75)
    DISPLAYSURF.blit(mpSurf, mpRect)

    # npc info text
    npcSurf, npcRect = makeText(BASICFONT, playerName.format(dotNpc.name), TEXTCOLOR, None, BOARDWIDTH + 50, BOARDHEIGHT//2)
    DISPLAYSURF.blit(npcSurf, npcRect)

    # add separator
    pygame.draw.line(DISPLAYSURF,
                     DARKGRAY,
                     (BOARDWIDTH + 50, BOARDHEIGHT//2 + 30),
                     (BOARDWIDTH + 150, BOARDHEIGHT//2 + 30))

    # add attributes (ap, mp, atks, ...)
    mpSurf, mpRect = makeText(STATUSFONT,
                              'Movement points: {}'.format(dotNpc.movement_points),
                              TEXTCOLOR,
                              None,
                              BOARDWIDTH  + 60,
                              BOARDHEIGHT//2 + 55)
    DISPLAYSURF.blit(mpSurf, mpRect)


def drawOptions():
    # separators at horizontal and vertical right beside and alongside last board point
    pygame.draw.line(DISPLAYSURF, DARKGRAY, (BOARDWIDTH, BOARDHEIGHT), (WINDOWWIDTH, BOARDHEIGHT))
    pygame.draw.line(DISPLAYSURF, DARKGRAY, (BOARDWIDTH, BOARDHEIGHT), (BOARDWIDTH, WINDOWHEIGHT))

    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(QUIT_SURF, QUIT_RECT)


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