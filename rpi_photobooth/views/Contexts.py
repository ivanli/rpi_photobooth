
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

    def __init__(self, start_resolution):
        self.resolution = resolution

        pygame.init()
        self.display_surface = pygame.display.set_mode(self.resolution)

    def BindEvent(event, callback):
        pass
