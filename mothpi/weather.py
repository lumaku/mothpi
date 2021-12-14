# !/usr/bin/python3
# -*- coding:utf-8 -*-

"""
Weather and Sunshine utilities.

2021, Technische Universität München, Ludwig Kürzinger
"""

import logging
import urllib.request
import json
import datetime
from suntime import Sun


class Weather:
    """Provide a weather interface.

    In this case, we use the Brightsky API.
    The last weather status is stored in the weather instance.

    Example:
    >> x = WeatherStation()
    >> x.get_todays_weather_dict()
    """

    current_weather = {"wind_speed": 0.0, "temperature": 15.0}
    server_weather = {}

    # Example:
    # https://api.brightsky.dev/weather?lat=48.150533822545&lon=11.56845056702451&date=2021-12-08
    brightsky_url = "https://api.brightsky.dev/weather?lat={lat}&lon={lon}&date={date}"

    def date_str_from_datetime(self, dt: datetime.datetime):
        """Convert date to the date string used in weather requests."""
        date_str = dt.strftime("%Y-%m-%d")
        return date_str

    def get_weather_dict(self, lat=48.151, lon=11.568, date=None):
        """Get weather information from API."""
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
        """Store latest weather information in the dictionary."""
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
        """Check wheather the weather is safe for moths.

        TODO: the values should be configurable
        """
        if self.current_weather["wind_speed"] > wind_speed_max:
            return False
        if temperature_min <= self.current_weather["temperature"] <= temperature_max:
            return False
        return True


def is_sunshine(lat=48.151, lon=11.568, at_time=None):
    """Determine whether we have sunshine or not."""
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
