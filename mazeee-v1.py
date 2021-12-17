#!/usr/bin/python3 -B
# -*- coding: utf-8 -*-

# https://en.wikipedia.org/wiki/Maze_generation_algorithm
# Randomized depth-first search
# Iterative implementation


import logging
import math
import random


LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'

MAZE_WIDTH = 40
MAZE_HEIGHT = 20
MAZE_START = 0

WALL_TOP = 0b0001
WALL_RIGHT = 0b0010
WALL_BOTTOM = 0b0100
WALL_LEFT = 0b1000

CELL_INIT = WALL_TOP | WALL_RIGHT | WALL_BOTTOM | WALL_LEFT
CELL_VISITED = 0b0001 << 4


class Maze():

    # --------------------------------------------------------------
    def __init__(self, width, height, start):
        self.width = width
        self.height = height
        self.cells = [CELL_INIT] * width * height
        self.stack = [start]

    # --------------------------------------------------------------
    def generate(self):

        # WIKI While the stack is not empty
        while (len(self.stack)):

            # WIKI Pop a cell from the stack and make it a current cell
            pos = self.stack.pop()
            posy = math.floor(pos / self.width)
            posx = pos - posy * self.width

            logging.debug('stack [%d] pop %d (%dx%d)' %
                          (len(self.stack), pos, posx, posy))

            # WIKI If the current cell has any neighbours which have not been visited
            neighbours = []

            if posx > 0 and not (self.cells[pos - 1] & CELL_VISITED):
                neighbours.append(pos - 1)

            if posx < self.width - 1 and not (self.cells[pos + 1] & CELL_VISITED):
                neighbours.append(pos + 1)

            if posy > 0 and not (self.cells[pos - self.width] & CELL_VISITED):
                neighbours.append(pos - self.width)

            if posy < self.height - 1 and not (self.cells[pos + self.width] & CELL_VISITED):
                neighbours.append(pos + self.width)

            if len(neighbours):

                # WIKI Push the current cell to the stack
                self.stack.append(pos)

                # WIKI Choose one of the unvisited neighbours
                visit = random.choice(neighbours)

                # WIKI Remove the wall between the current cell and the chosen cell
                diff = visit - pos

                if diff == -1:
                    self.cells[pos] &= ~WALL_LEFT
                    self.cells[visit] &= ~WALL_RIGHT
                elif diff == 1:
                    self.cells[pos] &= ~WALL_RIGHT
                    self.cells[visit] &= ~WALL_LEFT
                elif diff == -self.width:
                    self.cells[pos] &= ~WALL_TOP
                    self.cells[visit] &= ~WALL_BOTTOM
                elif diff == self.width:
                    self.cells[pos] &= ~WALL_BOTTOM
                    self.cells[visit] &= ~WALL_TOP
                else:
                    logging.critical(diff)
                    return

                # WIKI Mark the chosen cell as visited and push it to the stack
                self.cells[visit] |= CELL_VISITED
                self.stack.append(visit)

    # --------------------------------------------------------------
    def show(self):
        char = '#'
        pos = 0

        for posy in range(self.height):
            row = [''] * 3

            for posx in range(self.width):
                cell = self.cells[pos + posx]

                row[0] += char
                row[0] += char if (cell & WALL_TOP) else ' '
                row[0] += char

                row[1] += char if (cell & WALL_LEFT) else ' '
                row[1] += ' '
                row[1] += char if (cell & WALL_RIGHT) else ' '

                row[2] += char
                row[2] += char if (cell & WALL_BOTTOM) else ' '
                row[2] += char

            pos += self.width
            [print(str) for str in row]

    # --------------------------------------------------------------
    def show2(self):
        pos = 0

        for posy in range(self.height):
            row = [''] * 2

            for posx in range(self.width):
                cell = self.cells[pos + posx]
                row[0] += '##' if (cell & WALL_TOP) else '# '
                row[1] += '# ' if (cell & WALL_LEFT) else '  '

            pos += self.width
            [print(str + '#') for str in row]

        print('#' * (self.width * 2 + 1))


# ------------------------------------------------------------------
if __name__ == '__main__':
    logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)

    maze = Maze(MAZE_WIDTH, MAZE_HEIGHT, MAZE_START)
    maze.generate()
    maze.show()
    maze.show2()

# EoF
