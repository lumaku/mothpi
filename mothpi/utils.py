# !/usr/bin/python3
# -*- coding:utf-8 -*-

import argparse
from pathlib import Path
import urllib.request, json
import datetime
from threading import Timer, Lock
import os
import time


from display import Epaper, paint_simple_text_output


class WeatherStation:
    """
    Example:

    x = WeatherStation()
    x.get_todays_weather_dict()
    """

    # https://api.brightsky.dev/weather?lat=48.150533822545&lon=11.56845056702451&date=2021-08-27
    brightsky_url = "https://api.brightsky.dev/weather?lat={lat}&lon={lon}&date={date}"

    def date_str_from_datetime(self, dt: datetime.datetime):
        date_str = dt.strftime("%Y-%m-%d")
        return date_str

    def get_todays_weather_dict(self, lat=48.151, lon=11.568, date="2021-08-27"):
        parameter_dict = {"lat": lat, "lon": lon, "date": date}
        address = self.brightsky_url.format(**parameter_dict)
        print(address)
        try:
            with urllib.request.urlopen(address) as url:
                data = json.loads(url.read().decode())
                return data
        except:
            return {}


class Periodic(object):
    """
    A periodic task running in threading.Timers
    https://stackoverflow.com/questions/2398661/schedule-a-repeating-event-in-python-3
    """

    def __init__(self, interval, function, **kwargs):
        self._lock = Lock()
        self._timer = None
        self.function = function
        self.interval = interval
        self.kwargs = kwargs
        self._stopped = True
        if kwargs.pop("autostart", True):
            self.start()

    def start(self, from_run=False):
        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self._lock.release()

    def _run(self):
        self.start(from_run=True)
        self.function(**self.kwargs)

    def stop(self):
        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self._lock.release()


def get_parser():
    """Obtain an argument-parser for the script interface."""
    parser = argparse.ArgumentParser(
        description="Mothpi",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--log_level",
        type=lambda x: x.upper(),
        default="INFO",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"),
        help="The verbose level of logging",
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=False,
        default=None,
        help="Supplemental configuration file.",
    )
    return parser


def reboot():
    message = paint_simple_text_output(output_string="rebooting...")
    Epaper.display(message)
    time.sleep(1)
    os.system("sudo reboot")
