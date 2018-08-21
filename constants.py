#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created by lativ on 21/08/18 at 07:41
"""

# BOARD CONSTANTS
FPS = 15
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 720
BOARD_WIDTH = 600
BOARD_HEIGHT = 600
CELL_SIZE = 20
assert BOARD_WIDTH % CELL_SIZE == 0, "Window width must be a multiple of cell size."
assert BOARD_HEIGHT % CELL_SIZE == 0, "Window height must be a multiple of cell size."
CELL_WIDTH = int(BOARD_WIDTH / CELL_SIZE)
CELL_HEIGHT = int(BOARD_HEIGHT / CELL_SIZE)

# COLOR CONSTANTS
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

# MOVEMENT CONSTANTS
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

# TURN FLAGS
TURN_OK = 1
TURN_MOVE_FAIL_OB = 2  # OB stands for Off Board
TURN_MOVE_FAIL_MP = 3  # MP stands for Movement Points
TURN_ATK_FAIL = 4
TURN_ATK_KILLA = 5
