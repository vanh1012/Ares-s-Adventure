from collections import namedtuple
from Algorithm import ASTAR, BFS, DFS, Dijkstra, UCS, GBFS
from enum import Enum
import sys
import pygame
import time
import tracemalloc

Tile = namedtuple("Tile", "wall ares goal stone")
Dir = Enum('Dir', 'UP DN LT RT')
Key = Enum('Key', 'UP DOWN LEFT RIGHT QUIT SKIP')
icon = pygame.image.load(r'./Images/icon.ico') 
MOVE = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
pygame.init()
run_once = True

class World:
    def __init__(self, filename):
        try:
            with open(filename, "r") as f:
                lines = f.readlines()
            self.stone_weights = list(map(int, lines[0].split()))
            self.grid = [list(line.rstrip("\n")) for line in lines[1:]]
            self.player_pos = []
            self.boxes = []
            self.goals = []
            self.wall_pos = []
            self.nrows = 0
            self.ncols = 0
            for i, line in enumerate(lines[1:]):
                row = line.rstrip()
                for j, tile in enumerate(row):
                    pos = (i, j)
                    if tile in ('@', '+'):
                        self.player_pos.append(pos)
                    if tile in ('$', '*'):
                        self.boxes.append(pos)
                    if tile in ('.', '*', '+'):
                        self.goals.append(pos)
                    if tile == '#':
                        self.wall_pos.append(pos)
            
            self.stone_weights_map = {}
            self.stone_weights_map = {}
            for i in range(len(self.boxes)):            
                self.stone_weights_map[self.boxes[i]] = self.stone_weights[i]
            # để debug đảm bảo input vào là đúng
            '''for row in self.grid:
                print(row)
            print("Player Position:", self.player_pos)
            print("Boxes:", self.boxes)
            print("Goals:", self.goals)
            print("Box Weights:", self.stone_weights)
            print(self.stone_weights_map)'''
        except (OSError, IOError):
            print("sokoban: loading levels from text file failed!", file=sys.stderr)
            exit(1)
        self.load_size()

    def load_size(self):
        self.nrows = len(self.grid)
        self.ncols = max(len(row) for row in self.grid) if self.grid else 0

    def get(self, pos):
        return Tile(wall = (pos in self.wall_pos),
                    ares = (pos in self.player_pos),
                    goal = (pos in self.goals),
                    stone = (pos in self.boxes))

    def push_stone(self, from_pos, to_pos):
        if from_pos in self.boxes:
            self.boxes.remove(from_pos)
            self.boxes.append(to_pos)

            self.stone_weights_map[to_pos] = self.stone_weights_map.pop(from_pos)

    def move_ares(self, to_pos):
        self.player_pos = [to_pos]


class GameEngine:
    @staticmethod
    def move(direction, world):
        r, c = world.player_pos[0]  
        if direction == Dir.UP:
            next_pos = (r - 1, c)  
            push_pos = (r - 2, c)
        elif direction == Dir.DN:
            next_pos = (r + 1, c)  
            push_pos = (r + 2, c)
        elif direction == Dir.LT:
            next_pos = (r, c - 1) 
            push_pos = (r, c - 2)
        elif direction == Dir.RT:
            next_pos = (r, c + 1)  
            push_pos = (r, c + 2)

        next_tile = world.get(next_pos)
        push_tile = world.get(push_pos)
        if next_tile.wall:
            return

        if next_tile.stone:
            if not push_tile.wall and not push_tile.stone:
                world.push_stone(next_pos, push_pos)
                world.move_ares(next_pos)
            return

        world.move_ares(next_pos)

    @staticmethod
    def is_game_over(world):
        for stone in world.boxes:
            if stone not in world.goals:
                return False
        return True


class GameView:  
    TILE_SIZE = 64  

    def __init__(self):  
        pygame.init()
        self._screen = None  
        self._images = {}  
        self._done = False 
        pygame.display.set_caption("Sokoban - Amazing Puzzle Game")
        pygame.display.set_icon(icon)
        self._help = False

    def init_show_help(self, world):
        icon_size = 40  
        self.menu_rect = pygame.Rect(world.ncols * GameView.TILE_SIZE - icon_size - 10, 10, icon_size, icon_size)

    def show_help(self):
        #Hiển thị bảng chỉ dẫn 
        if self._help:
            screen_width, screen_height = self._screen.get_size()
            box_width, box_height = 500, 380
            box_x = (screen_width - box_width) // 2
            box_y = (screen_height - box_height) // 2

            overlay = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self._screen.blit(overlay, (0, 0))

            pygame.draw.rect(self._screen, (240, 240, 240), (box_x, box_y, box_width, box_height), border_radius=15)
            pygame.draw.rect(self._screen, (50, 50, 50), (box_x, box_y, box_width, box_height), 3, border_radius=15)

            title_font = pygame.font.Font(None, 36)
            title_text = title_font.render("How to Play", True, (0, 0, 0))
            self._screen.blit(title_text, (box_x + 20, box_y + 15))  # Căn trái

            font = pygame.font.Font(None, 28)
            options = [
                "Arrow keys: Move character",
                "Move all boxes to the goals",
                "Press R: Reset game",
                "Press 1: ASTAR Algorithm",
                "Press 2: BFS Algorithm",
                "Press 3: DFS Algorithm",
                "Press 4: Dijkstra Algorithm",
                "Press 5: GBFS Algorithm",
                "Press 6: UCS Algorithm"
            ]

            # Vẽ nội dung căn trái
            text_x = box_x + 20  # Căn trái đồng đều
            for i, text in enumerate(options):
                label = font.render(text, True, (80, 80, 80))
                text_rect = label.get_rect(topleft=(text_x, box_y + 60 + i * 30))  # Căn trái
                self._screen.blit(label, text_rect)

            # Nút "Close" ở góc trên phải
            self.close_btn = pygame.Rect(box_x + box_width - 40, box_y + 10, 30, 30)
            pygame.draw.circle(self._screen, (200, 0, 0), self.close_btn.center, 15)
            pygame.draw.circle(self._screen, (0, 0, 0), self.close_btn.center, 15, 2)  # Viền đen

            close_text = font.render("X", True, (255, 255, 255))
            close_text_rect = close_text.get_rect(center=self.close_btn.center)
            self._screen.blit(close_text, close_text_rect)

            pygame.display.flip()



    def load_images(self):  
        tile_names = (  
            ("wall", Tile(wall=True, ares=False, goal=False, stone=False)),  
            ("floor", Tile(wall=False, ares=False, goal=False, stone=False)),  
            ("goal", Tile(goal=True, wall=False, ares=False, stone=False)),  
            ("stone", Tile(stone=True, wall=False, ares=False, goal=False)),  
            ("ares", Tile(ares=True, wall=False, goal=False, stone=False)),  
            ("stone-goaled", Tile(stone=True, goal=True, wall=False, ares=False)),  
            ("ares-goaled", Tile(ares=True, goal=True, wall=False, stone=False))
        )  

        self._images = {}  
        for name, tile in tile_names:  
            img = pygame.image.load(f"./Images/{name}.png")
            #img = pygame.transform.scale(img, (GameView.TILE_SIZE, GameView.TILE_SIZE)) 
            self._images[tile] = img


    def setup_game(self, world):
        width = world.ncols * GameView.TILE_SIZE
        height = world.nrows * GameView.TILE_SIZE
        self._screen = pygame.display.set_mode((width, height))
        self.init_show_help(world)

    def show_world(self, world):  
        self._screen.fill((255, 0, 0))  
        font = pygame.font.Font(None, 36)  
        for i in range(world.nrows):  
            for j in range(world.ncols):  
                tile = world.get((i, j))  
                sx = j * GameView.TILE_SIZE  
                sy = i * GameView.TILE_SIZE  
                img = self._images[tile]  
                self._screen.blit(img, (sx, sy))  
        
        # Hiển thị trọng số trên stone
        for stone in world.boxes:
            if stone in world.stone_weights_map:
                weight = world.stone_weights_map[stone]
            else:
                weight = 0
            text = font.render(str(weight), True, (255, 255, 255))
            text_rect = text.get_rect(center=(stone[1] * GameView.TILE_SIZE + 32, stone[0] * GameView.TILE_SIZE + 32 - 11.5))
            self._screen.blit(text, text_rect)

        pygame.display.flip()

        # Vẽ icon `?` với viền trong suốt
        icon_radius = 20  # Bán kính icon
        pygame.draw.circle(self._screen, (255, 255, 255, 150), self.menu_rect.center, icon_radius)  # Nền trong suốt
        pygame.draw.circle(self._screen, (0, 0, 0), self.menu_rect.center, icon_radius, 2)  # Viền đen

        # Vẽ dấu `?`
        font = pygame.font.Font(None, 36)
        text = font.render("?", True, (0, 0, 0))  
        text_rect = text.get_rect(center=self.menu_rect.center)
        self._screen.blit(text, text_rect)

        # Hiển thị menu trợ giúp nếu đang bật
        self.show_help()

        pygame.display.flip()

    def quit(self):  
        pygame.quit()  
        self._done = True  

    def run_once(self, event_handler):  
        key_map = {  
            pygame.K_UP: Key.UP,  
            pygame.K_LEFT: Key.LEFT,  
            pygame.K_RIGHT: Key.RIGHT,  
            pygame.K_DOWN: Key.DOWN,  
            pygame.K_r: 'RESET',  
            pygame.K_1: 'ASTAR', 
            pygame.K_2: 'BFS', 
            pygame.K_3: 'DFS', 
            pygame.K_4: 'Dijkstra', 
            pygame.K_5: 'GBFS', 
            pygame.K_6: 'UCS', 
            pygame.K_ESCAPE : 'ECS'
        }  
        event = pygame.event.wait()  
        if event.type == pygame.QUIT:  
            event_handler.handle_key(Key.QUIT)  
        elif event.type == pygame.KEYDOWN:  
            try:  
                event_handler.handle_key(key_map[event.key])  
            except KeyError:  
                pass 
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self._help:
                # Nếu bấm vào nút Close, tắt bảng chỉ dẫn
                if hasattr(self, "close_btn") and self.close_btn.collidepoint(event.pos):
                    self._help = False
                    self.show_world(event_handler._world)  # Cập nhật lại màn hình
            elif self.menu_rect.collidepoint(event.pos):  
                self._help = True  
                self.show_world(event_handler._world)  

    def run(self, event_handler):  
        clock = pygame.time.Clock()  # Thêm vào đầu vòng lặp

        while not self._done: 
            clock.tick(60)  # Giữ FPS ở mức 60 
            self.run_once(event_handler)


    
class DisplayMSG:  
    def __init__(self, screen,sound_manager):  
        self.screen = screen  
        self.font = pygame.font.Font(None, 36)  
        self.level_images = {}  
        self.load_level_images()  
        self.sfx = sound_manager

    def load_level_images(self):  
        for level in range(1, 16):  
            image_path = f"./Images/MapImages/Level{level}.png"  
            try:  
                image = pygame.image.load(image_path) 
                image = pygame.transform.scale(image, (800,400))
                self.level_images[level] = image  
            except FileNotFoundError:  
                #print(f"Image for Level {level} not found!")  
                self.level_images[level] = pygame.Surface((600, 400)) 

    def show_loading_screen(self):
        self.sfx.play('menu',True) 
        self.sfx.set_volume(0.7)
        loading_img = pygame.image.load(r'./Images/loading.jpg')
        self.screen.fill((0, 0, 0))  
        self.screen.blit(loading_img,(0,0))
        loading_text = self.font.render("Loading Game...", True, (54, 35, 35)) 
        text_rect = loading_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 200))  
        self.screen.blit(loading_text, text_rect)  
        pygame.display.flip()  
        pygame.time.delay(2200) 

    def show_level_menu(self, selected_level):  
        self.screen.fill((0, 0, 0))  
        level_text = self.font.render(f"Level {selected_level}", True, (255, 255, 255))  
        text_rect = level_text.get_rect(center=(self.screen.get_width() // 2, 50))  
        self.screen.blit(level_text, text_rect)  

        level_image = self.level_images[selected_level]  
        image_rect = level_image.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))  
        self.screen.blit(level_image, image_rect)  

        instruction_text = self.font.render("Use LEFT/RIGHT to change level, ENTER to select", True, (255, 255, 255))  
        instruction_rect = instruction_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 50))  
        self.screen.blit(instruction_text, instruction_rect)  
        pygame.display.flip()  

    def show_end_MSG(self,game):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)  
        overlay.fill((0, 0, 0, 150))  
        if game.solution != "" and game.bot_play == False : text = " YOU WIN! "
        elif game.solution != "" and game.bot_play == True : text = f" BOT WIN! Algorithm used: {game.algorithm_choice}"
        else : text = " NO SLUTION! "
        end_text = self.font.render(text, True, (255, 255, 0))  
        text_rect = end_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))  
        instruction_text = self.font.render("ENTER to select level, ESC to exit, R to restart", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 20))
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(end_text, text_rect)
        self.screen.blit(instruction_text, instruction_rect)
        pygame.display.flip()
            
    def run_level_menu(self):  
        selected_level = 1  
        running = True  
        pygame.key.set_repeat(200, 100)  

        while running:  
            self.show_level_menu(selected_level)  

            for event in pygame.event.get():  
                if event.type == pygame.QUIT:  
                    running = False     
                    return None 

                elif event.type == pygame.KEYDOWN:  
                    if event.key == pygame.K_LEFT:  
                        self.sfx.play('select')        
                        selected_level = max(1, selected_level - 1)  
                    elif event.key == pygame.K_RIGHT:  
                        self.sfx.play('select')
                        selected_level = min(15, selected_level + 1)  
                    elif event.key == pygame.K_RETURN:  
                        return selected_level 

        return None  


class Sokoban:
    def __init__(self,filename,sound_manager):
        self._filename = filename  
        self._engine = GameEngine()
        self._view = GameView()
        self._view.load_images()
        self._world = World(filename)
        self.solution = ""
        self.steps = 0
        self.weight = 0
        self.node = 0
        self.time = 0
        self.memory = 0
        self.algorithm_choice = None
        self.bot_play = False
        self.sfx = sound_manager
    
    def run(self):
        self.sfx.stop('menu')
        self.sfx.play('background',True)
        self._view.setup_game(self._world)
        self._view.show_world(self._world)
        self._view.run(self)
    
    def _move(self, direction):
        self._engine.move(direction, self._world)
        self._view.show_world(self._world)

    def auto_move(self):
        if not self.solution:
            return None

        for c in self.solution:
            if c ==  'U' or c == 'u':
                self._move(Dir.UP)
            elif c == 'D' or c == 'd':
                self._move(Dir.DN)
            elif c == 'L' or c == 'l':
                self._move(Dir.LT)
            elif c == 'R' or c == 'r':
                self._move(Dir.RT)
            time.sleep(0.1)

    def write_output(self):
        filename = r'./Outputs/' + 'output-' + self._filename[-6:]
        with open(filename,"a") as f:
            f.write(f"Algorithm: {self.algorithm_choice} \n")
            f.write(f"Steps: {self.steps} \n")
            f.write(f"Weight: {self.weight} \n")
            f.write(f"Node: {self.node} \n")
            f.write(f"Time (ms) : {self.time:.3f}  \n")
            f.write(f"Memory (MB): {self.memory:.2f}  \n")
            f.write(f"Solution: {self.solution} \n")
            f.write("\n")
            
    def solve_with_algorithm(self, algorithm_class, algorithm_name):
        new_grid = check_and_pad_map(self._world.grid)
        solver = algorithm_class(
            new_grid,
            tuple(self._world.player_pos[0]),
            [tuple(pos) for pos in self._world.boxes],
            [tuple(pos) for pos in self._world.goals],
            self._world.stone_weights
        )
        tracemalloc.start()
        start_time = time.perf_counter()
        node_generated, total_weight, solution = solver.runner()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        end_time = time.perf_counter()
        if solution != "NoSol" and solution != None:
            self.bot_play = True
            self. algorithm_choice =  algorithm_name
            self.steps = len(solution)
            self.weight = total_weight
            self.node = node_generated
            self.time = (end_time - start_time)*1000
            self.memory = peak/(1024**2)
            self.solution = solution
            self.write_output()
            self.auto_move()
        else:
            display_msg = DisplayMSG(self._view._screen,self.sfx)
            display_msg.show_end_MSG(self)

    def handle_key(self, key):
        if key == Key.QUIT:
            self._view.quit()
            pygame.quit()
            sys.exit()
        elif key == Key.UP:
            self._move(Dir.UP)
        elif key == Key.RIGHT:
            self._move(Dir.RT)
        elif key == Key.LEFT:
            self._move(Dir.LT)
        elif key == Key.DOWN:
            self._move(Dir.DN)
        elif key == 'RESET':
            self.reset_game()
        elif key == 'ECS':
            self.sfx.stop('background')
            global run_once
            if run_once: run_once = False
            waiting = False
            pygame.display.quit()  
            pygame.init()  
            main_menu()
        elif key in ['BFS', 'DFS', 'UCS', 'ASTAR', 'GBFS', 'Dijkstra']:
            algorithm_map = {
                'BFS': BFS.BFS,
                'DFS': DFS.DFS,
                'UCS': UCS.UCS,
                'ASTAR': ASTAR.ASTAR,
                'GBFS': GBFS.GBFS,  
                'Dijkstra': Dijkstra.Dijkstra,
            }
            self.solve_with_algorithm(algorithm_map[key],key)

        if self._engine.is_game_over(self._world):
            display_msg = DisplayMSG(self._view._screen,self.sfx)
            display_msg.show_end_MSG(self)
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.sfx.stop('background')
                            if run_once:
                                run_once = False
                            waiting = False
                            pygame.display.quit()
                            pygame.init()
                            main_menu()
                        elif event.key == pygame.K_ESCAPE:
                            self.sfx.stop('background')
                            pygame.quit()
                            sys.exit()
                            main_menu()
                        elif event.key == pygame.K_r:
                            self.reset_game()


    def reset_game(self):
        self.sfx.stop('background')
        self._world = World(self._filename)  
        self.solution = ""       
        self.cost = 0       
        self.steps = 0      
        self.algorithm_choice = None 
        self.bot_play = False
        self.run()

class sfx:
    def __init__(self):
        pygame.mixer.init()
        self.Sound = {
            'menu': pygame.mixer.Sound(r'./Sound/menu.wav'),
            'select': pygame.mixer.Sound(r'./Sound/select.wav'),
            'background': pygame.mixer.Sound(r'./Sound/background.mp3'),
            'win': pygame.mixer.Sound(r'./Sound/win.mp3')
        }

    def play(self, sound_name, loop=False):
        if sound_name in self.Sound:
            if loop:
                self.Sound[sound_name].play(-1) 
            else:
                self.Sound[sound_name].play()

    def stop(self, sound_name):
        if sound_name in self.Sound:
            self.Sound[sound_name].stop()

    def set_volume(self, volume):
        for sound in self.Sound.values():
            sound.set_volume(volume)

def check_and_pad_map(grid):
    """
    Đảm bảo tất cả các dòng của grid có cùng số cột.
    Nếu dòng nào thiếu, ta sẽ thêm '#' hoặc ' ' (tuỳ ý)
    để tránh bị lỗi index khi truy cập grid[x][y].
    """
    max_len = max(len(row) for row in grid)
    new_grid = []
    for row in grid:
        # Nếu row đang là list, ta nối lại thành string
        # Trường hợp row đã là string thì không cần đổi
        # Tuỳ theo cách MapLoader bạn cài đặt
        if len(row) < max_len:
            row += "#" * (max_len - len(row))  # hoặc ' ' 
        new_grid.append(row)
    return new_grid


def main_menu():
    pygame.init() 
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Sokoban - Amazing Puzzle Game")
    pygame.display.set_icon(icon)
    sound_manager = sfx()
    display_msg = DisplayMSG(screen,sound_manager)
    sound_manager.play('menu', True)
    if run_once:
        display_msg.show_loading_screen()  
    while True:
        selected_level = display_msg.run_level_menu()  

        if selected_level:
            filename = f"./Inputs/input-{selected_level:02d}.txt"
            sokoban = Sokoban(filename,sound_manager)  
            sokoban.run()
        else:
            print("Game exited.")
            pygame.quit()
            sys.exit()

if __name__ == "__main__":  
    main_menu()
