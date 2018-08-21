#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created by lativ on 21/08/18 at 09:04
"""

def npcGaActions():
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
    pass
