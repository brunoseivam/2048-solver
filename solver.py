#!/usr/bin/python

import time
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

URL = "http://gabrielecirulli.github.io/2048"
NROWS,NCOLS = 4,4
NTILES = NROWS*NCOLS

# Helper functions

def parse_tiles(elems):
    tiles = []
    for e in elems:
        pos = e.get_attribute("class").split(' ')[2]
        row = int(pos[-1])-1
        col = int(pos[-3])-1
        val = int(e.text) if e.text else 0
        tiles.append((row,col,val))
    return tiles

def getAllTiles(d):
    elems = d.find_elements_by_xpath("//div[contains(@class,'tile-position')]")
    return parse_tiles(elems)

def getNewTile(d):
    elem = d.find_element_by_css_selector(".tile-new")

    while not elem.text:
        continue

    #print "new:",elem.text,elem.get_attribute("class")
    return parse_tiles([elem])

# Class that represents an instance of a game grid
class grid:

    # Create an empty 4 by 4 grid
    def __init__(self, driver = None):
        self.container = None
        self.data = [[0]*NCOLS for i in range(NROWS)]

        if driver:
            self.read(driver)

    def __getitem__(self,i):
        return self.data[i]

    def __eq__(self,g):
        for r in range(NROWS):
            for c in range(NCOLS):
                if self[r][c] != g[r][c]:
                    return False
        return True

    def __repr__(self):
        rows = ["".join(["%5d " % elem for elem in row]) for row in self.data]
        return "\n"+"\n".join(rows)+"\n"

    # Return a duplicate
    def dup(self):
        g = grid()
        g.data = [row[:] for row in self.data]
        g.container = self.container
        return g

    # Rotate the underlying matrix 90 degrees clockwise
    def rotateCW(self,turns=1):
        while turns > 0:
            d = [[0]*NCOLS for i in range(NROWS)]
            for r in range(NROWS):
                for c in range(NCOLS):
                    d[r][c] = self[NCOLS-c-1][r]
            self.data = d
            turns -= 1
        return self

    # Set the specified tiles' values
    def setTiles(self,tilesList):
        for row,col,value in tilesList:
            self.data[row][col] = value

    # Read values from webpage (using webdriver)
    def read(self, driver):
        self.setTiles(getAllTiles(driver))

    # Update values
    def update(self,driver):
        self.setTiles(getNewTile(driver))

    # "Move" the grid, returning the grid configuration after 'pressing' LEFT
    def move(self, direction):
        g = self.dup()

        merges = moveQty = 0

        rotDict = {"left":(0,0),"down":(1,3),"right":(2,2),"up":(3,1)}

        g.rotateCW(rotDict[direction][0])

        for r in range(NROWS):

            merged = [False]*NCOLS
            # Move everything non-zero to the left (except 1st elem)
            for c in range(1,NCOLS):

                # Find first non-zero
                if g[r][c] == 0:
                    continue

                i = c

                while i > 0:

                    # Just move left
                    if g[r][i-1] == 0:
                        moveQty += g[r][i]*2
                        g[r][i-1],g[r][i] = g[r][i],g[r][i-1]
                        i = i - 1

                    # Merge and stop
                    elif g[r][i-1] == g[r][i] and not merged[i-1]:
                        merged[i-1] = True
                        g[r][i-1] += g[r][i]
                        g[r][i] = 0
                        merges += 1
                        break

                    else:                           # Just stop
                        break

        g.rotateCW(rotDict[direction][1])
        return g,merges,moveQty

    def grade(self):
        count = 0
        neigh = 0
        maxElem = 0

        for r in range(NROWS):
            for c in range(NCOLS):
                elem = self[r][c]

                if not elem:
                    continue

                # Count elements in grid
                count += 1

                # Check maximum element
                maxElem = max([elem,maxElem])

                # Check neighbours:
                if c > 0 and elem == self[r][c-1]:          # Left
                    neigh += 1

                if r > 0 and elem == self[r-1][c]:          # Top
                    neigh += 1

                if c < NCOLS-1 and elem == self[r][c+1]:    # Right
                    neigh += 1

                if r < NROWS-1 and elem == self[r+1][c]:    # Bottom
                    neigh += 1

        neigh /= 2

        count = (NTILES-count)*1.0/NTILES
        neigh = neigh*1.0/24
        maxElem = maxElem*1.0/2048

        return 0.5*count+0.3*maxElem+0.2*neigh


drv = Firefox()
drv.get(URL)

dirs = ["left","right","up","down"]
acts = [ActionChains(drv).send_keys(Keys.LEFT),
        ActionChains(drv).send_keys(Keys.RIGHT),
        ActionChains(drv).send_keys(Keys.UP),
        ActionChains(drv).send_keys(Keys.DOWN)]

actDict = dict(zip(dirs,acts))

curGrid = grid(drv)

#print curGrid

while True:
    # Build a list with all possible moves along with the respective grades
    moves = []
    for d in dirs:
        g,merges,moveQty = curGrid.move(d)

        #print merges,moveQty

        if moveQty:
            #moves.append((g.grade(),d,g))
            moves.append((merges,moveQty,d,g))

    # Check game ended
    if not moves:
        print "I lost..."
        break


    # Choose the best move (order by grade)
    moves.sort(key=lambda g:g[0],reverse=True)
    moves.sort(key=lambda g:g[1])

    _,_,action,newGrid = moves[0]

    #for m in moves:
    #    print m[0:2]

    #x = raw_input()

    # Perform the chosen move
    actDict[action].perform()

    # Read new tile
    curGrid = newGrid
    curGrid.update(drv)

    #print curGrid
    #if not (curGrid == grid(drv)):
    #    print "fail"
    #    break

#drv.close()

