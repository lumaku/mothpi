# !/usr/bin/python
# -*- coding:utf-8 -*-

##################################################

#           P26 ----> Relay_Ch1
# 			P20 ----> Relay_Ch2
# 			P21 ----> Relay_Ch3

##################################################
import logging

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

try:
    import RPi.GPIO as GPIO

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(Relay_Ch1, GPIO.OUT)
    GPIO.setup(Relay_Ch2, GPIO.OUT)
    GPIO.setup(Relay_Ch3, GPIO.OUT)
    GPIO_IS_AVAILABLE = True
    logging.info("GPIO is available")
except:
    GPIO_IS_AVAILABLE = False
    logging.info("GPIO offline!")

relais_channels = {
    1: Relay_Ch1,
    2: Relay_Ch2,
    3: Relay_Ch3,
}

relais_states = {
    1: False,
    2: False,
    3: False,
}


class Relais:
    @staticmethod
    def cleanup():
        GPIO.cleanup()
        Relais.reset()

    @staticmethod
    def set_on(channel):
        if channel not in relais_channels.keys():
            raise ValueError(f"channel has to be in {relais_channels.keys()}")
        if GPIO_IS_AVAILABLE:
            GPIO.output(relais_channels[channel], GPIO.LOW)
        relais_states[channel] = True
        logging.info(f"Channel {channel} ON!")

    @staticmethod
    def set_off(channel):
        if channel not in relais_channels.keys():
            raise ValueError(f"channel has to be in {relais_channels.keys()}")
        if GPIO_IS_AVAILABLE:
            GPIO.output(relais_channels[channel], GPIO.HIGH)
        relais_states[channel] = False
        logging.info(f"Channel {channel} OFF!")

    @staticmethod
    def reset():
        relais_states[1] = False
        relais_states[2] = False
        relais_states[3] = False
