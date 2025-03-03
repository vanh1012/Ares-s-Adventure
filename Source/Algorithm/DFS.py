MOVE = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}


class DFS:
    def __init__(self, grid, player_pos, boxes, goals, weightOfBox):
        self.grid = grid
        self.player_pos = player_pos
        self.boxes = set(boxes)
        self.goals = set(goals)
        self.visited = set()
        self.box_weights = dict(zip((boxes), weightOfBox))
        self.countNode = 0

    def isNextValid(self, newPositionPlayer, newPositionBox=None):
        [x, y] = newPositionPlayer
        if self.grid[x][y] == "#":
            return False
        if not newPositionBox:
            return True
        [x, y] = newPositionBox
        if self.grid[x][y] != "#" and (x, y) not in self.boxes:
            return True
        return False

    def checkDeadlock(self, boxes):
        for x, y in boxes:
            if (x, y) in self.goals:
                continue

            if self.grid[x - 1][y] == "#" and self.grid[x][y - 1] == "#":
                return True
            if self.grid[x + 1][y] == "#" and self.grid[x][y + 1] == "#":
                return True
            if self.grid[x - 1][y] == "#" and self.grid[x][y + 1] == "#":
                return True
            if self.grid[x + 1][y] == "#" and self.grid[x][y - 1] == "#":
                return True

            if (x, y + 1) in boxes:
                if (x, y) in self.goals and (x, y + 1) in self.goals:
                    continue
                if self.grid[x - 1][y] == "#" and self.grid[x - 1][y + 1] == "#":
                    return True
                if self.grid[x + 1][y] == "#" and self.grid[x + 1][y + 1] == "#":
                    return True
            if (x + 1, y) in boxes:
                if (x, y) in self.goals and (x + 1, y) in self.goals:
                    continue
                if self.grid[x][y - 1] == "#" and self.grid[x + 1][y - 1] == "#":
                    return True
                if self.grid[x][y + 1] == "#" and self.grid[x + 1][y + 1] == "#":
                    return True
        return False

    def dfs(self, positionPlayer, road):
        self.countNode += 1
        if self.boxes == self.goals:
            return road
        if self.checkDeadlock(self.boxes):
            return
        for move, (dx, dy) in MOVE.items():
            newPositionPlayer = [positionPlayer[0] + dx, positionPlayer[1] + dy]
            if (newPositionPlayer[0], newPositionPlayer[1]) not in self.boxes:
                new_State = (tuple(newPositionPlayer), tuple(sorted(self.boxes)))
                if (
                    self.isNextValid(newPositionPlayer)
                    and new_State not in self.visited
                ):
                    self.visited.add(new_State)
                    result = self.dfs(newPositionPlayer, road + [[move.lower(), 1]])
                    if result:
                        return result
            else:
                newPositionBox = [newPositionPlayer[0] + dx, newPositionPlayer[1] + dy]
                if self.isNextValid(newPositionPlayer, newPositionBox):
                    self.boxes.remove((newPositionPlayer[0], newPositionPlayer[1]))
                    self.boxes.add((newPositionBox[0], newPositionBox[1]))
                    new_State = (tuple(newPositionPlayer), tuple(sorted(self.boxes)))
                    if new_State not in self.visited:
                        self.visited.add(new_State)
                        old_box_pos = tuple(newPositionPlayer)
                        cost = self.box_weights[old_box_pos]
                        self.box_weights.pop(old_box_pos)
                        self.box_weights[tuple(newPositionBox)] = cost
                        result = self.dfs(newPositionPlayer, road + [[move, cost]])
                        if result:
                            return result
                        self.box_weights.pop(tuple(newPositionBox))
                        self.box_weights[old_box_pos] = cost
                    self.boxes.remove((newPositionBox[0], newPositionBox[1]))
                    self.boxes.add((newPositionPlayer[0], newPositionPlayer[1]))
        return None

    def runner(self):
        self.visited.add((tuple(self.player_pos), tuple(sorted(self.boxes))))
        result = self.dfs(self.player_pos, [])
        sumCost = 0
        step = ""
        if result == None:
            return self.countNode, 0, "NoSol"
        for i in result:
            sumCost += i[1]
            step += i[0]
        if result:
            return [self.countNode, sumCost, step]