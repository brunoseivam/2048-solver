#!/usr/bin/python

import time
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

URL = "http://gabrielecirulli.github.io/2048"
NROWS,NCOLS = 4,4

# Class that represents an instance of a game grid
class grid:

    # Create an empty 4 by 4 grid
    def __init__(self, driver = None):
        self.data = [[0]*NCOLS for i in range(NROWS)]

        if driver:
            self.read(driver)

    def __getitem__(self,i):
        return self.data[i]

    def __repr__(self):
        rows = ["".join(["%5d " % elem for elem in row]) for row in self.data]
        return "\n".join(rows)+"\n"

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

    # Return a duplicate
    def dup(self):
        g = grid()
        g.data = [row[:] for row in self.data]
        return g

    # Read values from webpage (using webdriver)
    def read(self, driver):
        d = driver
        tilePos = ".tile-position-%d-%d"
        for r in range(NROWS):
            for c in range(NCOLS):
                tiles = d.find_elements_by_css_selector(tilePos % (c+1,r+1))
                if not tiles:
                    self.data[r][c] = 0
                elif len(tiles) > 1:
                    for t in tiles:
                        if "merged" in t.get_attribute("class"):
                            self.data[r][c] = int(t.text)
                else:
                    self.data[r][c] = int(tiles[0].text)

    # "Move" the grid, returning the grid configuration after 'pressing' LEFT
    def move(self, direction):
        g = self.dup()

        rotDict = {"left":(0,0),"down":(1,3),"right":(2,2),"up":(3,1)}

        g.rotateCW(rotDict[direction][0])

        moved = False
        for r in range(NROWS):

            # Move everything non-zero to the left (except 1st elem)
            for c in range(1,NCOLS):

                # Find first non-zero
                if g[r][c] == 0:
                    continue

                i = c

                while i > 0:
                    if g[r][i-1] == 0:              # Just move left
                        g[r][i-1],g[r][i] = g[r][i],g[r][i-1]
                        i = i - 1
                        moved = True

                    elif g[r][i-1] == g[r][i]:      # Merge and stop
                        g[r][i-1] += g[r][i]
                        g[r][i] = 0
                        moved = True
                        break

                    else:                           # Just stop
                        break

        g.rotateCW(rotDict[direction][1])
        return g,moved

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
        return (count,neigh,maxElem)


drv = Firefox()
drv.get(URL)

dirs = ["left","right","up","down"]
acts = [ActionChains(drv).send_keys(Keys.LEFT),
        ActionChains(drv).send_keys(Keys.RIGHT),
        ActionChains(drv).send_keys(Keys.UP),
        ActionChains(drv).send_keys(Keys.DOWN)]

actDict = dict(zip(dirs,acts))

while True:
    curGrid = grid(drv)

    grades = []
    for d in dirs:
        g,moved = curGrid.move(d)

        if moved:
            grades.append((g.grade(),d))

    print grades

    grades = sorted(grades,key=lambda g: g[0][2],reverse=True)
    grades = sorted(grades,key=lambda g: g[0][1],reverse=True)
    grades = sorted(grades,key=lambda g: g[0][0])

    print grades
    actDict[grades[0][1]].perform()
    #time.sleep(0.1)


