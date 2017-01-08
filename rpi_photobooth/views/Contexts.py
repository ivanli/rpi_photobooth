
import logging as log

import pygame

# 
# Events
#

EVT_KEY_PRESS = 0
EVT_TIMER_EXPIRY = 1
EVT_REFRESH = 2
EVT_SIZE = 3

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
        self.resolution = start_resolution
        self.event_bindings = {}

        KEY_ESCAPE = pygame.K_ESCAPE
        KEY_LEFT = pygame.K_LEFT
        KEY_RIGHT = pygame.K_RIGHT
        KEY_F12 = pygame.K_F12

        pygame.init()
        #self.display_surface = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
        self.display_surface = pygame.display.set_mode(self.resolution, pygame.DOUBLEBUF | pygame.HWSURFACE)

    def __del__(self):
        pygame.quit()

    def GetDisplaySurface(self):
        return self.display_surface

    def BindEvent(self, event, callback):
        if not event in self.event_bindings.keys():
            self.event_bindings[event] = []
        self.event_bindings[event].append(callback)

    def UnbindEvent(self, callback):
        # Remove all occurrances of this callback
        for key, value in self.event_bindings.iteritems():
            value = [x for x in a if x != callback]

    def StartPeriodicTimer(self, period, callback):
        pass

    def Refresh(self):
        pass

    def Run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:

                    if EVT_KEY_PRESS in self.event_bindings.keys():
                        for fn in self.event_bindings[EVT_KEY_PRESS]:
                            fn(KeyEvent(event.key))



class KeyEvent(object):

    def __init__(self, key_code):
        self.key_code = key_code

    def GetKeyCode(self):
        return self.key_code

