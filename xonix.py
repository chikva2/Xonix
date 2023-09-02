import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1400, 900
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Xonix Game")
GRID_SIZE = 20
ROWS, COLS = HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE
player_pos = [ROWS - 1, COLS // 2]
enemies = [[0, COLS // 2], [ROWS // 2, COLS // 2]]
enemy_directions = [[random.choice([-1, 1]), random.choice([-1, 1])] for _ in range(2)]
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
score = 0
lives = 3
half_conquered = []
last_conquered_pos = [ROWS - 1, COLS // 2]
# Initialize level
current_level = 1

# Initialize conquered territories
for i in range(ROWS):
    for j in range(COLS):
        if i < 2 or i > ROWS - 3 or j < 2 or j > COLS - 3:
            grid[i][j] = 1

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Function to flood fill unconquered territories
def flood_fill(x, y, visited):
    stack = [(x, y)]
    size = 0
    while stack:
        x, y = stack.pop()
        if x < 0 or x >= ROWS or y < 0 or y >= COLS:
            continue
        if visited[x][y] or grid[x][y] != 0:
            continue
        visited[x][y] = True
        size += 1
        stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
    return size

# Main Loop
run = True
while run:
    pygame.time.delay(100)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_pos[1] = max(0, player_pos[1] - 1)
    if keys[pygame.K_RIGHT]:
        player_pos[1] = min(COLS - 1, player_pos[1] + 1)
    if keys[pygame.K_UP]:
        player_pos[0] = max(0, player_pos[0] - 1)
    if keys[pygame.K_DOWN]:
        player_pos[0] = min(ROWS - 1, player_pos[0] + 1)
    
    # Update enemy positions
    for i, enemy in enumerate(enemies):
        dx, dy = enemy_directions[i]
        new_x, new_y = enemy[0] + dx, enemy[1] + dy
        
        # Collision check
        if i == 0:  # Enemy type one
            if new_x < 0 or new_x >= ROWS or grid[new_x][enemy[1]] == 0:
                dx = -dx
            if new_y < 0 or new_y >= COLS or grid[enemy[0]][new_y] == 0:
                dy = -dy
        else:  # Enemy type two
            if grid[new_x][enemy[1]] == 1:
                dx = -dx
            if grid[enemy[0]][new_y] == 1:
                dy = -dy
                
        enemy_directions[i] = [dx, dy]
        enemy[0] += dx
        enemy[1] += dy

    # Collision detection
    if player_pos in enemies:
        print("Game Over!")
        run = False

    # Territory conquering
    if grid[player_pos[0]][player_pos[1]] == 1:
        last_conquered_pos = player_pos.copy()
        for pos in half_conquered:
            grid[pos[0]][pos[1]] = 1
            score += 1
        half_conquered.clear()

        # Insert the new code snippet here
        # Flood fill to find isolated territories
        visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
        flood_fill(enemies[1][0], enemies[1][1], visited)

        # Conquer isolated territories
        for i in range(ROWS):
            for j in range(COLS):
                if not visited[i][j] and grid[i][j] == 0:
                    grid[i][j] = 1
                    score += 1

        if score >= 2000 * current_level:
            current_level += 1
            # Add new enemy of type 2 at a random position in unconquered territory
            while True:
                new_enemy = [random.randint(0, ROWS-1), random.randint(0, COLS-1)]
                if grid[new_enemy[0]][new_enemy[1]] == 0:
                    enemies.append(new_enemy)
                    enemy_directions.append([random.choice([-1, 1]), random.choice([-1, 1])])
                    break
    else:
        half_conquered.append(player_pos.copy())
        grid[player_pos[0]][player_pos[1]] = 0.5

    # Check if enemy type two hits half-conquered territory
    if enemies[1] in half_conquered:
        for pos in half_conquered:
            grid[pos[0]][pos[1]] = 0
        half_conquered.clear()
        player_pos = last_conquered_pos.copy()
        lives -= 1
        if lives == 0:
            print("Game Over!")
            run = False

    # Draw Grid and captured territory
    win.fill(BLACK)
    for i in range(ROWS):
        for j in range(COLS):
            color = BLUE if grid[i][j] == 1 else ORANGE if grid[i][j] == 0.5 else WHITE
            pygame.draw.rect(win, color, (j*GRID_SIZE, i*GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
    
    # Draw Player
    pygame.draw.rect(win, GREEN, (player_pos[1]*GRID_SIZE, player_pos[0]*GRID_SIZE, GRID_SIZE, GRID_SIZE))
    
    # Draw Enemies
    pygame.draw.rect(win, RED, (enemies[0][1]*GRID_SIZE, enemies[0][0]*GRID_SIZE, GRID_SIZE, GRID_SIZE))
    pygame.draw.circle(win, YELLOW, (enemies[1][1]*GRID_SIZE + GRID_SIZE//2, enemies[1][0]*GRID_SIZE + GRID_SIZE//2), GRID_SIZE//2)
    
    # Display Score and Lives
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f'Score: {score}', True, WHITE)
    lives_text = font.render(f'Lives: {lives}', True, WHITE)
    win.blit(score_text, (10, 10))
    win.blit(lives_text, (WIDTH - 100, 10))

    pygame.display.update()

pygame.quit()
