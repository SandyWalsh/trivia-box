import datetime
import json
import math
import pygame
import time
import sys

piface = None
try:
    import pifacedigitalio
    piface = pifacedigitalio.PiFaceDigital()
except ImportError:
    pass


pygame.init()
#size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
#font_size = 140
size = width, height = 1024, 768
font_size = 120
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


def read_right_or_wrong(can_steal):
    while True:
        event = wait_for_key()
        key = event.key
        if key == 27:
            sys.exit(1)
        if key == ord('y'):
            return "right"
        if key == ord('n'):
            return "wrong"
        if key == ord('s') and can_steal:
            return "steal"


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
    data = 0
    if piface:
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


def fast_scan_inputs(input_state):
    if piface:
        pin = 0
        for team_index, team_info in enumerate(teams):
            team, players = team_info
            for player_index, player_info in enumerate(players):
                input_state[team_index][player_index] = \
                    piface.input_pins[pin].value
                pin += 1

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == 27:
                sys.exit(1)
            if key == 32:
                return True
            if key >= ord('1') and key <= ord('8'):
                ch = event.key - ord('1')
                team, player = ch / 4, ch % 4
                input_state[team][player] = 1
        if event.type == pygame.KEYUP:
            key = event.key
            if key >= ord('1') and key <= ord('8'):
                ch = event.key - ord('1')
                team, player = ch / 4, ch % 4
                input_state[team][player] = 0
    return False


def load_image(filename):
    image = pygame.image.load(filename)
    image = image.convert(screen)
    return pygame.transform.scale(image, screen.get_size())


print "DISPLAY", pygame.display.get_driver()
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
plain = pygame.font.Font('BebasNeue.otf', font_size)
fancy = pygame.font.Font('LobsterTwo-Regular.otf', font_size)
title = fancy.render("TriviaBox", True, white)
listen = plain.render("Listen", True, black)
answer = plain.render("Give Your Answer", True, orange)
buzz_to_steal = plain.render("Buzz in to steal", True, orange)
answer_is = plain.render("Your answer is ...", True, orange)
buzz_in = plain.render("Buzz In", True, white)
right_answer = plain.render("Correct!", True, black)
wrong_answer = plain.render("Incorrect", True, blue)
nums = [fancy.render(str(num), True, white) for num in range(1, 6)]
outer = screen.get_rect()
inner = outer.inflate(-100, -50)
radian = 3.1415926 / 180.0

listen_image = load_image('listen.jpg')
button = load_image('button.png')
success = load_image('success.png')
failure = load_image('failure.png')
too_late = load_image('too_late.png')
steal = load_image('steal.png')

shhh = pygame.mixer.Sound('shhh.ogg')
jeopardy = pygame.mixer.Sound('jeopardy.ogg')
jeopardy.set_volume(.1)
tick = pygame.mixer.Sound('tick.ogg')
tick.set_volume(.1)
failure_sound = pygame.mixer.Sound('fail.ogg')
success_sound = pygame.mixer.Sound('success.ogg')
clong_sound = pygame.mixer.Sound('clong.ogg')
horns = [pygame.mixer.Sound('car_horn.ogg'),
         pygame.mixer.Sound('bike_horn.ogg')]


def ray(cx, cy, angle, radius):
    return (cx + (math.cos(angle) * radius), cy + (math.sin(angle) * radius))


def wait_for_sound(ch):
    while ch.get_busy():
        time.sleep(.1)


def show_buzzed_in(team, player):
    cls()
    color = [blue, green][team]
    team_name = teams[team][0]
    player_name = teams[team][1][player]
    team_text = plain.render(team_name, True, color)
    player_text = plain.render(player_name, True, color)
    draw_centered(team_text, screen, -1)
    draw_centered(player_text, screen)
    pygame.display.flip()
    ch = horns[team].play()
    wait_for_sound(ch)


def team_and_player_handler(handler_args):
    team, player = read_team_and_player()
    valid_teams = range(0, 4)
    if handler_args:
        valid_teams = handler_args
    if team in valid_teams:
        return (True, (team, player))

    return (False, (-1, -1))


def start_answer_handler(handler_args):
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == 27:
                sys.exit(1)
            return True, None
    return False, None


def clock(extra_text, handler, handler_args=None, background=None, sound=None):
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
            should_break, payload = handler(handler_args)
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


def wait_for_sound(ch):
    while ch.get_busy():
        time.sleep(.1)


def update_score(team, player, delta):
    scores[team][player] += delta
    save_state('state.json')


def get_answer(team, player, can_steal=True, answer_value=10):
    cls()
    color = [blue, white][team]
    team_name = teams[team][0]
    player_name = teams[team][1][player]
    team_text = plain.render(team_name, True, color)
    player_text = plain.render(player_name, True, color)
    extra_text = [(team_text, -2),
                  (player_text, -1),
                  (answer, 1)]

    clock(extra_text, start_answer_handler, sound=tick)
    cls()
    draw_centered(team_text, screen, -2)
    draw_centered(player_text, screen, -1)
    draw_centered(answer_is, screen, 1)
    pygame.display.flip()
    action = read_right_or_wrong(can_steal)

    x = _center(width, 0)
    y = _center(height, 0)
    x += (x/2)
    y -= (y/2)

    cls()
    ch = None
    if action == "right":
        screen.blit(success, (0,0))
        draw_centered(right_answer, screen)
        score_text = plain.render("+%d" % answer_value, True, black)
        screen.blit(score_text, (x, y))
        ch = success_sound.play()
        update_score(team, player, answer_value)
        pygame.display.flip()
        wait_for_key()
    elif action == "wrong":
        screen.blit(failure, (0,0))
        draw_centered(wrong_answer, screen)
        score_text = plain.render("-%d" % answer_value, True, black)
        screen.blit(score_text, (x, y))
        ch = failure_sound.play()
        update_score(team, player, -answer_value)
        pygame.display.flip()
        wait_for_key()
    elif action == "steal":
        update_score(team, player, -answer_value)
        team = (team + 1) % 2
        team_name = teams[team][0]
        team_text = plain.render(team_name, True, black)
        extra_text = [(team_text, -1),
                      (buzz_to_steal, 1)]
        ch = failure_sound.play()
        wait_for_sound(ch)
        team, player = clock(extra_text, team_and_player_handler,
                             handler_args=[team],
                             background=steal, sound=jeopardy)
        if team != -1:
            show_buzzed_in(team, player)
            get_answer(team, player, can_steal=False, answer_value=5)
            return
    if ch:
        ch.stop()


print "Welcome"
cls()
draw_centered(title, screen)
pygame.display.flip()
wait_for_key()

print "Test buzzers"
input_state = [[0,0,0,0], [0,0,0,0]]
x = _center(width, 0)
test_text = plain.render("Test your buzzers", True, white)
cache = {}
while True:
    cls()
    screen.blit(test_text, (_center(width, test_text.get_size()[0]), 0))
    stop = fast_scan_inputs(input_state)
    if stop:
        break
    for team in range(0, 2):
        for player in range(0, 4):
            if not input_state[team][player]:
                continue
            player_name = teams[team][1][player]
            player_text = cache.get(player_name)
            if not player_text:
                player_text = plain.render(player_name, True,
                                           [blue, green][team])
                cache[player_name] = player_text
            text_height = player_text.get_size()[1]
            screen.blit(player_text, (team * x, (1 + player) * text_height))

    pygame.display.flip()
    time.sleep(.1)


while state['current_round'] < 20:
    cls()
    print "Showing standings"
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
            show_buzzed_in(team, player)
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
