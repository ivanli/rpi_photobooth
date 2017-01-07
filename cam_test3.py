import wx
import cv2

import logging as log

class viewWindow(wx.Frame):
    imgSizer = (640,480)
    def __init__(self, parent, title="View Window"):
        super(viewWindow,self).__init__(parent)
        log.basicConfig(format='%(levelname)s: %(message)s (%(filename)s:%(lineno)d)', level=log.DEBUG)

        #self.pnl = wx.Panel(self)
        #self.vbox = wx.BoxSizer(wx.VERTICAL)
        #self.image = wx.Image(self.imgSizer[0],self.imgSizer[1])

        #self.imageBit = wx.BitmapFromImage(self.image)
        #self.staticBit = wx.StaticBitmap(self.pnl,wx.ID_ANY,
        #    self.imageBit)

        #self.vbox.Add(self.staticBit)
        #self.pnl.SetSizer(self.vbox)

        self.timex = wx.Timer(self, wx.ID_OK)
        self.timex.Start(1000/30)
        self.Bind(wx.EVT_TIMER, self.redraw, self.timex)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.capture = cv2.VideoCapture(0)

        self.SetSize(self.imgSizer)

    def redraw(self,e):
        log.debug('Redrawing')
        ret, frame = self.capture.read()
        if ret:
            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.Refresh()

    def OnPaint(self, e):
        log.debug('Painting')
        height, width = self.frame.shape[:2]
        image = wx.Image(width, height, self.frame)

        bitmap = wx.Bitmap(width, height)
        bitmap.CopyFromBuffer(self.frame, wx.BitmapBufferFormat_RGB)
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(bitmap, 0, 0)


def main():
    app = wx.App()
    frame = viewWindow(None)
    frame.Center()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
