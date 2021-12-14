# !/usr/bin/python3
# -*- coding:utf-8 -*-

"""
Mothpi.

Put a Raspberry Pi in the woods and take pictures of moths.
This unit provides the main control module.

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
from mothpi.camera import MothCamera
from mothpi.relais import Relais
from mothpi.display import Epaper, paint_status_page, paint_simple_text_output
from mothpi.config import config
from mothpi.utils import Periodic, reboot, is_disk_full, is_sunshine
from mothpi.utils import Weather, get_ip_addresses, get_disk_free_capacity


class MothPi:
    state_queue = queue.Queue()
    pictures_queue = queue.Queue()
    camera = MothCamera()
    epaper_available = Epaper.is_available
    services = {}
    started_on = datetime.datetime.now()

    def __init__(self):
        self.services["periodic_pictures"] = Periodic(
            interval=config.capture_interval,
            function=self.take_pictures,
            autostart=False,
        )
        self.services["periodic_status"] = Periodic(
            interval=config.polling_interval,
            function=self.poll_status,
            autostart=False,
        )
        self.status_dict = {
            "camera": self.camera.is_available,
            "display": Epaper.is_available,
            "up_since": datetime.datetime.now(),
            "last_picture": "No photo yet!",
        }
        # initialize GPIOs
        self.set_relais()
        self.status_dict["buttons"] = {1: "-", 2: "-", 3: "-", 4: "-"}
        self.status_dict["buttons"][1] = "Status"
        self.status_dict["buttons"][2] = "CamReconnect"
        self.status_dict["buttons"][3] = "Reboot"
        Epaper.set_button_handler(1, self.poll_status)
        Epaper.set_button_handler(2, self.camera.reconnect)
        Epaper.set_button_handler(3, reboot)
        # Utilities
        self.weather = Weather()
        self.weather.update_weather(lat=config.lat, lon=config.lon)
        # execute the services once to make sure they work:
        self.refresh_camera()
        self.poll_status()
        self.take_pictures()
        self.poll_status()

    def set_relais(self, state="on"):
        power_save_mode = self.power_save_mode
        if state == "on" and not power_save_mode:
            for item in config.relais_conf:
                if config.relais_conf[item]:
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
        self.status_dict["num_pics"] = config.get_num_stored_pictures()
        self.status_dict["num_free_space"] = get_disk_free_capacity(
            config.pictures_save_folder
        )
        self.status_dict["poll_time"] = datetime.datetime.now()
        self.status_dict["IP_addresses"] = get_ip_addresses()
        # text generation
        display_lines = []
        if "last_picture" in self.status_dict:
            display_lines += ["Pic ~" + self.status_dict["last_picture"]]
        num_total_pics = (
            self.status_dict["num_pics"] + self.status_dict["num_free_space"]
        )
        display_lines += [f"Disk #{self.status_dict['num_pics']}/{num_total_pics}"]
        camera_str = "OK" if self.status_dict["camera"] else "??"
        display_str = "OK" if self.status_dict["display"] else "??"
        display_lines += [f"Cam~{camera_str} Disp~{display_str}"]
        ips = get_ip_addresses()
        ip_addresses = [f"+|{item}: {ips[item][0]};" for item in ips.keys()]
        display_lines += ip_addresses
        buttons_str = "1:" + self.status_dict["buttons"][1]
        buttons_str += "   2:" + self.status_dict["buttons"][2]
        display_lines += [buttons_str]
        buttons_str = "3:" + self.status_dict["buttons"][3]
        buttons_str += "    4:" + self.status_dict["buttons"][4]
        display_lines += [buttons_str]
        # display and store text
        status_image = paint_status_page(display_lines)
        cc_to = config.get_status_img_path()
        Epaper.display(status_image, cc_to=str(cc_to))
        # If the device configured for reset
        if self.ready_for_restart:
            self.stop_service()
            reboot()

    def take_pictures(self):
        # switch off lamp if needed
        if not config.lamp_during_capture:
            self.set_relais("off")
        # capture
        picture_path = self.camera.capture()
        if picture_path and self.valid_capture_conditions:
            timestr = datetime.datetime.now().strftime("%d.%m. %H:%M:%S")
            self.status_dict["last_picture"] = timestr
            target = Path(config.pictures_save_folder) / (timestr + ".jpg")
            self.camera.save(picture_path, target)
        # turn lamp back on if needed
        if not config.lamp_during_capture:
            self.set_relais("on")

    def refresh_camera(self):
        self.camera.reconnect()

    @property
    def power_save_mode(self):
        if config.power_save_daylight and is_sunshine(lat=config.lat, lon=config.lon):
            return True
        if config.power_save_weather and Weather.safe_for_moths_weather():
            return True
        return False

    @property
    def valid_capture_conditions(self):
        if is_disk_full(config.pictures_save_folder):
            return False
        return not self.power_save_mode

    @property
    def ready_for_restart(self):
        if config.daily_reboot:
            # reboot "tomorrow noon".
            tomorrow_noon = self.started_on.replace(hour=12, minute=0, second=0)
            tomorrow_noon += datetime.timedelta(days=1)
            if datetime.datetime.now() > tomorrow_noon:
                return True
        return False
