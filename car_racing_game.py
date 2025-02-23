import pygame
import buttons # noqa
import sys # noqa
from pygame.locals import * # noqa
import random # noqa
import json
from pathlib import Path
import math
from pygame.locals import (
    K_RETURN, K_BACKSPACE, 
    QUIT, KEYDOWN, K_LEFT, K_RIGHT, K_a, K_d
)
import textwrap  # Make sure to import the textwrap module
import datetime  # Import datetime module for timestamps
import os

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)  # Initialize mixer with specific settings

# create game window first
size = width, height = (800, 800)
clock = pygame.time.Clock()
road_w = int(width/1.6)
roadmark_w = int(width/80)
right_lane = width/2 + road_w/4
left_lane = width/2 - road_w/4

# Define road boundaries
road_x = width / 2 - road_w / 2
road_right_x = road_x + road_w  # Correctly calculate road_right_x

speed = 1
text_col = (255, 255, 255)

# set the size of the window
screen = pygame.display.set_mode((size))

# Now load all button images after setting display mode
start_game_img = pygame.image.load("images/buttons/button_start.png").convert_alpha()
highscore_img = pygame.image.load("images/buttons/button_highscore.png").convert_alpha()
resume_img = pygame.image.load("images/buttons/button_resume.png").convert_alpha()
options_img = pygame.image.load("images/buttons/button_options.png").convert_alpha()
quit_img = pygame.image.load("images/buttons/button_quit.png").convert_alpha()
video_img = pygame.image.load("images/buttons/button_video.png").convert_alpha()
audio_img = pygame.image.load("images/buttons/button_audio.png").convert_alpha()
keys_img = pygame.image.load("images/buttons/button_keys.png").convert_alpha()
back_img = pygame.image.load("images/buttons/button_back.png").convert_alpha()
instructions_img = pygame.image.load("images/buttons/button_instructions.png").convert_alpha()  # Load instructions button

# Load toggle images
toggle_on_img = pygame.image.load("images/buttons/toggle_on.png").convert_alpha()
toggle_off_img = pygame.image.load("images/buttons/toggle_off.png").convert_alpha()

# Calculate center position for each button based on its actual width
def center_button_x(button_image):
    return width//2 - button_image.get_width()//2

# Create button instances with centered positions
resume_button = buttons.Button(center_button_x(resume_img), 200, resume_img, 1)
start_button = buttons.Button(center_button_x(start_game_img), 200, start_game_img, 1)
options_button = buttons.Button(center_button_x(options_img), 300, options_img, 1)
highscore_button = buttons.Button(center_button_x(highscore_img), 400, highscore_img, 1)
quit_button = buttons.Button(center_button_x(quit_img), 500, quit_img, 1)
instructions_button = buttons.Button(center_button_x(instructions_img), 100, instructions_img, 1)  # Position at the top

# Create button instances with centered positions
back_button = buttons.Button(center_button_x(back_img), 650, back_img, 1)

# Create toggle button instances
music_toggle = buttons.Button(center_button_x(toggle_on_img), 300, toggle_on_img, 1)  # Placeholder for music toggle
sfx_toggle = buttons.Button(center_button_x(toggle_on_img), 350, toggle_on_img, 1)  # Placeholder for sound effects toggle

# game variables
game_paused = False
menu_state = "startup"  # Changed from "main" to "startup"
game_started = False    # New variable to track if game has started
game_over = False
game_over_sound_played = False

# set the font of the text
font = pygame.font.SysFont("comicsans", 35)

# Define dark green color for game over text
dark_green_col = (0, 100, 0)

# set the title of the window
pygame.display.set_caption("Mustang Mayhem")

# Near the top with other image loading
# Load background image
background_img = pygame.image.load("images/game/background.jpeg")
# Scale it to fit the screen
background_img = pygame.transform.scale(background_img, (width, height))

# Near the top with other image loading
tree_img = pygame.image.load("images/scenery/tree.png").convert_alpha()
tree2_img = pygame.image.load("images/scenery/tree2.png").convert_alpha()  # Add second tree
bush_img = pygame.image.load("images/scenery/bush.png").convert_alpha()

# Scale the images to appropriate sizes - make everything bigger
tree_img = pygame.transform.scale(tree_img, (200, 300))  # First tree type
tree2_img = pygame.transform.scale(tree2_img, (200, 300))  # Second tree type
bush_img = pygame.transform.scale(bush_img, (200, 300))  # Same size as trees

# Create lists to store scenery positions
left_scenery = []
right_scenery = []

# Initialize scenery positions
def init_scenery():
    left_scenery.clear()
    right_scenery.clear()
    
    y = -300  # Start higher up (tree height) to prevent pop-in
    while y < height + 300:  # Extend below screen
        spacing = random.randint(200, 400)  # Increased spacing for larger objects
        
        # Left side - equal chance for each type
        scenery_type = random.choice(["tree", "tree2", "bush"])
        x_offset = random.randint(150, 220)  # Larger offset for bigger objects
        left_scenery.append({
            "type": scenery_type,
            "pos": (width//2 - road_w//2 - 15 - x_offset, y)
        })
        
        # Right side - independent placement
        scenery_type = random.choice(["tree", "tree2", "bush"])  # Correct selection
        right_scenery.append({
            "type": scenery_type,
            "pos": (width//2 + 75 + x_offset, y)
        })
        
        y += spacing

# Call this at game start
init_scenery()

# Replace the sound loading section with this
pygame.mixer.init()

# Near the top, add a new color constant for the title
TITLE_COLOR = (0, 0, 0)  # Black color for title text

# Helper function to safely load sounds
def load_sound(path, default_volume=1.0):
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(default_volume)
        return sound
    except FileNotFoundError:
        print(f"Warning: Sound file not found: {path}")
        return None


# Load sound effects with fallback
menu_music = load_sound("sounds/menu_music.wav", 0.5)
game_music = load_sound("sounds/game_music.mp3", 0.5)
crash_sound = load_sound("sounds/crash.wav", 0.7)
button_sound = load_sound("sounds/click.wav", 0.2)
car_driving_sound = load_sound("sounds/car_driving.mp3", 0.6)  # Add car driving sound
john_deere_sound = load_sound("sounds/john_deere.mp3", 0.1)  # Load John Deere sound
enemy2_pass_sound = load_sound("sounds/passing-car.mp3", 0.3)  # Add enemy passing sound
enemy1_pass_sound = load_sound("sounds/enemy1_pass.mp3", 0.3)  # Add enemy passing sound

# Add a variable to track playing sounds
current_music = None

# Add after other global variables
animation_counter = 0
title_y_offset = 0

# Add these variables to game variables section
username = ""
entering_username = False
MAX_USERNAME_LENGTH = 10

# Add a variable to track previous menu state
previous_menu_state = "startup"

# Add these variables near the top with other game variables
road_y = 0  # Track road marking position
base_speed = 2  # Lower initial speed
marking_gap = 100  # Increased gap between markings (was 50)
car_angle = 0  # Current car rotation angle
TILT_ANGLE = 25  # Maximum tilt angle in degrees
TILT_SPEED = 5  # Speed at which the car tilts
DECAY_RATE = 2    # Rate at which the car returns to upright position
LANE_CHANGE_SPEED = 12  # Increased from 8

# Define car dimensions
CAR_WIDTH = 105  # All cars are 105px wide
CAR_HEIGHT = 240  # All cars are 240px high

# Define John Deere dimensions
JOHN_DEERE_WIDTH = 210
JOHN_DEERE_HEIGHT = 413

# Adjust collision box size (make it slightly smaller than actual car for better gameplay)
COLLISION_MARGIN_X = 105   # Reduced margin for accurate collision detection
COLLISION_MARGIN_Y = 240
JOHN_DEERE_COLLISION_MARGIN_X = 200
JOHN_DEERE_COLLISION_MARGIN_Y = 400

# Add a variable to track if the car is on the course
on_course = True  # Initially, the car is on the course


# Before the game variables section, add these functions
def load_highscores():
    try:
        with open('highscores.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Return empty list if file doesn't exist or is invalid


# Function to clear the high score list
def clear_highscores():
    with open('highscores.json', 'w') as f:
        json.dump([], f)  # Write an empty list to clear the file


# Modify the save_highscore function to include a timestamp
def save_highscore(score_data):
    username, score = score_data
    # Don't save if player only reached level 1
    if score <= 1:
        return
        
    highscores = load_highscores()
    # Create a new dictionary for the current score with timestamp
    new_score = {
        "name": username,
        "score": score,
        "timestamp": datetime.datetime.now().strftime("%d-%m-%y %H:%M")  # Add timestamp in DD-MM-YY HH:MM format
    }
    
    # If highscores is empty or not a list, initialize it
    if not isinstance(highscores, list):
        highscores = []
    
    # If we already have 10 scores, check if current score is higher than the lowest
    if len(highscores) >= 10:
        lowest_score = min(highscores, key=lambda x: x["score"])
        if score <= lowest_score["score"]:
            return  # Don't save if current score is not higher than the lowest
    
    highscores.append(new_score)
    # Sort by score
    highscores.sort(key=lambda x: x["score"], reverse=True)
    highscores = highscores[:10]  # Keep top 10 scores instead of 5
    
    # Ensure the highscores.json directory exists
    Path('highscores.json').parent.mkdir(parents=True, exist_ok=True)
    
    with open('highscores.json', 'w') as f:
        json.dump(highscores, f)


# Add to game variables section
highscores = load_highscores()


def show_level():
    draw_text_with_outline(f"Level: {speed}", font, text_col, 5, 5)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_text_with_outline(text, font, text_col, x, y, outline_col=(0, 0, 0)):
    # Draw outline
    outline_offset = 2  # Offset for outline
    for dx in [-outline_offset, 0, outline_offset]:
        for dy in [-outline_offset, 0, outline_offset]:
            screen.blit(font.render(text, True, outline_col), (x + dx, y + dy))
    
    # Draw main text
    screen.blit(font.render(text, True, text_col), (x, y))


# draw graphics

# draw the road
pygame.draw.rect(
    screen,
    (50, 50, 50),
    (road_x, 0, road_w, height)
)

# Draw debugging guides for road boundaries
pygame.draw.line(screen, (255, 0, 0), (road_x, 0), (road_x, height), 2)  # Thinner red line for road_x
pygame.draw.line(screen, (255, 0, 0), (road_right_x, 0), (road_right_x, height), 2)  # Thinner red line for road_right_x

# draw the center line
pygame.draw.rect(
    screen,
    (255, 240, 60),
    (width/2-roadmark_w/2, 0, roadmark_w, height))

# draw right road mark
pygame.draw.rect(
    screen,
    (255, 255, 255),
    (road_x + road_w - roadmark_w*3, 0, roadmark_w, height))

# draw left road mark
pygame.draw.rect(
    screen,
    (255, 255, 255),
    (road_x + roadmark_w*2, 0, roadmark_w, height))

# apply the changes
pygame.display.update()

# load images
# load player car
car = pygame.image.load("images/cars/car.png")
car_loc = car.get_rect()
car_loc.center = left_lane, height*0.8

# load enemy cars
enemy_1 = pygame.image.load("images/cars/enemy_1.png")
enemy_2 = pygame.image.load("images/cars/enemy_2.png")
john_deere = pygame.image.load("images/cars/john_deere.PNG")  # Load John Deere image
enemy_cars = [enemy_1, enemy_2, john_deere]  # List of enemy car images

# Initialize enemy car with random image
car2 = random.choice(enemy_cars)
if car2 == john_deere:
    car2_loc = john_deere.get_rect()
    car2_loc.center = right_lane, height*0.2
else:
    car2_loc = car2.get_rect()
    car2_loc.center = right_lane, height*0.2

counter = 0
# game loop
run = True


# After loading sounds, add this function
def play_menu_music():
    global current_music
    if menu_music and music_enabled and (not current_music or current_music != menu_music):
        if current_music:
            current_music.stop()
        current_music = menu_music
        current_music.play(-1)  # -1 makes it loop indefinitely
    elif not music_enabled and current_music:
        current_music.stop()


# Modify the handle_username_input function to be more restrictive
def handle_username_input(event):
    global username, entering_username, menu_state
    if event.type == KEYDOWN:
        if event.key == K_RETURN:
            if username.strip():  # Only accept if username isn't empty
                entering_username = False
                save_highscore((username, speed))
                menu_state = "startup"  # Return to main menu
                play_menu_music()  # Start playing menu music
        elif event.key == K_BACKSPACE:
            username = username[:-1]
        elif event.key != K_SPACE and len(username) < MAX_USERNAME_LENGTH:  # Ignore spacebar
            # Only allow letters and numbers (no spaces or special characters)
            if event.unicode.isalnum():
                username = username + event.unicode


# Add this function to check if score qualifies for highscore
def score_qualifies(score):
    # Don't qualify if only reached level 1
    if score <= 1:
        return False
        
    highscores = load_highscores()
    # If less than 10 scores, any score above level 1 qualifies
    if len(highscores) < 10:
        return True
        
    # Check if score is higher than the lowest current score
    lowest_score = min(highscores, key=lambda x: x["score"])
    return score > lowest_score["score"]


# Near the top with other font definitions
title_font = pygame.font.SysFont("comicsans", 70, bold=True)  # Bigger and bolder

# Define a color palette for the title
darker_blue = (23, 139, 224)  # Darker blue
very_light_gray = (173, 180, 188)  # Very light gray


# Update the draw_glowing_text function to apply the new styles
def draw_glowing_text(text, font, x, y, animation_counter):
    """Draw text with specific colors and glowing effect."""
    total_width = sum(font.size(letter)[0] for letter in text)
    
    # Draw shadow
    shadow_offset = 3  # Offset for shadow
    shadow_color = (0, 0, 0)  # Black shadow
    current_x = x - total_width // 2
    for letter in text:
        shadow_surface = font.render(letter, True, shadow_color)
        screen.blit(shadow_surface, (current_x + shadow_offset, y + shadow_offset))
        current_x += font.size(letter)[0]

    # Draw main text with specified colors
    current_x = x - total_width // 2
    for i, letter in enumerate(text):
        if letter == 'M' and i == text.index('MAYHEM'):  # First 'M' in 'MAYHEM'
            color = very_light_gray
        elif letter == 'G' and i == text.index('MUSTANG') + 6:  # Last 'G' in 'MUSTANG'
            color = very_light_gray
        else:
            color = darker_blue  # Use the darker blue for other letters
        
        text_surface = font.render(letter, True, color)
        screen.blit(text_surface, (current_x, y))
        current_x += text_surface.get_width()


# Modified crash detection using rectangles with adjusted collision boxes
# Reduce width of collision boxes to match visible car parts
car_width_adjust = 10  # Pixels to subtract from each side
car_height_adjust = 5  # Pixels to subtract from top/bottom

# Keep only one definition of draw_rotated_car
def draw_rotated_car(surface, car_image, car_rect, angle):
    """
    Draw the car with rotation.
    
    Args:
        surface: pygame display surface
        car_image: the car image to draw
        car_rect: rectangle defining car position
        angle: rotation angle in degrees
    """
    rotated_image = pygame.transform.rotate(car_image, angle)
    rotated_rect = rotated_image.get_rect(center=car_rect.center)
    surface.blit(rotated_image, rotated_rect.topleft)


# Modify the draw_scenery function to be smoother
def draw_scenery():
    for scenery in left_scenery + right_scenery:
        new_y = (scenery["pos"][1] + current_speed)
        if new_y > height + 300:  # If object went off bottom
            new_y = -300  # Reset to top
        scenery["pos"] = (scenery["pos"][0], new_y)
        
        if -300 <= new_y <= height:
            if scenery["type"] == "tree":
                screen.blit(tree_img, scenery["pos"])
            elif scenery["type"] == "tree2":
                screen.blit(tree2_img, scenery["pos"])
            else:  # bush
                screen.blit(bush_img, scenery["pos"])


# Add this function to display "How to Play" instructions
def draw_how_to_play():
    how_to_play_text = [
        "Use the arrow keys to steer your Mustang.",
        "Avoid other vehicles on the road to keep your car safe.",
        "Do not go off the road or you will lose!",
        "Press the Space Bar to pause the game.",
        "The game gradually increases in speed and levels as you progress.",
        "Try to stay alive as long as possible to achieve the highest score!"
    ]

    padding = 50  # Keep the original padding
    line_height = 35  # Increased height for each line to add gaps
    max_width = width  # Calculate maximum width for text
    y_position = 50  # Starting Y position for the first line
    x_offset = 50  # Additional offset to move text to the right

    for index, line in enumerate(how_to_play_text, start=1):
        # Wrap the text to fit within the specified width
        wrapped_lines = textwrap.wrap(f"{index}. {line}", width=max_width // font.size('A')[0])  # Adjust width based on font size
        
        for wrapped_line in wrapped_lines:
            draw_text_with_outline(wrapped_line, font, (255, 255, 255), padding*3, y_position)  # Add outline to text
            y_position += line_height  # Move down for the next line

        # Increment y_position for the next numbered item
        y_position += 10  # Add extra space between numbered items


# Initialize toggle states
music_enabled = True  # Music is enabled by default
sfx_enabled = True    # Sound effects are enabled by default


# Update the toggle button images based on the state
def update_toggle_images():
    music_toggle.image = toggle_on_img if music_enabled else toggle_off_img
    sfx_toggle.image = toggle_on_img if sfx_enabled else toggle_off_img


# Call this function initially to set the correct images
update_toggle_images()


# Function to draw text with rainbow colors
def draw_rainbow_text(text, font, x, y):
    colors = [
        (255, 0, 0),    # Red
        (255, 127, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (75, 0, 130),   # Indigo
        (148, 0, 211)    # Violet
    ]

    for i, char in enumerate(text):
        color = colors[i % len(colors)]  # Cycle through colors
        char_surface = font.render(char, True, color)
        screen.blit(char_surface, (x + i * char_surface.get_width(), y))


# Load crash image for visual feedback
crash_img = pygame.image.load("images/cars/crash.png").convert_alpha()
crash_animation = False
crash_animation_frames = 5  # Number of frames for crash animation
crash_current_frame = 0
crash_animation_speed = 5  # Frames per second for the animation
crash_clock = pygame.time.Clock()

# Scale crash image to fit the screen
crash_img = pygame.transform.scale(crash_img, (width, height))

# Load enemy vehicle image
john_deere_image = pygame.image.load("images/cars/john_deere.PNG").convert_alpha()
john_deere_rect = john_deere_image.get_rect()
# Initialize collision rectangle for John Deere
john_deere_collision_rect = pygame.Rect(0, 0, 180, 320)  # Slightly smaller than actual size for better gameplay

# Enemy vehicle variables
john_deere_spawned = False  # Track if the enemy vehicle is on the screen

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

while run:
    screen.fill((34, 139, 34))

    if menu_state == "startup":
        play_menu_music()
        animation_counter += 0.05
        title_y_offset = math.sin(animation_counter) * 15
        
        # Draw background
        screen.blit(background_img, (0, 0))
        
        # Draw animated title with glow effect
        draw_glowing_text(
            "MUSTANG MAYHEM",
            title_font,
            width // 2,
            80,
            animation_counter
        )
 
        # Draw main menu buttons
        if start_button.draw(screen):
            if button_sound and sfx_enabled:
                button_sound.play()
            if current_music:
                current_music.stop()
            if game_music and music_enabled:
                current_music = game_music
                current_music.play(-1)  # Loop game music
            if car_driving_sound and sfx_enabled:
                car_driving_sound.play(-1)  # Loop car sound
            game_started = True
            menu_state = "game"
        if options_button.draw(screen):
            if button_sound and sfx_enabled:
                button_sound.play()
            menu_state = "options"
        if highscore_button.draw(screen):
            if button_sound and sfx_enabled:
                button_sound.play()
            menu_state = "highscore"
        if quit_button.draw(screen):
            if button_sound and sfx_enabled:
                button_sound.play()
            run = False

    elif menu_state == "options":
        play_menu_music()  # Play menu music in options
        # Draw options buttons
        if instructions_button.draw(screen):  # New button for instructions
            if button_sound and sfx_enabled:
                button_sound.play()
            menu_state = "instructions"  # Change to instructions state
        
        # Draw toggle buttons for music
        draw_text("Music:", font, text_col, width//2 - 280, 260)  # Label for music toggle
        music_toggle.rect.x = width//2 + 50  # Position music toggle button to the right of the label
        music_toggle.rect.y = 250  # Align with the label
        if music_toggle.draw(screen):
            music_enabled = not music_enabled  # Toggle music state
            if music_enabled:
                if menu_state == "game":
                    if game_music:
                        current_music = game_music
                        current_music.play(-1)
                else:
                    play_menu_music()
            update_toggle_images()  # Update button image

        # Draw toggle buttons for sound effects
        draw_text("Sound Effects:", font, text_col, width//2 - 280, 370)  # Adjusted Y position
        sfx_toggle.rect.x = width//2 + 50  # Position sound effects toggle button to the right of the label
        sfx_toggle.rect.y = 360  # Increased Y position for more space
        if sfx_toggle.draw(screen):
            sfx_enabled = not sfx_enabled  # Toggle sound effects state
            if not sfx_enabled and car_driving_sound:
                car_driving_sound.stop()
            update_toggle_images()  # Update button image

        if back_button.draw(screen):
            if button_sound and sfx_enabled:
                button_sound.play()
            menu_state = previous_menu_state  # Return to previous menu state

    elif menu_state == "highscore":
        play_menu_music()
        # Draw highscore screen
        draw_text_with_outline("HIGH SCORES", font, (255, 255, 255), width//2 - 100, 50)  # White text with black outline
        
        # Reload highscores each time we display them
        current_highscores = load_highscores()
        
        for i, score in enumerate(current_highscores):
            y_pos = 150 + (i * 50)  # Space out the scores
            name = score.get('name', 'Unknown')
            score_val = score.get('score', 0)
            timestamp = score.get('timestamp', 'N/A')  # Get timestamp

            # Define x positions for each column
            rank_x = width//2 - 375
            name_x = rank_x + 65  # Adjust this value to create more space
            score_x = name_x + 225
            timestamp_x = score_x + 185

            # Draw rank with outline
            rank_text = f"{i+1}."  # No extra space here
            draw_text_with_outline(rank_text, font, (255, 255, 255), rank_x, y_pos)

            # Draw name with outline
            draw_text_with_outline(name, font, (255, 255, 255), name_x, y_pos)

            # Draw score with outline
            score_text = f"Level: {score_val} "
            draw_text_with_outline(score_text, font, (255, 255, 255), score_x, y_pos)

            # Draw timestamp with outline
            draw_text_with_outline(timestamp, font, (255, 255, 255), timestamp_x, y_pos)
        
        if back_button.draw(screen):
            menu_state = "startup"
            if button_sound and sfx_enabled:
                button_sound.play()

    elif menu_state == "instructions":
        screen.fill((34, 139, 34))  # Background color
        
        # Display how to play instructions
        draw_how_to_play()
        
        # Back button to return to options menu
        if back_button.draw(screen):
            menu_state = "options"  # Return to options menu
            if button_sound and sfx_enabled:
                button_sound.play()

    elif menu_state == "game":
        if game_over is not True and game_paused is not True:
            counter += 1
            if counter == 800:
                speed += 1
                counter = 0
                # Only restart car driving sound if sfx are enabled
                if car_driving_sound and sfx_enabled:
                    car_driving_sound.stop()  # Stop any existing playback
                    car_driving_sound.play(-1)  # Restart the loop

            # Calculate current speed based on level
            current_speed = base_speed + (speed * 1.5)  # More gradual speed increase
            
            # Move road markings to create speed illusion
            road_y = (road_y + current_speed) % height
            
            # Draw the road with moving markings
            pygame.draw.rect(
                screen,
                (50, 50, 50),
                (road_x, 0, road_w, height)
            )

            # Draw moving center lines with gaps (dashed)
            for i in range(-1, height // marking_gap + 2):
                y_pos = ((i * marking_gap) + road_y) % height
                pygame.draw.rect(
                    screen,
                    (255, 240, 60),
                    (width//2 - roadmark_w/2, y_pos, roadmark_w, 40)
                )

            # Draw continuous side lines
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (road_x + road_w - roadmark_w*3, 0, roadmark_w, height)
            )
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (road_x + roadmark_w*2, 0, roadmark_w, height)
            )

            # Draw and update scenery
            draw_scenery()

            # Animate and draw enemy car
            car2_loc.y += current_speed * 1.2
            if car2_loc.y > height:
                # Reset enemy car position and randomly choose new enemy car image
                car2 = random.choice(enemy_cars)
                car2_loc = car2.get_rect()
                # Add random offset to lane position
                lane_offset = random.randint(-40, 40)  # Adjust these values to control spread
                if random.randint(0, 1):
                    car2_loc.center = (left_lane + lane_offset, -car2_loc.height)
                else:
                    car2_loc.center = (right_lane + lane_offset, -car2_loc.height)
                # Play sound when enemy1 appears
                if car2 == enemy_1 and enemy1_pass_sound and sfx_enabled:
                    enemy1_pass_sound.play()
                    john_deere_sound.stop()
                    enemy2_pass_sound.stop()
                if car2 == enemy_2 and enemy2_pass_sound and sfx_enabled:
                    enemy2_pass_sound.play()
                    john_deere_sound.stop()
                    enemy1_pass_sound.stop()
                # Play the John Deere sound when it spawns
                if car2 == john_deere and john_deere_sound and sfx_enabled:
                    if john_deere_sound and not john_deere_sound.get_num_channels():
                        john_deere_sound.set_volume(0.1)  # Set volume to maximum
                        john_deere_sound.play()
                        enemy1_pass_sound.stop()
                        enemy2_pass_sound.stop()

            # Also play sound when enemy1 first enters the screen
            if car2_loc.top <= 0 and car2_loc.bottom > 0:  # Just entered screen
                if car2 == enemy_1 and enemy1_pass_sound and sfx_enabled:
                    john_deere_sound.stop()
                    enemy1_pass_sound.play()
                    enemy2_pass_sound.stop()
                if car2 == enemy_2 and enemy2_pass_sound and sfx_enabled:
                    enemy2_pass_sound.play()
                    john_deere_sound.stop()
                    enemy1_pass_sound.stop()
                if car2 == john_deere and john_deere_sound and sfx_enabled:
                    if john_deere_sound and not john_deere_sound.get_num_channels():
                        john_deere_sound.set_volume(0.1)  # Set volume to maximum
                        john_deere_sound.play()  # Play the sound
                        enemy1_pass_sound.stop()
                        enemy2_pass_sound.stop()

            # Animate car tilt
            if car_angle > 0:
                car_angle = max(0, car_angle - TILT_SPEED)
            elif car_angle < 0:
                car_angle = min(0, car_angle + TILT_SPEED)

            # Update collision boxes with precise dimensions
            car_rect = pygame.Rect(
                car_loc.x + COLLISION_MARGIN_X,
                car_loc.y + COLLISION_MARGIN_Y,
                CAR_WIDTH - (COLLISION_MARGIN_X * 2),
                CAR_HEIGHT - (COLLISION_MARGIN_Y * 2)
            )
            if car2 == john_deere:
                car2_rect = pygame.Rect(
                    car2_loc.x + JOHN_DEERE_COLLISION_MARGIN_X,
                    car2_loc.y + JOHN_DEERE_COLLISION_MARGIN_Y,
                    JOHN_DEERE_WIDTH - (JOHN_DEERE_COLLISION_MARGIN_X * 2),
                    JOHN_DEERE_HEIGHT - (JOHN_DEERE_COLLISION_MARGIN_Y * 2)
                )
                pygame.draw.rect(screen, (255, 0, 0), car2_rect, 2)
            else:
                car2_rect = pygame.Rect(
                    car2_loc.x + COLLISION_MARGIN_X,
                    car2_loc.y + COLLISION_MARGIN_Y,
                    CAR_WIDTH - (COLLISION_MARGIN_X * 2),
                    CAR_HEIGHT - (COLLISION_MARGIN_Y * 2)
                )
 
            # Update John Deere collision box
            john_deere_collision_rect.centerx = john_deere_rect.centerx
            john_deere_collision_rect.centery = john_deere_rect.centery

            # Check if the enemy vehicle should spawn
            if not john_deere_spawned and car2_loc.y > height:  # Ensure no other enemy car is on screen
                # Randomly decide to spawn the enemy vehicle
                if random.randint(0, 100) < 5:  # Adjust the probability as needed
                    john_deere_spawned = True
                    john_deere_rect.y = -john_deere_rect.height  # Start off-screen
                    john_deere_rect.x = width // 2 - john_deere_rect.width // 2  # Centered in the middle of the road
                    
                    # Play the John Deere sound when it spawns
                    if john_deere_sound and not john_deere_sound.get_num_channels():
                        john_deere_sound.set_volume(1.0)  # Set volume to maximum
                        john_deere_sound.play()  # Play the sound

            # Update the john_deere vehicle position if it is spawned
            if john_deere_spawned:
                john_deere_rect.y += 5  # Move the john_deere vehicle down the screen

            # Handle collision detection for john_deere with the player's car
            if car_rect.colliderect(john_deere_collision_rect):
                game_over = True  # Set game over state if there is a collision
                if crash_sound and sfx_enabled:
                    crash_sound.play()
                # Flash the screen red
                for _ in range(5):
                    screen.fill((255, 0, 0))
                    pygame.display.flip()
                    pygame.time.delay(10)
                screen.fill((34, 139, 34))  # Restore background

            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    run = False
                if event.type == KEYDOWN:
                    if game_over and entering_username:
                        handle_username_input(event)
                    elif menu_state == "game":  # Only handle game controls if not entering username
                        if event.key in [K_LEFT, K_a]:
                            # Move left: decrement centerx by lane change speed
                            car_loc.centerx -= LANE_CHANGE_SPEED
                        elif event.key in [K_RIGHT, K_d]:
                            # Move right: increment centerx by lane change speed
                            car_loc.centerx += LANE_CHANGE_SPEED
                        if event.key == pygame.K_SPACE:
                            game_paused = True
                            if current_music:
                                current_music.stop()
                            if car_driving_sound:
                                car_driving_sound.stop()
                            play_menu_music()  # Switch to menu music when paused

            # Handle continuous movement
            keys = pygame.key.get_pressed()
            if keys[K_LEFT] or keys[K_a]:
                car_loc.centerx -= LANE_CHANGE_SPEED
                # Tilt car to the left
                car_angle += TILT_SPEED
                if car_angle > TILT_ANGLE:
                    car_angle = TILT_ANGLE
            elif keys[K_RIGHT] or keys[K_d]:
                car_loc.centerx += LANE_CHANGE_SPEED
                # Tilt car to the right
                car_angle -= TILT_SPEED
                if car_angle < -TILT_ANGLE:
                    car_angle = -TILT_ANGLE

            # Check if the car is off the tarmac
            if car_rect.left-80 < road_x or car_rect.right+80 > road_right_x:
                on_course = False  # The car is off the course
                game_over = True  # Set game over state
                car_driving_sound.stop()
                if crash_sound and sfx_enabled:
                    crash_sound.play()
                # Flash the screen red
                for _ in range(5):
                    screen.fill((255, 0, 0))
                    pygame.display.flip()
                    pygame.time.delay(10)
                screen.fill((34, 139, 34))  # Restore background
            else:
                on_course = True  # The car is on the course

            # Check for collision between the two rectangles
            if car_rect.colliderect(car2_rect):
                # Stop sounds on collision
                if car_driving_sound:
                    car_driving_sound.stop()
                if current_music:
                    current_music.stop()
                
                # Set game_over to True and play crash sound
                game_over = True
                if crash_sound and sfx_enabled:
                    crash_sound.play()
                # Flash the screen red
                for _ in range(5):
                    screen.fill((255, 0, 0))
                    pygame.display.flip()
                    pygame.time.delay(10)
                screen.fill((34, 139, 34))  # Restore background

            show_level()

            # Draw cars
            screen.blit(car2, car2_loc)
            draw_rotated_car(screen, car, car_loc, car_angle)

            # Draw pause instruction text last (on top of everything)
            small_font = pygame.font.SysFont("comicsans", 20)
            pause_text1 = "Press"
            pause_text2 = "SPACE"
            pause_text3 = "to pause"
            
            # Draw three lines with small vertical gaps
            draw_text_with_outline(pause_text1, small_font, text_col, 10, height - 85)
            draw_text_with_outline(pause_text2, small_font, text_col, 10, height - 60)
            draw_text_with_outline(pause_text3, small_font, text_col, 10, height - 35)

        # Add pause menu handling
        if game_paused:
            # Draw pause menu buttons
            if resume_button.draw(screen):
                if button_sound and sfx_enabled:
                    button_sound.play()
                if current_music:
                    current_music.stop()
                if music_enabled:
                    current_music = game_music
                    current_music.play(-1)  # Loop game music
                if car_driving_sound and sfx_enabled:
                    car_driving_sound.play(-1)  # Loop car sound
                game_paused = False
            if options_button.draw(screen):
                previous_menu_state = "game"  # Remember we came from game/pause menu
                menu_state = "options"
            if quit_button.draw(screen):
                if button_sound and sfx_enabled:
                    button_sound.play()
                menu_state = "startup"  # Return to main menu instead of quitting
                game_paused = False
                play_menu_music()

        if game_over:
            if not game_over_sound_played:
                # Stop all ongoing sounds
                if current_music:
                    current_music.stop()
                if car_driving_sound:
                    car_driving_sound.stop()
                if john_deere_sound:
                    john_deere_sound.stop()
                if enemy1_pass_sound:
                    enemy1_pass_sound.stop()
                if enemy2_pass_sound:
                    enemy2_pass_sound.stop()
                # Only play crash sound if sfx are enabled
                if crash_sound and sfx_enabled:
                    crash_sound.play()
                game_over_sound_played = True
                entering_username = score_qualifies(speed)
                username = ""
                crash_animation = True  # Start crash animation
            
            # Replace Game Over background with crash.png
            screen.blit(crash_img, (0, 0))
            
            # Display crash animation
            # Optionally, remove the crash animation blitting if not needed

            if entering_username:
                # Center all text elements
                title_text = "Enter your name:"
                title_width = font.size(title_text)[0]
                name_width = font.size(username + "_")[0]
                instruction_text = "Press ENTER when done"
                instruction_width = font.size(instruction_text)[0]
                
                draw_text_with_outline(title_text, font, (255, 255, 255), width//2 - title_width//2, 300)  # Title with outline
                draw_text_with_outline(username + "_", font, (255, 255, 255), width//2 - name_width//2, 350)  # Username with outline
                draw_text_with_outline(instruction_text, font, (255, 255, 255), width//2 - instruction_width//2, 400)  # Instruction with outline
            else:
                # Center the score text and stack buttons vertically
                draw_text_with_outline(f"Reached Level {speed}! Game Over", font, (255, 255, 255), width//2 - 250, 300)  # White text with black outline
                
                # Temporarily move buttons for game over screen
                start_button_original_y = start_button.rect.y
                quit_button_original_y = quit_button.rect.y
                
                # Position buttons with 100px gap
                start_button.rect.y = 400  # Move start button down
                quit_button.rect.y = 500   # Position quit button below
                
                # Draw buttons at new positions
                if start_button.draw(screen):
                    if button_sound and sfx_enabled:
                        button_sound.play()
                    game_over = False
                    game_over_sound_played = False
                    speed = 1
                    # Reset car positions
                    car_loc.center = left_lane, height*0.8
                    car2_loc.center = right_lane, height*0.2
                    # Reset game state
                    counter = 0
                    john_deere_spawned = False
                    # Reset scenery
                    init_scenery()
                    # Stop any currently playing sounds
                    if current_music:
                        current_music.stop()
                    if car_driving_sound:
                        car_driving_sound.stop()
                    if john_deere_sound:
                        john_deere_sound.stop()
                    if enemy1_pass_sound:
                        enemy1_pass_sound.stop()
                    if enemy2_pass_sound:
                        enemy2_pass_sound.stop()
                    # Start game music if enabled
                    if game_music and music_enabled:
                        current_music = game_music
                        current_music.play(-1)
                    # Start car sound if enabled
                    if car_driving_sound and sfx_enabled:
                        car_driving_sound.play(-1)
                    # Reset car angle
                    car_angle = 0
                    # Reset on_course state
                    on_course = True
                    menu_state = "game"
                
                if quit_button.draw(screen):
                    if button_sound and sfx_enabled:
                        button_sound.play()
                    play_menu_music()
                    menu_state = "startup"
                    game_over = False
                    game_over_sound_played = False
                    speed = 1
                    # Reset car positions
                    car_loc.center = left_lane, height*0.8
                    car2_loc.center = right_lane, height*0.2
                    # Reset game state
                    counter = 0
                    john_deere_spawned = False
                
                # Restore original positions
                start_button.rect.y = start_button_original_y
                quit_button.rect.y = quit_button_original_y


    # Update the display
    pygame.display.flip()

    # limits FPS to 60
    clock.tick(60)

    # event listeners
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN:
            if game_over and entering_username:
                handle_username_input(event)
            elif menu_state == "game":  # Only handle game controls if not entering username
                if event.key == pygame.K_SPACE:
                    game_paused = True
                    if current_music:
                        current_music.stop()
                    if car_driving_sound:
                        car_driving_sound.stop()
                    play_menu_music()  # Switch to menu music when paused

pygame.quit()
