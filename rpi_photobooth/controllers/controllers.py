import logging as log
import sys
import wx
import transitions
import pkg_resources

import PIL.Image
import numpy
import pygame

import cv2
import cv

from ..views import PygameViews as views
from ..views import Contexts

from . import Images

class Photobooth:

    def __init__(self, view_context, webcam, camera, photo_storage, printer):
        self.context = view_context
        self.webcam = webcam
        self.camera = camera
        self.photo_storage = photo_storage
        self.printer = printer
        self.print_count = 1
        
        # Configuration
        self.countdown_start = 1
        self.print_notif_period = 8000
        self.max_print_count = 3

        # Resources
        self.print_template_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'PrintTemplate.png')

        # Bind to events of interest. We use key presses to control the photobooth for now.
        self.context.BindEvent(self.context.EVT_KEY_PRESS, self.OnAnyButton)

        # Create state machine for photobooth
        s = [
            transitions.State(name='Init'),
            transitions.State(name='Start', on_enter=['ClearPhotos', 'RenderStart'], on_exit=['ClearScreen']),
            transitions.State(name='Countdown', on_enter=['RenderCountdown', 'StartCountdown'], on_exit=['StopCountdown', 'ClearScreen']),
            transitions.State(name='ReviewPhoto', on_enter=['RenderReviewPhoto'], on_exit=['ClearScreen']),
            transitions.State(name='PrintPhoto', on_enter=['RenderPrintPhoto'], on_exit=['ClearScreen']),
            transitions.State(name='SentToPrint', on_enter=['RenderSendToPrint', 'StartPrintNotifTimer'], on_exit=['StopPrintNotifTimer', 'ClearScreen']),
            transitions.State(name='Exit', on_enter=['ExitApp'])
        ]
        t = [
            { 'trigger':'KeyDown', 'source':'*', 'dest':'Exit', 'conditions':'IsEscKey' },

            { 'trigger':'KeyDown', 'source':'Start', 'dest':'Countdown', 'conditions':'IsLeftRightKey' },
            { 'trigger':'CountExpired', 'source':'Countdown', 'dest':'ReviewPhoto', 'conditions':'IsCountdownDone', 'prepare':'DecrementCountdown', 'before':'TakePhoto' },

            { 'trigger':'KeyDown', 'source':'ReviewPhoto', 'dest':'PrintPhoto', 'conditions':['IsRightKey', 'HasEnoughPhotos'], 'before':'CreatePrint' },
            # Fallthrough from the last condition. Still more photos to take.
            { 'trigger':'KeyDown', 'source':'ReviewPhoto', 'dest':'Countdown', 'conditions':'IsRightKey' },
            { 'trigger':'KeyDown', 'source':'ReviewPhoto', 'dest':'Countdown', 'conditions':'IsLeftKey', 'before':'DeleteLastPhoto' },
            
            { 'trigger':'KeyDown', 'source':'PrintPhoto', 'dest':'SentToPrint', 'conditions':'IsRightKey', 'before':'StartPrintPhoto' },
            { 'trigger':'KeyDown', 'source':'PrintPhoto', 'dest':'PrintPhoto', 'conditions':'IsLeftKey', 'before':'IncPrintCount' },

            { 'trigger':'PrintPeriodExpired', 'source':'SentToPrint', 'dest':'Start' },
            { 'trigger':'KeyDown', 'source':'SentToPrint', 'dest':'Start', 'conditions':'IsRightKey' }
        ]
        initial_s = 'Init'
        fsm = transitions.Machine(model=self, send_event=True, states=s, transitions=t, initial=initial_s)
        self.to_Start()


    # State / transition triggered methods

    def StartCountdown(self, event):
        log.info('Starting countdown.')

        self.countdown = self.countdown_start
        self.context.StartPeriodicTimer(1000, self.OnCountdownTimerExpiry)
        
        log.debug('Countdown started with initial count {}.'.format(self.countdown))

    def DecrementCountdown(self, event):
        log.info('Decrementing count.')
        self.countdown -= 1
        if self.countdown >= 0:
            self.current_view.SetCount(self.countdown)

        log.debug('Countdown is now {}'.format(self.countdown))

    def StopCountdown(self, event):
        self.context.StopTimer(self.OnCountdownTimerExpiry)

    def TakePhoto(self, event):
        self.camera.TakePhoto()

    def DeleteLastPhoto(self, event):
        self.photo_storage.DeleteLast()

    def CreatePrint(self, event):
        # TODO Refactor the need to know which image library is in use here. Could create a NativeImage class that extends the 
        # desired specific image class to use.
        print_surface = pygame.image.load(self.print_template_path)

        log.debug('Template image size is {}.'.format(print_surface.get_size()))

        # Assemble print image 
        photo_pos = [[], []]
        photo_pos[0].append((10, 314))
        photo_pos[0].append((10, 764))
        photo_pos[0].append((10, 1214))
        photo_pos[1].append((610, 314))
        photo_pos[1].append((610, 764))
        photo_pos[1].append((610, 1214))

        photo_size = tuple(numpy.subtract((590, 749), photo_pos[0][0]))

        photos = self.photo_storage.GetPhotos()

        for col in photo_pos:
            for i in range(0, len(col)):
                log.debug(i)
                pos = col[i]
                img = photos[i]
                img.ResizeProportional(photo_size)
                print_surface.blit(img.ToPygameSurface(), pos)

        self.final_print = Images.PyCamImage(print_surface)

    def StartPrintPhoto(self, event):
        log.info('Starting photo print.')

        for i in range(0, self.print_count):
            self.printer.PrintImage(self.final_print)

        log.debug('Photo printing started.')

    def ClearPhotos(self, event):
        self.photo_storage.Clear()

    def IncPrintCount(self, event):
        self.print_count = (self.print_count % self.max_print_count) + 1
        self.current_view.SetPrintCount(self.print_count)

    def ResetPrintVariables(self, event):
        self.print_count = 1

    def StartPrintNotifTimer(self, event):
        self.context.StartPeriodicTimer(self.print_notif_period, self.OnPrintNotifExpiry)

    def StopPrintNotifTimer(self, event):
        self.context.StopTimer(self.OnPrintNotifExpiry)

    #
    # Rendering methods
    #

    def RenderStart(self, event):
        self.current_view = views.StartView(self.context, self.webcam)
        self.current_view.Show()

    def RenderCountdown(self, event):
        self.current_view = views.CountdownView(self.context, self.webcam, self.countdown_start)
        self.current_view.Show()

    def RenderReviewPhoto(self, event):
        log.info('Rendering review photo screen.')

        self.current_view = views.ReviewPhotoView(self.context, self.photo_storage.GetLast())
        self.current_view.Show()

        log.debug('Render of review photo screen completed.')

    def RenderPrintPhoto(self, event):
        log.info('Rendering print photo screen.')

        self.current_view = views.PrintPhotoView(self.context, self.final_print, self.print_count)
        self.current_view.Show()

        log.debug('Render of print photo screen completed.')

    def RenderSendToPrint(self, event):
        log.info('Rendering sent to print screen.')

        self.current_view = views.SentToPrintView(self.context)
        self.current_view.Show()

    def ClearScreen(self, event):
        self.current_view.Destroy()
        
    def ExitApp(self, event):
        sys.exit()

    # Binded methods

    def IsEscKey(self, event):
        key_code = event.kwargs.get('key_code', wx.WXK_NONE)
        return (key_code == self.context.KEY_ESCAPE)

    def IsLeftKey(self, event):
        key_code = event.kwargs.get('key_code', wx.WXK_NONE)
        return (key_code == self.context.KEY_LEFT)

    def IsRightKey(self, event):
        key_code = event.kwargs.get('key_code', wx.WXK_NONE)
        return (key_code == self.context.KEY_RIGHT)

    def IsLeftRightKey(self, event):
        key_code = event.kwargs.get('key_code', wx.WXK_NONE)
        return (key_code == self.context.KEY_LEFT or key_code == self.context.KEY_RIGHT)

    def IsCountdownDone(self, event):
        return self.countdown < 0

    def HasEnoughPhotos(self, event):
        return len(self.photo_storage.GetPhotos()) >= 3

    # wxPython event bindings

    def OnAnyButton(self, event):
        key_code = event.GetKeyCode()
        log.debug('Got button event {}.'.format(key_code))
        
        if key_code == self.context.KEY_F12:
            self.frame.ShowFullScreen(True)

        self.KeyDown(key_code=key_code)

    def OnCountdownTimerExpiry(self, event):
        self.CountExpired()

    def OnPrintNotifExpiry(self, event):
        self.PrintPeriodExpired()
