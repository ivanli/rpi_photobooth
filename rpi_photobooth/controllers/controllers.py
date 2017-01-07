import logging as log
import sys
import wx
import transitions
import pkg_resources

import PIL.Image

import cv2
import cv

from ..views import views

class Photobooth:

    def __init__(self, frame, sizer, webcam, camera, photo_storage, printer):
        self.frame = frame
        self.sizer = sizer

        # Setup peripherals
        self.webcam = webcam
        self.webcam.Start()

        self.camera = camera
        self.photo_storage = photo_storage
        self.printer = printer

        # Create state machine for photobooth
        s = [
            transitions.State(name='Init'),
            transitions.State(name='Start', on_enter=['BindAnyButton', 'ClearPhotos', 'RenderStart'], on_exit=['ClearScreen']),
            transitions.State(name='Countdown', on_enter=['StartCountdown', 'RenderCountdown'], on_exit=['StopCountdown', 'ClearScreen']),
            transitions.State(name='ReviewPhoto', on_enter=['RenderReviewPhoto'], on_exit=['ClearScreen']),
            transitions.State(name='PrintPhoto', on_enter=['CreatePrint', 'RenderPrintPhoto', 'StartPrintPhoto'], on_exit=['ClearScreen']),
            transitions.State(name='Exit', on_enter=['ExitApp'])
        ]
        t = [
            { 'trigger':'KeyDown', 'source':'*', 'dest':'Exit', 'conditions':'IsEscKey' },

            { 'trigger':'KeyDown', 'source':'Start', 'dest':'Countdown', 'conditions':'IsLeftRightKey' },
            { 'trigger':'CountExpired', 'source':'Countdown', 'dest':'ReviewPhoto', 'conditions':'IsCountdownDone', 'prepare':'DecrementCountdown', 'before':'TakePhoto' },
            { 'trigger':'KeyDown', 'source':'ReviewPhoto', 'dest':'PrintPhoto', 'conditions':['IsRightKey', 'HasEnoughPhotos'] },
            { 'trigger':'KeyDown', 'source':'ReviewPhoto', 'dest':'Countdown', 'conditions':'IsRightKey' },
            { 'trigger':'KeyDown', 'source':'ReviewPhoto', 'dest':'Countdown', 'conditions':'IsLeftKey', 'before':'DeleteLastPhoto' },
            { 'trigger':'Printed', 'source':'PrintPhoto', 'dest':'Start' },
        ]
        initial_s = 'Init'
        fsm = transitions.Machine(model=self, send_event=True, states=s, transitions=t, initial=initial_s)
        self.to_Start()


    # State / transition triggered methods

    def BindAnyButton(self, event):
        self.frame.Bind(wx.EVT_CHAR_HOOK, self.OnAnyButton)

    def StartCountdown(self, event):
        log.info('Starting countdown.')
        self.countdown = 1

        self.countdown_timer = wx.Timer(self.frame)
        self.countdown_timer.Start(1000)
        self.frame.Bind(wx.EVT_TIMER, self.OnCountdownTimerExpiry)
        
        log.debug('Countdown started with initial count {}.'.format(self.countdown))

    def DecrementCountdown(self, event):
        log.info('Decrementing count.')
        self.countdown -= 1
        if self.countdown >= 0:
            self.current_view.SetCount(self.countdown)

        log.debug('Countdown is now {}'.format(self.countdown))

    def StopCountdown(self, event):
        self.frame.Unbind(wx.EVT_TIMER)
        self.countdown_timer.Stop()

    def TakePhoto(self, event):
        self.camera.TakePhoto()

    def DeleteLastPhoto(self, event):
        self.photo_storage.DeleteLast()

    def CreatePrint(self, event):
        template_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'PrintTemplate.png')
        image = PIL.Image.open(template_path)

        log.debug('Template image size is {}.'.format(image.size))

        # Assemble print image 
        photos = self.photo_storage.GetPhotos()
        photos[-3].thumbnail((560, 420))
        photos[-2].thumbnail((560, 420))
        photos[-1].thumbnail((560, 420))
        image.paste(photos[-3], (20, 154))
        image.paste(photos[-3], (620, 154))
        image.paste(photos[-2], (20, 621))
        image.paste(photos[-2], (620, 621))
        image.paste(photos[-1], (20, 1087))
        image.paste(photos[-1], (620, 1087))

        self.final_print = image

    def StartPrintPhoto(self, event):
        log.info('Starting photo print.')

        self.print_id = self.printer.PrintImage(self.final_print)

        # Set a timer to check whether the job was done
        self.frame.Bind(wx.EVT_TIMER, self.OnPrintPhotoTimerExpiry)
        self.print_timer = wx.Timer(self.frame)
        self.print_timer.Start(500)

        log.debug('Photo printing started.')

    def ClearPhotos(self, event):
        self.photo_storage.Clear()

    def RenderStart(self, event):
        self.current_view = views.StartPanel(self.frame, self.webcam)
        self.frame.Layout()
        self.frame.Refresh()

    def RenderCountdown(self, event):
        self.current_view = views.CountdownPanel(self.frame, self.webcam, 1)
        self.frame.Layout()
        self.frame.Refresh()

    def RenderReviewPhoto(self, event):
        log.info('Rendering review photo screen.')

        self.current_view = views.ReviewPhotoPanel(self.frame, self.photo_storage.GetLast())
        self.frame.Layout()
        self.frame.Refresh()

        log.debug('Render of review photo screen completed.')

    def RenderPrintPhoto(self, event):
        log.info('Rendering print photo screen.')

        self.current_view = views.PrintPhotoPanel(self.frame, self.final_print)
        self.frame.Layout()
        self.frame.Refresh()

        log.debug('Render of print photo screen completed.')

    def ClearScreen(self, event):
        self.frame.GetSizer().Clear()
        self.current_view.Destroy()
        
    def ExitApp(self, event):
        sys.exit()

    # Binded methods

    def IsEscKey(self, event):
        key_code = event.kwargs.get('key_code', wx.WXK_NONE)
        return (key_code == wx.WXK_ESCAPE)

    def IsLeftKey(self, event):
        key_code = event.kwargs.get('key_code', wx.WXK_NONE)
        return (key_code == wx.WXK_LEFT)

    def IsRightKey(self, event):
        key_code = event.kwargs.get('key_code', wx.WXK_NONE)
        return (key_code == wx.WXK_RIGHT)

    def IsLeftRightKey(self, event):
        key_code = event.kwargs.get('key_code', wx.WXK_NONE)
        return (key_code == wx.WXK_LEFT or key_code == wx.WXK_RIGHT)

    def IsCountdownDone(self, event):
        return self.countdown < 0

    def HasEnoughPhotos(self, event):
        return len(self.photo_storage.GetPhotos()) >= 3


    # wxPython event bindings

    def OnAnyButton(self, event):
        key_code = event.GetKeyCode()
        log.debug('Got button wx event {}.'.format(key_code))
        
        if key_code == wx.WXK_F12:
            self.frame.ShowFullScreen(True)

        self.KeyDown(key_code=key_code)

    def OnCountdownTimerExpiry(self, event):
        self.CountExpired()

    def OnPrintPhotoTimerExpiry(self, event):
        if self.printer.HasFinished():
            self.print_timer.Stop()
            self.Printed()


