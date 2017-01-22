import logging as log

import pkg_resources
import numpy

import pygame
import pygame.surfarray
from . import Contexts

class WebcamView(object):
    fps = 15

    def __init__(self, context, webcam, image_path):
        self.context = context

        self.frame_image_original = pygame.image.load(image_path).convert_alpha()
        self.frame_image_resized = self.frame_image_original.copy()

        self.webcam = webcam
        self.webcam_surface = None

        self.context.BindEvent(self.context.EVT_REFRESH, self.OnPaint)
        #self.context.BindEvent(Contexts.EVT_SIZE, self.OnSize)

        # Start a refresh timer so we know when to get the next frame from the webcam.
        self.context.StartPeriodicTimer(1000. / self.fps, self.GetNextFrame)

    def __del__(self):
        self.Destroy()

    def SetFrameImage(self, image_path):
        self.frame_image_original = pygame.image.load(image_path).convert_alpha()
        self.frame_image_resized = self.frame_image_original.copy()

    #
    # View interface implementation
    #

    def Show(self):
        log.debug('Showing view {}.'.format(self))
        self.OnSize(None)
        self.OnPaint(None)

    def Destroy(self):
        log.debug('Destroying view {}.'.format(self))
        self.context.StopTimer(self.GetNextFrame)
        self.context.UnbindEvent(self.OnPaint)
        self.context.UnbindEvent(self.OnSize)
        
    # 
    # Event handlers
    #

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
        #log.debug('Got paint event.')

        display_surface = self.context.GetDisplaySurface()
        if self.webcam_surface is not None:
            display_surface.blit(self.webcam_surface, (self.webcam_x, self.webcam_y))
        display_surface.blit(self.frame_image_resized, (0, 0))

        pygame.display.flip()

    def GetNextFrame(self, event):
        #log.debug('Capturing next frame.')

        ret, image = self.webcam.Read()
        if ret:
            self.webcam_surface = pygame.transform.scale(image.ToPygameSurface(), (self.webcam_w, self.webcam_h))
            # Force a re-paint with new frame retrieved.
            self.context.Refresh()


class StartView(WebcamView):

    def __init__(self, context, webcam):
        image_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'StartScreen.png')
        super(StartView, self).__init__(context, webcam, image_path)

class CountdownView(WebcamView):

    def __init__(self, context, webcam, start_count):
        image_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'CountdownScreen{}.png'.format(start_count))
        super(CountdownView, self).__init__(context, webcam, image_path)

    def SetCount(self, count):
        if count > 3 or count < 0:
            raise ViewException('Got out of range count {}.'.format(count))
        image_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'CountdownScreen{}.png'.format(count))
        self.SetFrameImage(image_path)

class ReviewPhotoView(object):

    def __init__(self, context, photo):
        self.context = context

        self.photo_surface_original = photo.ToPygameSurface()

        image_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'ReviewScreen.png')
        self.frame_surface = pygame.image.load(image_path).convert_alpha()

    def Show(self):
        self.window_w = self.context.GetClientSize(self)[0]
        self.window_h = self.context.GetClientSize(self)[1]

        self.webcam_x = int(304.0 / 1440.0 * self.window_w)
        self.webcam_y = int(132.0 / 900.0 * self.window_h)
        w = int(836.0 / 1440.0 * self.window_w)
        h = int(627.0 / 900.0 * self.window_h)

        photo_surface = pygame.transform.scale(self.photo_surface_original, (w, h))

        display_surface = self.context.GetDisplaySurface()
        display_surface.blit(photo_surface, (self.webcam_x, self.webcam_y))
        display_surface.blit(self.frame_surface, (0, 0))

        pygame.display.flip()


    def Destroy(self):
        pass 

class PrintPhotoView(object):

    def __init__(self, context, photo, print_count):
        self.context = context
        self.photo_print = photo.Copy()

        image_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'PrintScreen.png')
        self.background_surface = pygame.image.load(image_path).convert_alpha()

        self.print_count_images = [
                None,
                pygame.image.load(pkg_resources.resource_filename('rpi_photobooth.resources.images', 'PrintCount1.png')).convert_alpha(),
                pygame.image.load(pkg_resources.resource_filename('rpi_photobooth.resources.images', 'PrintCount2.png')).convert_alpha(),
                pygame.image.load(pkg_resources.resource_filename('rpi_photobooth.resources.images', 'PrintCount3.png')).convert_alpha()
                ]
        self.current_print_count = print_count

        # Need to repaint due to ability to update count
        self.context.BindEvent(self.context.EVT_REFRESH, self.OnRefresh)

    def __del__(self):
        self.Destroy()
        
    def Show(self):
        self.OnRefresh(None)

    def Destroy(self):
        self.context.UnbindEvent(self.OnRefresh)

    def SetPrintCount(self, count):
        self.current_print_count = count
        self.context.Refresh()

    def OnRefresh(self, event):
        window_w = self.context.GetClientSize(self)[0]
        window_h = self.context.GetClientSize(self)[1]

        print_w = int(333. / 1440. * window_w)
        print_h = int(500. / 900. * window_h)

        self.photo_print.ResizeProportional((print_w, print_h))

        print_x = int(window_w / 2 + 10)
        print_y = 240

        display_surface = self.context.GetDisplaySurface()
        display_surface.blit(self.background_surface, (0, 0))
        display_surface.blit(self.print_count_images[self.current_print_count], (400, 318))
        display_surface.blit(self.photo_print.ToPygameSurface(), (print_x, print_y))

        pygame.display.flip()

class SentToPrintView(object):

    def __init__(self, context):
        self.context = context

        background_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'SentToPrintScreen.png')
        self.background_surface = pygame.image.load(background_path).convert_alpha()

        self.context.BindEvent(self.context.EVT_REFRESH, self.OnRefresh)

    def Show(self):
        self.OnRefresh(None)

    def Destroy(self):
        self.context.UnbindEvent(self.OnRefresh)

    def OnRefresh(self, event):
        display_surface = self.context.GetDisplaySurface()
        display_surface.blit(self.background_surface, (0, 0))
        pygame.display.flip()
        
