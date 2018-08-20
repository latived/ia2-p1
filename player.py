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
        # Only considering two atkTypes, and one atk each. Need to update below whenever we add more atks.
        higherAtksCost = [atk[3] for atk in atkTypes.values()]
        higherAtksCost.sort(reverse=True)

        self.name = name
        self.position = location
        self.vitalityPoints = vitalityPoints
        self.actionPoints = sum(higherAtksCost[:2]) - 1  # So player can't use two atks.
        self.movementPoints = movPoints
        self.atkTypes = atkTypes
