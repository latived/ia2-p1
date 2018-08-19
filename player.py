#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created by lativ on 19/08/18 at 07:02
"""


class Player():

    def __init__(self, name, location, action_points, mov_points, atk_types):
        self.name = name
        self.position = location
        self.action_points = action_points
        self.movement_points = mov_points
        self.atk_types = atk_types
