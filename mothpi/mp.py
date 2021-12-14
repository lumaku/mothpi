# !/usr/bin/python3
# -*- coding:utf-8 -*-

"""
Mothpi

Put a Raspberry Pi in the woods and take pictures of moths.


2021, Technische Universität München, Ludwig Kürzinger
"""


import datetime
import queue
import logging
import time
from pathlib import Path
from typing import Union

# Mothpi imports
import gphoto2 as gp
from camera import MothCamera
from relais import Relais
from display import Epaper, paint_status_page, paint_simple_text_output
from config import MothConf
from utils import Periodic, reboot, is_disk_full, is_sunshine
from utils import Weather


class MothPi:
    state_queue = queue.Queue()
    pictures_queue = queue.Queue()
    camera = MothCamera()
    epaper_available = Epaper.is_available
    services = {}
    started_on = datetime.datetime.now()

    def __init__(self, configuration: Union[MothConf, str]):

        if type(configuration) == str:
            configuration = MothConf(config_file=configuration)

        self.config = configuration
        self.services["periodic_pictures"] = Periodic(
            interval=self.config.capture_interval,
            function=self.take_pictures,
            autostart=False,
        )
        self.services["periodic_status"] = Periodic(
            interval=self.config.polling_interval,
            function=self.poll_status,
            autostart=False,
        )
        self.status_dict = {
            "camera": self.camera.is_available,
            "display": Epaper.is_available,
            "up_since": datetime.datetime.now(),
            "last_picture": "No photo yet!",
            "footer1": "1:CamReconn",
            "footer2": "3: Reboot",
        }
        # initialize GPIOs
        self.set_relais()
        Epaper.set_button_handler(1, self.camera.reconnect)
        Epaper.set_button_handler(3, reboot)
        # Utilities
        self.weather = Weather
        self.weather.update_weather(lat=self.config.lat, lon = self.config.lon)
        # execute the services once to make sure they work:
        self.refresh_camera()
        self.poll_status()
        self.take_pictures()
        self.poll_status()

    def set_relais(self, state="on"):
        power_save_mode = self.power_save_mode
        if state == "on" and not power_save_mode:
            for item in self.config.relais_conf:
                if self.config.relais_conf[item]:
                    Relais.set_on(item)
                else:
                    Relais.set_off(item)
        elif state == "on" and power_save_mode:
            Relais.reset()
        elif state == "off":
            Relais.reset()
        else:
            logging.error(f"No valid relais state: {state}")

    def serve(self):
        for service in self.services.values():
            service.start()

    def stop_service(self):
        for service in self.services.values():
            service.stop()
        self.set_relais("off")
        time.sleep(1)

    def poll_status(self):
        self.status_dict["camera"] = self.camera.is_available
        self.status_dict["display"] = Epaper.is_available
        self.status_dict["num_pics"] = self.config.get_num_stored_pictures()
        self.status_dict["poll_time"] = datetime.datetime.now()
        status_image = paint_status_page(self.status_dict)
        cc_to =  self.config.get_status_img_path()
        Epaper.display(status_image, cc_to=str(cc_to))
        # If the device configured for reset
        if self.ready_for_restart:
            self.stop_service()
            reboot()

    def take_pictures(self):
        # switch off lamp if needed
        if self.config.capture_deactivate_lamp:
            self.set_relais("off")
        # capture
        picture_path = self.camera.capture()
        if picture_path and self.valid_capture_conditions:
            timestr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            self.status_dict["last_picture"] = timestr
            target = Path(self.config.pictures_save_folder) / (timestr + ".jpg")
            self.camera.save(picture_path, target)
        # turn lamp back on if needed
        if self.config.capture_deactivate_lamp:
            self.set_relais()

    def refresh_camera(self):
        self.camera.reconnect()

    @property
    def power_save_mode(self):
        if self.config.power_save_daylight and is_sunshine(lat=self.config.lat, lon = self.config.lon):
            return True
        if self.config.power_save_weather and Weather.safe_for_moths_weather():
            return True
        return False

    @property
    def valid_capture_conditions(self):
        if is_disk_full(self.config.pictures_save_folder):
            return False
        return not self.power_save_mode

    @property
    def ready_for_restart(self):
        if self.config.daily_reboot:
            # reboot "tomorrow noon".
            tomorrow_noon = self.started_on.replace(hour=12, minute=0, second=0)
            tomorrow_noon += datetime.timedelta(days=1)
            if datetime.datetime.now() > tomorrow_noon:
                return True
        return False

