import pygame
import sys
import time
import json

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = pygame.display.Info().current_w
SCREEN_HEIGHT = pygame.display.Info().current_h

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
YELLOW = (255, 255, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Cityfields Simulator 2025")

# Clock to control the frame rate
clock = pygame.time.Clock()

# City grid dimensions
CELL_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

# Building types and build times (in seconds)
BUILDING_TYPES = {
    "house": GREEN,
    "office": BLUE,
    "shop": RED,
    "road": GRAY
}
BUILD_TIMES = {
    "house": 15,
    "office": 20,
    "shop": 30
}
current_building = "house"

# City grid
city_grid = [["" for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
building_times = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Game mode
building_mode = True
game_started = False
loading_game = False

# Economy
money = 1000
guests = 0
guest_happiness = 100
player_level = 1
player_exp = 0
exp_to_level_up = 100
GUESTS_PER_BUILDING = {
    "house": 5,
    "office": 10,
    "shop": 15
}
MONEY_PER_GUEST = 1

# Save message and timer
save_message = ""
save_timer = 0

# Function to draw buildings with a 3D effect
def draw_building(screen, color, rect, construction=False):
    pygame.draw.rect(screen, color, rect)
    if construction:
        pygame.draw.rect(screen, DARK_GRAY, (rect.x + 5, rect.y + 5, rect.width - 10, rect.height - 10))

# Function to calculate guest happiness
def calculate_happiness(city_grid):
    building_count = sum(1 for row in city_grid for building in row if building and building != "road")
    return min(100, building_count * 2)  # Happiness increases with more buildings, max 100%

# Function to level up the player
def level_up(player_level, player_exp, exp_to_level_up):
    if player_exp >= exp_to_level_up:
        player_level += 1
        player_exp -= exp_to_level_up
        exp_to_level_up *= 1.5  # Increase the required experience for the next level
    return player_level, player_exp, exp_to_level_up

# Function to draw the main menu
def draw_main_menu():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    title_text = font.render("Cityfields Simulator 2025", True, BLACK)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4))

    button_font = pygame.font.Font(None, 50)
    button_text = button_font.render("New game", True, WHITE)
    button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 60)
    pygame.draw.rect(screen, BLACK, button_rect)
    screen.blit(button_text, (button_rect.x + (button_rect.width - button_text.get_width()) // 2, button_rect.y + (button_rect.height - button_text.get_height()) // 2))

    load_button_text = button_font.render("Load game", True, WHITE)
    load_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 60)
    pygame.draw.rect(screen, BLACK, load_button_rect)
    screen.blit(load_button_text, (load_button_rect.x + (load_button_rect.width - load_button_text.get_width()) // 2, load_button_rect.y + (load_button_rect.height - load_button_text.get_height()) // 2))

    pygame.display.flip()

# Function to save the game state
def save_game():
    global save_message, save_timer
    game_state = {
        "city_grid": city_grid,
        "money": money,
        "guests": guests,
        "guest_happiness": guest_happiness,
        "player_level": player_level,
        "player_exp": player_exp,
        "exp_to_level_up": exp_to_level_up
    }
    with open("savegame.json", "w") as save_file:
        json.dump(game_state, save_file)
    save_message = "Savegame is saving... Please do not turn off your device"
    save_timer = time.time() + 2  # Show message for 2 seconds

# Function to load the game state
def load_game():
    global city_grid, money, guests, guest_happiness, player_level, player_exp, exp_to_level_up
    try:
        with open("savegame.json", "r") as load_file:
            game_state = json.load(load_file)
            city_grid = game_state["city_grid"]
            money = game_state["money"]
            guests = game_state["guests"]
            guest_happiness = game_state["guest_happiness"]
            player_level = game_state["player_level"]
            player_exp = game_state["player_exp"]
            exp_to_level_up = game_state["exp_to_level_up"]
    except FileNotFoundError:
        print("No savegame found")

# Game loop flag
running = True

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_building = "house"
            elif event.key == pygame.K_2:
                current_building = "office"
            elif event.key == pygame.K_3:
                current_building = "shop"
            elif event.key == pygame.K_4:
                current_building = "road"
            elif event.key == pygame.K_p:
                building_mode = not building_mode
            elif event.key == pygame.K_s:
                save_game()
            elif event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_started:
            mouse_x, mouse_y = event.pos
            if SCREEN_WIDTH // 2 - 100 <= mouse_x <= SCREEN_WIDTH // 2 + 100 and SCREEN_HEIGHT // 2 <= mouse_y <= SCREEN_HEIGHT // 2 + 60:
                game_started = True
            elif SCREEN_WIDTH // 2 - 100 <= mouse_x <= SCREEN_WIDTH // 2 + 100 and SCREEN_HEIGHT // 2 + 80 <= mouse_y <= SCREEN_HEIGHT // 2 + 140:
                load_game()
                game_started = True

        elif event.type == pygame.MOUSEBUTTONDOWN and game_started and building_mode:
            mouse_x, mouse_y = event.pos
            col = mouse_x // CELL_SIZE
            row = mouse_y // CELL_SIZE
            if 0 <= col < GRID_WIDTH and 0 <= row < GRID_HEIGHT:
                if current_building in BUILD_TIMES:
                    building_times[row][col] = time.time() + BUILD_TIMES[current_building]
                else:
                    city_grid[row][col] = current_building

    if not game_started:
        draw_main_menu()
        continue

    # Update building construction progress
    current_time = time.time()
    construction_in_progress = False
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            if building_times[row][col]:
                if current_time >= building_times[row][col]:
                    city_grid[row][col] = current_building
                    building_times[row][col] = None
                    if current_building in GUESTS_PER_BUILDING:
                        guests += GUESTS_PER_BUILDING[current_building]
                        player_exp += GUESTS_PER_BUILDING[current_building] * 10  # Gain experience for building
                else:
                    construction_in_progress = True

    # Calculate guest happiness
    guest_happiness = calculate_happiness(city_grid)

    # Update player level
    player_level, player_exp, exp_to_level_up = level_up(player_level, player_exp, exp_to_level_up)

    # Update money based on guests and happiness
    if guest_happiness >= 20:
        money += guests * MONEY_PER_GUEST * (guest_happiness / 100) * (1 + (player_level - 1) * 0.1) * clock.get_time() / 1000

    # Update the game state
    screen.fill(WHITE)

    # Draw city grid
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)
            if city_grid[row][col]:
                building_color = BUILDING_TYPES[city_grid[row][col]]
                if building_mode or city_grid[row][col] != "road":
                    draw_building(screen, building_color, rect, construction=False)
                else:
                    draw_building(screen, building_color, rect, construction=True)
                if not building_mode and city_grid[row][col] == "road":
                    pygame.draw.line(screen, YELLOW, (rect.x, rect.y + rect.height // 2), (rect.x + rect.width, rect.y + rect.height // 2), 2)
            elif building_times[row][col]:
                pygame.draw.rect(screen, GRAY, rect, 0)

    # Display the current building type, mode, money, guests, guest happiness, and player level
    font = pygame.font.Font(None, 36)
    if building_mode:
        text = font.render(f"Current building: {current_building}", True, BLACK)
    else:
        text = font.render("Preview Mode", True, BLACK)
    screen.blit(text, (10, SCREEN_HEIGHT - 40))

    stats_text = font.render(f"Money: ${int(money)}  Guests: {guests}  Happiness: {int(guest_happiness)}%  Level: {player_level}  Exp: {int(player_exp)}", True, BLACK)
    screen.blit(stats_text, (10, SCREEN_HEIGHT - 80))

    # Display construction progress message
    if construction_in_progress:
        construction_text = font.render("Construction in progress", True, BLACK)
        screen.blit(construction_text, (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 40))

    # Display save message
    if save_message and time.time() < save_timer:
        save_text = font.render(save_message, True, RED)
        screen.blit(save_text, (SCREEN_WIDTH // 2 - save_text.get_width() // 2, SCREEN_HEIGHT // 2 - save_text.get_height() // 2))
    elif time.time() >= save_timer:
        save_message = ""

    # Refresh the screen
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Clean up
pygame.quit()
sys.exit()
