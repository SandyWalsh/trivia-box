import datetime
import json
import math
import pygame
import time
import sys

import pifacedigitalio

piface = pifacedigitalio.PiFaceDigital()

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


def save_state(filename):
    with file(filename, 'w') as f:
        json.dump(state, f)


def load_state(filename):
    with file(filename) as f:
        return json.load(f)


with open('config.json') as config_file:
    config = json.load(config_file)

teams = config['teams']

scores = [[0] * len(team[1]) for team in teams]
state = {'scores': scores,
         'current_round': 1}

try:
    state = load_state('state.json')
    scores = state['scores']
except IOError:
    save_state('state.json')


for score in scores:
    print "Team:", score

for team, players in teams:
    print "Team:", team, "Players:", players

def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == 27:
                    sys.exit(1)
                return event

def _center(larger, smaller):
    return (larger/2) - (smaller/2)


def cls(color=black):
    screen.fill(color)


def draw_centered(image, dest, row=0):
    this_size = image.get_size()
    height = this_size[1]
    dest_size = dest.get_size()
    left = _center(dest_size[0], this_size[0])
    top = _center(dest_size[1], this_size[1])
    top += (row * height)
    dest.blit(image, (left, top))


def read_right_or_wrong():
    while True:
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
                team, player = ch / 4, ch % 4
                print "Team: %d, Player: %d" % (team, player)
                return (team, player)
            else:
                return (-2, -2)
    return (-1, -1)


def read_team_and_player():
    data = piface.input_port.value
    if not data:
        return read_team_and_player_kb()

    pin = 0
    for team_index, team_info in enumerate(teams):
        team, players = team_info
        for player_index, player_info in enumerate(players):
            print piface.input_pins[pin].value
            if piface.input_pins[pin].value:
                print "Team: %d, Player: %d" % (team_index, player_index)
                return (team_index, player_index)
            pin += 1
    return read_team_and_player_kb()


def load_image(filename):
    image = pygame.image.load(filename)
    image = image.convert(screen)
    return pygame.transform.scale(image, screen.get_size())


print "DISPLAY", pygame.display.get_driver()
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
plain = pygame.font.Font('BebasNeue.otf', 140)
fancy = pygame.font.Font('LobsterTwo-Regular.otf', 140)
title = fancy.render("TriviaBox", True, white)
listen = plain.render("Listen", True, black)
answer = plain.render("Give Your Answer", True, orange)
answer_is = plain.render("Your answer is ...", True, orange)
buzz_in = plain.render("Buzz In", True, white)
right_answer = plain.render("Correct!", True, black)
wrong_answer = plain.render("Incorrect", True, blue)
nums = [fancy.render(str(num), True, white) for num in range(1, 6)]
outer = screen.get_rect()
inner = outer.inflate(-100, -50)
radian = 3.1415926/180.0

listen_image = load_image('listen.jpg')
button = load_image('button.png')
success = load_image('success.png')
failure = load_image('failure.png')
too_late = load_image('too_late.png')

shhh = pygame.mixer.Sound('shhh.ogg')
jeopardy = pygame.mixer.Sound('jeopardy.ogg')
jeopardy.set_volume(.1)
tick = pygame.mixer.Sound('tick.ogg')
tick.set_volume(.1)
failure_sound = pygame.mixer.Sound('fail.ogg')
success_sound = pygame.mixer.Sound('success.ogg')
clong_sound = pygame.mixer.Sound('clong.ogg')

def ray(cx, cy, angle, radius):
    return (cx + (math.cos(angle) * radius), cy + (math.sin(angle) * radius))


def team_and_player_handler():
    team, player = read_team_and_player()
    if team > -1 and team < 4:
        return (True, (team, player))

    return (False, (-1, -1))


def start_answer_handler():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == 27:
                sys.exit(1)
            return True, None
    return False, None


def clock(extra_text, handler, background=None, sound=None):
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
    if sound:
        sound.play()
    while end < 360:
        cls()
        if background:
            screen.blit(background, (0, 0))

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
        for extra, row_offset in extra_text:
            draw_centered(extra, screen, row_offset)
        pygame.display.flip()
        lag_end = datetime.datetime.utcnow()
        diff = lag_end - lag_start
        lag = diff.total_seconds()
        # print "LAG:", lag
        lag_total += lag

        # Fast poll to avoid sleep() calls which could
        # result in missing the first-to-press.
        wait = datetime.datetime.utcnow()
        duration = (0.9 * time_between_frames) - lag
        while (wait - lag_end).total_seconds() < duration:
            should_break, payload = handler()
            if should_break:
                break

            wait = datetime.datetime.utcnow()

        if should_break:
            break
        elapsed += time_between_frames
        end += inc

    print "NUM %.3f %s / Lag Total: %f" % \
        (elapsed, datetime.datetime.utcnow() - now, lag_total)

    if sound:
        sound.stop()

    if not should_break:
        clong_sound.play()
        cls()
        screen.blit(too_late, (0, 0))
        pygame.display.flip()
        wait_for_key()

    return payload


def get_answer(team, player):
    cls()
    team_name = teams[team][0]
    player_name = teams[team][1][player]
    team_text = plain.render(team_name, True, white)
    player_text = plain.render(player_name, True, white)
    extra_text = [(team_text, -2),
                  (player_text, -1),
                  (answer, 1)]

    clock(extra_text, start_answer_handler, sound=tick)
    cls()
    draw_centered(answer_is, screen)
    pygame.display.flip()
    correct = read_right_or_wrong()

    cls()
    ch = None
    if correct:
        screen.blit(success, (0,0))
        draw_centered(right_answer, screen)
        ch = success_sound.play()
        scores[team][player] += 10
    else:
        screen.blit(failure, (0,0))
        draw_centered(wrong_answer, screen)
        ch = failure_sound.play()
        scores[team][player] -= 10
    pygame.display.flip()
    save_state('state.json')
    wait_for_key()
    ch.stop()
    return correct

print "Welcome"
cls()
draw_centered(title, screen)
pygame.display.flip()
wait_for_key()

while state['current_round'] < 20:
    cls()
    row = -2
    colors = [green, blue]
    for idx, score in enumerate(scores):
        team_name = teams[idx][0]
        team_text = plain.render(team_name, True, colors.pop())
        score = plain.render(str(sum(score)), True, white)
        draw_centered(team_text, screen, row=row)
        draw_centered(score, screen, row=row+1)
        row += 2
    this_round = fancy.render("Round %d" % state['current_round'], True, orange)
    draw_centered(this_round, screen, 2)
    pygame.display.flip()
    wait_for_key()

    print "Listen"
    cls()
    screen.blit(listen_image, (0, 0))
    draw_centered(listen, screen, -2)
    shhh.play()
    pygame.display.flip()

    while True:
        team, player = read_team_and_player()
        if team == -1:
            continue
        if team == -2:
            extra_text = [(buzz_in, -1)]
            team, player = clock(extra_text, team_and_player_handler,
                                 background=button, sound=jeopardy)
        if team > -1:
            state['current_round'] = state['current_round'] + 1
            get_answer(team, player)
        else:
            # Timed out ... no winner
            pass

        break

# Final Score
cls()
row = -2
colors = [green, blue]
for idx, score in enumerate(scores):
    team_name = teams[idx][0]
    team_text = plain.render(team_name, True, colors.pop())
    score = plain.render(str(sum(score)), True, white)
    draw_centered(team_text, screen, row=row)
    draw_centered(score, screen, row=row+1)
    row += 2
this_round = fancy.render("GAME OVER", True, orange)
draw_centered(this_round, screen, 2)
pygame.display.flip()
wait_for_key()


