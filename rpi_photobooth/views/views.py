import logging as log

import pkg_resources
import wx
import wx.lib.newevent
import cv2
import cv

import PIL.Image

ReadyEvent, EVT_READY = wx.lib.newevent.NewEvent()
PhotoTakenEvent, EVT_PHOTO_TAKEN = wx.lib.newevent.NewEvent()

class PhotoboothPanel(wx.Panel):

    def __init__(self, parent):
        super(PhotoboothPanel, self).__init__(parent)

    def ToWxImage(self, myPilImage, copyAlpha=False):
        hasAlpha = myPilImage.mode[ -1 ] == 'A'
        if copyAlpha and hasAlpha :  # Make sure there is an alpha layer copy.
    
            myWxImage = wx.Image( *myPilImage.size )
            myPilImageCopyRGBA = myPilImage.copy()
            myPilImageCopyRGB = myPilImageCopyRGBA.convert( 'RGB' )    # RGBA --> RGB
            myPilImageRgbData =myPilImageCopyRGB.tobytes()
            myWxImage.SetData( myPilImageRgbData )
            myWxImage.SetAlphaBuffer( myPilImageCopyRGBA.tobytes()[3::4] )  # Create layer and insert alpha values.
    
        else :    # The resulting image will not have alpha.
    
            myWxImage = wx.Image( *myPilImage.size )
            myPilImageCopy = myPilImage.copy()
            myPilImageCopyRGB = myPilImageCopy.convert( 'RGB' )    # Discard any alpha from the PIL image.
            myPilImageRgbData =myPilImageCopyRGB.tobytes()
            myWxImage.SetData( myPilImageRgbData )
    
        return myWxImage

    def ToWxBitmap(self, pil_image, with_alpha=False):
        return wx.Bitmap(self.ToWxImage(pil_image, with_alpha))
    
class StartPanel(PhotoboothPanel):
    fps = 30

    def __init__(self, parent, webcam):
        super(StartPanel, self).__init__(parent)

        # Setup background image. Load it as a PIL image as the library seems to be more stable in the Pi. Had
        # segfault issues with wx's imaging operations.
        frame_image_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'StartScreen.png')
        self.frame_image = PIL.Image.open(frame_image_path)
        self.scaled_frame_bitmap = None

        width, height = self.frame_image.size
        self.SetSize(0, 0, width, height)

        self.webcam = webcam
        self.webcam_bitmap = None

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.GetNextFrame)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Start a refresh timer so we know when to get the next frame from the webcam.
        self.timer = wx.Timer(self)
        self.timer.Start(1000. / self.fps)

        # Add self to parent so it's displayed. We want to keep the correct aspect ratio for images to look nice
        parent.GetSizer().Add(self, 1, wx.SHAPED | wx.ALIGN_CENTER)
        self.SetFocus()
        self.Show()

    def __del__(self):
        self.timer.Stop()
        self.Unbind(wx.EVT_PAINT)
        self.Unbind(wx.EVT_TIMER)
        self.Unbind(wx.EVT_SIZE)
        
    def OnSize(self, event):
        self.window_h = self.GetClientSize()[1]
        self.window_w = self.GetClientSize()[0]
        #log.debug("Got size event with {}x{}".format(self.window_w, self.window_h))

        # Webcam feed is resized on each frame received.
        self.webcam_x = int(304.0 / 1440.0 * self.window_w)
        self.webcam_y = int(132.0 / 900.0 * self.window_h)
        self.webcam_w = int(836.0 / 1440.0 * self.window_w)
        self.webcam_h = int(627.0 / 900.0 * self.window_h)

        # Resize the image here. Only done when window is resized.
        resized_frame_image = self.frame_image.resize((self.window_w, self.window_h), PIL.Image.BILINEAR)
        self.scaled_frame_bitmap = self.ToWxBitmap(resized_frame_image, with_alpha=True)

        #log.debug('Webcam size is {}x{}.'.format(self.webcam_w, self.webcam_h))

    def OnPaint(self, event):
        # Here we draw all elements of the screen. Need to manually draw because we want to control the overlaying of elements
        # ourselves - ie. the background is above the webcam view so it creates a border.
        #log.debug('Got paint event.')

        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        if self.webcam_bitmap:
            dc.DrawBitmap(self.webcam_bitmap, self.webcam_x, self.webcam_y)
        if self.scaled_frame_bitmap is not None:
            dc.DrawBitmap(self.scaled_frame_bitmap, 0, 0)

    def GetNextFrame(self, event):
        #log.debug('Capturing next frame.')

        ret, frame = self.webcam.Read()
        if ret:
            img = PIL.Image.fromarray(frame)
            img = img.resize((self.webcam_w, self.webcam_h), PIL.Image.NEAREST)
            self.webcam_bitmap = self.ToWxBitmap(img)

            # Force a re-paint with new frame retrieved.
            self.Refresh()


class CountdownPanel(wx.Panel):
    fps = 15
    ID_COUNTDOWN_TIMER = 0
    ID_REFRESH_TIMER = 1

    def __init__(self, parent, webcam, start_count):
        super(CountdownPanel, self).__init__(parent)
        
        self.current_count = start_count
        self.countdown_done = False

        # Setup first background image.
        bgimg_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'CountdownScreen{}.png'.format(start_count))
        self.bg_img = wx.Image(bgimg_path, wx.BITMAP_TYPE_PNG)

        # Need to set size to ensure our parent gives us the correct space to render. Due to not using sizer.:wa
        self.SetSize(0, 0, self.bg_img.GetWidth(), self.bg_img.GetHeight())

        # Save webcame for later use
        self.webcam = webcam
        self.webcam_bitmap = None

        # Bind to wx events.
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.OnTimerExpiry)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Start a refresh timer so we know when to get the next frame from the webcam.
        self.refresh_timer = wx.Timer(self, self.ID_REFRESH_TIMER)
        self.refresh_timer.Start(1000. / self.fps)

        # Add self to parent so it's displayed. We want to keep the correct aspect ratio for images to look nice
        parent.GetSizer().Add(self, 1, wx.SHAPED | wx.ALIGN_CENTER)
        self.SetFocus()
        self.Show()

    def __del__(self):
        self.refresh_timer.Stop()

    def SetCount(self, count):
        bgimg_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'CountdownScreen{}.png'.format(count))
        self.bg_img = wx.Image(bgimg_path, wx.BITMAP_TYPE_PNG)
        

    def OnSize(self, event):
        window_h = self.GetClientSize()[1]
        window_w = self.GetClientSize()[0]
        log.debug("Got size event with {}x{}".format(window_w, window_h))

        # Webcam feed is resized on each frame received.
        self.webcam_x = 380.0 / 1920.0 * window_w
        self.webcam_y = 220.0 / 1201.0 * window_h
        self.webcam_w = 1165.0 / 1920.0 * window_w
        self.webcam_h = 765.0 / 1201.0 * window_h

    def OnPaint(self, event):
        # Here we draw all elements of the screen. Need to manually draw because we want to control the overlaying of elements
        # ourselves - ie. the background is above the webcam view so it creates a border.
        log.debug('Got paint event.')

        window_h = self.GetClientSize()[1]
        window_w = self.GetClientSize()[0]
        background_image_copy = wx.Image(self.bg_img)
        background_image_copy.Rescale(window_w, window_h, wx.IMAGE_QUALITY_HIGH)
        self.scaled_bg_img = wx.Bitmap(background_image_copy)

        dc = wx.BufferedPaintDC(self)
        if self.webcam_bitmap:
            dc.DrawBitmap(self.webcam_bitmap, self.webcam_x, self.webcam_y)

        dc.DrawBitmap(self.scaled_bg_img, 0, 0, useMask=True)

    def OnTimerExpiry(self, event):
        if (event.GetId() == self.ID_REFRESH_TIMER):
            self.GetNextFrame()

    def GetNextFrame(self):
        log.debug('Capturing next frame.')

        ret, frame = self.webcam.Read()
        if ret:
            height, width = frame.shape[:2]
            log.debug('Got webcam frame. Size: {}x{}'.format(width, height))

            img = wx.Image(width, height, frame)
            img.Rescale(self.webcam_w, self.webcam_h, wx.IMAGE_QUALITY_HIGH)
            self.webcam_bitmap = wx.Bitmap(img)

            # Force a re-paint with new frame retrieved.
            self.Refresh()

class ReviewPhotoPanel(wx.Panel):

    def __init__(self, parent, image):
        super(ReviewPhotoPanel, self).__init__(parent)
        
        # Setup first background image.
        bgimg_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'ReviewPhotoScreen.png')
        self.bg_img = wx.Image(bgimg_path, wx.BITMAP_TYPE_PNG)

        # Need to set size to ensure our parent gives us the correct space to render. Due to not using sizer.:wa
        self.SetSize(0, 0, self.bg_img.GetWidth(), self.bg_img.GetHeight())

        self.photo_image = PilImageToWxImage(image)

        # Bind to wx events.
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Add self to parent so it's displayed. We want to keep the correct aspect ratio for images to look nice
        parent.GetSizer().Add(self, 1, wx.SHAPED | wx.ALIGN_CENTER)
        self.SetFocus()
        self.Show()

    def OnSize(self, event):
        window_h = self.GetClientSize()[1]
        window_w = self.GetClientSize()[0]
        log.debug("Got size event with {}x{}".format(window_w, window_h))

        # Webcam feed is resized on each frame received.
        self.photo_x = 380.0 / 1920.0 * window_w
        self.photo_y = 220.0 / 1201.0 * window_h
        self.photo_w = 1165.0 / 1920.0 * window_w
        self.photo_h = 765.0 / 1201.0 * window_h

    def OnPaint(self, event):
        # Here we draw all elements of the screen. Need to manually draw because we want to control the overlaying of elements
        # ourselves - ie. the background is above the webcam view so it creates a border.
        log.debug('Got paint event.')

        window_h = self.GetClientSize()[1]
        window_w = self.GetClientSize()[0]

        bg_image = wx.Image(self.bg_img)
        bg_image.Rescale(window_w, window_h, wx.IMAGE_QUALITY_HIGH)
        scaled_bg_bitmap = wx.Bitmap(bg_image)

        photo_image = wx.Image(self.photo_image)
        photo_image.Rescale(self.photo_w, self.photo_h, wx.IMAGE_QUALITY_HIGH)
        scaled_photo_bitmap = wx.Bitmap(photo_image)

        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(scaled_photo_bitmap, self.photo_x, self.photo_y)
        dc.DrawBitmap(scaled_bg_bitmap, 0, 0, useMask=True)
        
class PrintPhotoPanel(wx.Panel):

    def __init__(self, parent, final_print):
        super(PrintPhotoPanel, self).__init__(parent)

        # Setup first background image.
        bgimg_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'PrintPhotoScreen.png')
        self.bg_img = wx.Image(bgimg_path, wx.BITMAP_TYPE_PNG)
        self.scaled_bg_bitmap = None

        # Need to set size to ensure our parent gives us the correct space to render. Due to not using sizer.:wa
        self.SetSize(0, 0, self.bg_img.GetWidth(), self.bg_img.GetHeight())

        self.photo_image = final_print
        self.scaled_photo_image = None

        # Bind to wx events.
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Add self to parent so it's displayed. We want to keep the correct aspect ratio for images to look nice
        parent.GetSizer().Add(self, 1, wx.SHAPED | wx.ALIGN_CENTER)
        self.SetFocus()
        self.Show()

    def OnSize(self, event):
        window_h = self.GetClientSize()[1]
        window_w = self.GetClientSize()[0]

        bg_image = wx.Image(self.bg_img)
        bg_image.Rescale(window_w, window_h, wx.IMAGE_QUALITY_HIGH)
        self.scaled_bg_bitmap = wx.Bitmap(bg_image)

        photo_w = int(467. / 1920. * window_w)
        photo_h = int(700. / 1200. * window_h)
        self.photo_x = int(window_w / 2 - photo_w / 2)
        self.photo_y = int(310. / 1200. * window_h)

        log.debug('Scaling to {}x{}..'.format(photo_w, photo_h))

        resized_image = self.photo_image.resize((photo_w, photo_h))
        photo_image = PilImageToWxImage(resized_image)
        self.scaled_photo_bitmap = wx.Bitmap(photo_image)

        self.Refresh()

    def OnPaint(self, event):
        # Here we draw all elements of the screen. Need to manually draw because we want to control the overlaying of elements
        # ourselves - ie. the background is above the webcam view so it creates a border.
        log.debug('Got paint event.')

        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self.scaled_bg_bitmap, 0, 0)
        dc.DrawBitmap(self.scaled_photo_bitmap, self.photo_x, self.photo_y)
        
        log.debug('Paint event handled.')

def PilImageToWxImage(myPilImage, copyAlpha=True ) :
    """This function was copied from https://wiki.wxpython.org/WorkingWithImages"""

    hasAlpha = myPilImage.mode[ -1 ] == 'A'
    if copyAlpha and hasAlpha :  # Make sure there is an alpha layer copy.

        myWxImage = wx.Image( *myPilImage.size )
        myPilImageCopyRGBA = myPilImage.copy()
        myPilImageCopyRGB = myPilImageCopyRGBA.convert( 'RGB' )    # RGBA --> RGB
        myPilImageRgbData =myPilImageCopyRGB.tobytes()
        myWxImage.SetData( myPilImageRgbData )
        myWxImage.SetAlphaBuffer( myPilImageCopyRGBA.tobytes()[3::4] )  # Create layer and insert alpha values.

    else :    # The resulting image will not have alpha.

        myWxImage = wx.Image( *myPilImage.size )
        myPilImageCopy = myPilImage.copy()
        myPilImageCopyRGB = myPilImageCopy.convert( 'RGB' )    # Discard any alpha from the PIL image.
        myPilImageRgbData =myPilImageCopyRGB.tobytes()
        myWxImage.SetData( myPilImageRgbData )

    return myWxImage

