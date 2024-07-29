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

# create button instances
resume_button = buttons.Button(300, 125, resume_img, 1)


# game variables
game_paused = False

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


# def main_menu():
#     while True:
#         screen.fill((0, 0, 0))
#         draw_text("Main Menu", font, (255, 255, 255), 200, 200)

#         for event in pygame.event.get():
#             if event.type == QUIT: # noqa
#                 pygame.quit()
#                 sys.exit()
#             if event.type == K_ESCAPE: # noqa
#                 pygame.quit()
#                 sys.exit()

#         pygame.display.update()
#         clock.tick(60)


def game_over():
    screen.fill((0, 0, 0))
    over_obj = pygame.font.SysFont("comicsans", 50, True)
    over_txt = over_obj.render("Game Over", 1, (255, 255, 255))
    screen.blit(over_txt, (width/2, height/2))


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
    screen.fill((52, 78, 91))

    # check if game is paused
    if game_paused:
        if resume_button.draw(screen):
            game_paused = False
        # display menu
    else:
        draw_text("Press SPACE to pause", font, text_col, 160, 250)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_paused = True
        if event.type == pygame.QUIT:
            run = False

    # counter += 1

    # if counter == 800:
    #     speed += 1
    #     counter = 0

    #     print("Level up! Speed increased to", speed)
    # # animate enemy car
    # car2_loc[1] += speed
    # if car2_loc[1] > height:
    #     if random.randint(0, 1):
    #         car2_loc.center = left_lane, -200
    #     else:
    #         car2_loc.center = right_lane, -200
    # # end game
    # if car_loc[0] == car2_loc[0] and car2_loc[1] > car_loc[1] - 250:
    #     game_over()
    #     print("Game Over")
    #     # break

    # # event listeners
    # for event in pygame.event.get():
    #     if event.type == QUIT: # noqa
    #         running = False
    #     if event.type == KEYDOWN: # noqa
    #         if event.key in [K_LEFT, K_a] and car_loc[0] == 400: # noqa
    #             car_loc = car_loc.move([-int(road_w/2), 0])
    #         if event.key in [K_RIGHT, K_d] and car_loc[0] == 150: # noqa
    #             car_loc = car_loc.move([+int(road_w/2), 0])

    # # draw the road
    # pygame.draw.rect(
    #     screen,
    #     (50, 50, 50),
    #     (width/2-road_w/2, 0, road_w, height)
    # )

    # # draw the center line
    # pygame.draw.rect(
    #     screen,
    #     (255, 240, 60),
    #     (width/2-roadmark_w/2, 0, roadmark_w, height))

    # # draw right road mark
    # pygame.draw.rect(
    #     screen,
    #     (255, 255, 255),
    #     (width/2+road_w/2 - roadmark_w*3, 0, roadmark_w, height))

    # # draw left road mark
    # pygame.draw.rect(
    #     screen,
    #     (255, 255, 255),
    #     (width/2-road_w/2 + roadmark_w*2, 0, roadmark_w, height))

    # show_level()

    # screen.blit(car, car_loc)
    # screen.blit(car2, car2_loc)
    pygame.display.update()

    # limits FPS to 60
    clock.tick(60)
    pygame.display.flip()

pygame.quit()
