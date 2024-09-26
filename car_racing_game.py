import pygame
import buttons # noqa
import sys # noqa
from pygame.locals import * # noqa
import random # noqa

pygame.init()


# create game window

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

# load button images
resume_img = pygame.image.load("images/button_resume.png").convert_alpha()
options_img = pygame.image.load("images/button_options.png").convert_alpha()
quit_img = pygame.image.load("images/button_quit.png").convert_alpha()
video_img = pygame.image.load("images/button_video.png").convert_alpha()
audio_img = pygame.image.load("images/button_audio.png").convert_alpha()
keys_img = pygame.image.load("images/button_keys.png").convert_alpha()
back_img = pygame.image.load("images/button_back.png").convert_alpha()

# create button instances
resume_button = buttons.Button(300, 125, resume_img, 1)
options_button = buttons.Button(293, 250, options_img, 1)
quit_button = buttons.Button(330, 375, quit_img, 1)
video_button = buttons.Button(226, 75, video_img, 1)
audio_button = buttons.Button(225, 200, audio_img, 1)
keys_button = buttons.Button(246, 325, keys_img, 1)
back_button = buttons.Button(332, 450, back_img, 1)


# game variables
game_paused = False
menu_state = "main"
game_over = False

# set the font of the text
font = pygame.font.SysFont("arialblack", 35)

# set the title of the window
pygame.display.set_caption("Indrek's Car Racing Game")

# set the background color of the window
screen.fill((60, 220, 0))


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
car = pygame.image.load("car.png")
car_loc = car.get_rect()
car_loc.center = left_lane, height*0.8

# load enemy car
car2 = pygame.image.load("otherCar.png")
car2_loc = car2.get_rect()
car2_loc.center = right_lane, height*0.2

counter = 0


# game loop
run = True

while run:
    screen.fill((34, 139, 34))

    # check if game is paused
    if game_paused is True:
        # check menu state
        if menu_state == "main":
            # draw pause screen buttons
            if resume_button.draw(screen):
                game_paused = False
            if options_button.draw(screen):
                menu_state = "options"
            if quit_button.draw(screen):
                run = False
        if menu_state == "options":
            # dra options buttons
            if video_button.draw(screen):
                print("Video settings")
            if audio_button.draw(screen):
                print("Audio settings")
            if keys_button.draw(screen):
                print("Key settings")
            if back_button.draw(screen):
                print("Back to main menu")
                menu_state = "main"

        # display menu
    # else:
        # draw_text("Press SPACE to pause", font, text_col, 160, 250)
    if game_over is not True and game_paused is not True:
        counter += 1

        if counter == 800:
            speed += 1
            counter = 0

            print("Level up! Speed increased to", speed)
        # animate enemy car
        car2_loc[1] += speed
        if car2_loc[1] > height:
            if random.randint(0, 1):
                car2_loc.center = left_lane, -200
            else:
                car2_loc.center = right_lane, -200
        # end game
        if car_loc[0] == car2_loc[0] and car2_loc[1] > car_loc[1] - 250:
            game_over = True
            draw_text("Game Over", font, text_col, 160, 250)
            print("Game Over")

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

        show_level()

        screen.blit(car, car_loc)
        screen.blit(car2, car2_loc)

        pygame.display.update()
    if game_over:
        draw_text("Game Over", font, text_col, 300, 250)
        if resume_button.draw(screen):
            game_paused = False
            game_over = False
            level = 1
            car_loc.center = left_lane, height*0.8
            car2_loc.center = right_lane, height*0.2
    # limits FPS to 60
    clock.tick(60)
    pygame.display.flip()
    # event listeners

    for event in pygame.event.get():
        if event.type == QUIT: # noqa
            run = False
        if event.type == KEYDOWN: # noqa
            if event.key in [K_LEFT, K_a] and car_loc[0] == 400: # noqa
                car_loc = car_loc.move([-int(road_w/2), 0])
            if event.key in [K_RIGHT, K_d] and car_loc[0] == 150: # noqa
                car_loc = car_loc.move([+int(road_w/2), 0])
            if event.key == pygame.K_SPACE:
                game_paused = True

pygame.quit()
