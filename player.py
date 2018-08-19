#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created by lativ on 19/08/18 at 07:02
"""


class Player():

    def __init__(self, name, location, vitalityPoints, actionPoints, movPoints, atkTypes):
        self.name = name
        self.position = location
        self.vitalityPoints = vitalityPoints
        self.actionPoints = actionPoints
        self.movementPoints = movPoints
        self.atkTypes = atkTypes
