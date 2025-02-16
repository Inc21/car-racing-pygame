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

pygame.init()

# create game window first
size = width, height = (800, 800)
clock = pygame.time.Clock()
road_w = int(width/1.6)
roadmark_w = int(width/80)
right_lane = width/2 + road_w/4
left_lane = width/2 - road_w/4
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

# Calculate center position for each button based on its actual width
def center_button_x(button_image):
    return width//2 - button_image.get_width()//2

# Create button instances with centered positions
resume_button = buttons.Button(center_button_x(resume_img), 200, resume_img, 1)
start_button = buttons.Button(center_button_x(start_game_img), 200, start_game_img, 1)
options_button = buttons.Button(center_button_x(options_img), 300, options_img, 1)
highscore_button = buttons.Button(center_button_x(highscore_img), 400, highscore_img, 1)
quit_button = buttons.Button(center_button_x(quit_img), 500, quit_img, 1)

# Options menu buttons
video_button = buttons.Button(center_button_x(video_img), 200, video_img, 1)
audio_button = buttons.Button(center_button_x(audio_img), 300, audio_img, 1)
keys_button = buttons.Button(center_button_x(keys_img), 400, keys_img, 1)
back_button = buttons.Button(center_button_x(back_img), 650, back_img, 1)

# game variables
game_paused = False
menu_state = "startup"  # Changed from "main" to "startup"
game_started = False    # New variable to track if game has started
game_over = False
game_over_sound_played = False

# set the font of the text
font = pygame.font.SysFont("arialblack", 35)

# set the title of the window
pygame.display.set_caption("Indrek's Car Racing Game")

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
            "pos": (width//2 - road_w//2 - x_offset, y)
        })
        
        # Right side - independent placement
        scenery_type = random.choice(["tree", "tree2", "bush"])
        x_offset = random.randint(50, 120)  # Adjusted for right side
        right_scenery.append({
            "type": scenery_type,
            "pos": (width//2 + road_w//2 + x_offset, y)
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
button_sound = load_sound("sounds/click.wav", 0.3)
car_driving_sound = load_sound("sounds/car_driving.mp3", 0.4)  # Add car driving sound

# Near the top with other sound loading
enemy1_pass_sound = load_sound("sounds/enemy1_pass.aiff", 0.3)  # Add enemy passing sound

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
TILT_ANGLE = 10  # Reduced from 15
TILT_SPEED = 1.5  # Slightly increased from 1.2
LANE_CHANGE_SPEED = 12  # Increased from 8

# Define car dimensions
CAR_WIDTH = 105  # All cars are 105px wide
PLAYER_HEIGHT = 250  # Player car is 250px high
ENEMY_HEIGHT = 240  # Enemy cars are 240px high

# Adjust collision box size (make it slightly smaller than actual car for better gameplay)
COLLISION_MARGIN_X = 15  # Pixels to subtract from each side
COLLISION_MARGIN_Y = 20  # Pixels to subtract from top/bottom

# Before the game variables section, add these functions
def load_highscores():
    try:
        with open('highscores.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Return empty list if file doesn't exist or is invalid


def save_highscore(score_data):
    username, score = score_data
    # Don't save if player only reached level 1
    if score <= 1:
        return
        
    highscores = load_highscores()
    # Create a new dictionary for the current score
    new_score = {"name": username, "score": score}
    
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
    level_obj = pygame.font.SysFont("comicsans", 35, True)
    level_txt = level_obj.render("Level: " + str(speed), 1, (255, 255, 255))
    screen.blit(level_txt, (5, 5))


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# draw graphics

# draw the road
pygame.draw.rect(
    screen,
    (50, 50, 50),
    (width/2-road_w/2, 0, road_w, height)
)

# draw the center line
pygame.draw.rect(
    screen,
    (255, 240, 60),
    (width/2-roadmark_w/2, 0, roadmark_w, height))

# draw right road mark
pygame.draw.rect(
    screen,
    (255, 255, 255),
    (width/2+road_w/2 - roadmark_w*3, 0, roadmark_w, height))

# draw left road mark
pygame.draw.rect(
    screen,
    (255, 255, 255),
    (width/2-road_w/2 + roadmark_w*2, 0, roadmark_w, height))

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
enemy_cars = [enemy_1, enemy_2]  # List of enemy car images

# Initialize enemy car with random image
car2 = random.choice(enemy_cars)
car2_loc = car2.get_rect()
car2_loc.center = right_lane, height*0.2

counter = 0

# game loop
run = True

# Update the adjust_music_speed function
def adjust_music_speed(level):
    global current_music
    if current_music:
        pygame.mixer.stop()
    # Play at increased speed based on level
    game_music_file = f"sounds/game_music_level_{min(level, 5)}.wav"
    
    new_music = load_sound(game_music_file)
    if new_music:
        current_music = new_music
    elif game_music:  # Fallback to base game music if level variant not found
        current_music = game_music
    
    if current_music:
        current_music.play()


# After loading sounds, add this function
def play_menu_music():
    global current_music
    if menu_music and (not current_music or current_music != menu_music):
        if current_music:
            current_music.stop()
        current_music = menu_music
        current_music.play(-1)  # -1 makes it loop indefinitely


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
title_font = pygame.font.SysFont("arialblack", 70, bold=True)  # Bigger and bolder

# Add this function after other drawing functions
def draw_glowing_rainbow_text(text, font, x, y, animation_counter):
    """Draw text with rainbow colors and glowing effect."""
    colors = [
        (255, 0, 0),    # Red
        (255, 127, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (75, 0, 130),   # Indigo
        (148, 0, 211)   # Violet
    ]
    
    total_width = sum(font.size(letter)[0] for letter in text)
    
    # Draw multiple layers for glow effect
    glow_layers = 3  # Number of glow layers
    for glow in range(glow_layers, -1, -1):
        current_x = x - total_width//2
        scale = 1 + (glow * 0.1)  # Increase size for outer layers
        alpha = 255 - (glow * 60)  # Decrease opacity for outer layers
        
        for i, letter in enumerate(text):
            color_index = i % len(colors)
            base_color = colors[color_index]
            
            # Create glowing color (lighter version of base color)
            glow_color = tuple(min(255, c + 100) for c in base_color)
            
            # Add wave animation
            offset_y = math.sin(animation_counter + i * 0.5) * 15
            
            text_surface = font.render(letter, True, glow_color)
            # Scale for glow effect
            size = (int(text_surface.get_width() * scale), 
                   int(text_surface.get_height() * scale))
            glow_surface = pygame.transform.scale(text_surface, size)
            
            # Set transparency
            glow_surface.set_alpha(alpha)
            
            # Position with wave offset
            pos = (current_x, y + offset_y)
            screen.blit(glow_surface, pos)
            current_x += font.size(letter)[0]
    
    # Draw the main text on top
    current_x = x - total_width//2
    for i, letter in enumerate(text):
        color_index = i % len(colors)
        offset_y = math.sin(animation_counter + i * 0.5) * 15
        text_surface = font.render(letter, True, colors[color_index])
        screen.blit(text_surface, (current_x, y + offset_y))
        current_x += text_surface.get_width()


# Improved crash detection using rectangles with adjusted collision boxes
# Reduce width of collision boxes to match visible car parts
car_width_adjust = 10  # Pixels to subtract from each side
car_height_adjust = 5  # Pixels to subtract from top/bottom

# Add this function before the game loop
def draw_rotated_car(screen, car_image, car_location, angle):
    """
    Draw the car with rotation.
    
    Args:
        screen: pygame display surface
        car_image: the car image to draw
        car_location: rectangle defining car position
        angle: rotation angle in degrees
    """
    # Only rotate if there's an angle
    if angle != 0:
        # Get the center before rotation
        center = car_location.center
        # Rotate the car image
        rotated_car = pygame.transform.rotate(car_image, angle)
        # Get the new rectangle
        new_rect = rotated_car.get_rect()
        # Set the center of the new rectangle to the old center
        new_rect.center = center
        # Draw the rotated car
        screen.blit(rotated_car, new_rect)
    else:
        # Draw the car without rotation
        screen.blit(car_image, car_location)


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


while run:
    screen.fill((34, 139, 34))

    if menu_state == "startup":
        play_menu_music()
        animation_counter += 0.05
        title_y_offset = math.sin(animation_counter) * 15
        
        # Draw background
        screen.blit(background_img, (0, 0))
        
        # Draw animated title with glow effect
        draw_glowing_rainbow_text(
            "Car Racing Game",
            title_font,
            width//2,
            80,
            animation_counter
        )
        
        # Add hover effect to buttons
        if start_button.draw(screen):
            button_sound.play()
            if current_music:
                current_music.stop()
            if game_music:
                current_music = game_music
                current_music.play(-1)  # Loop game music
            if car_driving_sound:
                car_driving_sound.play(-1)  # Loop car sound
            game_started = True
            menu_state = "game"
        if options_button.draw(screen):
            button_sound.play()
            menu_state = "options"
        if highscore_button.draw(screen):
            button_sound.play()
            menu_state = "highscore"
        if quit_button.draw(screen):
            button_sound.play()
            run = False

        # Draw moving background cars higher up
        screen.blit(car2, (50 + math.sin(animation_counter) * 30, 
                          450 + math.cos(animation_counter) * 20))  # Was 600
        screen.blit(car, (width - 150 + math.cos(animation_counter) * 30, 
                         450 + math.sin(animation_counter) * 20))  # Was 600

    elif menu_state == "options":
        play_menu_music()  # Play menu music in options
        # Draw options buttons
        if video_button.draw(screen):
            print("Video settings")
        if audio_button.draw(screen):
            print("Audio settings")
        if keys_button.draw(screen):
            print("Key settings")
        if back_button.draw(screen):
            menu_state = previous_menu_state  # Return to previous menu state
            button_sound.play()

    elif menu_state == "highscore":
        play_menu_music()
        # Center and capitalize the title
        draw_text("HIGH SCORES", font, text_col, width//2 - 120, 50)
        
        # Reload highscores each time we display them
        current_highscores = load_highscores()
        
        for i, score in enumerate(current_highscores):
            y_pos = 150 + (i * 50)
            # Safely access score data with get() method
            name = score.get('name', 'Unknown')
            score_val = score.get('score', 0)
            score_text = f"{i+1}. {name}: Level {score_val}"
            # Center each score entry
            text_width = font.size(score_text)[0]  # Get width of text
            x_pos = width//2 - text_width//2  # Calculate center position
            draw_text(score_text, font, text_col, x_pos, y_pos)
        
        if back_button.draw(screen):
            menu_state = "startup"
            button_sound.play()
            # Reset game state when returning to main menu
            game_over = False
            game_over_sound_played = False
            speed = 1
            car_loc.center = left_lane, height*0.8
            car2_loc.center = right_lane, height*0.2

    elif menu_state == "game":
        if game_over is not True and game_paused is not True:
            counter += 1
            if counter == 800:
                speed += 1
                counter = 0
                print("Level up! Speed increased to", speed)
                # Save current music state
                was_playing = current_music is not None
                adjust_music_speed(speed)
                # Restart car driving sound if it was stopped
                if car_driving_sound:
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
                (width/2-road_w/2, 0, road_w, height)
            )

            # Draw moving center lines with gaps (dashed)
            for i in range(-1, height // marking_gap + 2):
                y_pos = ((i * marking_gap) + road_y) % height
                pygame.draw.rect(
                    screen,
                    (255, 240, 60),
                    (width/2-roadmark_w/2, y_pos, roadmark_w, 40)
                )

            # Draw continuous side lines
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (width/2+road_w/2 - roadmark_w*3, 0, roadmark_w, height)
            )
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (width/2-road_w/2 + roadmark_w*2, 0, roadmark_w, height)
            )

            # Draw and update scenery
            draw_scenery()

            # Animate and draw enemy car
            car2_loc.y += current_speed * 1.2
            if car2_loc.y > height:
                # Reset enemy car position and randomly choose new enemy car image
                car2 = random.choice(enemy_cars)
                car2_loc = car2.get_rect()
                if random.randint(0, 1):
                    car2_loc.center = (left_lane, -car2_loc.height)
                else:
                    car2_loc.center = (right_lane, -car2_loc.height)
                # Play sound when enemy1 appears
                if car2 == enemy_1 and enemy1_pass_sound:
                    enemy1_pass_sound.play()

            # Also play sound when enemy1 first enters the screen
            if car2_loc.top <= 0 and car2_loc.bottom > 0:  # Just entered screen
                if car2 == enemy_1 and enemy1_pass_sound:
                    enemy1_pass_sound.play()

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
                PLAYER_HEIGHT - (COLLISION_MARGIN_Y * 2)
            )

            car2_rect = pygame.Rect(
                car2_loc.x + COLLISION_MARGIN_X,
                car2_loc.y + COLLISION_MARGIN_Y,
                CAR_WIDTH - (COLLISION_MARGIN_X * 2),
                ENEMY_HEIGHT - (COLLISION_MARGIN_Y * 2)
            )

            # Check for collision between the two rectangles
            if car_rect.colliderect(car2_rect):
                # Stop sounds on collision
                if car_driving_sound:
                    car_driving_sound.stop()
                if current_music:
                    current_music.stop()
                
                # More precise collision response
                if car2_loc.centery < car_loc.centery:  # Enemy is above player
                    car_loc.top = car2_loc.bottom + COLLISION_MARGIN_Y
                elif car2_loc.centery > car_loc.centery:  # Enemy is below player
                    car_loc.bottom = car2_loc.top - COLLISION_MARGIN_Y
                elif car2_loc.centerx < car_loc.centerx:  # Enemy is to the left
                    car_loc.left = car2_loc.right + COLLISION_MARGIN_X
                else:  # Enemy is to the right
                    car_loc.right = car2_loc.left - COLLISION_MARGIN_X
                
                game_over = True
                if crash_sound:
                    crash_sound.play()

            show_level()

            # Draw cars
            screen.blit(car2, car2_loc)
            draw_rotated_car(screen, car, car_loc, car_angle)
            
            # Draw pause instruction text last (on top of everything)
            small_font = pygame.font.SysFont("arialblack", 20)
            pause_text1 = "Press"
            pause_text2 = "SPACE"
            pause_text3 = "to pause"
            
            # Draw three lines with small vertical gaps
            draw_text(pause_text1, small_font, text_col, 10, height - 85)
            draw_text(pause_text2, small_font, text_col, 10, height - 60)
            draw_text(pause_text3, small_font, text_col, 10, height - 35)

        # Add pause menu handling
        if game_paused:
            # Draw pause menu buttons
            if resume_button.draw(screen):
                button_sound.play()
                if current_music:
                    current_music.stop()
                current_music = game_music
                current_music.play(-1)  # Loop game music
                if car_driving_sound:
                    car_driving_sound.play(-1)  # Loop car sound
                game_paused = False
            if options_button.draw(screen):
                previous_menu_state = "game"  # Remember we came from game/pause menu
                menu_state = "options"
            if quit_button.draw(screen):
                button_sound.play()
                menu_state = "startup"  # Return to main menu instead of quitting
                game_paused = False
                play_menu_music()

        if game_over:
            if not game_over_sound_played:
                if crash_sound:
                    crash_sound.play()
                if current_music:
                    current_music.stop()
                game_over_sound_played = True
                entering_username = score_qualifies(speed)
                username = ""
            
            draw_text("Game Over", font, text_col, 300, 250)
            
            if entering_username:
                # Center all text elements
                title_text = "Enter your name:"
                title_width = font.size(title_text)[0]
                name_width = font.size(username + "_")[0]
                instruction_text = "Press ENTER when done"
                instruction_width = font.size(instruction_text)[0]
                
                draw_text(title_text, font, text_col, width//2 - title_width//2, 300)
                draw_text(username + "_", font, text_col, width//2 - name_width//2, 350)
                draw_text(instruction_text, font, text_col, 
                         width//2 - instruction_width//2, 400)
            else:
                # Center the score text and stack buttons vertically
                draw_text(f"Final Score: Level {speed}", font, text_col, width//2 - 150, 300)
                
                # Temporarily move buttons for game over screen
                start_button_original_y = start_button.rect.y
                quit_button_original_y = quit_button.rect.y
                
                # Position buttons with 100px gap
                start_button.rect.y = 400  # Move start button down
                quit_button.rect.y = 500   # Position quit button below
                
                # Draw buttons at new positions
                if start_button.draw(screen):
                    button_sound.play()
                    game_over = False
                    game_over_sound_played = False
                    speed = 1
                    car_loc.center = left_lane, height*0.8
                    car2_loc.center = right_lane, height*0.2
                
                if quit_button.draw(screen):
                    button_sound.play()
                    play_menu_music()
                    menu_state = "startup"
                    game_over = False
                    game_over_sound_played = False
                    speed = 1
                    car_loc.center = left_lane, height*0.8
                    car2_loc.center = right_lane, height*0.2
                
                # Restore original positions
                start_button.rect.y = start_button_original_y
                quit_button.rect.y = quit_button_original_y

    # limits FPS to 60
    clock.tick(60)
    pygame.display.flip()

    # event listeners
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN:
            if game_over and entering_username:
                handle_username_input(event)
            elif menu_state == "game":  # Only handle game controls if not entering username
                if event.key in [K_LEFT, K_a] and car_loc.centerx == right_lane:
                    # Start moving left
                    target_x = left_lane
                    current_x = car_loc.centerx
                    # Smoother movement
                    while current_x > target_x:
                        current_x -= LANE_CHANGE_SPEED
                        car_loc.centerx = max(current_x, target_x)
                        car_angle = TILT_ANGLE
                        
                        # Update road position during turn
                        road_y = (road_y + current_speed) % height
                        
                        # Redraw everything
                        screen.fill((34, 139, 34))
                        
                        # Draw road
                        pygame.draw.rect(
                            screen,
                            (50, 50, 50),
                            (width/2-road_w/2, 0, road_w, height)
                        )
                        
                        # Draw moving center lines
                        for i in range(-1, height // marking_gap + 2):
                            y_pos = ((i * marking_gap) + road_y) % height
                            pygame.draw.rect(
                                screen,
                                (255, 240, 60),
                                (width/2-roadmark_w/2, y_pos, roadmark_w, 40)
                            )
                        
                        # Draw continuous side lines
                        pygame.draw.rect(
                            screen,
                            (255, 255, 255),
                            (width/2+road_w/2 - roadmark_w*3, 0, roadmark_w, height)
                        )
                        pygame.draw.rect(
                            screen,
                            (255, 255, 255),
                            (width/2-road_w/2 + roadmark_w*2, 0, roadmark_w, height)
                        )
                        
                        # Draw scenery before cars
                        draw_scenery()
                        
                        # Move and draw enemy car
                        car2_loc.y += current_speed * 1.2
                        if car2_loc.y > height:
                            if random.randint(0, 1):
                                car2_loc.center = (left_lane, -car2_loc.height)
                            else:
                                car2_loc.center = (right_lane, -car2_loc.height)
                        screen.blit(car2, car2_loc)
                        draw_rotated_car(screen, car, car_loc, car_angle)
                        show_level()
                        
                        pygame.display.update()
                        clock.tick(60)
                if event.key in [K_RIGHT, K_d] and car_loc.centerx == left_lane:
                    # Start moving right
                    target_x = right_lane
                    current_x = car_loc.centerx
                    # Smoother movement
                    while current_x < target_x:
                        current_x += LANE_CHANGE_SPEED
                        car_loc.centerx = min(current_x, target_x)
                        car_angle = -TILT_ANGLE
                        
                        # Update road position during turn
                        road_y = (road_y + current_speed) % height
                        
                        # Redraw everything
                        screen.fill((34, 139, 34))
                        
                        # Draw road
                        pygame.draw.rect(
                            screen,
                            (50, 50, 50),
                            (width/2-road_w/2, 0, road_w, height)
                        )
                        
                        # Draw moving center lines
                        for i in range(-1, height // marking_gap + 2):
                            y_pos = ((i * marking_gap) + road_y) % height
                            pygame.draw.rect(
                                screen,
                                (255, 240, 60),
                                (width/2-roadmark_w/2, y_pos, roadmark_w, 40)
                            )
                        
                        # Draw continuous side lines
                        pygame.draw.rect(
                            screen,
                            (255, 255, 255),
                            (width/2+road_w/2 - roadmark_w*3, 0, roadmark_w, height)
                        )
                        pygame.draw.rect(
                            screen,
                            (255, 255, 255),
                            (width/2-road_w/2 + roadmark_w*2, 0, roadmark_w, height)
                        )
                        
                        # Draw scenery before cars
                        draw_scenery()
                        
                        # Move and draw enemy car
                        car2_loc.y += current_speed * 1.2
                        if car2_loc.y > height:
                            if random.randint(0, 1):
                                car2_loc.center = (left_lane, -car2_loc.height)
                            else:
                                car2_loc.center = (right_lane, -car2_loc.height)
                        screen.blit(car2, car2_loc)
                        draw_rotated_car(screen, car, car_loc, car_angle)
                        show_level()
                        
                        pygame.display.update()
                        clock.tick(60)
                if event.key == pygame.K_SPACE:
                    game_paused = True
                    if current_music:
                        current_music.stop()
                    if car_driving_sound:
                        car_driving_sound.stop()
                    play_menu_music()  # Switch to menu music when paused

pygame.quit()
