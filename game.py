# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license
#
# Adapted by latived

import random, pygame, sys, time

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

    # Setting up player and NPC
    dotPlayer = Player('latived', getRandomLocation(xby=True), 'pl1')  # Last parameter defines dotType
    dotNpc = Player('npc_01', getRandomLocation(ybx=True), 'nl1')
    dotNpc2 = Player('npc_02', getRandomLocation(ybx=True), 'nl1')

    # TODO: define a method to do all this automatically and scale to more NPCs
    turnControl = {'dots' :
                       [{'dot' : dotPlayer, 'canMove' : True, 'direction' : None, 'canAtk' : True, 'atkType' : None},
                       {'dot' : dotNpc, 'canMove' : False, 'direction' : None, 'futureMoves' : [], 'canAtk' : False, 'atkType' : None, 'actionsBy' : 'GA'},  # actionsBy can be "random" too
                       {'dot' : dotNpc2, 'canMove' : False, 'direction' : None, 'futureMoves' : [], 'canAtk' : False, 'atkType' : None, 'actionsBy' : 'GA'},  # actionsBy can be "random" too
                        ],
                   'counter' :
                       {'number' : 1, 'showed' : False},
                   'turn' :
                       {'dot': dotPlayer.name, 'id' : 0, 'totalDots' : 3, 'isOver' : False}
                   }

    dots = [dot['dot'] for dot in turnControl['dots']]
    drawGameWindow(dots=dots)

    counter = turnControl['counter']
    turn = turnControl['turn']

    while True: # main game loop

        # Checks if has showed counter previously
        if not counter['showed']:
            print("Turn {} [{} plays]".format(counter['number'], turn['dot']))
            for dot in turnControl['dots']:
                print("\t* {} points: {} VP, {} AP, {} MP.".format(dot['dot'].name, dot['dot'].vitalityPoints, dot['dot'].actionPoints, dot['dot'].movementPoints))
            counter['showed'] = True

        dotPlaying = None

        # Checks for who is playing (if 0, its player's turn)
        if turn['id']:
            # If we have 3 dots (one player with id 0, two npcs with ids 1 and 2)
            dotPlaying = turnControl['dots'][turn['id']]
            dotPlayer = turnControl['dots'][0]

            if dotPlaying['actionsBy'] == 'GA':
                if len(dotPlaying['futureMoves']) == 0:
                    dotPlaying['canAtk'], dotPlaying['atkType'] = ga.isAttackPossible(dotPlayer['dot'], dotPlaying['dot'])
                    turn['isOver'] = True

                    # If we want to move after attack, just delete 'and not dotCanAtk' term
                    if dotPlaying['canMove'] and not dotPlaying['canAtk']:
                        # npcGaActions returns a list of directions to move
                        dotPlaying['futureMoves'] = ga.npcGaActions(dotPlayer['dot'], dotPlaying['dot'])
                        dotPlaying['direction'] = dotPlaying['futureMoves'].pop()
                        turn['isOver'] = False
                else:
                    dotPlaying['direction'] = dotPlaying['futureMoves'].pop()
            else:
                dotPlaying['direction'], dotPlaying['atkType'], turn['isOver'] = npcRandomActions(dotPlaying['dot'].atkTypes)

        else:
            dotPlaying = turnControl['dots'][0]
            ret, dotPlaying['direction'], dotPlaying['atkType'], turn['isOver'] = getPlayerAction()

            if ret:
                return #

        # Get turn results
        turnResult, dotsKilled = doDotTurn(turnControl)  # turnControl has inside both dotPlayer and dotPlaying

        if turnResult == config.TURN_MOVE_FAIL_OB:
            continue
        elif turnResult == config.TURN_MOVE_FAIL_MP:
            # force player/npc to atk or pass turn
            dotPlaying['canMove'] = False
            continue
        elif turnResult == config.TURN_ATK_FAIL:
            # force player/npc to move or pass turn
            dotPlaying['canAtk'] = False
            continue
        elif turnResult == config.TURN_OK:
            if turn['totalDots'] - dotsKilled == 1:
                return # Game is over...

        # Change turn
        if turn['isOver']:
            # Increment counter
            counter['number'] += 1
            # Define next dot to play
            turn['id'] = (turn['id'] + 1) % turn['totalDots']
            dotPlayingNext = turnControl['dots'][turn['id']]
            turn['dot'] = dotPlayingNext['dot'].name

            print("\t{} passes the turn over to {}.".format(dotPlaying['dot'].name, dotPlayingNext['dot'].name))

            counter['showed'] = False  # Last log message wasn't counter

            dotPlayingNext['canMove'] = True
            dotPlayingNext['canAtk'] = True

            # Regenerate status
            for dot in dots:
                dot.regenerateMP()
                dot.regenerateAP()

        drawGameWindow(dots)


def drawGameWindow(dots, attacking=False, atkInfo=None):

    config.G_DISPLAY_SURF.fill(config.BGCOLOR)

    drawGrid()

    namePosGapY = 0
    lineStartGapY = 0
    lineEndGapY = 0

    nDots = len(dots)

    for dot in dots:
        # Draw the dot (dotType is used to modify the dot draw)
        # TODO: modify NPCs dot colors somehow (new parameter dotBeauty?)
        drawDot(dot.position, dot.dotType)
        drawStatus(player=dot,
                   namePosx=config.BOARD_WIDTH + 10,
                   namePosy=20 + namePosGapY,
                   lineStart=(config.BOARD_WIDTH + 10, 50 + lineStartGapY),
                   lineEnd=(config.BOARD_WIDTH + 150, 50 + lineEndGapY))
        namePosGapY += config.BOARD_HEIGHT//nDots
        lineStartGapY += config.BOARD_HEIGHT//nDots
        lineEndGapY += config.BOARD_HEIGHT//nDots

    drawOptions()

    if attacking:
        dotPlayingPos, dotAtkType, rangeAtk = atkInfo
        drawAttack(dotPlayingPos, dotAtkType, rangeAtk)
        pygame.display.update()
        time.sleep(0.5)
    else:
        pygame.display.update()

    config.G_FPS_CLOCK.tick(config.FPS)


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


def doDotTurn(turnControl):

    dots = [dot for dot in turnControl['dots']]
    dotsKilled = 0

    turn = turnControl['turn']

    if turn['id']:
        whichDotIsPlaying = turn['id'] % turn['totalDots']
        dotPlaying = dots[whichDotIsPlaying]
        dotsWaiting = [dot['dot'] for dot in dots if dot['dot'] != dotPlaying]  # Get all dots except the dotPlaying
    else:
        dotPlaying = dots[0]
        dotsWaiting = [dot['dot'] for dot in dots[1:]]  # Iterate through remaining dots (all npcs)

    if not dotPlaying['canMove']:
        dotPlaying['direction'] = None

    if not dotPlaying['canAtk']:
        dotPlaying['atkType'] = None

    previousPos = dotPlaying['dot'].position.copy()

    if dotPlaying['atkType']:

        rangeAtk = dotPlaying['dot'].atkTypes[dotPlaying['atkType']][0]
        costAtk = dotPlaying['dot'].atkTypes[dotPlaying['atkType']][2]

        hits = []
        for dotWaiting in dotsWaiting:
            hit = dotAttack(dotPlaying['dot'].position, dotWaiting.position, dotPlaying['atkType'], rangeAtk)
            hits.append((hit, dotWaiting))

        if dotPlaying['dot'].actionPoints >= costAtk:
            dotPlaying['dot'].actionPoints -= costAtk
        else:
            print("\t{} couldn't attack: low action points.".format(dotPlaying['dot'].name))
            return config.TURN_ATK_FAIL, dotsKilled

        # actualize window to show attack (need this here because we need to draw attack)
        # TODO: would exist a way to draw attack like we draw a movement? i.e., at the end of runGame
        drawGameWindow(dots=[dot['dot'] for dot in dots], attacking=True, atkInfo=[dotPlaying['dot'].position, dotPlaying['atkType'], rangeAtk])

        for hit, dotHit in hits:
            if hit:
                damage = dotPlaying['dot'].atkTypes[dotPlaying['atkType']][1]

                dotHit.vitalityPoints -= damage

                print("\t{} attacked {}ly {} and infriges {} damage points (now with {} VPs).".
                      format(dotPlaying['dot'].name, dotPlaying['atkType'], dotHit.name, damage, dotHit.vitalityPoints))

                if dotHit.vitalityPoints <= 0:
                    print("\t{} fucking killed {}, man. Well done, well done.".format(dotPlaying['dot'].name, dotHit.name))
                    dotsKilled += 1

            else:
                print("\t{} attacked {}ly {} but missed.".
                      format(dotPlaying['dot'].name, dotPlaying['atkType'], dotHit.name))

        print("\t\t... its action points goes to {}.".format(dotPlaying['dot'].actionPoints))
    # move the dot in the direction it is moving, obviously
    elif dotPlaying['direction']:

        if not dotPlaying['dot'].movementPoints:  # if mp is 0, dot can't move
            print("\t{} couldn't move: low movement points.".format(dotPlaying['dot'].name))
            return config.TURN_MOVE_FAIL_MP, dotsKilled

        moveResult = dotMove(dotPlaying['direction'], dotPlaying['dot'].position)  # only false at first game start (and if not atk, will move)

        if moveResult:
            dotPlaying['dot'].movementPoints -= 1
            print("\t{} moves from ({}, {}) to ({}, {}).".format(dotPlaying['dot'].name,
                                                previousPos['x'], previousPos['y'],
                                                dotPlaying['dot'].position['x'], dotPlaying['dot'].position['y']))
            print("\t\t... its movement points goes to {}.".format(dotPlaying['dot'].movementPoints))
        else:
            print("\t{}: movement to off the board is invalid. Try again.".format(dotPlaying['dot'].name))
            return config.TURN_MOVE_FAIL_OB, dotsKilled
    else:
        print("\t{} stays at ({}, {}).".format(dotPlaying['dot'].name, dotPlaying['dot'].position['x'], dotPlaying['dot'].position['y']))

    return config.TURN_OK, dotsKilled


def getPlayerAction(dotDirection=None, dotAtkType=None, dotTurnOver=False):
    # If game started and is player turn, wait event (move or attack or pass over the turn)
    while not dotDirection and not dotAtkType and not dotTurnOver:
        for event in pygame.event.get(): # event handling loop
            if event.type == pl.MOUSEBUTTONUP:
                if config.G_QUIT_RECT.collidepoint(event.pos):
                    terminate()
                elif config.G_RESET_RECT.collidepoint(event.pos):
                    return True, dotDirection, dotAtkType, dotTurnOver
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

    # Needed?
    return False, dotDirection, dotAtkType, dotTurnOver


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


def drawDot(dotCoords, dotType):
    x = dotCoords['x'] * config.CELL_SIZE
    y = dotCoords['y'] * config.CELL_SIZE
    dotSegmentRect = pygame.Rect(x, y, config.CELL_SIZE, config.CELL_SIZE)

    if dotType == 'player':
        pygame.draw.rect(config.G_DISPLAY_SURF, config.DARKGREEN, dotSegmentRect)
        dotInnerSegmentRect = pygame.Rect(x + 4, y + 4, config.CELL_SIZE - 8, config.CELL_SIZE - 8)
        pygame.draw.rect(config.G_DISPLAY_SURF, config.GREEN, dotInnerSegmentRect)
    else:
        pygame.draw.rect(config.G_DISPLAY_SURF, config.RED, dotSegmentRect)


def drawGrid():
    for x in range(0, config.BOARD_WIDTH + 1, config.CELL_SIZE): # draw vertical lines
        pygame.draw.line(config.G_DISPLAY_SURF, config.DARKGRAY, (x, 0), (x, config.BOARD_HEIGHT))
    for y in range(0, config.BOARD_HEIGHT + 1, config.CELL_SIZE): # draw horizontal lines
        pygame.draw.line(config.G_DISPLAY_SURF, config.DARKGRAY, (0, y), (config.BOARD_WIDTH, y))


if __name__ == '__main__':
    main()
