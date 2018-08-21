# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys, time
from pygame.locals import *

from player import Player

FPS = 15
WINDOWWIDTH = 1080
WINDOWHEIGHT = 720
BOARDWIDTH = 600
BOARDHEIGHT = 600
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
BLUE      = (  0,   0, 255)
DARKBLUE  = (  0,   0, 155)
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

# TURN FLAGS
TURN_OK = 1
TURN_MOVE_FAIL_OB = 2  # OB stands for Off Board
TURN_MOVE_FAIL_MP = 3  # MP stands for Movement Points
TURN_ATK_FAIL = 4

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, STATUSFONT
    global RESET_SURF, RESET_RECT, QUIT_SURF, QUIT_RECT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('DOT-ATTACK')

    fontName = 'dejavusansmonoforpowerline'
    fontPath = pygame.font.match_font(fontName)
    BASICFONT = pygame.font.Font(fontPath, 18)
    STATUSFONT = pygame.font.Font(fontPath, 12)

    # store options
    RESET_SURF, RESET_RECT = makeText(BASICFONT, 'Reset game', TEXTCOLOR, TILECOLOR, BOARDWIDTH + 50, BOARDHEIGHT + 50)
    QUIT_SURF, QUIT_RECT = makeText(BASICFONT, 'Quit game', TEXTCOLOR, TILECOLOR, BOARDWIDTH + 50, BOARDHEIGHT + 80)

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():

    ATK_PLAYER = {'horizontal': (10, 10, 5), 'vertical': (5, 5, 5) }  # atk : (range_space, range_damage, range_cost)
    ATK_NPC = {'horizontal': (5, 5, 5), 'vertical': (10, 10, 5) }  # atk : (range_space, range_damage, range_cost)

    dotPlayer = Player('latived', getRandomLocation(xby=True), ATK_PLAYER)
    dotNpc = Player('npc_01', getRandomLocation(ybx=True), ATK_NPC)

    gameStarted = False  # inhibit necessity for one move before the game starts

    dotTurn = True  # control if dot or npc can move (true if player, false if npc)
    dotCanAtk = True  # just initializing
    dotCanMove = True
    turnCounter = 1
    showedTurnCounter = False

    while True: # main game loop
        # direction = getRandomDirection()
        dotDirection = None  # inhibit continuous movement
        dotAtkType = None
        dotTurnOver = False

        # TEMP CODE JUST FOR TEST PURPOSES
        #for event in pygame.event.get(): # event handling loop
        #    if event.type == MOUSEBUTTONUP:
        #        if QUIT_RECT.collidepoint(event.pos):
        #            terminate()

        # if game started and is player turn, wait event (move or attack or pass over the turn)
        while (gameStarted and dotTurn) and not dotDirection and not dotAtkType and not dotTurnOver:
            for event in pygame.event.get(): # event handling loop
                if event.type == MOUSEBUTTONUP:
                    if QUIT_RECT.collidepoint(event.pos):
                        terminate()
                elif event.type == QUIT:
                    terminate()
                elif event.type == KEYDOWN:
                    # check for pass over turn
                    if (event.key == K_p):
                        dotTurnOver = True
                    # check for attack
                    elif (event.key == K_h):
                        dotAtkType = 'horizontal'
                    elif (event.key == K_v):
                        dotAtkType = 'vertical'
                    # check for movement
                    elif (event.key == K_LEFT or event.key == K_a) and dotDirection != RIGHT:
                        dotDirection = LEFT
                    elif (event.key == K_RIGHT or event.key == K_d) and dotDirection != LEFT:
                        dotDirection = RIGHT
                    elif (event.key == K_UP or event.key == K_w) and dotDirection != DOWN:
                        dotDirection = UP
                    elif (event.key == K_DOWN or event.key == K_s) and dotDirection != UP:
                        dotDirection = DOWN
                    elif event.key == K_ESCAPE:
                        terminate()

        # TODO: put these print below in a log section at game window
        if gameStarted:
            if not showedTurnCounter:
                print("Turn {}".format(turnCounter))
                showedTurnCounter = True

            if not dotTurn:
                dotDirection = getRandomDirection()
                dotAtkType = random.choice(list(dotNpc.atkTypes))  # because only npc enters here (it is its turn)
                dotTurnOver = random.choice([True, False])
                # choose action (1 to move, 2 to atk, 3 to turn over)
                action = random.randint(1, 3)

                if action == 1:
                    dotAtkType = None
                    dotTurnOver = False
                elif action == 2:
                    dotDirection = None
                    dotTurnOver = False
                else:
                    dotDirection = None
                    dotAtkType = None

                # swap turn, reset variable
                dotCanAtk = True
                dotCanMove = True

            if not dotCanMove:
                dotDirection = None

            if not dotCanAtk:  # if cannot atk, doesn't matter if he wants
                dotAtkType = None

            turnResult, turnFlag = doDotTurn(dotPlayer, dotNpc, dotDirection, dotTurn, dotAtkType)

            if not turnFlag:
                if turnResult == TURN_MOVE_FAIL_OB:
                    pass
                elif turnResult == TURN_MOVE_FAIL_MP:
                    # force player/npc to atk or pass turn
                    dotCanMove = False
                elif turnResult == TURN_ATK_FAIL:
                    # force player/npc to move or pass turn
                    dotCanAtk = False

                continue

            # change turn
            if dotTurnOver:
                turnCounter += 1
                showedTurnCounter = False
                dotTurn = not dotTurn

                dotPlayer.regenerateMP()
                dotPlayer.regenerateAP()
                dotNpc.regenerateMP()
                dotNpc.regenerateAP()

        gameStarted = True  # not necessary anymore after the game starts

        drawGameWindow(dotPlayer, dotNpc)
        # time.sleep(1)  # wait 1 second before npc moves at window
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawGameWindow(dotPlayer, dotNpc):
    DISPLAYSURF.fill(BGCOLOR)

    drawGrid()

    drawDotPlayer(dotPlayer.position)
    drawNpcPlayer(dotNpc.position)

    drawStatus(dotPlayer, BOARDWIDTH + 10, 20, (BOARDWIDTH + 10, 50), (BOARDWIDTH + 150, 50))
    drawStatus(dotNpc, BOARDWIDTH + 10, BOARDHEIGHT//2, (BOARDWIDTH + 10, BOARDHEIGHT//2 + 30), (BOARDWIDTH + 150, BOARDHEIGHT//2 + 30))

    drawOptions()


def dotAttack(dotPlayingCoords, dotWaitingCoords, atkType, rangeAtk):
    px = dotPlayingCoords['x']
    py = dotPlayingCoords['y']
    nx = dotWaitingCoords['x']
    ny = dotWaitingCoords['y']

    if atkType == 'horizontal':
        if (px - rangeAtk <= nx <= px) and (py == ny):
            return True
        elif (px <= nx <= px + rangeAtk) and (py == ny):
            return True
    elif atkType == 'vertical':
        if (py <= ny <= py + rangeAtk) and (px == nx):
            return True
        elif (py - rangeAtk <= ny <= py) and (px == nx):
            return True
    else:
        return False


def doDotTurn(player, npc, dotDirection, dotTurn, dotAtkType):

    dotPlaying = npc
    dotWaiting = player

    if dotTurn:
        dotPlaying = player
        dotWaiting = npc

    previousPos = dotPlaying.position.copy()

    if dotAtkType:  # if players wants to atk (npc atk is always set randomly in its, player not) (for now

        rangeAtk = dotPlaying.atkTypes[dotAtkType][0]
        costAtk = dotPlaying.atkTypes[dotAtkType][2]

        hit = dotAttack(dotPlaying.position, dotWaiting.position, dotAtkType, rangeAtk)

        if dotPlaying.actionPoints >= costAtk:
            dotPlaying.actionPoints -= costAtk
        else:
            print("\t{} couldn't attack: low action points.".format(dotPlaying.name))
            return TURN_ATK_FAIL, False

        # actualize window to show attack (need this here because we need to draw attack)
        drawGameWindow(player, npc)
        drawAttack(dotPlaying.position, dotAtkType, rangeAtk)
        pygame.display.update()
        time.sleep(0.5)

        if hit:
            damage = dotPlaying.atkTypes[dotAtkType][1]

            print("\t{} attacked {}ly {} and infriges {} damage points.".
                  format(dotPlaying.name, dotAtkType, dotWaiting.name, damage))

            dotWaiting.vitalityPoints -= damage
        else:
            print("\t{} attacked {}ly {} but missed.".
                  format(dotPlaying.name, dotAtkType, dotWaiting.name))

    # move the dot in the direction it is moving, obviously
    elif dotDirection:

        if not dotPlaying.movementPoints:  # if mp is 0, dot can't move
            print("\t{} couldn't move: low movement points.".format(dotPlaying.name))
            return TURN_MOVE_FAIL_MP, False

        moveResult = dotMove(dotDirection, dotPlaying.position)  # only false at first game start (and if not atk, will move)

        if moveResult:
            dotPlaying.movementPoints -= 1
            print("\t{} moves from ({}, {}) to ({}, {})".format(dotPlaying.name,
                                                previousPos['x'], previousPos['y'],
                                                dotPlaying.position['x'], dotPlaying.position['y']))

        else:
            print("\t{}: movement to off the board is invalid. Try again.".format(dotPlaying.name))
            return TURN_MOVE_FAIL_OB, False
    else:
        print("\t{} stays at ({}, {}).".format(dotPlaying.name, dotPlaying.position['x'], dotPlaying.position['y']))

    return TURN_OK, True


def getRandomDirection():
    directions = [UP, DOWN, LEFT, RIGHT]
    return random.choice(directions)


def dotMove(direction, dotPosition):

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
        return False
    elif dotPosition['y'] == -1:
        dotPosition['y'] = 0
        return False
    elif dotPosition['x'] == CELLWIDTH:
        dotPosition['x'] = CELLWIDTH - 1
        return False
    elif dotPosition['y'] == CELLHEIGHT:
        dotPosition['y'] = CELLHEIGHT - 1
        return False

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


def getRandomLocation(xby=False, ybx=False):

    x = random.randint(0, CELLWIDTH - 1)
    y = random.randint(0, CELLHEIGHT - 1)

    if xby:
        x = random.randint(0, CELLWIDTH - 1)
        y = random.randint(x, CELLHEIGHT - 1)

    if ybx:
        y = random.randint(0, CELLHEIGHT - 1)
        x = random.randint(y, CELLWIDTH - 1)

    return {'x' : x, 'y': y}


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


def drawStatus(player, namePosx, namePosy, lineStart, lineEnd):

    playerName = "Player {}"

    # title info text
    surf, rect = makeText(BASICFONT, playerName.format(player.name), TEXTCOLOR, None, namePosx, namePosy)
    DISPLAYSURF.blit(surf, rect)

    # add separator
    pygame.draw.line(DISPLAYSURF, DARKGRAY, lineStart, lineEnd)

    # add attributes (vp, ap, mp, atks, ...)

    gapFromNamePosx = 10

    # ap
    vpSurf, vpRect = makeText(STATUSFONT,
                              'Vitality points: {}'.format(player.vitalityPoints),
                              TEXTCOLOR,
                              None,
                              namePosx + gapFromNamePosx,
                              namePosy + 55)

    # ap
    apSurf, apRect = makeText(STATUSFONT,
                              'Action points: {}'.format(player.actionPoints),
                              TEXTCOLOR,
                              None,
                              namePosx + gapFromNamePosx,
                              namePosy + 55 + 15)

    # mp
    mpSurf, mpRect = makeText(STATUSFONT,
                              'Movement points: {}'.format(player.movementPoints),
                              TEXTCOLOR,
                              None,
                              namePosx + gapFromNamePosx,
                              namePosy + 55 + 30)


    atkHorSurf, atkHorRect = makeText(STATUSFONT,
                                      'Horizontal attack: takes {} VPs in any dot at the range {}.'.
                                      format(player.atkTypes['horizontal'][0], player.atkTypes['horizontal'][1]),
                                      TEXTCOLOR,
                                      None,
                                      namePosx + gapFromNamePosx,
                                      namePosy + 55 + 45)

    atkVerSurf, atkVerRect = makeText(STATUSFONT,
                                      'Vertical attack: takes {} VPs in any dot at the range {}.'.
                                      format(player.atkTypes['vertical'][0], player.atkTypes['vertical'][1]),
                                      TEXTCOLOR,
                                      None,
                                      namePosx + gapFromNamePosx,
                                      namePosy + 55 + 60)

    DISPLAYSURF.blit(vpSurf, vpRect)
    DISPLAYSURF.blit(apSurf, apRect)
    DISPLAYSURF.blit(mpSurf, mpRect)
    DISPLAYSURF.blit(atkHorSurf, atkHorRect)
    DISPLAYSURF.blit(atkVerSurf, atkVerRect)



def drawOptions():
    # separators at horizontal and vertical right beside and alongside last board point
    pygame.draw.line(DISPLAYSURF, DARKGRAY, (BOARDWIDTH, BOARDHEIGHT), (WINDOWWIDTH, BOARDHEIGHT))
    pygame.draw.line(DISPLAYSURF, DARKGRAY, (BOARDWIDTH, BOARDHEIGHT), (BOARDWIDTH, WINDOWHEIGHT))

    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(QUIT_SURF, QUIT_RECT)


def drawAttack(dotPlayingCoords, atkType, atkRange):

    dotPosx = dotPlayingCoords['x']
    dotPosy = dotPlayingCoords['y']

    atkCoords = []
    if atkType == 'horizontal':
        for i in range(atkRange):
            if dotPosx + i + 1 < CELLWIDTH:
                newCellAtRight = {'x' : dotPosx + i + 1, 'y': dotPosy }
                atkCoords.append(newCellAtRight)
            if dotPosx - i - 1 >= 0:
                newCellAtLeft = {'x' : dotPosx - i - 1, 'y': dotPosy }
                atkCoords.insert(0, newCellAtLeft)
    elif atkType == 'vertical':
        for i in range(atkRange):
            if dotPosy - i - 1 >= 0:
                newCellAbove = {'x': dotPosx, 'y' : dotPosy - i - 1 }
                atkCoords.append(newCellAbove)
            if dotPosy + i + 1 < CELLHEIGHT:
                newCellBelow = {'x': dotPosx, 'y' : dotPosy + i + 1 }
                atkCoords.insert(0, newCellBelow)

    for coord in atkCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        dotSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKBLUE, dotSegmentRect)
        dotInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, BLUE, dotInnerSegmentRect)


def drawDotPlayer(playerCoords):
    x = playerCoords['x'] * CELLSIZE
    y = playerCoords['y'] * CELLSIZE
    dotSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, DARKGREEN, dotSegmentRect)
    dotInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
    pygame.draw.rect(DISPLAYSURF, GREEN, dotInnerSegmentRect)


def drawNpcPlayer(npcCoords):
    x = npcCoords['x'] * CELLSIZE
    y = npcCoords['y'] * CELLSIZE
    npcRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, npcRect)


def drawGrid():
    for x in range(0, BOARDWIDTH + 1, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, BOARDHEIGHT))
    for y in range(0, BOARDHEIGHT + 1, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (BOARDWIDTH, y))


if __name__ == '__main__':
    main()