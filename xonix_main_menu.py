# xonix_main_menu.py - Main menu and launcher for Xonix game

import pygame
import sys
import subprocess

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Xonix Game - Main Menu")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLUE = (64, 164, 223)
GREEN = (34, 139, 34)
HIGHLIGHT_COLOR = (255, 165, 0)

# Font setup
title_font = pygame.font.SysFont(None, 80)
button_font = pygame.font.SysFont(None, 40)
info_font = pygame.font.SysFont(None, 30)

# Button class for menu options
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.highlighted = False
        
    def draw(self, surface):
        # Draw button background
        color = HIGHLIGHT_COLOR if self.highlighted else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)  # Border
        
        # Draw button text
        text_surf = button_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, mouse_pos):
        self.highlighted = self.rect.collidepoint(mouse_pos)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.highlighted and self.action:
                return self.action
        return None

# Create menu buttons
def create_buttons():
    buttons = []
    button_width = 200
    button_height = 60
    margin = 20
    start_y = SCREEN_HEIGHT // 2 - 50
    
    # Game size buttons
    buttons.append(Button(SCREEN_WIDTH // 4 - button_width // 2, start_y, 
                         button_width, button_height, "Small", lambda: set_game_option('size', 'small')))
    
    buttons.append(Button(3 * SCREEN_WIDTH // 4 - button_width // 2, start_y, 
                         button_width, button_height, "Big", lambda: set_game_option('size', 'big')))
    
    # Game view buttons
    buttons.append(Button(SCREEN_WIDTH // 4 - button_width // 2, start_y + button_height + margin, 
                         button_width, button_height, "Classic", lambda: set_game_option('view', 'classic')))
    
    buttons.append(Button(3 * SCREEN_WIDTH // 4 - button_width // 2, start_y + button_height + margin, 
                         button_width, button_height, "Modern", lambda: set_game_option('view', 'modern')))
    
    # Start game button
    buttons.append(Button(SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + margin) + 20, 
                         button_width, button_height, "Start Game", start_game))
    
    return buttons

# Game options
game_options = {
    'size': 'small',
    'view': 'classic'
}

def set_game_option(option, value):
    game_options[option] = value
    return None

def start_game():
    # Update the game_mode in xonix_gui.py
    update_game_mode_in_file()
    
    # Launch the game
    try:
        pygame.quit()  # Close the menu window
        subprocess.run(["python", "xonix_gui.py"])
        pygame.init()  # Reinitialize pygame when returning to menu
        pygame.font.init()
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception as e:
        print(f"Error launching game: {e}")
    return None

def update_game_mode_in_file():
    try:
        # Read the xonix_gui.py file
        with open("xonix_gui.py", "r") as file:
            content = file.readlines()
        
        # Find the GAME_MODE definition and update it
        for i, line in enumerate(content):
            if "GAME_MODE = {" in line:
                # Update the view and size settings
                content[i+1] = f"    'view': '{game_options['view']}',  # 'classic' or 'modern'\n"
                content[i+2] = f"    'size': '{game_options['size']}'    # 'small' or 'big'\n"
                break
        
        # Write the updated content back to the file
        with open("xonix_gui.py", "w") as file:
            file.writelines(content)
            
    except Exception as e:
        print(f"Error updating game mode: {e}")

def draw_title():
    title_surf = title_font.render("XONIX", True, WHITE)
    subtitle_surf = button_font.render("Choose Your Game Options", True, BLUE)
    
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 120))
    subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, 180))
    
    screen.blit(title_surf, title_rect)
    screen.blit(subtitle_surf, subtitle_rect)

def draw_option_labels():
    # Size label
    size_text = info_font.render("Game Size:", True, WHITE)
    screen.blit(size_text, (SCREEN_WIDTH // 2 - size_text.get_width() // 2, SCREEN_HEIGHT // 2 - 90))
    
    # View label
    view_text = info_font.render("Game View:", True, WHITE)
    screen.blit(view_text, (SCREEN_WIDTH // 2 - view_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
    
    # Current selection
    selected_text = info_font.render(f"Current Selection: {game_options['size'].capitalize()} - {game_options['view'].capitalize()}", True, GREEN)
    screen.blit(selected_text, (SCREEN_WIDTH // 2 - selected_text.get_width() // 2, SCREEN_HEIGHT - 50))

def draw_instructions():
    instructions = [
        "How to Play:",
        "- Use arrow keys to move",
        "- Claim territory by drawing lines and returning to your territory",
        "- Avoid enemies and your own trail",
        "- Fill 75% of the screen to advance to the next level"
    ]
    
    start_y = SCREEN_HEIGHT - 180
    for i, line in enumerate(instructions):
        text_surf = info_font.render(line, True, WHITE)
        screen.blit(text_surf, (20, start_y + i * 25))

def main_menu():
    buttons = create_buttons()
    running = True
    
    while running:
        screen.fill(BLACK)
        
        # Draw title and labels
        draw_title()
        draw_option_labels()
        draw_instructions()
        
        # Handle events
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.check_hover(mouse_pos)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
                
            for button in buttons:
                result = button.handle_event(event)
                if result:
                    result()
        
        # Draw buttons
        for button in buttons:
            button.draw(screen)
            
        pygame.display.flip()
        pygame.time.Clock().tick(30)

if __name__ == "__main__":
    main_menu()