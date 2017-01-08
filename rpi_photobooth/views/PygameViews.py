import logging as log

import pkg_resources

import pygame
from . import Contexts

class StartPanel(object):
    fps = 15

    def __init__(self, context, webcam):
        self.context = context

        frame_image_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'StartScreen.png')
        self.frame_image_original = pygame.image.load(frame_image_path).convert_alpha()
        self.frame_image_resized = self.frame_image_original.copy()

        self.webcam = webcam
        self.webcam_surface = None

        self.context.BindEvent(Contexts.EVT_REFRESH, self.OnPaint)
        self.context.BindEvent(Contexts.EVT_SIZE, self.OnSize)

        # Start a refresh timer so we know when to get the next frame from the webcam.
        self.context.StartPeriodicTimer(1000. / self.fps, self.GetNextFrame)

    def __del__(self):
        self.context.StopTimer(self.GetNextFrame)
        self.UnbindEvent(self.OnPaint)
        self.UnbindEvent(self.OnSize)
        
    def OnSize(self, event):
        self.window_w = self.context.GetClientSize(self)[0]
        self.window_h = self.context.GetClientSize(self)[1]

        log.debug("Got size event with {}x{}".format(self.window_w, self.window_h))

        # Webcam feed is resized on each frame received.
        self.webcam_x = int(304.0 / 1440.0 * self.window_w)
        self.webcam_y = int(132.0 / 900.0 * self.window_h)
        self.webcam_w = int(836.0 / 1440.0 * self.window_w)
        self.webcam_h = int(627.0 / 900.0 * self.window_h)

        log.debug('Webcam size is {}x{}.'.format(self.webcam_w, self.webcam_h))

    def OnPaint(self, event):
        # Here we draw all elements of the screen. Need to manually draw because we want to control the overlaying of elements
        # ourselves - ie. the background is above the webcam view so it creates a border.
        log.debug('Got paint event.')

        display_surface = self.context.GetDisplaySurface()
        if self.webcam_surface is not None:
            display_surface.blit(self.webcam_surface, (self.webcam_x, self.webcam_y))
        display_surface.blit(self.frame_image_resized, (0, 0))

        pygame.display.flip()

    def GetNextFrame(self, event):
        log.debug('Capturing next frame.')

        ret, surface = self.webcam.Read()
        if ret:
            self.webcam_surface = pygame.transform.scale(surface, (self.webcam_w, self.webcam_h))
            # Force a re-paint with new frame retrieved.
            self.context.Refresh()

    def Show(self):
        self.OnPaint(None)

    def Destroy(self):
        pass
