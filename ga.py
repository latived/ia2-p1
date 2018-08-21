#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created by lativ on 21/08/18 at 09:04
"""
import random
import config

POPULATION_LIMT = 50
EPOCH_LIMIT = 1

def npcGaActions(dotPlayer, dotNpc):
    """
    1. Verify se npc can attack player
    1.1 If can, attack and pass turn.
    1.2 If not, call findNewCoords(playerXY, npcXY, npcPM) --> npcXYNew

        - findNewCoords will GENERATE an initial population.
          : population -> two dimensional vectors with integers in (0, 30) [30 because CELL WIDTH and CELL HEIGHT]
        - findNewCoords will VERIFY monster individuals and eliminate them.
          : monster individual
                -> is a individual who doesn't satisfies abs(x1 - x2) + abs(y1 - y2) <= N
                     ... where (x1, y1) are individual coords and (x2, y2) are npc initial coords,
                     and N is npc movement points (PM)
                -> is a individual who happens to fall in players coords.

    ################################ FITNESS PHASE
        - findNewCoords will now COMPUTE the fitness of each individual who is not a monster.
          : fitness of a individual is how close NPC is to PLAYER (horizontal or vertical)
                -> suffices to verify proximity of player and individual npc coords
                     ... let (x3, y3) be player coords and (x4, y4) coords of the individual being evaluated
                     ... we have the highest rank individuals those who minimize z = (abs(x3 - x4), abs(y3 - y4))
          -> 50% of those individuals with higher ranks PASS TO another test (each one have an attr name fitness1)
          -> this new TEST consists in verify the proximity with the npc_atk_range.
             -> first) we must know which coords verify, because if in previous MINIMIZATION we had x3 < x4 and y3 << y4,
             then the vertical line have more chances of being formed.
                -> this means that horizontal indexes must be <= npc_atk_range.
                -> in other words, "if we are close to make a vertical line, we have to be close in the vertical too"

                if (abs(x3 - x4) < abs(y3 - y4):
                    fitness2 = abs(y3 - y4)
                else:
                    fitness2 = abs(x3 - x4)

                totalFitness = fitness1 + fitness2

    ################################ SELECTION PHASE
        - findNewCoords will rank the individuals according with their fitness, in ascending order (lower to higher).
             -> if in this population THERE IS OPTIMAL INDIVIDUAL, finalize iterations and return the individual.
                : optimal individual is that which is in position to attack: make line and is in npc_atk_range.
                 -> after return, compute how much MPs has been expended to account for and write in log.
                    : MPs = abs(xi - xf) + abs(yi - yf)
                 -> finally we can perform the attack and pass the turn over.

    ################################ CROSSOVER PHASE
        - findNewCoords will do...
             -> if there is not, PERFORM CROSSOVER in the 50% best ranked individuals

                 (x1, y1) cross (x2, y2) results in { (x1, y2), (x2, y1) }

             -> after crossover, add recently generated individuals and remove monster individuals from these.

    ################################ MUTATATION PHASE
        - findNewCoords will do...
             -> for each individual, toss a coin and verify if it will MUTATE.
                 -> if YES, toss another coin to choose one of the genes. Replace gene value with another in (0, 30).
                    add mutated individual to the new population.
             -> remove monster individuals.
             -> if in this population THERE IS OPTIMAL INDIVIDUAL, finalize iterations and return the individual.
                 -> after return, compute how much MPs has been expended to account for and write in log.
                    : MPs = abs(xi - xf) + abs(yi - yf)
                 -> finally we can perform the attack and pass the turn over.
             -> if THERE IS NOT optimal individual, we save these info:
                : most_adapted_ind_in_epoch = (best_individual, best_individual_fitness, ga_epoch)
                : ga_epoch have MAX_EPOCHS = 1000 limit

             -> BACK TO BEGIN, but skip initial population generation phase.


    """
    dotDirection = None  # UP, DOWN, RIGHT, LEFT (see pygame.locals)
    dotAtkType = None    # vertical or horizontal
    dotTurnOver = False  # simple flag indiciate if npc will pass turn

    epoch = 0
    dotDirectionList = []
    population = []

    while epoch <= EPOCH_LIMIT:
        epoch += 1
        # npcNewCoords is dict like Player position attribute

        npcNewCoords = findNewCoords(dotPlayer.position, dotNpc.position, dotNpc.movementPoints, population)

        # Here we need to transform npcNewCoords to a list of actions (moves, attack and/or turn over)
        # I think we will need to use python generator
        # But for now we don't. Just return a list with directions. A list as stack, remember. First moves at the top.
        dotDirectionList = transformCoordsToMoveDirections(dotNpc.position, npcNewCoords)

    return dotDirectionList


def transformCoordsToMoveDirections(dotNpcCoords, dotNpcCoordsNew):

    fromPosx = dotNpcCoords['x']
    fromPosy = dotNpcCoords['y']
    toPosx = dotNpcCoordsNew['x']
    toPosy = dotNpcCoordsNew['y']

    horizontalMoves = toPosx - fromPosx
    verticalMoves = toPosy - fromPosy
    actualMoves = []


    if horizontalMoves > 0:
        actualMoves += [config.RIGHT] * abs(horizontalMoves)
    else:
        actualMoves += [config.LEFT] * abs(horizontalMoves)

    if verticalMoves > 0:
        actualMoves += [config.DOWN] * abs(verticalMoves)
    else:
        actualMoves += [config.UP] * abs(verticalMoves)

    # as stack
    actualMoves.reverse()

    return actualMoves


def generateInitialPopulation():
    population = []
    for _ in range(POPULATION_LIMT):
        x = random.randint(0, config.CELL_WIDTH - 1)
        y = random.randint(0, config.CELL_HEIGHT - 1)
        individual = {'x' : x, 'y': y}
        population.append(individual)

    return population

def findNewCoords(dotPlayerCoords, dotNpcCoords, dotNpcMP, population):

    if len(population) == 0:
        population = generateInitialPopulation()

    population = removeMonstersIfAny(population, dotPlayerCoords, dotNpcCoords, dotNpcMP)

    population = computeIndividualsFitness(population, dotPlayerCoords)

    population = sorted(population, key=lambda tup: tup[0])

    return population[0][1]
    # first individual, its coords


def computeIndividualsFitness(population, dotPlayerCoords):

    px = dotPlayerCoords['x']
    py = dotPlayerCoords['y']

    populationRanked = []

    for individual in population:
        ix = individual['x']
        iy = individual['y']
        fitness = min(abs(px - ix), abs(py - iy))
        populationRanked.append((fitness, individual))

    # 2nd step
    populationRanked = sorted(populationRanked, key=lambda tup: tup[0])
    sizePopRank = len(populationRanked)
    population = populationRanked[:sizePopRank//2].copy()
    populationRanked = []

    for (fitness, individual) in population:
        ix = individual['x']
        iy = individual['y']
        if (abs(px - ix) < abs(py - iy)):
            newFitness = fitness + abs(py - iy)
        else:
            newFitness = fitness + abs(px - ix)
        populationRanked.append((newFitness, individual))

    return populationRanked

def removeMonstersIfAny(population, dotPlayerCoords, dotNpcCoords, dotNpcMP):
    newPopulation = []
    for individual in population:
        ix = individual['x']
        iy = individual['y']
        npcx = dotNpcCoords['x']
        npcy = dotNpcCoords['y']
        px = dotPlayerCoords['x']
        py = dotPlayerCoords['y']
        monster = abs(ix - npcx) + abs(iy - npcy) <= dotNpcMP or (ix == px and iy == py)
        if not monster:
            newPopulation.append(individual)

    return newPopulation

def isAttackPossible(dotPlayer, dotNpc):
    nx = dotNpc.position['x']
    ny = dotNpc.position['y']
    px = dotPlayer.position['x']
    py = dotPlayer.position['y']

    canAtk = False
    atkType = None
    atkRangeHor = dotNpc.atkTypes['horizontal'][0]
    atkRangeVer = dotNpc.atkTypes['vertical'][0]


    if (nx - atkRangeHor <= px <= nx) and (ny == py):
        atkType = 'horizontal'
        canAtk = True
    elif (nx <= px <= nx + atkRangeHor) and (ny == py):
        atkType = 'horizontal'
        canAtk = True
    elif (ny <= py <= ny + atkRangeVer) and (nx == px):
        atkType = 'vertical'
        canAtk = True
    elif (ny - atkRangeVer <= py <= ny) and (nx == px):
        atkType = 'vertical'
        canAtk = True
    else:
        canAtk = False

    # len(enoughAP) = 0 indicates that actionPoints is low
    enoughAP = [ranges[2] for ranges in dotNpc.atkTypes.values() if dotNpc.actionPoints >= ranges[2]]

    if not len(enoughAP):
        canAtk = False

    # npc can atk but have low action points if atkType != None

    return canAtk, atkType

