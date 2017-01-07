
import logging as log

import pygame

# 
# Events
#

EVT_KEY_PRESS = 0
EVT_TIMER_EXPIRY = 1

#
# View Contexts
#

class PygameViewContext(object):
    """
    This class provides the abstraction for hiding the actual UI implementation as much as possible.
    """

    KEY_ESCAPE = 0
    KEY_LEFT = 0
    KEY_RIGHT = 0
    KEY_F12 = 0

    def __init__(self, start_resolution):
        self.resolution = resolution

        KEY_ESCAPE = pygame.K_ESCAPE
        KEY_LEFT = pygame.K_LEFT
        KEY_RIGHT = pygame.K_RIGHT
        KEY_F12 = pygame.K_F12

        pygame.init()
        self.display_surface = pygame.display.set_mode(self.resolution)

    def BindEvent(event, callback):
        pass

    def StartPeriodicTimer(period, callback)
        pass
