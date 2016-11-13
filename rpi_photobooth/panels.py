
import wx
import pkg_resources

class ScreenSaverPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        bgimg_path = pkg_resources.resource_filename('rpi_photobooth.resources.images', 'ScreenSaver.jpg')
        self.bg_img = wx.Image(bgimg_path, wx.BITMAP_TYPE_JPEG)
        self.img_ctrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(self.bg_img))

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Layout()
        self.Update()

    def OnSize(self, event):

        h = event.GetSize()[1]
        w = event.GetSize()[0]

        print("Resizing image {}x{}".format(w, h))
        self.bg_img.Rescale(w, h, wx.IMAGE_QUALITY_HIGH)
        self.img_ctrl.SetBitmap(wx.Bitmap(self.bg_img))
        self.Layout()
        self.Refresh()

