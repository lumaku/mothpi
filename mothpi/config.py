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
import yaml
from utils import get_parser

MOTHPI_BASE_DIRECTORY = Path.home() / "mothpi"
CONFIG_BASE_NAME = "mothpi.conf"
# Add possible configuration file locations (last item is taken first)
CONFIG_FILE_PATHS: list = [
    Path.home() / ".config" / CONFIG_BASE_NAME,
    Path.home() / CONFIG_BASE_NAME,
    Path.home() / ".mothpi",
]


class MothConf(SimpleNamespace):
    # Take pictures in a certain interval (in seconds)
    capture_interval = 60 * 4
    polling_interval = 60 * 1
    cam_reconnect_interval = 60 * 60 * 5
    # Folder to save pictures
    pictures_save_folder = str(Path.home() / "pics")
    # Default relais config
    relais_conf = {1: True, 2: False, 3: False}
    config_file_name = None
    # optional: use weather data to restrict storage use
    use_weather_data = False
    # optional daily reboot at noon (only do this with correct time stamps)
    daily_reboot = False

    def __init__(self, config_file=None, **kwargs):
        super().__init__(**kwargs)
        # Take the next best config file,
        # or the one supplied by argument
        for item in CONFIG_FILE_PATHS:
            fname = Path(item)
            if not config_file and fname.is_file():
                config_file = fname
        if config_file is None:
            logging.error("No Configuration file found or supplied as argument!")
            logging.error("Starting with default config.")
            config_file = CONFIG_FILE_PATHS[-1]
            logging.error(f"Config file: {config_file}")
        else:
            logging.info(f"Loading configuration from {config_file}")
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
            self.__dict__.update(config)
        self.config_file_name = config_file
        Path(self.pictures_save_folder).mkdir(parents=True, exist_ok=True)

    def save_config(self):
        with open(self.config_file_name, "w") as f:
            yaml.dump(self.__dict__, f)

    def print_bash_variables(self):
        print(f"{'pictures_save_folder'.upper}={self.pictures_save_folder}")

    @property
    def num_stored_pictures(self):
        return len(list(Path(self.pictures_save_folder).glob("*.jpg")))


def main():
    # Initialize
    parser = get_parser()
    logging.getLogger().setLevel(logging.INFO)
    args = parser.parse_args()
    config = MothConf(config_file=args.config)
    config.print_bash_variables()


if __name__ == "__main__":
    main()
