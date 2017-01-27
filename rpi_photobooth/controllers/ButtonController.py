import logging as log

import RPi.GPIO as gpio

from ..views import Buttons

class GpioContext(object):
    def __init__(self):
        gpio.setmode(gpio.BOARD)

class ButtonCtrl(object):
    """Base class for implementing button controlling behaviour"""

    def Start(self):
        pass
    
    def Stop(self):
        """Puts the buttons back to a default state"""
        for button in self.buttons:
            button.SetLed(Buttons.STATE_OFF)

class AlternateButtonCtrl(ButtonCtrl):

    __STATE_LEFT = 0
    __STATE_RIGHT = 1

    def __init__(self, context, flash_rate_ms, left_button, right_button):
        self.flash_rate_ms = flash_rate_ms
        self.context = context
        self.left_button = left_button
        self.right_button = right_button

        self.state = self.__STATE_LEFT
        left_button.SetLed(Buttons.STATE_ON)
        right_button.SetLed(Buttons.STATE_OFF)
        
    def Start(self):
        self.context.StartPeriodicTimer(self.flash_rate_ms, self.__OnFlashExpiry)

    def Stop(self):
        self.context.StopTimer(self.__OnFlashExpiry)
        super(AlternateFlashButtonController, self).Stop()

    def __OnFlashExpiry(self, event):
        if self.state is self.__STATE_LEFT:
            left_button.SetLed(Buttons.STATE_OFF)
            right_button.SetLed(Buttons.STATE_ON)
            self.state = self.__STATE_RIGHT
        elif self.state is self.__STATE_RIGHT:
            left_button.SetLed(Buttons.STATE_ON)
            right_button.SetLed(Buttons.STATE_OFF)
            self.state = self.__STATE_LEFT




