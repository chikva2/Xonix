# xonix_logic.py - Game logic for Xonix

import random

class GameConfig:
    def __init__(self, view='modern', size='small'):
        self.view = view
        self.size = size
        
        # Game settings based on size
        if self.size == 'small':
            self.UNITS_TO_WIN = 200
            self.UNIT_SIZE = 35
            self.GAME_LOGIC_AREA_WIDTH = 30
            self.GAME_LOGIC_AREA_HEIGHT = 18
            self.GAME_SPEED_ADJUSTMENT = 7
            self.SCORE_FONT_SIZE = self.UNIT_SIZE
            self.MESSAGE_FONT_SIZE = self.UNIT_SIZE * 3
        else:  # 'big'
            self.UNITS_TO_WIN = 1000
            self.UNIT_SIZE = 21
            self.GAME_LOGIC_AREA_WIDTH = 51
            self.GAME_LOGIC_AREA_HEIGHT = 34
            self.GAME_SPEED_ADJUSTMENT = 12
            self.SCORE_FONT_SIZE = int(self.UNIT_SIZE * 1.5)
            self.MESSAGE_FONT_SIZE = self.UNIT_SIZE * 4
        
        # Common settings
        self.DEBUG = False
        
        # Constants
        self.SCORE_SPACE = self.UNIT_SIZE * 2
        self.GAME_AREA_WIDTH = self.GAME_LOGIC_AREA_WIDTH * self.UNIT_SIZE
        self.GAME_AREA_HEIGHT = self.GAME_LOGIC_AREA_HEIGHT * self.UNIT_SIZE
        self.SCREEN_WIDTH = self.GAME_AREA_WIDTH
        
        # Adjust SCREEN_HEIGHT based on DEBUG status
        if self.DEBUG:
            self.DEBUG_SPACE = self.UNIT_SIZE * 12
        else:
            self.DEBUG_SPACE = 0
            
        self.SCREEN_HEIGHT = self.GAME_AREA_HEIGHT + self.SCORE_SPACE + self.DEBUG_SPACE
        self.PLAYER_SPEED = self.UNIT_SIZE
        self.ENEMY_SPEED = self.UNIT_SIZE
        
        # Game field state constants
        self.GAME_FIELD_UNFILLED = 0
        self.GAME_FIELD_FILLED = 1
        self.GAME_FIELD_LINE = 2
        self.GAME_FIELD_PLAYER = 3
        self.GAME_FIELD_ENEMY_U = 4
        self.GAME_FIELD_ENEMY_F = 5
        self.GAME_FIELD_TEMP_FILLED = 6

class GameState:
    def __init__(self, config):
        self.config = config
        self.lives = 5
        self.score = 0
        self.filled_units = 0
        self.level = 1
        self.game_field = None
        self.player = None
        self.enemies = []
        self.dx = 0
        self.dy = 0
        self.initialize_game_field()
        
    def initialize_game_field(self):
        # Reset game field
        self.game_field = [[self.config.GAME_FIELD_UNFILLED for _ in range(self.config.GAME_LOGIC_AREA_WIDTH)] 
                           for _ in range(self.config.GAME_LOGIC_AREA_HEIGHT)]
        
        # Fill borders
        for x in range(self.config.GAME_LOGIC_AREA_WIDTH):
            for y in range(2):  # Top two rows
                self.game_field[y][x] = self.config.GAME_FIELD_FILLED
            for y in range(self.config.GAME_LOGIC_AREA_HEIGHT - 2, self.config.GAME_LOGIC_AREA_HEIGHT):  # Bottom two rows
                self.game_field[y][x] = self.config.GAME_FIELD_FILLED
                
        for y in range(self.config.GAME_LOGIC_AREA_HEIGHT):
            for x in range(3):  # Left three columns
                self.game_field[y][x] = self.config.GAME_FIELD_FILLED
            for x in range(self.config.GAME_LOGIC_AREA_WIDTH - 3, self.config.GAME_LOGIC_AREA_WIDTH):  # Right three columns
                self.game_field[y][x] = self.config.GAME_FIELD_FILLED
    
    def initialize_enemies(self):
        # Create filled enemy at top middle
        self.enemies = [Enemy(self.config.GAME_AREA_WIDTH // 2, 0, 'filled', self.config)]
        
        # Create unfilled enemies based on current level
        for _ in range(self.level):
            x = random.randint(3, self.config.GAME_LOGIC_AREA_WIDTH - 4) * self.config.UNIT_SIZE
            y = random.randint(2, self.config.GAME_LOGIC_AREA_HEIGHT - 3) * self.config.UNIT_SIZE
            self.enemies.append(Enemy(x, y, 'unfilled', self.config))
    
    def reset_game(self):
        self.lives = 5
        self.score = 0
        self.filled_units = 0
        self.level = 1
        self.player = Player(self.config)
        self.initialize_enemies()
        self.initialize_game_field()
    
    def temp_flood_fill(self, start_pos, fill_value, boundary_values):
        x_size = len(self.game_field[0])
        y_size = len(self.game_field)
        queue = [start_pos]
        filled_area = []

        while queue:
            x, y = queue.pop(0)
            if not (0 <= x < x_size and 0 <= y < y_size) or self.game_field[y][x] in boundary_values:
                continue
            self.game_field[y][x] = fill_value
            filled_area.append((y, x))
            
            # Add adjacent cells to queue
            queue.append((x - 1, y))
            queue.append((x + 1, y))
            queue.append((x, y - 1))
            queue.append((x, y + 1))
                
        return filled_area
    
    def is_point_in_subarea(self, point, subarea):
        # Convert point to match subarea format (y, x)
        point_yx = (point[1], point[0])
        return point_yx in subarea
    
    def identify_subareas_starting_points(self, player_line):
        subareas_starting_points = set()  # Use a set to avoid duplicates
        
        # Find points adjacent to the player's line
        for point in player_line:
            adjacent_points = [
                (point[0] + 1, point[1]),  # Right
                (point[0] - 1, point[1]),  # Left
                (point[0], point[1] + 1),  # Down
                (point[0], point[1] - 1)   # Up
            ]
            
            for adj_point in adjacent_points:
                x, y = adj_point
                if 0 <= x < self.config.GAME_LOGIC_AREA_WIDTH and 0 <= y < self.config.GAME_LOGIC_AREA_HEIGHT:
                    if self.game_field[y][x] == self.config.GAME_FIELD_UNFILLED:
                        subareas_starting_points.add(adj_point)
                        
        return list(subareas_starting_points)
    
    def handle_area_filling(self):
        if self.player.returned_to_filled_area:
            subareas_start_positions = self.identify_subareas_starting_points(self.player.line)
            
            while subareas_start_positions:
                start_pos = subareas_start_positions.pop(0)
                sub_area = self.temp_flood_fill(start_pos, self.config.GAME_FIELD_TEMP_FILLED, 
                                               boundary_values=[self.config.GAME_FIELD_FILLED, self.config.GAME_FIELD_TEMP_FILLED])
                
                if all(not self.is_point_in_subarea((enemy.x // self.config.UNIT_SIZE, enemy.y // self.config.UNIT_SIZE), sub_area) 
                       for enemy in self.enemies if enemy.type == 'unfilled'):
                    # No enemies in this subarea, fill it
                    self.score += len(sub_area)
                    self.filled_units += len(sub_area)
                    for y, x in sub_area:
                        self.game_field[y][x] = self.config.GAME_FIELD_FILLED
                else:
                    # Enemies found, revert to unfilled
                    for y, x in sub_area:
                        self.game_field[y][x] = self.config.GAME_FIELD_UNFILLED
                        
            self.player.line.clear()
    
    def handle_player_movement(self, keys_pressed):
        self.dx, self.dy = 0, 0
        
        if keys_pressed[0]:  # LEFT
            self.dx = -1
        elif keys_pressed[1]:  # RIGHT
            self.dx = 1
        elif keys_pressed[2]:  # UP
            self.dy = -1
        elif keys_pressed[3]:  # DOWN
            self.dy = 1
            
        if self.dx != 0 or self.dy != 0:
            self.player.move(self.dx, self.dy, self.game_field, self)
        elif self.player.needs_snapping():
            self.player.snap_to_grid_stopped(self.dx, self.dy)
        else:
            self.player.moving = False
            self.player.movement_direction = None
    
    def handle_collisions(self):
        player_grid_x = self.player.x // self.config.UNIT_SIZE
        player_grid_y = self.player.y // self.config.UNIT_SIZE
        
        # Check enemy collisions
        for enemy in self.enemies:
            enemy.move(self.game_field)
            enemy_grid_x = enemy.x // self.config.UNIT_SIZE
            enemy_grid_y = enemy.y // self.config.UNIT_SIZE
            
            # Player and enemy collision
            if player_grid_x == enemy_grid_x and player_grid_y == enemy_grid_y:
                if enemy.type == 'filled':
                    # Collision with filled enemy (wolf)
                    self.lives -= 1
                    self.player.reset_position()
                    enemy.x = self.config.GAME_AREA_WIDTH // 2
                    enemy.x = enemy.x - (enemy.x % self.config.UNIT_SIZE)
                    enemy.y = 0
                    return True
                elif enemy.type == 'unfilled' and self.game_field[player_grid_y][player_grid_x] == self.config.GAME_FIELD_UNFILLED:
                    # Collision with unfilled enemy (crocodile) in unfilled area
                    self.player.line.clear()
                    self.lives -= 1
                    self.player.reset_position()
                    return True
            elif enemy.type == 'unfilled':
                # Enemy colliding with player's line
                for position in self.player.line:
                    line_grid_x, line_grid_y = position[0], position[1]
                    if enemy_grid_x == line_grid_x and enemy_grid_y == line_grid_y:
                        self.player.line.clear()
                        self.lives -= 1
                        self.player.reset_position()
                        return True
        
        # Check for player colliding with own line
        for position in self.player.line[:-1]:  # Exclude the last line segment
            line_grid_x, line_grid_y = position[0], position[1]
            if player_grid_x == line_grid_x and player_grid_y == line_grid_y:
                self.lives -= 1
                self.player.reset_position()
                self.player.line.clear()
                return True
        
        return False
    
    def handle_level_up(self):
        if self.filled_units >= self.config.UNITS_TO_WIN:
            self.level += 1
            self.filled_units = 0
            
            # Reset for new level
            self.player.reset_position_new_level()
            self.player.line.clear()
            self.enemies.clear()
            self.initialize_enemies()
            self.initialize_game_field()
            return True
        
        return False

class Player:
    def __init__(self, config):
        self.config = config
        self.x = config.GAME_AREA_WIDTH // 2
        self.y = config.GAME_AREA_HEIGHT - 2 * config.UNIT_SIZE
        self.x = self.x - (self.x % config.UNIT_SIZE)  # Align to the nearest grid position on the left
        self.y = self.y - (self.y % config.UNIT_SIZE)  # Align to the nearest grid position on the top        
        self.width = config.UNIT_SIZE
        self.height = config.UNIT_SIZE
        self.start_x = self.x  # Starting x position
        self.start_y = self.y  # Starting y position
        self.line = []  # List to store the line positions
        self.movement_direction = None  # None, 'horizontal', or 'vertical'
        self.moving = False
        self.returned_to_filled_area = False

    def reset_position_new_level(self):
        self.x = self.config.GAME_AREA_WIDTH // 2
        self.y = self.config.GAME_AREA_HEIGHT - 2 * self.config.UNIT_SIZE
        self.x = self.x - (self.x % self.config.UNIT_SIZE)  # Align to the nearest grid position on the left
        self.y = self.y - (self.y % self.config.UNIT_SIZE)  # Align to the nearest grid position on the top
        self.start_x = self.x
        self.start_y = self.y

    def reset_position(self):
        self.x = self.start_x
        self.y = self.start_y

    def move(self, dx, dy, game_field, game_state):
        # Reset movement direction when player stops
        if dx == 0 and dy == 0:
            self.moving = False
            self.movement_direction = None
        else:
            self.moving = True

        self.returned_to_filled_area = False

        if self.moving:
            # Determine new direction if not already moving
            if self.movement_direction is None:
                if dx != 0:
                    self.movement_direction = 'horizontal'
                elif dy != 0:
                    self.movement_direction = 'vertical'

            # Restrict movement to the current direction
            if self.movement_direction == 'horizontal':
                dy = 0
            elif self.movement_direction == 'vertical':
                dx = 0

            new_x = self.x + dx * self.config.PLAYER_SPEED
            new_y = self.y + dy * self.config.PLAYER_SPEED
            new_x1 = max(0, min(new_x, self.config.GAME_AREA_WIDTH - self.width))
            new_y1 = max(0, min(new_y, self.config.GAME_AREA_HEIGHT - self.height))

            if(new_x != new_x1):
                new_x = new_x1
                self.movement_direction = None
                self.moving = False
                dx = 0
            if(new_y != new_y1):
                new_y = new_y1
                self.movement_direction = None
                self.moving = False
                dy = 0

            # Update the line if moving in an unfilled area
            self.update_line(new_x // self.config.UNIT_SIZE, new_y // self.config.UNIT_SIZE, game_field, game_state)
            self.x = new_x
            self.y = new_y

            if (self.movement_direction == 'horizontal' and abs(new_x - self.start_x) >= self.config.UNIT_SIZE) or \
               (self.movement_direction == 'vertical' and abs(new_y - self.start_y) >= self.config.UNIT_SIZE):
                self.movement_direction = None

    def needs_snapping(self):
        # Check if the player's position is not on a UNIT_SIZE grid
        off_grid_x = self.x % self.config.UNIT_SIZE != 0
        off_grid_y = self.y % self.config.UNIT_SIZE != 0
        return off_grid_x or off_grid_y

    # New logic to ensure movement completes to the nearest UNIT_SIZE boundary
    def snap_to_grid_stopped(self, dx, dy):
        # Calculate how much the player needs to move to align with UNIT_SIZE grid
        remainder_x = self.x % self.config.UNIT_SIZE
        remainder_y = self.y % self.config.UNIT_SIZE
        self.moving = False

        if remainder_x != 0:
            if dx > 0:  # Moving right
                self.x += (self.config.UNIT_SIZE - remainder_x)
            else:
                self.x -= remainder_x

        if remainder_y != 0:
            if dy > 0:  # Moving down
                self.y += (self.config.UNIT_SIZE - remainder_y)
            else:
                self.y -= remainder_y

    def update_line(self, new_x, new_y, game_field, game_state):
        if game_field[new_y][new_x] == self.config.GAME_FIELD_UNFILLED:  # Check if in unfilled area
            # Add the coordinate to the line based on movement direction
            if self.movement_direction == 'horizontal':
                self.line.append((new_x, self.y // self.config.UNIT_SIZE))
            elif self.movement_direction == 'vertical':
                self.line.append((self.x // self.config.UNIT_SIZE, new_y))
        else:
            # Player returns to a filled area, check if the line is not empty
            if self.line:
                # Iterate through the line positions and mark them as filled
                for (lx, ly) in self.line:
                    game_field[ly][lx] = self.config.GAME_FIELD_FILLED
                # Increase the score by the number of items in the line
                game_state.score += len(self.line)
                game_state.filled_units += len(self.line) 
                # Set flag for flood fill algorithm
                self.returned_to_filled_area = True
            self.start_x = new_x * self.config.UNIT_SIZE
            self.start_y = new_y * self.config.UNIT_SIZE

class Enemy:
    def __init__(self, x, y, type, config):
        self.config = config
        self.x = x - (x % config.UNIT_SIZE)  # Align to the nearest grid position on the left
        self.y = y - (y % config.UNIT_SIZE)  # Align to the nearest grid position on the top
        self.type = type
        self.dx = config.ENEMY_SPEED if random.random() < 0.5 else -config.ENEMY_SPEED
        self.dy = config.ENEMY_SPEED if random.random() < 0.5 else -config.ENEMY_SPEED

    def move(self, game_field):
        new_x = self.x + self.dx
        new_y = self.y + self.dy

        # Ensure new_x and new_y are within the boundaries of the game field
        if not (0 <= new_x <= self.config.GAME_AREA_WIDTH - self.config.UNIT_SIZE):
            self.dx = -self.dx
            new_x = self.x + self.dx  # Update new_x after changing direction
        if not (0 <= new_y <= self.config.GAME_AREA_HEIGHT - self.config.UNIT_SIZE):
            self.dy = -self.dy
            new_y = self.y + self.dy  # Update new_y after changing direction

        # Check if the new position is within a filled area
        # Adjust rejection logic based on enemy type
        if self.type == 'unfilled':
            restricting_type = self.config.GAME_FIELD_FILLED
        elif self.type == 'filled':
            restricting_type = self.config.GAME_FIELD_UNFILLED

        # Predictive collision detection
        grid_x = new_x // self.config.UNIT_SIZE
        grid_y = new_y // self.config.UNIT_SIZE
        next_grid_x = (new_x + self.config.UNIT_SIZE - 1) // self.config.UNIT_SIZE
        next_grid_y = (new_y + self.config.UNIT_SIZE - 1) // self.config.UNIT_SIZE

        next_grid_x_check = next_grid_x
        if(self.dx < 0):
            next_grid_x_check = grid_x
        next_grid_y_check = next_grid_y
        if(self.dy < 0):
            next_grid_y_check = grid_y

        will_collide_x = game_field[self.y // self.config.UNIT_SIZE][next_grid_x_check] == restricting_type
        will_collide_y = game_field[next_grid_y_check][self.x // self.config.UNIT_SIZE] == restricting_type

        if (will_collide_x == False and will_collide_y == False):
            will_collide_y = will_collide_x = game_field[next_grid_y_check][next_grid_x_check] == restricting_type

        if will_collide_x:
            self.dx = -self.dx
        else:
            self.x = new_x

        if will_collide_y:
            self.dy = -self.dy
        else:
            self.y = new_y