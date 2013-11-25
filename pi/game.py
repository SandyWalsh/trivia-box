import datetime
import json
import math
import pygame
import time
import smbus
import sys

# RPI version 1, must use "bus = smbus.SMBus(0)"
bus = smbus.SMBus(0)

# This is the address we setup in the Arduino Program
address = 0x04

pygame.init()
size = width, height = 1024, 768
black = 0, 0, 0
white = 255, 255, 255
orange = 255, 102, 51
green = 61, 235, 61

with open('config.json') as config_file:
    config = json.load(config_file)

teams = config['teams']


def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                return event

def _center(larger, smaller):
    return (larger/2) - (smaller/2)


def cls(color=black):
    screen.fill(color)


def draw_centered(image, dest):
    this_size = image.get_size()
    dest_size = dest.get_size()
    left = _center(dest_size[0], this_size[0])
    top = _center(dest_size[1], this_size[1])
    dest.blit(image, (left, top))


def read_team_and_player():
    try:
        data = bus.read_i2c_block_data(address, 0, 2)
        team = data[0];
        player = data[1];
        return (team, player)
    except IOError:
        return (-1, -1)


print "DISPLAY", pygame.display.get_driver()
screen = pygame.display.set_mode(size)
plain = pygame.font.Font('BebasNeue.otf', 140)
fancy = pygame.font.Font('LobsterTwo-Regular.otf', 140)
title = fancy.render("TriviaBox", True, white)
listen = plain.render("Listen", True, orange)
nums = [fancy.render(str(num), True, white) for num in range(1, 6)]
outer = screen.get_rect()
inner = outer.inflate(-100, -50)
radian = 3.1415926/180.0

if False:
    print "Welcome"
    cls()
    draw_centered(title, screen)
    pygame.display.flip()
    time.sleep(3)

if False:
    print "Listen"
    cls()
    draw_centered(listen, screen)
    pygame.display.flip()
    wait_for_key()


def ray(cx, cy, angle, radius):
    return (cx + (math.cos(angle) * radius), cy + (math.sin(angle) * radius))


print "Clock"
x = _center(width, 0)
y = _center(height, 0)
expected_fps = 8
time_between_frames = (1.0 / float(expected_fps))
inc = 360 / (5 * expected_fps)
end = 0
elapsed = 0.0
now = datetime.datetime.utcnow()
lag_total = 0.0
computed_points = []
team = -1
player = -1
while end < 360:
    cls()

    if end + inc >= 360:
        computed_points.append(ray(x, y, 360 * radian, 300))
    else:
        for p in range(end, end + inc, 5):  # 5 degree steps always
            computed_points.append(ray(x, y, p * radian, 300))

    lag_start = datetime.datetime.utcnow()
    points = [(x, y)]
    points.extend(computed_points)
    points.append((x,y))
    pygame.draw.polygon(screen, green, points)
    left = 4 - int(elapsed)
    draw_centered(nums[left], screen)
    pygame.display.flip()
    lag_end = datetime.datetime.utcnow()
    diff = lag_end - lag_start
    lag = diff.total_seconds()
    # print "LAG:", lag
    lag_total += lag

    time.sleep((0.9 * time_between_frames) - lag)
    elapsed += time_between_frames
    end += inc

    team, player = read_team_and_player()
    if team > -1 and team < 4:
        break

print "Winner: %d, Player: %d" % (team, player)
print

print "NUM %.3f %s / Lag Total: %f" % (elapsed, datetime.datetime.utcnow() - now, lag_total)
