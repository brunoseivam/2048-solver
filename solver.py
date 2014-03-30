#!/usr/bin/python

import g2048

from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

URL = "http://gabrielecirulli.github.io/2048"

drv = Firefox()

# Map a direction to an action
ACTION = dict(zip(g2048.DIRECTIONS,
                  (ActionChains(drv).send_keys(Keys.LEFT),
                   ActionChains(drv).send_keys(Keys.UP),
                   ActionChains(drv).send_keys(Keys.RIGHT),
                   ActionChains(drv).send_keys(Keys.DOWN))))

drv.get(URL)
curGrid = g2048.Grid(drv)

def valDensity(grid):
    nTiles = 0
    totValue = 0
    for row in grid:
        for elem in row:
            if elem:
                nTiles += 1
                totValue += elem
    return totValue / nTiles

while True:
    moves = curGrid.allMoves()

    # Check if game ended
    if not moves:
        print "I lost..."
        break

    moves = [(d,g,valDensity(g)) for d,g in moves]

    # Choose the best move
    moves.sort(key=lambda g:g[-1],reverse=True)

    # Perform the chosen move
    ACTION[moves[0][0]].perform()

    # Read new grid
    curGrid = g2048.Grid(drv)

drv.close()

