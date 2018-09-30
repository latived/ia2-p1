#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created by lativ on 19/08/18 at 07:02
"""

# Set a random start point for dot and NPC-dot
START_VP = 20  # Vitality points
START_MP = 10   # Move points

class Player():

    def __init__(self, name, location, dotType, vitalityPoints=START_VP, movPoints=START_MP):
        self.name = name
        self.position = location
        self.atkTypes = self._selectAtkTypes(dotType)
        self.vitalityPoints = vitalityPoints
        self.actionPoints = self.getMaximumAP()
        self.movementPoints = movPoints
        self.dotType = self._setDotType(dotType)


    def _setDotType(self, dotType):
        if dotType[0] == 'p':
            return "player"
        else:
            return "npc"

    def regenerateMP(self):
        self.movementPoints = START_MP
        print("\t{} regenerates to {} movement points.".format(self.name, self.movementPoints))


    def regenerateAP(self):
        if self.actionPoints < self.getMaximumAP():
            self.actionPoints += 1
            print("\t{} regenerates 1 action point: {} now.".format(self.name, self.actionPoints))


    def getMaximumAP(self):
        higherAtksCost = [atk[2] for atk in self.atkTypes.values()]
        higherAtksCost.sort(reverse=True)
        return sum(higherAtksCost[:2]) - 1


    def _selectAtkTypes(self, dotType):
        atk = None

        if dotType == 'pl1':
            atk = {'horizontal': (10, 10, 5), 'vertical': (5, 5, 5) }  # atk : (range_space, range_damage, range_cost)
        if dotType == 'nl1':
            atk = {'horizontal': (5, 5, 5), 'vertical': (10, 10, 5) }  # atk : (range_space, range_damage, range_cost)

        return atk
