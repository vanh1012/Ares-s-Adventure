from queue import PriorityQueue
from scipy.optimize import linear_sum_assignment
import numpy as np

MOVE = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}


class ASTAR:
    def __init__(self, grid, player_pos, boxes, goals, weightOfBox):
        self.grid = grid
        self.player_pos = player_pos
        self.boxes = set(boxes)
        self.goals = set(goals)
        self.visited = {}  # = [g_cost,parrentState,move] , move = [cost,direction]
        self.box_weights = dict(zip(boxes, weightOfBox))
        self.pq = PriorityQueue()
        self.countNode = 0

    def manhattan_distance(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def MinimumCostFromBoxToGoal(self, box_weight):
        cost = []
        for box, w in box_weight.items():
            row_cost = []
            for goal in self.goals:
                row_cost.append(w * self.manhattan_distance(box, goal))
            cost.append(row_cost)

        np_cost = np.array(cost)
        row_ind, col_ind = linear_sum_assignment(np_cost)
        return np_cost[row_ind, col_ind].sum()

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

    def isNextValid(self, newPositionPlayer, box_pos=None, newPositionBox=None):
        x, y = newPositionPlayer
        if self.grid[x][y] == "#":
            return False
        if not newPositionBox:
            return True
        x, y = newPositionBox
        return self.grid[x][y] != "#" and (x, y) not in box_pos

    def winning(self, boxes):
        """Checks if all boxes are on goal positions."""
        return self.goals == boxes

    def buildPathToGoal(self, State, initial_State):
        path = []
        while State != initial_State:
            data = self.visited.get(State)
            if not data:
                break
            State = data[1]
            path.append(data[2])
        path.reverse()
        return path

    def runner(self):
        initial_State = (
            self.player_pos,
            tuple(sorted(self.box_weights.items())),
        )
        initial_heuristic = self.MinimumCostFromBoxToGoal(self.box_weights)
        self.pq.put(
            (
                initial_heuristic,
                0,
                self.player_pos,
                self.boxes.copy(),
                tuple(sorted(self.box_weights.items())),
            )
        )
        self.visited[initial_State] = [0, []]
        while not self.pq.empty():
            self.countNode += 1
            f, g, player_pos, boxes_pos, boxes_weights_tuple = self.pq.get()
            boxes_weights = dict(boxes_weights_tuple)
            current_state = (
                player_pos,
                tuple(sorted(boxes_weights.items())),
            )
            if self.winning(boxes_pos):
                result = self.buildPathToGoal(current_state, initial_State)
                sumCost = 0
                step = ""
                for i in result:
                    sumCost += i[1]
                    step += i[0]
                return [self.countNode, sumCost, step]
            if self.checkDeadlock(boxes_pos):
                continue
            for move, (dx, dy) in MOVE.items():
                newPlayer_pos = (player_pos[0] + dx, player_pos[1] + dy)
                if newPlayer_pos not in boxes_pos:
                    new_State = (
                        newPlayer_pos,
                        tuple(sorted(boxes_weights.items())),
                    )
                    new_g = g + 1
                    if self.isNextValid(newPlayer_pos):
                        if new_State not in self.visited:
                            self.visited[new_State] = [
                                new_g,
                                current_state,
                                [move.lower(), 1],
                            ]
                            h_cost = self.MinimumCostFromBoxToGoal(boxes_weights)
                            self.pq.put(
                                (
                                    new_g + h_cost,
                                    new_g,
                                    newPlayer_pos,
                                    boxes_pos.copy(),
                                    tuple(sorted(boxes_weights.items())),
                                )
                            )
                        if new_g < self.visited[new_State][0]:
                            self.visited[new_State] = [
                                new_g,
                                current_state,
                                [move.lower(), 1],
                            ]
                else:
                    newBox_pos = (newPlayer_pos[0] + dx, newPlayer_pos[1] + dy)

                    if self.isNextValid(newPlayer_pos, boxes_pos, newBox_pos):
                        new_boxes_weights = boxes_weights.copy()
                        weight = new_boxes_weights.pop(newPlayer_pos)
                        new_boxes_weights[newBox_pos] = weight
                        new_boxes_pos = boxes_pos.copy()
                        new_boxes_pos.remove(newPlayer_pos)
                        new_boxes_pos.add(newBox_pos)

                        new_State = (
                            newPlayer_pos,
                            tuple(sorted(new_boxes_weights.items())),
                        )
                        new_g = g + weight
                        if new_State not in self.visited:
                            self.visited[new_State] = [
                                new_g,
                                current_state,
                                [move, weight],
                            ]
                            h_cost = self.MinimumCostFromBoxToGoal(new_boxes_weights)
                            self.pq.put(
                                (
                                    new_g + h_cost,
                                    new_g,
                                    newPlayer_pos,
                                    new_boxes_pos,
                                    tuple(sorted(new_boxes_weights.items())),
                                )
                            )
                        if new_g < self.visited[new_State][0]:
                            self.visited[new_State] = [
                                new_g,
                                current_state,
                                [move, weight],
                            ]
        return self.countNode, 0, "NoSol"