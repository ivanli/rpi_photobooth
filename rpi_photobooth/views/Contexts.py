
import logging as log

import sys
import pygame

#
# View Contexts
#

class PygameViewContext(object):
    """
    This class provides the abstraction for hiding the actual UI implementation as much as possible.
    """

    KEY_ESCAPE = pygame.K_ESCAPE
    KEY_LEFT = pygame.K_LEFT
    KEY_RIGHT = pygame.K_RIGHT
    KEY_F12 = pygame.K_F12

    EVT_KEY_PRESS = pygame.KEYDOWN
    EVT_REFRESH = pygame.USEREVENT + 1
    EVT_BUTTON_PRESSED = pygame.USEREVENT + 2
    EVT_TIMER_START = pygame.USEREVENT + 3
    EVT_TIMER_END = pygame.NUMEVENTS

    def __init__(self, start_resolution):
        log.debug('Initialising context.')

        self.resolution = start_resolution
        self.event_bindings = {}

        for i in range(0, pygame.NUMEVENTS + 1):
            self.event_bindings[i] = []

        pygame.init()
        self.display_surface = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
        #self.display_surface = pygame.display.set_mode(self.resolution, pygame.DOUBLEBUF | pygame.HWSURFACE)

    def __del__(self):
        pygame.quit()

    def GetDisplaySurface(self):
        return pygame.display.get_surface()

    def BindEvent(self, event, callback):
        self.event_bindings[event].append(callback)

    def UnbindEvent(self, callback):
        # Remove all occurrances of this callback
        for key, value in self.event_bindings.iteritems():
            value[:] = [x for x in value if x != callback]

    def StartPeriodicTimer(self, period, callback):
        free_id = 0
        for i in range(self.EVT_TIMER_START, self.EVT_TIMER_END + 1):
            if len(self.event_bindings[i]) is 0:
                free_id = i
                break
        if free_id is 0:
            raise ViewException('Failed to find free event id for new timer.')
        
        self.BindEvent(free_id, callback)
        pygame.time.set_timer(free_id, int(period))

        log.info('Started timer with period {} id {} callback {}'.format(period, free_id, callback))

    def StopTimer(self, callback):
        for i in range(self.EVT_TIMER_START, self.EVT_TIMER_END + 1):
            if callback in self.event_bindings[i]:
                self.UnbindEvent(callback)
                pygame.time.set_timer(i, 0)

    def Refresh(self):
        if not pygame.event.peek(self.EVT_REFRESH):
            pygame.event.post(pygame.event.Event(self.EVT_REFRESH))

    def Run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == self.EVT_BUTTON_PRESSED:

                    if self.EVT_KEY_PRESS in self.event_bindings.keys():
                        for fn in self.event_bindings[self.EVT_KEY_PRESS]:
                            fn(KeyEvent(event.key))
                    
                elif event.type >= self.EVT_TIMER_START and event.type <= self.EVT_TIMER_END:
                    if event.type in self.event_bindings.keys() and len(self.event_bindings[event.type]) > 0:
                        self.event_bindings[event.type][0](None)

                else:
                    for fn in self.event_bindings[event.type]:
                        fn(None)
            
            pygame.time.wait(20)

    def GetClientSize(self, view):
        return (1440, 900)

class KeyEvent(object):

    def __init__(self, key_code):
        self.key_code = key_code

    def GetKeyCode(self):
        return self.key_code


class ViewException(Exception):
    pass


