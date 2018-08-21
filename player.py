#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created by lativ on 19/08/18 at 07:02
"""

# Set a random start point for dot and NPC-dot
START_VP = 100  # Vitality points
START_MP = 10   # Move points

class Player():

    def __init__(self, name, location, atkTypes, vitalityPoints=START_VP, movPoints=START_MP):
        self.name = name
        self.position = location
        self.atkTypes = atkTypes
        self.vitalityPoints = vitalityPoints
        self.actionPoints = self.getMaximumAP()
        self.movementPoints = movPoints
        self.futureMoves = []


    def regenerateMP(self):
        self.movementPoints = START_MP
        print("\t{} regenerates to {} movement points.".format(self.name, self.movementPoints))


    def regenerateAP(self):
        if self.actionPoints < self.getMaximumAP():
            print("\t{} regenerates 1 action point: {} now.".format(self.name, self.actionPoints))
            self.actionPoints += 1


    def getMaximumAP(self):
        higherAtksCost = [atk[2] for atk in self.atkTypes.values()]
        higherAtksCost.sort(reverse=True)
        return sum(higherAtksCost[:2]) - 1
