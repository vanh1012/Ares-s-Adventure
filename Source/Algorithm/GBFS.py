import heapq  
from collections import deque  
MOVE = {
    "U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1),
    "u": (-1, 0), "d": (1, 0), "l": (0, -1), "r": (0, 1)
} 

class GBFS:  
    def __init__(self, grid, player_pos, boxes, goals, weightOfBox):  
        self.grid = grid  
        self.player_pos = player_pos  
        self.boxes = set(boxes)  
        self.goals = set(goals)  
        self.nodes_generated = 0  
        
        # Associate weights with boxes  
        if isinstance(weightOfBox, list) and len(weightOfBox) == len(boxes):  
            self.weightOfBox = {box: weight for box, weight in zip(boxes, weightOfBox)}  
        else:  
            print("Warning: Weight mismatch, using default weights")  
            self.weightOfBox = {box: 1 for box in boxes}  
        
        # Track each box's original position  
        self.box_origins = {box: box for box in boxes}  
        
        # Pre-calculate deadlock positions to avoid  
        self.deadlock_positions = self.identify_deadlocks()  
    
    def identify_deadlocks(self):  
        deadlocks = set()  
        rows, cols = len(self.grid), len(self.grid[0])  

        for r in range(rows):  
            for c in range(cols):  
                if not self.is_wall(r, c) and (r, c) not in self.goals:  
                    if ((self.is_wall(r-1, c) and self.is_wall(r, c-1)) or  
                        (self.is_wall(r-1, c) and self.is_wall(r, c+1)) or  
                        (self.is_wall(r+1, c) and self.is_wall(r, c-1)) or  
                        (self.is_wall(r+1, c) and self.is_wall(r, c+1))):  
                        deadlocks.add((r, c))  

        return deadlocks  
    
    def is_wall(self, x, y):  
        if not (0 <= x < len(self.grid) and 0 <= y < len(self.grid[0])):  
            return True  
        return self.grid[x][y] == "#"  
    
    def is_next_valid(self, player_pos, box_pos=None):  
        px, py = player_pos  
        if self.is_wall(px, py):  
            return False  
        if box_pos is not None:  
            bx, by = box_pos  
            if self.is_wall(bx, by) or (bx, by) in self.boxes or (bx, by) in self.deadlock_positions:  
                return False  
        return True  
    
    def is_solved(self, boxes):  
        return boxes.issubset(self.goals) and len(boxes) == len(self.goals)  
    
    def manhattan_distance(self, a, b):  
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  
    
    def can_reach(self, start, target, boxes):  
        if start == target:  
            return True  
        
        queue = deque([start])  
        visited = {start}  
        
        while queue:  
            pos = queue.popleft()  
            px, py = pos  
            
            for _, (dx, dy) in MOVE.items():  
                new_pos = (px + dx, py + dy)  
                
                if (new_pos not in visited and   
                    not self.is_wall(*new_pos) and   
                    new_pos not in boxes):  
                    if new_pos == target:  
                        return True  
                    visited.add(new_pos)  
                    queue.append(new_pos)  
        
        return False  
    
    def calculate_heuristic(self, boxes):  
        if not boxes or not self.goals:  
            return float('inf')  

        total = 0  
        remaining_goals = list(self.goals)  

        for box in boxes:  
            if box in self.goals:  
                if box in remaining_goals:  
                    remaining_goals.remove(box)  
                total += 0  
            else:  
                if remaining_goals:  
                    closest_dist = min(self.manhattan_distance(box, goal) for goal in remaining_goals)  
                    closest_goal = min(remaining_goals, key=lambda g: self.manhattan_distance(box, g))  
                    total += closest_dist  
                    if closest_goal in remaining_goals:  
                        remaining_goals.remove(closest_goal)  
                else:  
                    total += 99  

        return total  
    
    def gbfs(self):  
        priority_queue = []  
        initial_heuristic = self.calculate_heuristic(self.boxes)  
        
        initial_state = (initial_heuristic, 0, self.player_pos, frozenset(self.boxes), [])  
        
        heapq.heappush(priority_queue, initial_state)  
        visited = set()  
        self.nodes_generated = 1  
        total_weight = 0  # Khởi tạo tổng trọng lượng  
        max_iterations = 500000  
        
        while priority_queue and self.nodes_generated < max_iterations:  
            current_heuristic, steps, player_pos, boxes_frozen, path = heapq.heappop(priority_queue)  
            boxes = set(boxes_frozen)  

            if self.is_solved(boxes):  
                # Tính toán tổng trọng lượng từ các bước đẩy thùng  
                total_weight = sum(move_info[2] for move_info in path if move_info[1])  
                return path, total_weight  # Trả về path và total_weight  
            
            # Tạo khóa trạng thái cho tập visited  
            state_key = (player_pos, boxes_frozen)  
            if state_key in visited:  
                continue  
            
            visited.add(state_key)  
            
            # Thử từng bước di chuyển có thể  
            px, py = player_pos  
            for move, (dx, dy) in MOVE.items():  
                new_pos = (px + dx, py + dy)  
                new_box_pos = (new_pos[0] + dx, new_pos[1] + dy)  
                
                # Trường hợp 1: Di chuyển vào không gian trống - không đẩy thùng  
                if new_pos not in boxes and not self.is_wall(*new_pos):  
                    # Thêm bước di chuyển vào path  
                    new_path = path + [[move, False, 1]]  # Weight cho di chuyển thường là 1  
                    new_state = (self.calculate_heuristic(boxes), steps + 1, new_pos, boxes_frozen, new_path)  
                    
                    new_state_key = (new_pos, boxes_frozen)  
                    if new_state_key not in visited:  
                        heapq.heappush(priority_queue, new_state)  
                        self.nodes_generated += 1  
                
                # Trường hợp 2: Di chuyển và đẩy thùng  
                elif new_pos in boxes and not self.is_wall(*new_box_pos) and new_box_pos not in boxes:  
                    # Kiểm tra xem vị trí mới có phải là điểm chết hay không, hoặc có phải là mục tiêu  
                    if new_box_pos not in self.deadlock_positions or new_box_pos in self.goals:  
                        # Cập nhật vị trí của thùng  
                        new_boxes = set(boxes)  
                        old_box_pos = new_pos  # Vị trí cũ của thùng  
                        new_boxes.remove(old_box_pos)  
                        new_boxes.add(new_box_pos)  
                        
                        # Lấy trọng lượng của thùng dựa vào vị trí ban đầu  
                        original_box_pos = self.box_origins[old_box_pos]  
                        box_weight = self.weightOfBox.get(original_box_pos, 1)  
                        
                        # Cập nhật vị trí ban đầu của thùng  
                        self.box_origins[new_box_pos] = original_box_pos  
                        
                        new_boxes_frozen = frozenset(new_boxes)  
                        # Thêm bước đẩy vào path với trọng lượng  
                        new_path = path + [[move, True, box_weight]]  
                        
                        # Tính toán heuristic mới  
                        new_heuristic = self.calculate_heuristic(new_boxes)  
                        new_state = (new_heuristic, steps + 1, new_pos, new_boxes_frozen, new_path)  
                        
                        new_state_key = (new_pos, new_boxes_frozen)  
                        if new_state_key not in visited:  
                            heapq.heappush(priority_queue, new_state)  
                            self.nodes_generated += 1  
        return None, 0    
    
    def runner(self):  
        try:  
            result, total_weight = self.gbfs()  
            if result:  
                # Chuyển đổi result sang dạng chuỗi các bước  
                solution = []  
                for move_info in result:  
                    move, is_push, weight = move_info  
                    if is_push:  
                        solution.append(move.upper())  # Đẩy thùng: chữ hoa  
                    else:  
                        solution.append(move.lower())  # Di chuyển thường: chữ thường  
                solution_str = ''.join(solution)  
                return self.nodes_generated, total_weight, solution_str  
            else:  
                return None, 0, "NoSol"  
        except Exception as e:  
            print(f"Error in GBFS runner: {e}")  
            import traceback  
            traceback.print_exc()  
            return None, 0, "NoSol"