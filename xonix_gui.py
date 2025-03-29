# xonix_gui.py - GUI and main game loop for Xonix

import pygame
import sys
import xonix_logic

# Initialize Pygame
pygame.init()
pygame.font.init()

# Game configuration
GAME_MODE = {
    'view': 'modern',  # 'classic' or 'modern'
    'size': 'big'    # 'small' or 'big'
}

# Create game config and state
config = xonix_logic.GameConfig(GAME_MODE['view'], GAME_MODE['size'])
game_state = xonix_logic.GameState(config)

# Setup the screen
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Xonix Game - " + GAME_MODE['view'].capitalize() + " " + GAME_MODE['size'].capitalize())
game_area = pygame.Surface((config.GAME_AREA_WIDTH, config.GAME_AREA_HEIGHT))

# Colors
GRAY = (128, 128, 128)
WATER_BLUE = (64, 164, 223)
GRASS_GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Load images for modern mode
RABBIT_IMG = None
CROCODILE_IMG = None
WOLF_IMG = None
WATER_IMG = None
SAND_IMG = None

if GAME_MODE['view'] == 'modern':
    try:
        # Load images with error handling
        RABBIT_IMG = pygame.image.load('rabbit.png')
        RABBIT_IMG = pygame.transform.scale(RABBIT_IMG, (config.UNIT_SIZE, config.UNIT_SIZE))
        
        CROCODILE_IMG = pygame.image.load('crocodile.png')
        CROCODILE_IMG = pygame.transform.scale(CROCODILE_IMG, (config.UNIT_SIZE, config.UNIT_SIZE))
        
        WOLF_IMG = pygame.image.load('wolf.png')
        WOLF_IMG = pygame.transform.scale(WOLF_IMG, (config.UNIT_SIZE, config.UNIT_SIZE))

        WATER_IMG = pygame.image.load('water.png')
        WATER_IMG = pygame.transform.scale(WATER_IMG, (config.UNIT_SIZE, config.UNIT_SIZE))
        
        SAND_IMG = pygame.image.load('sand.png')
        SAND_IMG = pygame.transform.scale(SAND_IMG, (config.UNIT_SIZE, config.UNIT_SIZE))
    except Exception as e:
        print(f"Image loading error: {e}")
        print("Using fallback geometric shapes")
        # If images fail to load, fall back to classic mode
        GAME_MODE['view'] = 'classic'

# Font setup
font = pygame.font.SysFont(None, config.SCORE_FONT_SIZE)

# Initialize game state
game_state.player = xonix_logic.Player(config)
game_state.initialize_enemies()

# GUI Helper Functions
def clear_score_area():
    clear_rect = pygame.Rect(0, 0, config.GAME_AREA_WIDTH, config.UNIT_SIZE*2)
    screen.fill(BLACK, clear_rect)

def display_debug_info():
    # Clear debug area
    debug_area_rect = pygame.Rect(0, config.SCREEN_HEIGHT - config.DEBUG_SPACE, config.SCREEN_WIDTH, config.DEBUG_SPACE)
    screen.fill(BLACK, debug_area_rect)

    # Define debug variables
    debug_info = {
        'start X': game_state.player.start_x,
        'start Y': game_state.player.start_y,
        'Player Moving': game_state.player.moving,
        'movement_direction': game_state.player.movement_direction,
        'Line Size': len(game_state.player.line),
        'Line ': game_state.player.line,
    }

    # Calculate starting Y position
    start_y = config.SCREEN_HEIGHT - config.DEBUG_SPACE + 5

    # Display debug information
    for i, (name, value) in enumerate(debug_info.items()):
        name_surface = font.render(f'{name}:', True, WHITE)
        name_x = 10
        screen.blit(name_surface, (name_x, start_y + i * 30))

        value_surface = font.render(f'{value}', True, WHITE)
        value_x = config.SCREEN_WIDTH // 2 - value_surface.get_width() // 2
        screen.blit(value_surface, (value_x, start_y + i * 30))

def display_game_score_level_lives_etc():
    # Draw game area on screen
    screen.blit(game_area, (0, config.SCORE_SPACE))
    
    # Show debug info if enabled
    if config.DEBUG:
        display_debug_info()
    
    # Clear score area with black background
    pygame.draw.rect(screen, BLACK, (0, 0, config.SCREEN_WIDTH, config.SCORE_SPACE))
        
    # Display game stats with appropriate vertical positioning
    vertical_position = config.SCORE_SPACE // 2 - font.get_height() // 2
    
    # Create text surfaces with appropriate font size
    level_text = font.render(f'Level: {game_state.level}', True, WHITE)
    lives_text = font.render(f'Lives: {game_state.lives}', True, WHITE)
    score_text = font.render(f'Score: {game_state.score}', True, WHITE)
    filled_units_text = font.render(f'Filled: {game_state.filled_units}/{config.UNITS_TO_WIN}', True, WHITE)
    
    # Position text according to game size - calculate dynamically
    # to ensure proper spacing regardless of font size
    if GAME_MODE['size'] == 'small':
        total_width = level_text.get_width() + lives_text.get_width() + score_text.get_width() + filled_units_text.get_width()
        spacing = (config.SCREEN_WIDTH - total_width) // 5  # Divide remaining space by 5 (4 gaps + extra padding)
        
        x_position = spacing
        screen.blit(level_text, (x_position, vertical_position))
        
        x_position += level_text.get_width() + spacing
        screen.blit(lives_text, (x_position, vertical_position))
        
        x_position += lives_text.get_width() + spacing
        screen.blit(score_text, (x_position, vertical_position))
        
        x_position += score_text.get_width() + spacing
        screen.blit(filled_units_text, (x_position, vertical_position))
    else:  # 'big'
        # For big mode, similar approach but with different proportions
        total_width = level_text.get_width() + lives_text.get_width() + score_text.get_width() + filled_units_text.get_width()
        spacing = (config.SCREEN_WIDTH - total_width) // 5
        
        x_position = spacing
        screen.blit(level_text, (x_position, vertical_position))
        
        x_position += level_text.get_width() + spacing
        screen.blit(lives_text, (x_position, vertical_position))
        
        x_position += lives_text.get_width() + spacing
        screen.blit(score_text, (x_position, vertical_position))
        
        x_position += score_text.get_width() + spacing
        screen.blit(filled_units_text, (x_position, vertical_position))

def draw_game_field():
    # Fill background
    if GAME_MODE['view'] == 'modern':
        # Use water image tiles if available
        if WATER_IMG:
            for y in range(0, config.GAME_AREA_HEIGHT, config.UNIT_SIZE):
                for x in range(0, config.GAME_AREA_WIDTH, config.UNIT_SIZE):
                    game_area.blit(WATER_IMG, (x, y))
        else:
            game_area.fill(WATER_BLUE)
    else:  # classic
        game_area.fill(BLACK)
        
    # Draw borders
    color = GRAY
    pygame.draw.rect(game_area, color, (0, 0, config.GAME_AREA_WIDTH, 2 * config.UNIT_SIZE))  # Top
    pygame.draw.rect(game_area, color, (0, config.GAME_AREA_HEIGHT - 2 * config.UNIT_SIZE, config.GAME_AREA_WIDTH, 2 * config.UNIT_SIZE))  # Bottom
    pygame.draw.rect(game_area, color, (0, 0, 3 * config.UNIT_SIZE, config.GAME_AREA_HEIGHT))  # Left
    pygame.draw.rect(game_area, color, (config.GAME_AREA_WIDTH - 3 * config.UNIT_SIZE, 0, 3 * config.UNIT_SIZE, config.GAME_AREA_HEIGHT))  # Right
    
    # Draw filled areas
    for y in range(config.GAME_LOGIC_AREA_HEIGHT):
        for x in range(config.GAME_LOGIC_AREA_WIDTH):
            if game_state.game_field[y][x] == config.GAME_FIELD_FILLED:
                if GAME_MODE['view'] == 'modern' and SAND_IMG:
                    game_area.blit(SAND_IMG, (x * config.UNIT_SIZE, y * config.UNIT_SIZE))
                else:
                    fill_color = GRASS_GREEN if GAME_MODE['view'] == 'modern' else GRAY
                    pygame.draw.rect(game_area, fill_color, (x * config.UNIT_SIZE, y * config.UNIT_SIZE, config.UNIT_SIZE, config.UNIT_SIZE))
    
    # Draw player's line
    for position in game_state.player.line:
        pygame.draw.rect(game_area, GREEN, (position[0]*config.UNIT_SIZE+config.UNIT_SIZE/4, position[1]*config.UNIT_SIZE+config.UNIT_SIZE/4, config.UNIT_SIZE/2, config.UNIT_SIZE/2))
    
    # Draw player
    if GAME_MODE['view'] == 'modern' and RABBIT_IMG:
        game_area.blit(RABBIT_IMG, (game_state.player.x, game_state.player.y))
    else:
        pygame.draw.rect(game_area, WHITE, (game_state.player.x, game_state.player.y, game_state.player.width, game_state.player.height))
    
    # Draw enemies
    for enemy in game_state.enemies:
        if enemy.type == 'filled':
            # Wolf in modern mode, black box in classic
            if GAME_MODE['view'] == 'modern' and WOLF_IMG:
                game_area.blit(WOLF_IMG, (enemy.x, enemy.y))
            else:
                pygame.draw.rect(game_area, BLACK, (enemy.x, enemy.y, config.UNIT_SIZE, config.UNIT_SIZE))
        else:
            # Crocodile in modern mode, white circle in classic
            if GAME_MODE['view'] == 'modern' and CROCODILE_IMG:
                game_area.blit(CROCODILE_IMG, (enemy.x, enemy.y))
            else:
                pygame.draw.circle(game_area, WHITE, (enemy.x + config.UNIT_SIZE // 2, enemy.y + config.UNIT_SIZE // 2), config.UNIT_SIZE // 2, 1)

def display_game_over_message():
    # Use predefined MESSAGE_FONT_SIZE that scales with game size
    font_large = pygame.font.SysFont(None, config.MESSAGE_FONT_SIZE)
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Black with alpha (transparency)
    screen.blit(overlay, (0, 0))
    
    # Main message
    game_over_text = font_large.render("GAME OVER", True, RED)
    text_rect = game_over_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - config.MESSAGE_FONT_SIZE // 2))
    screen.blit(game_over_text, text_rect)
    
    # Secondary message with instruction
    font_small = pygame.font.SysFont(None, config.MESSAGE_FONT_SIZE // 2)
    continue_text = font_small.render("Starting New Game...", True, WHITE)
    continue_rect = continue_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + config.MESSAGE_FONT_SIZE // 2))
    screen.blit(continue_text, continue_rect)
    
    pygame.display.flip()
    pygame.time.delay(2000)

def display_level_up_message():
    # Use predefined MESSAGE_FONT_SIZE that scales with game size
    font_large = pygame.font.SysFont(None, config.MESSAGE_FONT_SIZE)
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Black with alpha (transparency)
    screen.blit(overlay, (0, 0))
    
    # Main message
    level_up_text = font_large.render(f"LEVEL {game_state.level-1} COMPLETED!", True, GREEN)
    text_rect = level_up_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - config.MESSAGE_FONT_SIZE // 2))
    screen.blit(level_up_text, text_rect)
    
    # Secondary message with next level information
    font_small = pygame.font.SysFont(None, config.MESSAGE_FONT_SIZE // 2)
    next_level_text = font_small.render(f"Starting Level {game_state.level}...", True, WHITE)
    next_level_rect = next_level_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + config.MESSAGE_FONT_SIZE // 2))
    screen.blit(next_level_text, next_level_rect)
    
    pygame.display.flip()
    pygame.time.delay(2000)

# Main game loop
def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        if game_state.lives <= 0:
            display_game_over_message()
            game_state.reset_game()
        
        # Get key states for player movement
        keys = pygame.key.get_pressed()
        keys_pressed = [
            keys[pygame.K_LEFT],
            keys[pygame.K_RIGHT],
            keys[pygame.K_UP],
            keys[pygame.K_DOWN]
        ]
        
        # Update game state
        game_state.handle_player_movement(keys_pressed)
        collision_occurred = game_state.handle_collisions()
        if collision_occurred:
            clear_score_area()
            pygame.time.delay(1000)
            
        game_state.handle_area_filling()
        
        # Draw everything
        draw_game_field()
        display_game_score_level_lives_etc()
        
        # Check for level completion
        if game_state.handle_level_up():
            display_level_up_message()
            clear_score_area()
            display_game_score_level_lives_etc()
        
        # Update display
        pygame.display.flip()
        pygame.time.Clock().tick(config.GAME_SPEED_ADJUSTMENT)

    # Quit the game
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()