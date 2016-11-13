
from . import state
from . import panels
import wx
import wx.lib.newevent



# Custom events emitted by the system
AnyButtonEvent, EVT_ANY_BUTTON = wx.lib.newevent.NewCommandEvent()

class MainStateMacine(state.StateMachine):
    def OnEntry(self):
        pass


class ScreenSaverState(state.State):

    Activated = False

    def __init__(self, frame):
        self.frame = frame
        self.activated = False

    def OnEntry(self):
        panel = panels.ScreenSaverPanel(self.frame)
        self.frame.Show()
        pass

    def OnEvent(self, event):
        print("got the event!")

    def OnExit(self):
        pass
