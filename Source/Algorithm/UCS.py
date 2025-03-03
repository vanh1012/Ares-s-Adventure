import heapq
import math
from collections import deque

MOVE = {
    "U": (-1, 0),
    "D": (1, 0),
    "L": (0, -1),
    "R": (0, 1)
}

class UCS:
    def __init__(self, grid, player_pos, boxes, goals, weightOfBox):
        self.grid = grid
        self.start_player = tuple(player_pos)
        self.start_boxes = tuple(sorted(boxes))
        self.goals = set(goals)
        d = dict(zip(boxes, weightOfBox))
        self.start_box_weights = frozenset(d.items())

    def is_wall(self, x, y):
        if not (0 <= x < len(self.grid) and 0 <= y < len(self.grid[0])):
            return True
        return self.grid[x][y] == "#"

    def can_player_reach(self, start, target, boxes_set):
        if start == target:
            return True
        visited = set()
        queue = deque([start])
        while queue:
            cx, cy = queue.popleft()
            for dx, dy in MOVE.values():
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < len(self.grid) and 0 <= ny < len(self.grid[0]):
                    if not self.is_wall(nx, ny) and (nx, ny) not in boxes_set:
                        if (nx, ny) not in visited:
                            if (nx, ny) == target:
                                return True
                            visited.add((nx, ny))
                            queue.append((nx, ny))
        return False

    def is_deadlock(self, boxes_set):
        for box in boxes_set:
            if box in self.goals:
                continue
            x, y = box
            if ((self.is_wall(x-1, y) and self.is_wall(x, y-1)) or
                (self.is_wall(x-1, y) and self.is_wall(x, y+1)) or
                (self.is_wall(x+1, y) and self.is_wall(x, y-1)) or
                (self.is_wall(x+1, y) and self.is_wall(x, y+1))):
                return True
        return False

    def ucs(self):
        start_state = (self.start_player, self.start_boxes, self.start_box_weights)
        pq = [(0, start_state, "", 0)]
        best_cost = {start_state: 0}
        node_generated = 0

        while pq:
            cost, (player, boxes_tuple, box_weights_fro), path, total_weight = heapq.heappop(pq)
            node_generated += 1

            if cost > best_cost[(player, boxes_tuple, box_weights_fro)]:
                continue

            boxes_set = set(boxes_tuple)

            if self.is_deadlock(boxes_set):
                continue

            if boxes_set == self.goals:
                return node_generated, total_weight, path

            box_weights = dict(box_weights_fro)
            px, py = player

            for mv, (dx, dy) in MOVE.items():
                nx, ny = px + dx, py + dy
                if (nx, ny) not in boxes_set and not self.is_wall(nx, ny):
                    if self.can_player_reach((px, py), (nx, ny), boxes_set):
                        new_cost = cost + 1
                        new_state = ((nx, ny), boxes_tuple, box_weights_fro)
                        if new_cost < best_cost.get(new_state, math.inf):
                            best_cost[new_state] = new_cost
                            new_path = path + mv.lower()
                            heapq.heappush(pq, (new_cost, new_state, new_path, total_weight))
                elif (nx, ny) in boxes_set:
                    bx, by = nx + dx, ny + dy
                    if (bx, by) not in boxes_set and not self.is_wall(bx, by):
                        if self.can_player_reach((px, py), (nx, ny), boxes_set - {(nx, ny)}):
                            w = box_weights.get((nx, ny), 0)
                            new_cost = cost + w
                            new_boxes = set(boxes_set)
                            new_boxes.remove((nx, ny))
                            new_boxes.add((bx, by))
                            new_boxes_tuple = tuple(sorted(new_boxes))
                            new_dict = dict(box_weights)
                            if (nx, ny) in new_dict:
                                tmp = new_dict.pop((nx, ny))
                                new_dict[(bx, by)] = tmp
                            nw_fro = frozenset(new_dict.items())
                            new_state = ((nx, ny), new_boxes_tuple, nw_fro)
                            new_total_weight = total_weight + w
                            if new_cost < best_cost.get(new_state, math.inf):
                                best_cost[new_state] = new_cost
                                new_path = path + mv.upper()
                                heapq.heappush(pq, (new_cost, new_state, new_path, new_total_weight))
        return node_generated, 0, "NoSol"

    def runner(self):
        return self.ucs()