# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys, time

# from pygame.locals import *
import pygame.locals as pl

import config, ga
from player import Player


def main():

    pygame.init()
    config.G_FPS_CLOCK = pygame.time.Clock()
    config.G_DISPLAY_SURF = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption('DOT-ATTACK')

    fontName = 'dejavusansmonoforpowerline'
    fontPath = pygame.font.match_font(fontName)
    config.G_BASIC_FONT = pygame.font.Font(fontPath, 18)
    config.G_STATUS_FONT = pygame.font.Font(fontPath, 12)

    # store options
    config.G_RESET_SURF, config.G_RESET_RECT = makeText(config.G_BASIC_FONT, 'Reset game', config.TEXTCOLOR, config.TILECOLOR, config.BOARD_WIDTH + 50, config.BOARD_HEIGHT + 50)
    config.G_QUIT_SURF, config.G_QUIT_RECT = makeText(config.G_BASIC_FONT, 'Quit game', config.TEXTCOLOR, config.TILECOLOR, config.BOARD_WIDTH + 50, config.BOARD_HEIGHT + 80)

    drawStartScreen()
    while True:
        runGame()
        drawGameOverScreen()


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

    npcGaControlled = True  # tell if we have random actions or ga controlled actions

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
                if event.type == pl.MOUSEBUTTONUP:
                    if config.G_QUIT_RECT.collidepoint(event.pos):
                        terminate()
                    elif config.G_RESET_RECT.collidepoint(event.pos):
                        return
                elif event.type == pl.QUIT:
                    terminate()
                elif event.type == pl.KEYDOWN:
                    # check for pass over turn
                    if (event.key == pl.K_p):
                        dotTurnOver = True
                    # check for attack
                    elif (event.key == pl.K_h):
                        dotAtkType = 'horizontal'
                    elif (event.key == pl.K_v):
                        dotAtkType = 'vertical'
                    # check for movement
                    elif (event.key == pl.K_LEFT or event.key == pl.K_a):
                        dotDirection = config.LEFT
                    elif (event.key == pl.K_RIGHT or event.key == pl.K_d):
                        dotDirection = config.RIGHT
                    elif (event.key == pl.K_UP or event.key == pl.K_w):
                        dotDirection = config.UP
                    elif (event.key == pl.K_DOWN or event.key == pl.K_s):
                        dotDirection = config.DOWN
                    elif event.key == pl.K_ESCAPE:
                        terminate()

        # TODO: put these print below in a log section at game window
        if gameStarted:
            if not showedTurnCounter:
                print("Turn {}".format(turnCounter))
                print("\t* {} points: {} VP, {} AP, {} MP.".format(dotPlayer.name, dotPlayer.vitalityPoints, dotPlayer.actionPoints, dotPlayer.movementPoints))
                print("\t* {} points: {} VP, {} AP, {} MP.".format(dotNpc.name, dotNpc.vitalityPoints, dotNpc.actionPoints, dotNpc.movementPoints))
                showedTurnCounter = True

            if not dotTurn:
                if npcGaControlled:

                    # set next direction move
                    if len(dotNpc.futureMoves) == 0 and dotCanMove:
                        dotNpc.futureMoves = ga.npcGaActions(dotPlayer, dotNpc)
                        dotDirection = dotNpc.futureMoves.pop()
                        dotCanAtk = False
                        if dotDirection == None:
                            dotCanAtk, dotAtkType = ga.isAttackPossible(dotPlayer, dotNpc)
                            dotTurnOver = True
                    else:
                        # dotCantAtk is True always, here.
                        if len(dotNpc.futureMoves) == 0:
                            dotCanAtk, dotAtkType = ga.isAttackPossible(dotPlayer, dotNpc)
                            dotCanMove = False  # we assume we are in attack position here
                            # if dotCanAtk is false, it means that npc is with low action points
                            # if dotAtkType is None, it means that npc is not in line with player
                            if dotCanAtk == False:
                                dotTurnOver = True
                            elif dotCanAtk:
                                dotTurnOver = True

                        else:
                            dotDirection = dotNpc.futureMoves.pop()
                else:
                    dotDirection, dotAtkType, dotTurnOver = npcRandomActions(dotNpc.atkTypes)


            if not dotCanMove:
                dotDirection = None

            if not dotCanAtk:  # if cannot atk, doesn't matter if he wants
                dotAtkType = None

            turnResult, turnFlag = doDotTurn(dotPlayer, dotNpc, dotDirection, dotTurn, dotAtkType)

            if not turnFlag:
                if turnResult == config.TURN_MOVE_FAIL_OB:
                    pass
                elif turnResult == config.TURN_MOVE_FAIL_MP:
                    # force player/npc to atk or pass turn
                    dotCanMove = False
                elif turnResult == config.TURN_ATK_FAIL:
                    # force player/npc to move or pass turn
                    dotCanAtk = False

                continue
            else:
                if turnResult == config.TURN_ATK_KILLA:  # Game is over, okay?
                    return #

            # change turn
            if dotTurnOver:
                if dotTurn:
                    print("\t{} passes the turn over to {}.".format(dotPlayer.name, dotNpc.name))
                else:
                    print("\t{} passes the turn over to {}.".format(dotNpc.name, dotPlayer.name))

                turnCounter += 1
                showedTurnCounter = False
                dotTurn = not dotTurn

                # Right place to these
                dotCanMove = True
                dotCanAtk = True  # for player

                dotPlayer.regenerateMP()
                dotPlayer.regenerateAP()
                dotNpc.regenerateMP()
                dotNpc.regenerateAP()

        gameStarted = True  # not necessary anymore after the game starts

        drawGameWindow(dotPlayer, dotNpc)
        # time.sleep(1)  # wait 1 second before npc moves at window
        pygame.display.update()
        config.G_FPS_CLOCK.tick(config.FPS)


def drawGameWindow(dotPlayer, dotNpc):
    config.G_DISPLAY_SURF.fill(config.BGCOLOR)

    drawGrid()

    drawDotPlayer(dotPlayer.position)
    drawNpcPlayer(dotNpc.position)

    drawStatus(dotPlayer, config.BOARD_WIDTH + 10, 20,
               (config.BOARD_WIDTH + 10, 50),
               (config.BOARD_WIDTH + 150, 50))
    drawStatus(dotNpc, config.BOARD_WIDTH + 10, config.BOARD_HEIGHT//2,
               (config.BOARD_WIDTH + 10, config.BOARD_HEIGHT//2 + 30),
               (config.BOARD_WIDTH + 150, config.BOARD_HEIGHT//2 + 30))

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
            return config.TURN_ATK_FAIL, False

        # actualize window to show attack (need this here because we need to draw attack)
        drawGameWindow(player, npc)
        drawAttack(dotPlaying.position, dotAtkType, rangeAtk)
        pygame.display.update()
        time.sleep(0.5)

        if hit:
            damage = dotPlaying.atkTypes[dotAtkType][1]

            print("\t{} attacked {}ly {} and infriges {} damage points (now with {} VPs).".
                  format(dotPlaying.name, dotAtkType, dotWaiting.name, damage, dotWaiting.vitalityPoints - damage))

            dotWaiting.vitalityPoints -= damage

            if dotWaiting.vitalityPoints <= 0:
                print("\t{} fucking killed {}, man. Well done, well done.".format(dotPlaying.name, dotWaiting.name))
                return config.TURN_ATK_KILLA, True

        else:
            print("\t{} attacked {}ly {} but missed.".
                  format(dotPlaying.name, dotAtkType, dotWaiting.name))

        print("\t\t... its action points goes to {}.".format(dotPlaying.actionPoints))
    # move the dot in the direction it is moving, obviously
    elif dotDirection:

        if not dotPlaying.movementPoints:  # if mp is 0, dot can't move
            print("\t{} couldn't move: low movement points.".format(dotPlaying.name))
            return config.TURN_MOVE_FAIL_MP, False

        moveResult = dotMove(dotDirection, dotPlaying.position)  # only false at first game start (and if not atk, will move)

        if moveResult:
            dotPlaying.movementPoints -= 1
            print("\t{} moves from ({}, {}) to ({}, {}).".format(dotPlaying.name,
                                                previousPos['x'], previousPos['y'],
                                                dotPlaying.position['x'], dotPlaying.position['y']))
            print("\t\t... its movement points goes to {}.".format(dotPlaying.movementPoints))
        else:
            print("\t{}: movement to off the board is invalid. Try again.".format(dotPlaying.name))
            return config.TURN_MOVE_FAIL_OB, False
    else:
        print("\t{} stays at ({}, {}).".format(dotPlaying.name, dotPlaying.position['x'], dotPlaying.position['y']))

    return config.TURN_OK, True


def getRandomDirection():
    directions = [config.UP, config.DOWN, config.LEFT, config.RIGHT]
    return random.choice(directions)


def dotMove(direction, dotPosition):

    if direction == config.UP:
        dotPosition['y'] -= 1
    elif direction == config.DOWN:
        dotPosition['y'] += 1
    elif direction == config.LEFT:
        dotPosition['x'] -= 1
    elif direction == config.RIGHT:
        dotPosition['x'] += 1

    # if try to move pass edges, stay at the actual cell
    if dotPosition['x'] == -1:
        dotPosition['x'] = 0
        return False
    elif dotPosition['y'] == -1:
        dotPosition['y'] = 0
        return False
    elif dotPosition['x'] == config.CELL_WIDTH:
        dotPosition['x'] = config.CELL_WIDTH - 1
        return False
    elif dotPosition['y'] == config.CELL_HEIGHT:
        dotPosition['y'] = config.CELL_HEIGHT - 1
        return False

    return True


def npcRandomActions(dotNpcAtkTypes):
    dotDirection = getRandomDirection()
    dotAtkType = random.choice(list(dotNpcAtkTypes))  # because only npc enters here (it is its turn)
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

    return dotDirection, dotAtkType, dotTurnOver


def drawPressKeyMsg():
    pressKeySurf = config.G_BASIC_FONT.render('Press a key to play.', True, config.DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (config.BOARD_WIDTH - 200, config.BOARD_HEIGHT - 30)
    config.G_DISPLAY_SURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(pl.QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(pl.KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == pl.K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def drawStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('DotAtk!!', True, config.WHITE, config.DARKGREEN)
    titleSurf2 = titleFont.render('DotAtk!!', True, config.GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        config.G_DISPLAY_SURF.fill(config.BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (config.BOARD_WIDTH / 2, config.BOARD_HEIGHT / 2)
        config.G_DISPLAY_SURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (config.BOARD_WIDTH / 2, config.BOARD_HEIGHT / 2)
        config.G_DISPLAY_SURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        config.G_FPS_CLOCK.tick(config.FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation(xby=False, ybx=False):

    x = random.randint(0, config.CELL_WIDTH - 1)
    y = random.randint(0, config.CELL_HEIGHT - 1)

    if xby:
        x = random.randint(0, config.CELL_WIDTH - 1)
        y = random.randint(x, config.CELL_HEIGHT - 1)

    if ybx:
        y = random.randint(0, config.CELL_HEIGHT - 1)
        x = random.randint(y, config.CELL_WIDTH - 1)

    return {'x' : x, 'y': y}


def drawGameOverScreen():

    print('GAME OVER, FRIEND.')

    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, config.WHITE)
    overSurf = gameOverFont.render('Over', True, config.WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (config.BOARD_WIDTH / 2, 10)
    overRect.midtop = (config.BOARD_WIDTH / 2, gameRect.height + 10 + 25)

    config.G_DISPLAY_SURF.blit(gameSurf, gameRect)
    config.G_DISPLAY_SURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(5)
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
    surf, rect = makeText(config.G_BASIC_FONT, playerName.format(player.name), config.TEXTCOLOR, None, namePosx, namePosy)
    config.G_DISPLAY_SURF.blit(surf, rect)

    # add separator
    pygame.draw.line(config.G_DISPLAY_SURF, config.DARKGRAY, lineStart, lineEnd)

    # add attributes (vp, ap, mp, atks, ...)

    gapFromNamePosx = 10

    # ap
    vpSurf, vpRect = makeText(config.G_STATUS_FONT,
                              'Vitality points: {}'.format(player.vitalityPoints),
                              config.TEXTCOLOR,
                              None,
                              namePosx + gapFromNamePosx,
                              namePosy + 55)

    # ap
    apSurf, apRect = makeText(config.G_STATUS_FONT,
                              'Action points: {}'.format(player.actionPoints),
                              config.TEXTCOLOR,
                              None,
                              namePosx + gapFromNamePosx,
                              namePosy + 55 + 15)

    # mp
    mpSurf, mpRect = makeText(config.G_STATUS_FONT,
                              'Movement points: {}'.format(player.movementPoints),
                              config.TEXTCOLOR,
                              None,
                              namePosx + gapFromNamePosx,
                              namePosy + 55 + 30)


    atkHorSurf, atkHorRect = makeText(config.G_STATUS_FONT,
                                      'Horizontal attack: takes {} VPs in any dot at the range {}.'.
                                      format(player.atkTypes['horizontal'][0], player.atkTypes['horizontal'][1]),
                                      config.TEXTCOLOR,
                                      None,
                                      namePosx + gapFromNamePosx,
                                      namePosy + 55 + 45)

    atkVerSurf, atkVerRect = makeText(config.G_STATUS_FONT,
                                      'Vertical attack: takes {} VPs in any dot at the range {}.'.
                                      format(player.atkTypes['vertical'][0], player.atkTypes['vertical'][1]),
                                      config.TEXTCOLOR,
                                      None,
                                      namePosx + gapFromNamePosx,
                                      namePosy + 55 + 60)

    config.G_DISPLAY_SURF.blit(vpSurf, vpRect)
    config.G_DISPLAY_SURF.blit(apSurf, apRect)
    config.G_DISPLAY_SURF.blit(mpSurf, mpRect)
    config.G_DISPLAY_SURF.blit(atkHorSurf, atkHorRect)
    config.G_DISPLAY_SURF.blit(atkVerSurf, atkVerRect)


def drawOptions():
    # separators at horizontal and vertical right beside and alongside last board point
    pygame.draw.line(config.G_DISPLAY_SURF, config.DARKGRAY, (config.BOARD_WIDTH, config.BOARD_HEIGHT), (config.WINDOW_WIDTH, config.BOARD_HEIGHT))
    pygame.draw.line(config.G_DISPLAY_SURF, config.DARKGRAY, (config.BOARD_WIDTH, config.BOARD_HEIGHT), (config.BOARD_WIDTH, config.WINDOW_HEIGHT))

    config.G_DISPLAY_SURF.blit(config.G_RESET_SURF, config.G_RESET_RECT)
    config.G_DISPLAY_SURF.blit(config.G_QUIT_SURF, config.G_QUIT_RECT)


def drawAttack(dotPlayingCoords, atkType, atkRange):

    dotPosx = dotPlayingCoords['x']
    dotPosy = dotPlayingCoords['y']

    atkCoords = []
    if atkType == 'horizontal':
        for i in range(atkRange):
            if dotPosx + i + 1 < config.CELL_WIDTH:
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
            if dotPosy + i + 1 < config.CELL_HEIGHT:
                newCellBelow = {'x': dotPosx, 'y' : dotPosy + i + 1 }
                atkCoords.insert(0, newCellBelow)

    for coord in atkCoords:
        x = coord['x'] * config.CELL_SIZE
        y = coord['y'] * config.CELL_SIZE
        dotSegmentRect = pygame.Rect(x, y, config.CELL_SIZE, config.CELL_SIZE)
        pygame.draw.rect(config.G_DISPLAY_SURF, config.DARKBLUE, dotSegmentRect)
        dotInnerSegmentRect = pygame.Rect(x + 4, y + 4, config.CELL_SIZE - 8, config.CELL_SIZE - 8)
        pygame.draw.rect(config.G_DISPLAY_SURF, config.BLUE, dotInnerSegmentRect)


def drawDotPlayer(playerCoords):
    x = playerCoords['x'] * config.CELL_SIZE
    y = playerCoords['y'] * config.CELL_SIZE
    dotSegmentRect = pygame.Rect(x, y, config.CELL_SIZE, config.CELL_SIZE)
    pygame.draw.rect(config.G_DISPLAY_SURF, config.DARKGREEN, dotSegmentRect)
    dotInnerSegmentRect = pygame.Rect(x + 4, y + 4, config.CELL_SIZE - 8, config.CELL_SIZE - 8)
    pygame.draw.rect(config.G_DISPLAY_SURF, config.GREEN, dotInnerSegmentRect)


def drawNpcPlayer(npcCoords):
    x = npcCoords['x'] * config.CELL_SIZE
    y = npcCoords['y'] * config.CELL_SIZE
    npcRect = pygame.Rect(x, y, config.CELL_SIZE, config.CELL_SIZE)
    pygame.draw.rect(config.G_DISPLAY_SURF, config.RED, npcRect)


def drawGrid():
    for x in range(0, config.BOARD_WIDTH + 1, config.CELL_SIZE): # draw vertical lines
        pygame.draw.line(config.G_DISPLAY_SURF, config.DARKGRAY, (x, 0), (x, config.BOARD_HEIGHT))
    for y in range(0, config.BOARD_HEIGHT + 1, config.CELL_SIZE): # draw horizontal lines
        pygame.draw.line(config.G_DISPLAY_SURF, config.DARKGRAY, (0, y), (config.BOARD_WIDTH, y))


if __name__ == '__main__':
    main()