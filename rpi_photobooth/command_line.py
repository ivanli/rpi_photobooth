import logging as log
import wx
import transitions

from .controllers import controllers
from .controllers import Cameras
from .controllers import Printers
from .views import Contexts

def main():
    global photobooth
    # Configure logging globally
    log.basicConfig(format='%(levelname)s: %(message)s (%(filename)s:%(lineno)d)', level=log.DEBUG)

    # Setup peripherals
    #webcam = Cameras.OpencvWebcam(0, (320, 240))
    webcam = Cameras.PygameWebcam(0, (320, 240))
    #webcam = Cameras.DummyPygameWebcam()
    webcam.Start()

    photo_storage = Cameras.FileSystemCameraStorage('./tmp/photobooth')

    camera = Cameras.GPhotoCamera(photo_storage, './tmp/photobooth/camera')
    #camera = Cameras.WebcamCamera(webcam, photo_storage)

    printer = Printers.CupsPrinter('CP910', './tmp/photobooth/printer')
    #printer = Printers.FilePrinter('./tmp/photobooth/printer', 5000)
    printer.Start()

    # Start the GUI app and create basic frame
    context = Contexts.PygameViewContext((1440, 900))

    photobooth = controllers.Photobooth(context, webcam, camera, photo_storage, printer)

    context.Run()
