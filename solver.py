#!/usr/bin/python

from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

URL = "http://gabrielecirulli.github.io/2048"



SIZE = 4
LEFT=0
UP=1
RIGHT=2
DOWN=3
DIRECTIONS=(LEFT,UP,RIGHT,DOWN)
HORZ_DIRS=(LEFT,RIGHT)
VERT_DIRS=(UP,DOWN)

# HELPER: Returns a new row, moved left or right
def moveRow(row, pad):

    res = [x for x in row if x] # Filter out zeroes

    i = 0
    while i < len(res):
        try:
            if res[i] == res[i+1]:
                res[i] += res[i+1] # Merge
                del res[i+1]
        except IndexError:
            pass

        i += 1

    # Pad result
    padding = [0]*(SIZE-len(res))
    if pad == LEFT:
        res = res + padding
    else:
        res = padding + res

    return res

# Class that represents an instance of a game grid
class Grid:

    # Create an empty SIZE by SIZE grid
    def __init__(self, driver = None):
        self.data = [[0]*SIZE for i in range(SIZE)]

        if driver:
            self.read(driver)

    # This allows us to do grid[1][2], for instance
    def __getitem__(self,i):
        return self.data[i]

    # A Grid is equal to another if their items are the same
    def __eq__(self,g):
        for r in range(SIZE):
            for c in range(SIZE):
                if self[r][c] != g[r][c]:
                    return False
        return True

    def __repr__(self):
        rows = ["".join(["%5d " % elem for elem in row]) for row in self.data]
        return "\n"+"\n".join(rows)+"\n"

    # Read values from webpage (using webdriver)
    def read(self, d):
        tiles = d.execute_script("return eval('('+window.localStorage.gameState+')')")

        for column in tiles['grid']['cells']:
            for cell in column:
                if cell:
                    pos = cell['position']
                    self.data[pos['y']][pos['x']] = cell['value']

    # Returns a new Grid moved in the specified direction
    def move(self,direction):
        g = Grid()

        # Horizontal movement is easy
        if direction in HORZ_DIRS:
            for r,row in enumerate(self.data):
                g.data[r] = moveRow(row, direction)

        # Vertical movement is trickier
        else:
            # Treat columns as rows and move them
            colDir = LEFT if direction == UP else RIGHT
            cols = [moveRow([row[c] for row in self.data],colDir) for c in range(SIZE)]

            # Map the columns back into rows
            for r in range(SIZE):
                for c in range(SIZE):
                    g[r][c] = cols[c][r]

        return g

    # Returns a list of tuples (direction, result) for all possible movements
    def allMoves(self):
        moves = []
        for d in DIRECTIONS:
            g = self.move(d)
            if not g == self:
                moves.append((d,g))

        return moves

class Game:
    def __init__(self, h = None):
        self.drv = Firefox()

        # Map a direction to an action
        self.ACTION = dict(zip(g2048.DIRECTIONS,
                  (ActionChains(drv).send_keys(Keys.LEFT),
                   ActionChains(drv).send_keys(Keys.UP),
                   ActionChains(drv).send_keys(Keys.RIGHT),
                   ActionChains(drv).send_keys(Keys.DOWN))))

        self.drv.get(URL)
        self.grid = Grid(self.drv)

    def play(self):
        while True:
            moves = self.grid.allMoves()

            # Check if game ended
            if not moves:
                print "I lost..."
                break

            moves = [(d,g,valDensity(g)) for d,g in moves]

            # Choose the best move
            moves.sort(key=lambda g:g[-1],reverse=True)

            print [(d,v) for d,_,v in moves]

            # Perform the chosen move
            ACTION[moves[0][0]].perform()

            # Read new grid
            self.grid = Grid(self.drv)

        self.drv.close()


def valDensity(grid):

    nTiles = 0
    nZeroes = 0
    totValue = 0
    for row in grid:
        for elem in row:
            if elem:
                nTiles += 1
                totValue += elem
            else:
                nZeroes += 1
    return nZeroes + totValue*1.0 / nTiles




