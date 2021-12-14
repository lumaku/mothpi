# !/usr/bin/python3
# -*- coding:utf-8 -*-

"""
Mothpi

Configuration utility for Mothpi.

Usage:
    - Import as regular Python object
    - Run this file from bash to obtain configuration

2021, Technische Universität München, Ludwig Kürzinger

"""

import logging
import sys
from pathlib import Path
from types import SimpleNamespace
import json

MOTHPI_BASE_DIRECTORY = Path.home() / "mothpi"
CONFIG_BASE_NAME = "mothpi.conf"
# Add possible configuration file locations (last item is taken first)
CONFIG_FILE_PATHS: list = [
    Path.home() / ".config" / CONFIG_BASE_NAME,
    Path.home() / CONFIG_BASE_NAME,
    Path.home() / ".mothpi",
]


class MothConf(SimpleNamespace):
    """Configuration object for MothPi.

    The dict of this object contains the configuration.
    This is not compatible with @property decorators.

    Also, variables are described by the same variable name
    with a preceding underscore (always type str).
    """
    # coordinates
    _lat = "Latitude coordinate"
    lat = 48.151
    _lon = "Longitude coordinate"
    lon = 11.568
    # Take pictures in a certain interval (in seconds)
    _capture_interval = "Take pictures in a certain interval (in seconds)"
    capture_interval = 60 * 5
    _polling_interval = "Obtain status information and " \
                        "update epaper screen at a certain interval (s)"
    polling_interval = 60 * 1
    _cam_reconnect_interval = "Interval time to reconnect to the camera (s)"
    cam_reconnect_interval = 60 * 60 * 5
    # Folder to save pictures
    # _pictures_save_folder = "Folder to save pictures in (Path)"
    pictures_save_folder = str(Path.home() / "pics")
    status_image_filename = "epaper_display.png"
    # Pictures file format (without * and .)
    # _pictures_file_format = "Pictures file format (without * and .)"
    pictures_file_format = "jpg"
    # Default relais config
    # _relais_conf = "Default relais configuration"
    relais_conf = {1: False, 2: False, 3: True}
    config_file_name = None
    # optional: use weather data to restrict storage use
    _use_weather_data = "Optional: use weather data to restrict storage use"
    use_weather_data = False
    # optional daily reboot at noon (only do this with correct time stamps)
    _daily_reboot = "Daily reboot at noon " \
                    "(only activate this with correct system time)"
    daily_reboot = True
    # if needed, only capture at good weather conditions
    _power_save_weather = "Only capture at good weather conditions"
    power_save_weather = False
    # if needed, deactivate the lamp during daytime
    _power_save_daylight = "Deactivate the lamp during daytime"
    power_save_daylight = True
    # if needed, deactivate the lamp when taking a picture
    _lamp_during_capture = "Deactivate the lamp when taking a picture"
    lamp_during_capture = False
    # if needed, only capture at daylight times
    _capture_filter_daytime = "Only capture at daylight times"
    capture_filter_daytime = False

    def __init__(self, config_file=None, **kwargs):
        super().__init__(**kwargs)
        # Take the next best config file,
        # or the one supplied by argument
        for item in CONFIG_FILE_PATHS:
            fname = Path(item)
            if not config_file and fname.is_file():
                config_file = str(fname)
        if config_file is None:
            logging.error("No Configuration file found or supplied as argument!")
            logging.error("Starting with default config.")
            config_file = CONFIG_FILE_PATHS[-1]
        else:
            logging.info(f"Loading configuration from {config_file}")
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                self.__dict__.update(config)
            except:
                logging.error("Error reading file, using default configuration.")
        self.config_file_name = str(config_file)
        Path(self.pictures_save_folder).mkdir(parents=True, exist_ok=True)

    def save_config(self):
        with open(self.config_file_name, "w") as f:
            json.dump(self.__dict__, f)

    def get_dict(self):
        return {x: getattr(self, x) for x in self.__dir__() if not (x.startswith('_') or type(x) not in [int, float, dict, str, bool])}

    def get_descriptive_list(self):
        """Get a triple of key, value, description for configuration entries.

        dicts are not yet inlcuded, as they are harder to process.
        """
        descriptive_list = []
        for x in self.__dir__():
            description = "_" + x
            is_not_special = not x.startswith('_')
            has_description = hasattr(self, description)
            is_correct_type = type(x) in [int, float, str, bool]
            if is_not_special and has_description and is_correct_type:
                descriptive_list += [(x, getattr(self, x), getattr(self, description))]
        return descriptive_list

    def get_status_img_path(self):
        return Path(self.pictures_save_folder) / self.status_image_filename

    def __str__(self):
        config_dict = self.get_full_configuration()
        return str(config_dict)

    def get_num_stored_pictures(self):
        return len(list(Path(self.pictures_save_folder).glob(f"*.{self.pictures_file_format}")))
