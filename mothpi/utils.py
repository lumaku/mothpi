# !/usr/bin/python3
# -*- coding:utf-8 -*-

import logging
import urllib.request, json
import datetime
from threading import Timer, Lock
import os
import time
import shutil
from suntime import Sun
from netifaces import interfaces, ifaddresses, AF_INET


# mothpi-specific
from display import Epaper, paint_simple_text_output


class Weather:
    """
    Example:

    x = WeatherStation()
    x.get_todays_weather_dict()
    """

    current_weather = {"wind_speed": 0.0, "temperature": 15.0}
    server_weather = {}

    # https://api.brightsky.dev/weather?lat=48.150533822545&lon=11.56845056702451&date=2021-12-08
    brightsky_url = "https://api.brightsky.dev/weather?lat={lat}&lon={lon}&date={date}"

    def date_str_from_datetime(self, dt: datetime.datetime):
        date_str = dt.strftime("%Y-%m-%d")
        return date_str

    def get_weather_dict(self, lat=48.151, lon=11.568, date=None):
        if not date:
            date = self.date_str_from_datetime(datetime.datetime.now())
        parameter_dict = {"lat": lat, "lon": lon, "date": date}
        address = self.brightsky_url.format(**parameter_dict)
        data = {}
        try:
            with urllib.request.urlopen(address) as url:
                data = json.loads(url.read().decode())
            logging.info(f"Reading weather information from {address}")
        except:
            logging.error(f"Failed to retrieve weather information from {address}")
        return data

    def update_weather(self, lat=48.151, lon=11.568):
        weather_dict = self.get_weather_dict(lat, lon)
        hour = datetime.datetime.now().hour
        if "weather" in weather_dict and hour in weather_dict["weather"]:
            self.current_weather["wind_speed"] = float(
                weather_dict["weather"][hour]["wind_speed"]
            )
            self.current_weather["temperature"] = float(
                weather_dict["weather"][hour]["temperature"]
            )

    def safe_for_moths_weather(
        self, wind_speed_max=10, temperature_min=-5.0, temperature_max=50.0
    ):
        if self.current_weather["wind_speed"] > wind_speed_max:
            return False
        if temperature_min <= self.current_weather["temperature"] <= temperature_max:
            return False
        return True


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


def reboot():
    message = paint_simple_text_output(output_string="rebooting...")
    Epaper.display(message)
    time.sleep(1)
    os.system("sudo reboot")


def is_disk_full(path):
    total, used, free = shutil.disk_usage(path)
    mib = 1000 * 1000
    if free < (50 * mib):
        return True
    else:
        return False


def get_disk_free_capacity(path):
    total, used, free = shutil.disk_usage(path)
    mib = 1000 * 1000
    free -= 50 * mib
    if free <= 0:
        free = 0
    free /= 5 * mib  # how many 5MiB pics fit into the remaining space?
    return int(free)


def is_sunshine(lat=48.151, lon=11.568, at_time=None):
    if at_time is None:
        at_time = datetime.datetime.now(datetime.timezone.utc)
    # Please assert correct time zone information
    assert at_time.tzinfo
    sun = Sun(lat, lon)
    today_sun_rises_at = sun.get_local_sunrise_time(at_time)
    today_sun_sets_at = sun.get_local_sunset_time(at_time)
    if today_sun_rises_at < at_time < today_sun_sets_at:
        return True
    return False


def get_ip_addresses():
    filter_addresses = ["127.0.0.1", "No IP addr"]
    local_interfaces = {}
    for interface_name in interfaces():
        addresses = [
            i["addr"]
            for i in ifaddresses(interface_name).setdefault(
                AF_INET, [{"addr": "No IP addr"}]
            )
        ]
        addresses = list(filter(lambda item: item not in filter_addresses, addresses))
        if interface_name not in ["lo"] and addresses:
            local_interfaces[interface_name] = addresses
    return local_interfaces
    # As string:
    # " ".join([f"{item}:{a[item][0]};" for item in a.keys()])
