#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created by lativ on 21/08/18 at 07:41
"""
FPS = 15
WINDOWWIDTH = 1080
WINDOWHEIGHT = 720
BOARDWIDTH = 600
BOARDHEIGHT = 600
CELLSIZE = 20
assert BOARDWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert BOARDHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(BOARDWIDTH / CELLSIZE)
CELLHEIGHT = int(BOARDHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
BLUE      = (  0,   0, 255)
DARKBLUE  = (  0,   0, 155)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

TILECOLOR = RED
TEXTCOLOR = WHITE

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the dot's head

# TURN FLAGS
TURN_OK = 1
TURN_MOVE_FAIL_OB = 2  # OB stands for Off Board
TURN_MOVE_FAIL_MP = 3  # MP stands for Movement Points
TURN_ATK_FAIL = 4
TURN_ATK_KILLA = 5
