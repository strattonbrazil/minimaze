import sys
import random

from itertools import product

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
    return create_maze_with_hunt_and_kill(numRows, numColumns)
    #return create_maze_with_wilson(numRows, numColumns)
    #return create_maze_with_depth_sections(numRows, numColumns)
    #return create_maze_with_depth_and_stuff(numRows, numColumns)

def create_maze_with_braid(numRows, numColumns):
    halfMaze = create_maze_with_depth(numRows / 2, numColumns / 2)
    
    openWalls = []
    
    for row in range(numRows / 2):
        for column in range(numColumns / 2):
            if (row,column,"right") in halfMaze:
                openWalls.append((row*2,column*2+2,"right"))
                openWalls.append((row*2+1,column*2+2,"right"))
                
                openWalls.append((row*2,column*2+1,"right"))
                
                openWalls.append((row*2+1,column*2+1,"right"))
            if (row,column,"down") in halfMaze:
                openWalls.append((row*2+1,column*2,"down"))
                openWalls.append((row*2+1,column*2+1,"down"))
                
                if (row,column-1,"right") not in halfMaze:
                    openWalls.append((row*2,column*2+1,"right"))
    return openWalls

def create_maze_with_depth_and_stuff(numRows, numColumns):
    startCell = (0,0)

    visited = set()
    openWalls = []

    for row in range(numRows):
        for column in range(numColumns):
            if row % 3 == 2 and column % 3 == 1:
                visited.add((row,column))

    # add stuff
    size = 6
    for row in range(3,size):
        for column in range(3,size):
            if not (row == 3 and column == 3) and not (row == size-1 and column == size-1):
                visited.add((row,column))
            
            if row != size-1 and column == size-1 and row % 2 == 0:
                openWalls.append((row,column,"down"))
            elif row != size-1 and column == 0 and row % 2 == 1:
                openWalls.append((row,column,"down"))
            if column != size:
               openWalls.append((row,column,"right"))

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

def create_maze_with_hunt_and_kill(numRows, numColumns):
    startCell = (0,0)
    
    visited = set()
    openWalls = []
    
    counter = { "count" : 0 }
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
        neighbors = filter(lambda cell: cell not in visited, neighbors)
        
        if counter["count"] % 3 != 0:
            random.shuffle(neighbors) # TODO: play with this
        counter["count"] += 1
        
        if len(neighbors) > 0 and neighbors[0] not in visited:
            traverse(neighbors[0], cell)

        #for neighbor in neighbors:
        #   if neighbor not in visited:
        #        traverse(neighbor, cell)
    
    traverse(startCell)
    
    # hunt - find unvisited cell to traverse through
    while True:
        unvisited = None
        for column, row in product(range(numColumns), range(numRows)):
            cell = (row, column)
            if cell not in visited:
                neighbors = create_neighbors_for_cell(cell, numRows, numColumns)
                random.shuffle(neighbors)
                visitedNeighbor = None
                for neighbor in neighbors:
                    if neighbor in visited:
                        visitedNeighbor = neighbor
                        break
                        
                if visitedNeighbor:
                    unvisited = cell
                    break
                
        if unvisited is None:
            break
                
        traverse(unvisited, visitedNeighbor)
    
    return openWalls

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

def create_maze_with_depth_sections(numRows, numColumns):
    sections = []
    def divideSections(rowIndex, numSectionRows, columnIndex, numSectionColumns):
        if numSectionRows + numSectionColumns < 10:
            sections.append({
                "rowIndex" : rowIndex,
                "numRows" : numSectionRows, 
                "columnIndex" : columnIndex, 
                "numColumns" : numSectionColumns
            })
        else:
            def split_horizontal():
                numRowsOnTop = random.randint(2,numSectionRows-2) # TODO: verify range here
                divideSections(rowIndex, numRowsOnTop, columnIndex, numSectionColumns) # new top section
                divideSections(rowIndex + numRowsOnTop, numSectionRows - numRowsOnTop, columnIndex, numSectionColumns) # new bottom section
                
            def split_vertical():
                numColumnsOnLeft = random.randint(2,numSectionColumns-2) # TODO: verify range here
                divideSections(rowIndex, numSectionRows, columnIndex, numColumnsOnLeft)
                divideSections(rowIndex, numSectionRows, columnIndex + numColumnsOnLeft, numSectionColumns - numColumnsOnLeft)
            
            if numSectionColumns < 5:
                split_horizontal()
            elif numSectionRows < 5:
                split_vertical()
            else:
                if random.random() < 0.5:
                    split_vertical()
                else:
                    split_horizontal()
    
    divideSections(0, numRows, 0, numColumns)
    print sections
    
    def move_columns(walls, offset):
        return map(lambda wall: (wall[0], wall[1] + offset, wall[2]), walls)
    def move_rows(walls, offset):
        return map(lambda wall: (wall[0] + offset, wall[1], wall[2]), walls)

    openWalls = []
    for section in sections:
        sectionOpenWalls = move_columns(move_rows(create_maze_with_depth(section["numRows"], section["numColumns"]), section["rowIndex"]), section["columnIndex"])

        openWalls += sectionOpenWalls
        
    # connect the sections by creating a wall between them
    visitedSections = set()
    
    def get_overlap(a1, a2, b1, b2):
        left = max(a1, b1)
        right = min(a2, b2)
        
        if left <= right:
            return (left, right)
        return None
    
    def traverse(section):
        visitedSections.add(str(section))
        
        # get unvisited neighbor sections
        random.shuffle(sections)
        for neighbor in sections:
            if str(neighbor) not in visitedSections:
                # if neighbor adjacent to current section
                if section["columnIndex"] + section["numColumns"] == neighbor["columnIndex"]: # right neighbor
                    overlap = get_overlap(section["rowIndex"], section["rowIndex"] + section["numRows"],
                                          neighbor["rowIndex"], neighbor["rowIndex"] + neighbor["numRows"])
                    if overlap:
                        # TODO: pick the best number here
                        randomRowIndex = random.randint(overlap[0], overlap[1])
                        openWalls.append((randomRowIndex, neighbor["columnIndex"] - 1, "right"))
                        
                        traverse(neighbor)
                        
                elif section["rowIndex"] + section["numRows"] == neighbor["rowIndex"]: # neighbor below
                    overlap = get_overlap(section["columnIndex"], section["columnIndex"] + section["numColumns"],
                                          neighbor["columnIndex"], neighbor["columnIndex"] + neighbor["numColumns"])
                    if overlap:
                        # TODO: pick the best number here
                        randomColumnIndex = random.randint(overlap[0], overlap[1])
                        openWalls.append((neighbor["rowIndex"] - 1, randomColumnIndex, "down"))
                        
                        traverse(neighbor)
                elif section["columnIndex"] - neighbor["numColumns"] == neighbor["columnIndex"]: # left neighbor
                    overlap = get_overlap(section["rowIndex"], section["rowIndex"] + section["numRows"],
                                          neighbor["rowIndex"], neighbor["rowIndex"] + neighbor["numRows"])
                                          
                    if overlap:
                        # TODO: pick the best number here
                        randomRowIndex = random.randint(overlap[0], overlap[1])
                        openWalls.append((randomRowIndex, section["columnIndex"] - 1, "right"))
                        
                        traverse(neighbor)
                        
                elif section["rowIndex"] - neighbor["numRows"] == neighbor["rowIndex"]: # neighbor above
                    overlap = get_overlap(section["rowIndex"], section["columnIndex"] + section["numColumns"],
                                          neighbor["rowIndex"], neighbor["columnIndex"] + neighbor["numColumns"])
                                          
                    if overlap:
                         # TODO: pick the best number here
                        randomColumnIndex = random.randint(overlap[0], overlap[1])
                        openWalls.append((section["rowIndex"] - 1, randomColumnIndex, "down"))
                        
                        traverse(neighbor)
    
    traverse(sections[0])
    
    return openWalls

def get_clockwise_spiral(numRows, numColumns):
    openWalls = []
    visited = set()
    row, column = (0,0)
    
    visited.add((row,column))
    step = 0
    while True:
        cellsBefore = len(visited)
        while (row,column+1) not in visited and column+1 < numColumns: # right
            openWalls.append((row,column,"right"))
            visited.add((row,column+1))
            column += 1
            step += 1
        while (row+1,column) not in visited and row+1 < numRows: # down
            openWalls.append((row,column,"down"))
            visited.add((row+1,column))
            row += 1
            step += 1
        while (row,column-1) not in visited and column - 1 >= 0: # left
            openWalls.append((row,column-1,"right"))
            visited.add((row,column-1))
            column -= 1
            step += 1
        while (row-1,column) not in visited and row - 1 >= 0: # up
            openWalls.append((row-1,column,"down"))
            visited.add((row-1,column))
            row -= 1
            step += 1
            
        if len(visited) == cellsBefore:
            break
    return openWalls

def create_maze_with_special_sections(numRows, numColumns):
    sections = []
    def divideSections(rowIndex, numSectionRows, columnIndex, numSectionColumns):
        if numSectionRows + numSectionColumns < 10:
            sections.append({
                "rowIndex" : rowIndex,
                "numRows" : numSectionRows, 
                "columnIndex" : columnIndex, 
                "numColumns" : numSectionColumns
            })
        else:
            def split_horizontal():
                numRowsOnTop = random.randint(2,numSectionRows-2) # TODO: verify range here
                divideSections(rowIndex, numRowsOnTop, columnIndex, numSectionColumns) # new top section
                divideSections(rowIndex + numRowsOnTop, numSectionRows - numRowsOnTop, columnIndex, numSectionColumns) # new bottom section
                
            def split_vertical():
                numColumnsOnLeft = random.randint(2,numSectionColumns-2) # TODO: verify range here
                divideSections(rowIndex, numSectionRows, columnIndex, numColumnsOnLeft)
                divideSections(rowIndex, numSectionRows, columnIndex + numColumnsOnLeft, numSectionColumns - numColumnsOnLeft)
            
            if numSectionColumns < 5:
                split_horizontal()
            elif numSectionRows < 5:
                split_vertical()
            else:
                if random.random() < 0.5:
                    split_vertical()
                else:
                    split_horizontal()
    
    divideSections(0, numRows, 0, numColumns)
    print sections
    
    def move_columns(walls, offset):
        return map(lambda wall: (wall[0], wall[1] + offset, wall[2]), walls)
    def move_rows(walls, offset):
        return map(lambda wall: (wall[0] + offset, wall[1], wall[2]), walls)

    openWalls = []
    for section in sections:
        if random.random() < 0.8:
            sectionOpenWalls = get_clockwise_spiral(section["numRows"], section["numColumns"])
        else:
            sectionOpenWalls = create_maze_with_depth(section["numRows"], section["numColumns"])
        
        sectionOpenWalls = move_columns(move_rows(sectionOpenWalls, section["rowIndex"]), section["columnIndex"])

        openWalls += sectionOpenWalls
        
    # connect the sections by creating a wall between them
    visitedSections = set()
    
    def get_overlap(a1, a2, b1, b2):
        left = max(a1, b1)
        right = min(a2, b2)
        
        if left <= right:
            return (left, right)
        return None
    
    def traverse(section):
        visitedSections.add(str(section))
        
        # get unvisited neighbor sections
        random.shuffle(sections)
        for neighbor in sections:
            if str(neighbor) not in visitedSections:
                # if neighbor adjacent to current section
                if section["columnIndex"] + section["numColumns"] == neighbor["columnIndex"]:
                    overlap = get_overlap(section["rowIndex"], section["rowIndex"] + section["numRows"],
                                               neighbor["rowIndex"], neighbor["rowIndex"] + neighbor["numRows"])
                    if overlap:
                        # TODO: pick the best number here
                        randomRowIndex = random.randint(overlap[0], overlap[1])
                        openWalls.append((randomRowIndex, neighbor["columnIndex"] - 1, "right"))
                        
                        traverse(neighbor)
                        
                elif section["rowIndex"] + section["numRows"] == neighbor["rowIndex"]:
                    overlap = get_overlap(section["columnIndex"], section["columnIndex"] + section["numColumns"],
                                          neighbor["columnIndex"], neighbor["columnIndex"] + neighbor["numColumns"])
                    if overlap:
                        # TODO: pick the best number here
                        randomColumnIndex = random.randint(overlap[0], overlap[1])
                        openWalls.append((neighbor["rowIndex"] - 1, randomColumnIndex, "down"))
    
    traverse(sections[0])
    
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