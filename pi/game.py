import pygame
import sys


pygame.init()
size = width, height = 1024, 768
black = 0, 0, 0
white = 255, 255, 255


def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                return event


def draw_centered(image, dest):
    dest_size = dest.get_size()
    this_size = image.get_size()
    left = (dest_size[0]/2) - (this_size[0]/2)
    top = (dest_size[1]/2) - (this_size[1]/2)
    dest.blit(image, (left, top))


screen = pygame.display.set_mode(size)

font = pygame.font.Font('BebasNeue.otf', 96)
screen.fill(black)
title = font.render("TriviaBox", True, white)
draw_centered(title, screen)
pygame.display.flip()

wait_for_key()
