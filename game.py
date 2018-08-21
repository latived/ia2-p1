# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys, time
from pygame.locals import *

from player import Player
from constants import *

def main():
    global G_FPS_CLOCK, G_DISPLAY_SURF, G_BASIC_FONT, G_STATUS_FONT
    global G_RESET_SURF, G_RESET_RECT, G_QUIT_SURF, G_QUIT_RECT

    pygame.init()
    G_FPS_CLOCK = pygame.time.Clock()
    G_DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('DOT-ATTACK')

    fontName = 'dejavusansmonoforpowerline'
    fontPath = pygame.font.match_font(fontName)
    G_BASIC_FONT = pygame.font.Font(fontPath, 18)
    G_STATUS_FONT = pygame.font.Font(fontPath, 12)

    # store options
    G_RESET_SURF, G_RESET_RECT = makeText(G_BASIC_FONT, 'Reset game', TEXTCOLOR, TILECOLOR, BOARD_WIDTH + 50, BOARD_HEIGHT + 50)
    G_QUIT_SURF, G_QUIT_RECT = makeText(G_BASIC_FONT, 'Quit game', TEXTCOLOR, TILECOLOR, BOARD_WIDTH + 50, BOARD_HEIGHT + 80)

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
                    if G_QUIT_RECT.collidepoint(event.pos):
                        terminate()
                    elif G_RESET_RECT.collidepoint(event.pos):
                        return
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
                print("\t* {} points: {} VP, {} AP, {} MP.".format(dotPlayer.name, dotPlayer.vitalityPoints, dotPlayer.actionPoints, dotPlayer.movementPoints))
                print("\t* {} points: {} VP, {} AP, {} MP.".format(dotNpc.name, dotNpc.vitalityPoints, dotNpc.actionPoints, dotNpc.movementPoints))
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
            else:
                if turnResult == TURN_ATK_KILLA:  # Game is over, okay?
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

                dotPlayer.regenerateMP()
                dotPlayer.regenerateAP()
                dotNpc.regenerateMP()
                dotNpc.regenerateAP()

        gameStarted = True  # not necessary anymore after the game starts

        drawGameWindow(dotPlayer, dotNpc)
        # time.sleep(1)  # wait 1 second before npc moves at window
        pygame.display.update()
        G_FPS_CLOCK.tick(FPS)


def drawGameWindow(dotPlayer, dotNpc):
    G_DISPLAY_SURF.fill(BGCOLOR)

    drawGrid()

    drawDotPlayer(dotPlayer.position)
    drawNpcPlayer(dotNpc.position)

    drawStatus(dotPlayer, BOARD_WIDTH + 10, 20, (BOARD_WIDTH + 10, 50), (BOARD_WIDTH + 150, 50))
    drawStatus(dotNpc, BOARD_WIDTH + 10, BOARD_HEIGHT//2, (BOARD_WIDTH + 10, BOARD_HEIGHT//2 + 30), (BOARD_WIDTH + 150, BOARD_HEIGHT//2 + 30))

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

            print("\t{} attacked {}ly {} and infriges {} damage points (now with {} VPs).".
                  format(dotPlaying.name, dotAtkType, dotWaiting.name, damage, dotWaiting.vitalityPoints - damage))

            dotWaiting.vitalityPoints -= damage

            if dotWaiting.vitalityPoints <= 0:
                print("\t{} fucking killed {}, man. Well done, well done.".format(dotPlaying.name, dotWaiting.name))
                return TURN_ATK_KILLA, True

        else:
            print("\t{} attacked {}ly {} but missed.".
                  format(dotPlaying.name, dotAtkType, dotWaiting.name))

        print("\t\t... its action points goes to {}.".format(dotPlaying.actionPoints))
    # move the dot in the direction it is moving, obviously
    elif dotDirection:

        if not dotPlaying.movementPoints:  # if mp is 0, dot can't move
            print("\t{} couldn't move: low movement points.".format(dotPlaying.name))
            return TURN_MOVE_FAIL_MP, False

        moveResult = dotMove(dotDirection, dotPlaying.position)  # only false at first game start (and if not atk, will move)

        if moveResult:
            dotPlaying.movementPoints -= 1
            print("\t{} moves from ({}, {}) to ({}, {}).".format(dotPlaying.name,
                                                previousPos['x'], previousPos['y'],
                                                dotPlaying.position['x'], dotPlaying.position['y']))
            print("\t\t... its movement points goes to {}.".format(dotPlaying.movementPoints))
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
    elif dotPosition['x'] == CELL_WIDTH:
        dotPosition['x'] = CELL_WIDTH - 1
        return False
    elif dotPosition['y'] == CELL_HEIGHT:
        dotPosition['y'] = CELL_HEIGHT - 1
        return False

    return True


def drawPressKeyMsg():
    pressKeySurf = G_BASIC_FONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (BOARD_WIDTH - 200, BOARD_HEIGHT - 30)
    G_DISPLAY_SURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def drawStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('DotAtk!!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('DotAtk!!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        G_DISPLAY_SURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (BOARD_WIDTH / 2, BOARD_HEIGHT / 2)
        G_DISPLAY_SURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (BOARD_WIDTH / 2, BOARD_HEIGHT / 2)
        G_DISPLAY_SURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        G_FPS_CLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation(xby=False, ybx=False):

    x = random.randint(0, CELL_WIDTH - 1)
    y = random.randint(0, CELL_HEIGHT - 1)

    if xby:
        x = random.randint(0, CELL_WIDTH - 1)
        y = random.randint(x, CELL_HEIGHT - 1)

    if ybx:
        y = random.randint(0, CELL_HEIGHT - 1)
        x = random.randint(y, CELL_WIDTH - 1)

    return {'x' : x, 'y': y}


def drawGameOverScreen():

    print('GAME OVER, FRIEND.')

    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (BOARD_WIDTH / 2, 10)
    overRect.midtop = (BOARD_WIDTH / 2, gameRect.height + 10 + 25)

    G_DISPLAY_SURF.blit(gameSurf, gameRect)
    G_DISPLAY_SURF.blit(overSurf, overRect)
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
    surf, rect = makeText(G_BASIC_FONT, playerName.format(player.name), TEXTCOLOR, None, namePosx, namePosy)
    G_DISPLAY_SURF.blit(surf, rect)

    # add separator
    pygame.draw.line(G_DISPLAY_SURF, DARKGRAY, lineStart, lineEnd)

    # add attributes (vp, ap, mp, atks, ...)

    gapFromNamePosx = 10

    # ap
    vpSurf, vpRect = makeText(G_STATUS_FONT,
                              'Vitality points: {}'.format(player.vitalityPoints),
                              TEXTCOLOR,
                              None,
                              namePosx + gapFromNamePosx,
                              namePosy + 55)

    # ap
    apSurf, apRect = makeText(G_STATUS_FONT,
                              'Action points: {}'.format(player.actionPoints),
                              TEXTCOLOR,
                              None,
                              namePosx + gapFromNamePosx,
                              namePosy + 55 + 15)

    # mp
    mpSurf, mpRect = makeText(G_STATUS_FONT,
                              'Movement points: {}'.format(player.movementPoints),
                              TEXTCOLOR,
                              None,
                              namePosx + gapFromNamePosx,
                              namePosy + 55 + 30)


    atkHorSurf, atkHorRect = makeText(G_STATUS_FONT,
                                      'Horizontal attack: takes {} VPs in any dot at the range {}.'.
                                      format(player.atkTypes['horizontal'][0], player.atkTypes['horizontal'][1]),
                                      TEXTCOLOR,
                                      None,
                                      namePosx + gapFromNamePosx,
                                      namePosy + 55 + 45)

    atkVerSurf, atkVerRect = makeText(G_STATUS_FONT,
                                      'Vertical attack: takes {} VPs in any dot at the range {}.'.
                                      format(player.atkTypes['vertical'][0], player.atkTypes['vertical'][1]),
                                      TEXTCOLOR,
                                      None,
                                      namePosx + gapFromNamePosx,
                                      namePosy + 55 + 60)

    G_DISPLAY_SURF.blit(vpSurf, vpRect)
    G_DISPLAY_SURF.blit(apSurf, apRect)
    G_DISPLAY_SURF.blit(mpSurf, mpRect)
    G_DISPLAY_SURF.blit(atkHorSurf, atkHorRect)
    G_DISPLAY_SURF.blit(atkVerSurf, atkVerRect)



def drawOptions():
    # separators at horizontal and vertical right beside and alongside last board point
    pygame.draw.line(G_DISPLAY_SURF, DARKGRAY, (BOARD_WIDTH, BOARD_HEIGHT), (WINDOW_WIDTH, BOARD_HEIGHT))
    pygame.draw.line(G_DISPLAY_SURF, DARKGRAY, (BOARD_WIDTH, BOARD_HEIGHT), (BOARD_WIDTH, WINDOW_HEIGHT))

    G_DISPLAY_SURF.blit(G_RESET_SURF, G_RESET_RECT)
    G_DISPLAY_SURF.blit(G_QUIT_SURF, G_QUIT_RECT)


def drawAttack(dotPlayingCoords, atkType, atkRange):

    dotPosx = dotPlayingCoords['x']
    dotPosy = dotPlayingCoords['y']

    atkCoords = []
    if atkType == 'horizontal':
        for i in range(atkRange):
            if dotPosx + i + 1 < CELL_WIDTH:
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
            if dotPosy + i + 1 < CELL_HEIGHT:
                newCellBelow = {'x': dotPosx, 'y' : dotPosy + i + 1 }
                atkCoords.insert(0, newCellBelow)

    for coord in atkCoords:
        x = coord['x'] * CELL_SIZE
        y = coord['y'] * CELL_SIZE
        dotSegmentRect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(G_DISPLAY_SURF, DARKBLUE, dotSegmentRect)
        dotInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELL_SIZE - 8, CELL_SIZE - 8)
        pygame.draw.rect(G_DISPLAY_SURF, BLUE, dotInnerSegmentRect)


def drawDotPlayer(playerCoords):
    x = playerCoords['x'] * CELL_SIZE
    y = playerCoords['y'] * CELL_SIZE
    dotSegmentRect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(G_DISPLAY_SURF, DARKGREEN, dotSegmentRect)
    dotInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELL_SIZE - 8, CELL_SIZE - 8)
    pygame.draw.rect(G_DISPLAY_SURF, GREEN, dotInnerSegmentRect)


def drawNpcPlayer(npcCoords):
    x = npcCoords['x'] * CELL_SIZE
    y = npcCoords['y'] * CELL_SIZE
    npcRect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(G_DISPLAY_SURF, RED, npcRect)


def drawGrid():
    for x in range(0, BOARD_WIDTH + 1, CELL_SIZE): # draw vertical lines
        pygame.draw.line(G_DISPLAY_SURF, DARKGRAY, (x, 0), (x, BOARD_HEIGHT))
    for y in range(0, BOARD_HEIGHT + 1, CELL_SIZE): # draw horizontal lines
        pygame.draw.line(G_DISPLAY_SURF, DARKGRAY, (0, y), (BOARD_WIDTH, y))


if __name__ == '__main__':
    main()