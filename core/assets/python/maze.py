import sys
import random

class RandomWallSet(object):
    def __init__(self):
        self._walls = set()

    def add(self, wall):
        self._walls.add(wall)

    def _getWall(self):
        # this is SLOW, but the set should never be very big (I think)
        return random.sample(self._walls, 1)[0]

    def take(self):
        wall = self._getWall()
        self._walls.remove(wall)
        return wall

    def empty(self):
        return len(self._walls) == 0

class ZigZagWallSet(RandomWallSet):
    def __init__(self, numRows, numColumns):
        super(ZigZagWallSet, self).__init__()
        self._numRows = numRows
        self._numColumns = numColumns
        self._processedTopRight = False
        self._processedBottomLeft = False

    def _getWall(self):
        if not self._processedTopRight and random.random() < 0.2:
            closestWall = None
            closestDistance = None # manhattan distance
            for wall in self._walls:
                distance = wall[0] + (self._numColumns - wall[1])
                if closestDistance is None or distance < closestDistance:
                    closestWall = wall
                    closestDistance = distance
            if closestWall[0] == 0 and closestWall[1] == self._numColumns - 1:
                self._processedTopRight = True
            return closestWall
        elif not self._processedBottomLeft and random.random() and random.random() < 0.2:
            closestWall = None
            closestDistance = None # manhattan distance
            for wall in self._walls:
                distance = (self._numRows - wall[0]) + wall[1]
                if closestDistance is None or distance < closestDistance:
                    closestWall = wall
                    closestDistance = distance
            if closestWall[0] == self._numRows - 1 and closestWall[1] == 0:
                self._processedBottomLeft = True
            return closestWall
        return random.sample(self._walls, 1)[0]

class DirectionCounterWallSet(RandomWallSet):
    def __init__(self, flipCount):
        super(DirectionCounterWallSet, self).__init__()
        self._flipCount = flipCount
        self._counter = 0
        self._horizontal = True

    def _getWall(self):
        if self._counter % self._flipCount == 0:
            self._counter = 0
            self._horizontal = not self._horizontal
        self._counter += 1
        if self._horizontal:
            walls = [wall for wall in self._walls if wall[2] == "right"]
        else:
            walls = [wall for wall in self._walls if wall[2] == "down"]
        if len(walls) > 0:
            return random.choice(walls)
        return random.sample(self._walls, 1)[0]

def create_walls_for_cell(cell, numRows, numColumns):
    row,column = cell
    walls = []
    if column > 0: # left wall
        walls.append((row,column-1,"right"))
    if column < numColumns - 1: # right wall
        walls.append((row,column,"right"))
    if row > 0: # up wall
        walls.append((row-1,column,"down"))
    if row < numRows - 1: # down wall
        walls.append((row, column, "down"))
    return walls

def create_neighbors_for_cell(cell, numRows, numColumns):
    row,column = cell
    neighbors = []
    if column > 0: # left neighbor
        neighbors.append((cell[0], cell[1]-1))
    if column < numColumns - 1: # right neighbor
        neighbors.append((cell[0], cell[1]+1))
    if row > 0: # top neighbor
        neighbors.append((cell[0]-1, cell[1]))
    if row < numRows - 1: # bottom neighbor
        neighbors.append((cell[0]+1, cell[1]))
    return neighbors

def create_maze(numRows, numColumns):
    #return create_maze_with_prim(numRows, numColumns)
    return create_maze_with_depth(numRows, numColumns)

def create_maze_with_depth(numRows, numColumns):
    startCell = (0,0)

    visited = set()
    openWalls = []

    # depth-first traversal
    def traverse(cell, prevCell = None):
        visited.add(cell)
        if prevCell:
            if cell[0] != prevCell[0]: # vertical neighbor
                topRow = min(cell[0], prevCell[0])
                openWalls.append((topRow, cell[1], "down"))
            else: # horizontal neighbor
                leftColumn = min(cell[1], prevCell[1])
                openWalls.append((cell[0], leftColumn, "right"))

        # get unvisited neighbors
        neighbors = create_neighbors_for_cell(cell, numRows, numColumns)
        random.shuffle(neighbors)

        for neighbor in neighbors:
            if neighbor not in visited:
                traverse(neighbor, cell)

    traverse(startCell)

    return openWalls

def create_maze_with_prim(numRows, numColumns):
    print "creating maze (rows: %i, columns: %i)" % (numRows, numColumns)

    #walls = ZigZagWallSet(height, width)
    #walls = RandomWallSet()
    walls = DirectionCounterWallSet(5)
    path = set()

    startCell = (0,0)
    path.add(startCell)

    walls.add((0,0,"right"))
    walls.add((0,0,"down"))

    openWalls = []

    while not walls.empty():
        wall = walls.take()

        # get two rooms
        if wall[2] == "right":
            room1 = (wall[0], wall[1])
            room2 = (wall[0], wall[1]+1)
        else: # down
            room1 = (wall[0], wall[1])
            room2 = (wall[0]+1, wall[1])

        # only one of the rooms is in the path
        if (room1 in path and room2 not in path) or (room1 not in path and room2 in path):
            openWalls.append(wall)
            if room1 in path:
                path.add(room2)
                for wall in create_walls_for_cell(room2, numRows, numColumns):
                    walls.add(wall)
            else: # room2 already in path
                path.add(room1)
                for wall in create_walls_for_cell(room1, numRows, numColumns):
                    walls.add(wall)

    return openWalls

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: ./maze.py rows columns")
        exit(1)
    print create_maze(int(sys.argv[1]), int(sys.argv[2]))