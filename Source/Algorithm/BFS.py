import time
import queue

TIME_LIMITED = 1800

MOVE = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1),
}

class BFS:
    def __init__(self, grid, player_pos, box_positions, goals, weight_of_boxes):
        """
        box_positions: list hoặc tuple các vị trí của hộp theo thứ tự (hộp i)
        weight_of_boxes: list các trọng lượng tương ứng cùng thứ tự
        """
        self.grid = grid
        self.n_boxes = len(box_positions)
        self.goals = set(goals)
        # Lưu weights vào list, index tương ứng với box i
        self.weights = weight_of_boxes
        # Tạo state khởi đầu
        #   mỗi box i đang ở box_positions[i]
        self.start_state = (
            player_pos,                       # (r, c) player
            tuple(box_positions),             # ( (r0,c0), (r1,c1), ... )
            0                                 # total_weight
        )

    def is_goal(self, box_positions_tuple):
        """
        Kiểm tra nếu tất cả hộp đều nằm trong goals.
        """
        return all(pos in self.goals for pos in box_positions_tuple)

    def is_deadlock(self, box_positions_tuple):
        """
        Deadlock cơ bản: nếu hộp không ở goal và bị kẹt góc 2 tường.
        """
        for (r, c) in box_positions_tuple:
            if (r, c) not in self.goals:
                # Kiểm tra 4 thế kẹt góc
                if (
                    (self.grid[r-1][c] == "#" and self.grid[r][c-1] == "#") or
                    (self.grid[r-1][c] == "#" and self.grid[r][c+1] == "#") or
                    (self.grid[r+1][c] == "#" and self.grid[r][c-1] == "#") or
                    (self.grid[r+1][c] == "#" and self.grid[r][c+1] == "#")
                ):
                    return True
        return False

    def build_pos_to_index(self, box_positions_tuple):
        """
        Xây dict: pos -> chỉ số hộp
        """
        d = {}
        for i, pos in enumerate(box_positions_tuple):
            d[pos] = i
        return d

    def move_state(self, state, dx, dy):
        """
        Thực hiện di chuyển (dx, dy). 
        state = (player_pos, box_positions_tuple, total_weight)
        Trả về (new_state, is_pushing) hoặc (None, False) nếu không di chuyển được.
        """
        (player_pos, box_positions, total_w) = state
        px, py = player_pos

        new_px = px + dx
        new_py = py + dy

        # Check tường
        if self.grid[new_px][new_py] == "#":
            return None, False

        # Tạo dict vị trí -> chỉ số hộp
        pos_to_idx = self.build_pos_to_index(box_positions)

        # Kiểm tra xem ô trước mặt có hộp không
        if (new_px, new_py) in pos_to_idx:
            # Có hộp
            box_i = pos_to_idx[(new_px, new_py)]
            # Vị trí mới của hộp
            box_x = new_px + dx
            box_y = new_py + dy

            # Không thể đẩy vào tường hoặc hộp khác
            if self.grid[box_x][box_y] == "#" or (box_x, box_y) in pos_to_idx:
                return None, False

            # Tính cost đẩy
            cost_push = self.weights[box_i]
            new_total = total_w + cost_push

            # Cập nhật vị trí hộp i
            # box_positions là tuple, ta phải chuyển sang list để sửa
            new_box_positions = list(box_positions)
            new_box_positions[box_i] = (box_x, box_y)
            new_box_positions = tuple(new_box_positions)

            new_state = ((new_px, new_py), new_box_positions, new_total)
            return new_state, True

        else:
            # Di chuyển thường, không đẩy
            new_state = ((new_px, new_py), box_positions, total_w)
            return new_state, False

    def reconstruct_path(self, parents, end_state):
        """
        Dựng đường đi từ end_state ngược về start_state
        parents[s] = (parent_s, move_char)
        """
        path = []
        current = end_state
        while current in parents:
            (p_state, move_c) = parents[current]
            path.append(move_c)
            current = p_state
        path.reverse()
        return "".join(path)

    def solve(self):
        start_time = time.time()

        from collections import deque
        frontier = deque()
        frontier.append(self.start_state)

        # visited: set các (player_pos, box_positions_tuple)
        visited = set()
        player_pos, box_positions, _ = self.start_state
        visited.add((player_pos, box_positions))

        # parents[state] = (parent_state, move_char)
        parents = {}

        node_generated = 1

        while frontier:
            if (time.time() - start_time) >= TIME_LIMITED:
                return node_generated, 0, "TimeOut"

            current_state = frontier.popleft()
            (cur_player, cur_boxes, cur_weight) = current_state

            # Check goal
            if self.is_goal(cur_boxes):
                # Dựng lời giải
                sol = self.reconstruct_path(parents, current_state)
                return node_generated, cur_weight, sol

            # Mở rộng 4 hướng
            for move_key, (dx, dy) in MOVE.items():
                new_state, is_pushing = self.move_state(current_state, dx, dy)
                if new_state is None:
                    continue

                (n_player, n_boxes, n_weight) = new_state
                # Deadlock?
                if self.is_deadlock(n_boxes):
                    continue

                if (n_player, n_boxes) not in visited:
                    visited.add((n_player, n_boxes))
                    node_generated += 1
                    # Quy ước ký tự di chuyển
                    move_char = move_key.upper() if is_pushing else move_key.lower()

                    parents[new_state] = (current_state, move_char)
                    frontier.append(new_state)

        # Không tìm được lời giải
        return node_generated, 0, "NoSol"
    def runner(self):
        return self.solve()

def parse_grid(grid):
    player_pos = None
    boxes = []
    goals = []
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == "@":
                player_pos = (r, c)
            elif ch == "$":
                boxes.append((r, c))
            elif ch == ".":
                goals.append((r, c))
    return player_pos, boxes, goals
