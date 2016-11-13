import wx
from . import states

current_frame = None
button_state = 'up'
def main():
    global current_frame
    # Do the main function here.
    app = wx.App()

    frame = wx.Frame(None, style=wx.DEFAULT_FRAME_STYLE)
    frame.ShowFullScreen(True)

    state = states.ScreenSaverState(frame)
    state.OnEntry()

    # Create the timers to check buttons
    timer = wx.Timer(frame)
    frame.Bind(wx.EVT_TIMER, CheckButton, timer)
    
    current_frame = frame
    timer.Start(100)
    app.MainLoop()

def CheckButton(event):
    global button_state
    if button_state == 'down':
        if not wx.GetKeyState(wx.WXK_HOME):
            print('keyup')
            wx.PostEvent(current_frame, states.AnyButtonEvent(wx.NewId()))
            button_state = 'up' 
    elif button_state == 'up':
        print('checking')
        if wx.GetKeyState(wx.WXK_HOME):
            print('keydown')
            button_state = 'down'
