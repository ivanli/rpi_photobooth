import logging as log
import wx
import transitions

from .controllers import controllers
from .controllers import Cameras
from .controllers import Printers

def main():
    global photobooth
    # Configure logging globally
    log.basicConfig(format='%(levelname)s: %(message)s (%(filename)s:%(lineno)d)', level=log.DEBUG)

    # Setup peripherals
    webcam = Cameras.OpencvWebcam(0, (320, 240))
    webcam.Start()
    photo_storage = Cameras.FileSystemCameraStorage('./tmp/photobooth')
    #camera = Cameras.GPhotoCamera(photo_storage, './tmp/photobooth/camera')
    camera = Cameras.WebcamCamera(webcam, photo_storage)
    printer = Printers.CupsPrinter('CP910', './tmp/photobooth/printer')
    printer.Start()

    # Start the GUI app and create basic frame
    app = wx.App()

    frame = wx.Frame(None, style=wx.DEFAULT_FRAME_STYLE)
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    frame.SetSizer(sizer)

    photobooth = controllers.Photobooth(frame, sizer, webcam, camera, photo_storage, printer)

    app.Bind(wx.EVT_CHAR_HOOK, OnKeyDown)

    log.info('Starting app')

    frame.Show()
    app.MainLoop()

def OnKeyDown(event):
    global photobooth
    log.debug('Got key down event')
    key_code = event.GetKeyCode()
    photobooth.KeyDown(key_code=key_code)

if __name__ == '__main__':
    main()
