#!/usr/bin/python3 -B
# -*- coding: utf-8 -*-

# https://en.wikipedia.org/wiki/Maze_generation_algorithm
# Randomized depth-first search
# Iterative implementation


import logging
import math
import random
import numpy
from PIL import Image, ImageDraw


LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'

PIL_BOX = 10
PIL_MARGIN = 20

NOISE_START_X = 0.0
NOISE_END_X = 10.0
NOISE_START_Y = 0.0
NOISE_END_Y = 5.0
NOISE_SEED = 22
NOISE_GRADIENT_MIN = 0.0
NOISE_GRADIENT_MAX = 255.0
NOISE_THRESHOLD = 140.0

MAZE_WIDTH = 160
MAZE_HEIGHT = 80
MAZE_START = 0

WALL_TOP = 0b0001
WALL_RIGHT = 0b0010
WALL_BOTTOM = 0b0100
WALL_LEFT = 0b1000

CELL_INIT = WALL_TOP | WALL_RIGHT | WALL_BOTTOM | WALL_LEFT
CELL_VISITED = 0b0001 << 4
CELL_SOLID = 0b0010 << 4


# https://stackoverflow.com/a/42154921
class Perlin():

    def perlin(self, x, y, seed=0):
        # permutation table
        numpy.random.seed(seed)
        p = numpy.arange(256, dtype=int)
        numpy.random.shuffle(p)
        p = numpy.stack([p, p]).flatten()
        # coordinates of the top-left
        xi = x.astype(int)
        yi = y.astype(int)
        # internal coordinates
        xf = x - xi
        yf = y - yi
        # fade factors
        u = self.fade(xf)
        v = self.fade(yf)
        # noise components
        n00 = self.gradient(p[p[xi]+yi], xf, yf)
        n01 = self.gradient(p[p[xi]+yi+1], xf, yf-1)
        n11 = self.gradient(p[p[xi+1]+yi+1], xf-1, yf-1)
        n10 = self.gradient(p[p[xi+1]+yi], xf-1, yf)
        # combine noises
        x1 = self.lerp(n00, n10, u)
        x2 = self.lerp(n01, n11, u)  # FIX1: I was using n10 instead of n01
        # FIX2: I also had to reverse x1 and x2 here
        return self.lerp(x1, x2, v)

    def lerp(self, a, b, x):
        "linear interpolation"
        return a + x * (b-a)

    def fade(self, t):
        "6t^5 - 15t^4 + 10t^3"
        return 6 * t**5 - 15 * t**4 + 10 * t**3

    def gradient(self, h, x, y):
        "grad converts h to the right gradient vector and return the dot product with (x,y)"
        vectors = numpy.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
        g = vectors[h % 4]
        return g[:, :, 0] * x + g[:, :, 1] * y


class Maze():

    # --------------------------------------------------------------
    def __init__(self, width, height, start):
        self.width = width
        self.height = height
        self.cells = [CELL_INIT] * width * height
        self.stack = [start]
        self.noise = None

    # --------------------------------------------------------------
    def rocks(self):
        linx = numpy.linspace(NOISE_START_X, NOISE_END_X,
                              self.width, endpoint=False)
        liny = numpy.linspace(NOISE_START_Y, NOISE_END_Y,
                              self.height, endpoint=False)

        (xx, yy) = numpy.meshgrid(linx, liny)
        pp = Perlin()
        grid = pp.perlin(xx, yy, NOISE_SEED)
        self.noise = numpy.interp(grid, [grid.min(), grid.max()], [
                                  NOISE_GRADIENT_MIN, NOISE_GRADIENT_MAX])

        pos = 0
        for posy in range(self.height):
            for posx in range(self.width):
                noise = int(self.noise[posy][posx])
                if (noise > NOISE_THRESHOLD):
                    self.cells[pos] |= CELL_VISITED | CELL_SOLID
                pos += 1

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

                if (cell & CELL_SOLID):

                    noise = int(self.noise[posy][posx])
                    draw.rectangle([
                        (x, y), (x+PIL_BOX, y+PIL_BOX)],
                        fill=(noise, noise, noise))

                else:

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
    maze.rocks()
    maze.generate()
    maze.pil()

# EoF
