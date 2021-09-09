# !/usr/bin/python3
# -*- coding:utf-8 -*-

"""
Mothpi

Put a Rapsberry Pi in the woods and take pictures of moths.

2021, Technische Universität München, Ludwig Kürzinger

"""


import time
import datetime
import queue
import sys
import logging
import systemd.daemon
import argparse
from pathlib import Path

# Mothpi imports
import gphoto2 as gp
from camera import MothCamera
from relais import Relais
from display import Epaper, paint_status_page, paint_simple_text_output
from config import MothConf
from utils import Periodic, get_parser, reboot


class MothPi:
    state_queue = queue.Queue()
    pictures_queue = queue.Queue()
    camera = MothCamera()
    epaper_available = Epaper.is_available()
    services = {}

    def __init__(self, configuration: MothConf):
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
            "camera": self.camera.is_available(),
            "display": Epaper.is_available(),
            "up_since": datetime.datetime.now(),
            "last_picture": "None yet!",
            "footer1": "1:CamReconn",
            "footer2": "3: Reboot",
        }
        for item in self.config.relais_conf:
            if self.config.relais_conf[item]:
                Relais.set_on(item)
            else:
                Relais.set_off(item)
        # initialize buttons
        Epaper.set_button_handler(1, self.camera.reconnect)
        Epaper.set_button_handler(3, reboot)
        # execute the services once to make sure they work:
        self.poll_status()
        self.take_pictures()

    def serve(self):
        for service in self.services.values():
            service.start()

    def stop_service(self):
        for service in self.services.values():
            service.stop()

    def poll_status(self):
        self.status_dict["camera"] = self.camera.is_available()
        self.status_dict["display"] = Epaper.is_available()
        self.status_dict["poll_time"] = datetime.datetime.now()
        self.status_dict["num_pics"] = self.config.num_stored_pictures
        status_image = paint_status_page(self.status_dict)
        Epaper.display(status_image)

    def take_pictures(self):
        picture_path = None
        try:
            picture_path = self.camera.capture()
        except gp.GPhoto2Error as e:
            cam_active_str = (
                "Cam available" if self.camera.is_available() else "no camera"
            )
            logging.error(f"GPhoto2Error ({cam_active_str}): {e}")
            self.camera.reconnect()
            # try again
            try:
                picture_path = self.camera.capture()
            except:
                logging.error("Camera capture failed again after reconnect.")
        if picture_path:
            timestr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            self.status_dict["last_picture"] = timestr
            target = self.config.pictures_save_folder / (timestr + ".jpg")
            self.camera.save(picture_path, target)


def main():
    # Initialize
    parser = get_parser()
    args = parser.parse_args()
    logger = logging.getLogger()
    logger.setLevel(args.log_level)
    formatter = logging.Formatter(
        "%(asctime)s (%(module)s:%(lineno)d) %(levelname)s: %(message)s"
    )
    logger.handlers[0].setFormatter(formatter)

    # Set up Mothpi
    config = MothConf(config_file=args.config)
    mothpi = MothPi(configuration=config)

    # Systemd service notification
    # https://github.com/torfsen/python-systemd-tutorial
    systemd.daemon.notify("READY=1")
    logging.info("Ready.")

    try:
        mothpi.serve()
        while True:
            time.sleep(1000)
    finally:
        logging.info(" -- Shutting down")
        # Stop all processes and wait until completion (with timeout)
        mothpi.stop_service()
        logging.info("The End!")


if __name__ == "__main__":
    main()
