import datetime
import json
import math
import pygame
import time

bus = None
try:
    import smbus

    # RPI version 1, must use "bus = smbus.SMBus(0)"
    bus = smbus.SMBus(0)
except:
    pass

import sys

# This is the address we setup in the Arduino Program
address = 0x04

pygame.init()
#size = width, height = 1024, 768
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
width, height = size
print "CONSOLE", size
black = 0, 0, 0
white = 255, 255, 255
orange = 255, 102, 51
green = 61, 235, 61
blue = 61, 61, 235


with open('config.json') as config_file:
    config = json.load(config_file)

teams = config['teams']


def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
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


def read_right_or_wrong():
    event = wait_for_key()
    key = event.key
    if key == 27:
        sys.exit(1)
    if key == ord('y'):
        return True
    if key == ord('n'):
        return False


def read_team_and_player_kb():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == 27:
                sys.exit(1)
            if key >= ord('1') and key <= ord('8'):
                ch = event.key - ord('1')
                return (ch % 4, ch / 4)
            else:
                return (-2, -2)
    return (-1, -1)


def read_team_and_player():
    if not bus:
        return read_team_and_player_kb()

    try:
        data = bus.read_i2c_block_data(address, 0, 2)
        team = data[0];
        player = data[1];
        return (team, player)
    except IOError:
        return (-1, -1)



print "DISPLAY", pygame.display.get_driver()
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
plain = pygame.font.Font('BebasNeue.otf', 140)
fancy = pygame.font.Font('LobsterTwo-Regular.otf', 140)
title = fancy.render("TriviaBox", True, white)
listen = plain.render("Listen", True, orange)
team_text = plain.render(  "Team  : ", True, white)
player_text = plain.render("Player: ", True, white)
answer = plain.render("Give Your Answer", True, orange)
buzz_in = plain.render("Buzz In", True, orange)
right_answer = plain.render("Correct!", True, green)
wrong_answer = plain.render("Incorrect", True, blue)
buzz_in = plain.render("Buzz In", True, orange)
nums = [fancy.render(str(num), True, white) for num in range(1, 6)]
outer = screen.get_rect()
inner = outer.inflate(-100, -50)
radian = 3.1415926/180.0


def ray(cx, cy, angle, radius):
    return (cx + (math.cos(angle) * radius), cy + (math.sin(angle) * radius))


def clock(extra_text, offset):
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

    print "NUM %.3f %s / Lag Total: %f" % \
        (elapsed, datetime.datetime.utcnow() - now, lag_total)
    return team, player

def get_answer(team, player):
    cls()
    draw_centered(answer, screen)
    pygame.display.flip()
    correct = read_right_or_wrong()

    cls()
    if correct:
        draw_centered(right_answer, screen)
    else:
        draw_centered(wrong_answer, screen)
    pygame.display.flip()
    wait_for_key()
    return correct

if False:
    print "Welcome"
    cls()
    draw_centered(title, screen)
    pygame.display.flip()
    time.sleep(3)

while True:
    print "Listen"
    cls()
    draw_centered(listen, screen)
    pygame.display.flip()
    while True:
        team, player = read_team_and_player()
        if team == -1:
            continue
        if team == -2:
            team, player = clock(buzz_in, (0, -200))
        if team > -1:
            correct = get_answer(team, player)
        else:
            # Timed out ... no winner
            pass

        break
