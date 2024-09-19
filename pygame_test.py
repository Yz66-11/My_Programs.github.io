import sys
import pygame
import cfg
pygame.init()
screen = pygame.display.set_mode((400,400))
pygame.display.set_caption('新窗口')
f = pygame.font.Font('C:/Windows/Fonts/simhei.ttf',50)
text = f.render("China",True,(200,55,0),(55,0,200))
textRect = text.get_rect()
textRect.center = (200,200)
screen.blit(text,textRect)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.flip()