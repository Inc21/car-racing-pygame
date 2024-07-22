import pygame
from pygame.locals import *
import random

size = width, height = (800, 800)
road_w = int(width/1.6)
roadmark_w = int(width/80)
right_lane = width/2 + road_w/4
left_lane = width/2 - road_w/4
speed = 1

pygame.init()

running = True
# set the size of the window
screen = pygame.display.set_mode((size))
# set the title of the window
pygame.display.set_caption("Indrek's Car Racing Game")
# set the background color of the window
screen.fill((60, 220, 0))

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
while running:
    counter += 1
    if counter == 5000:
        speed += 0.15
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
        print("Game Over")
        break

    # event listeners
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key in [K_LEFT, K_a]:
                car_loc = car_loc.move([-int(road_w/2), 0])
            if event.key in [K_RIGHT, K_d]:
                car_loc = car_loc.move([+int(road_w/2), 0])

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

    screen.blit(car, car_loc)
    screen.blit(car2, car2_loc)
    pygame.display.update()

pygame.quit()
