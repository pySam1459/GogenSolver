import pygame
from time import sleep
import os
pygame.init()

showPos = False
width, height = 780, 780
os.environ['SDL_VIDEO_WINDOW_POS'] = "10,40"
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Gogen")

alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y']
around = [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]

layout = [["m", " ", "g", " ", "d"],
          [" ", " ", " ", " ", " "],
          ["w", " ", "l", " ", "y"],
          [" ", " ", " ", " ", " "],
          ["s", " ", "j", " ", "b"]]

words = ["acquire", "axle", "cut", "derv", "fir", "just", "keg", "man", "pile", "pry", "rob", "wham"]


def getsides(word, char):
    chrs = []
    for i, let in enumerate(word):
        if let == char:
            if i != 0:
                chrs.append(word[i-1])
            if i != len(word)-1:
                chrs.append(word[i+1])
    return chrs

def getaround(array, cell):
    return [array[dj+cell.j][di+cell.i] for di, dj in around if 0 <= cell.i + di <= 4 and 0 <= cell.j + dj <= 4]

def text(n, pos, size):
    font = pygame.font.SysFont("comicsansms", size)
    surf = font.render(n, True, [16, 16, 16])
    rect = surf.get_rect()
    rect.center = pos
    screen.blit(surf, rect)


class Cell:
    def __init__(self, s, i, j):
        self.i = i
        self.j = j
        self.pos = alpha[:]
        self.set(s)
        self.mid = [(i+1)*width//6, (j+1)*height//6]
        self.starting = s != " "


    def __str__(self):
        return self.s

    def set(self, s):
        global alpha
        self.s = s
        if s != " ":
            self.f = True
            alpha.remove(s)
            self.pos = []
        else:
            self.f = False

    def render(self):
        col = [255, 255, 255] if not self.starting else [255, 225, 0]
        pygame.draw.circle(screen, col, self.mid, width // 16)
        pygame.draw.circle(screen, [0, 0, 0], self.mid, width//16, 2)
        if self.f:
            text(self.s, [self.mid[0], self.mid[1]-4], width//12)
        elif showPos:
            x = self.mid[0] - width//32
            y = self.mid[1] - width//32
            for p in self.pos:
                text(p, [x, y], width//48)
                x += width//64
                if x >= self.mid[0] + width//32 + width//128:
                    y += height//64
                    x = self.mid[0] - width//32


def render(array):
    screen.fill([255, 255, 255])
    for row in array:
        for c in row:
            arcells = getaround(array, c)
            for arc in arcells:
                pygame.draw.line(screen, [10, 10, 10], c.mid, arc.mid, 2)

    for row in array:
        for c in row:
            c.render()

    pygame.display.update()


arr = [[Cell(s, i, j) for i, s in enumerate(row)] for j, row in enumerate(layout)]

replay = []
while True:
    # render(arr)
    # sleep(0.15)
    con = True
    for row in arr:
        for c in row:
            for j in range(5):
                for i in range(5):
                    if arr[j][i].f:
                        if arr[j][i].s in c.pos:
                            c.pos.remove(arr[j][i].s)
                            con = False

    if not con:
        continue

    for word in words:
        for let in word:

            cell = None
            for row in arr:
                for c in row:
                    if c.s == let:
                        cell = c
                        break
                if cell is not None:
                    break

            if cell is not None:
                sides = getsides(word, let)
                arcells = getaround(arr, cell)
                for row in arr:
                    for c in row:
                        if c not in arcells and not c.f:
                            for p in sides:
                                if p in c.pos:
                                    c.pos.remove(p)

    data = {a: [] for a in alpha}  ### here
    for row in arr:
        for c in row:
            if not c.f:
                for p in c.pos:
                    data[p].append(c)
    for a in alpha:
        if len(data[a]) == 1:
            replay.append({"a": a, "ij": [data[a][0].i, data[a][0].j]})
            data[a][0].set(a)
            con = False

    if not con:
        continue

    for p in alpha:   ##### remove s from pos if not able to connect to sides
        for w in words:
            sides = getsides(w, p)
            for char in sides:
                inGrid = False
                for row in arr:
                    for c in row:
                        if not c.f and char in c.pos:
                            inGrid = True
                if inGrid:
                    for row in arr:
                        for c in row:
                            if not c.f and p in c.pos:
                                here = False
                                arcells = getaround(arr, c)
                                for arc in arcells:
                                    if not arc.f and char in arc.pos:
                                        here = True
                                if not here:
                                    while p in c.pos:
                                        c.pos.remove(p)
                                        con = False

    if not con:
        continue

    for row in arr:
        for c in row:
            if len(c.pos) == 1:
                replay.append({"a": c.pos[0], "ij": [c.i, c.j]})
                c.set(c.pos[0])
                con = False

    if not con:
        continue

    break


alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y']
array = [[Cell(s, i, j) for i, s in enumerate(row)] for j, row in enumerate(layout)]
for p in replay:
    render(array)
    i, j = p["ij"]
    array[j][i].set(p["a"])
    sleep(0.2)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    render(array)
