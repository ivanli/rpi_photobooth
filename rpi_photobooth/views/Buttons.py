import logging as log

import RPi.GPIO as gpio

STATE_OFF = 0
STATE_ON = 1

class IlluminatedButton(object):

    __BOUNCE_TIME = 800
    __GPIO_EDGE = gpio.FALLING

    def __init__(self, gpio_context, input_channel, led_channel):
        self.gpio_context = gpio_context
        self.input_channel = input_channel
        self.led_channel = led_channel

        gpio.setup(input_channel, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.setup(led_channel, gpio.OUT)

        self.SetLed(STATE_OFF)

    def __del__(self):
        gpio.remove_event_detect(self.input_channel)
        self.SetLed(STATE_OFF)

    def SetLed(self, state):
        gpio.output(self.led_channel, state)

    def RegisterListener(self, listener):
        gpio.add_event_detect(self.input_channel, self.__GPIO_EDGE, callback=listener, bouncetime=self.__BOUNCE_TIME)

