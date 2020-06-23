# testing gpio pins
import pygame
from pygame.locals import *
import RPi.GPIO as GPIO
from time import sleep

pygame.init()
pygame.display.set_mode((100, 100))

GPIO.setmode(GPIO.BCM)

chanUpBtn = 17

GPIO.setup(chanUpBtn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(chanUpBtn, GPIO.RISING)
counter = 0

while True:
    inputState = GPIO.input(17)
    if inputState == False:
        print('button pressed')
        sleep(0.5)
    events = pygame.event.get()
    
    for event in events:
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                print("LEFT")

