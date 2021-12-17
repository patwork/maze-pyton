#!/usr/bin/python3 -B
# -*- coding: utf-8 -*-

# https://en.wikipedia.org/wiki/Maze_generation_algorithm
# Randomized depth-first search
# Iterative implementation


import logging
import math
import random
from PIL import Image, ImageDraw


LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'

PIL_BOX = 10
PIL_MARGIN = 20

MAZE_WIDTH = 160
MAZE_HEIGHT = 80
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
                    exit()

                # WIKI Mark the chosen cell as visited and push it to the stack
                self.cells[visit] |= CELL_VISITED
                self.stack.append(visit)

    # --------------------------------------------------------------
    def pil(self):

        sizex = self.width * PIL_BOX + PIL_MARGIN * 2
        sizey = self.height * PIL_BOX + PIL_MARGIN * 2
        img = Image.new('RGB', (sizex, sizey))
        draw = ImageDraw.Draw(img)

        draw.rectangle([
            (PIL_MARGIN, PIL_MARGIN),
            (PIL_MARGIN + self.width * PIL_BOX, PIL_MARGIN + self.height * PIL_BOX)],
            fill='darkblue', outline='white')

        pos = 0
        x = PIL_MARGIN
        y = PIL_MARGIN

        for posy in range(self.height):
            for posx in range(self.width):
                cell = self.cells[pos + posx]

                if (cell & WALL_TOP):
                    draw.line([(x, y), (x + PIL_BOX, y)])

                if (cell & WALL_LEFT):
                    draw.line([(x, y), (x, y + PIL_BOX)])

                x += PIL_BOX

            pos += self.width
            x = PIL_MARGIN
            y += PIL_BOX

        img.show()


# ------------------------------------------------------------------
if __name__ == '__main__':
    logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)

    maze = Maze(MAZE_WIDTH, MAZE_HEIGHT, MAZE_START)
    maze.generate()
    maze.pil()

# EoF
