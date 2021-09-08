# !/usr/bin/python3
# -*- coding:utf-8 -*-


import logging
from pathlib import Path
import gphoto2 as gp
import os
import datetime

# For gphoto2 example code, visit
# https://github.com/jim-easterbrook/python-gphoto2/tree/master/examples
# for gphoto command line utility see
# http://www.gphoto.org/doc/manual/ref-gphoto2-cli.html


class MothCamera:
    camera = None

    def __init__(self):
        self.reconnect()

    def reconnect(self):
        if self.camera:
            self.close()
        try:
            self.camera = gp.Camera()
            self.camera.init()
            logging.info("Camera is available.")
        except gp.GPhoto2Error:
            self.camera = None
            logging.error("No Camera found!")

    def is_available(self):
        return True if self.camera else False

    def summary(self):
        if self.is_available():
            text = self.camera.get_summary()
        else:
            text = "Camera not connected."
        return str(text)

    def get_camera_clock(self):
        raise NotImplementedError

    def capture(self):
        if self.is_available():
            file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
            logging.info(f"New picture: {file_path.name}")
            return file_path
        else:
            logging.warning("No Capture, camera not connected.")
            return None

    def save(self, file_path, target=Path("/tmp") / "out.jpg"):
        if self.is_available():
            logging.info(f"Copying image {file_path.name} to {target}")
            camera_file = self.camera.file_get(
                file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL
            )
            camera_file.save(str(target))

    def close(self):
        if self.is_available:
            self.camera.exit()
            self.camera = None

    def get_file_time(self, filename):
        info = get_file_info(self.camera, filename)
        mtime = datetime.datetime.fromtimestamp(info.file.mtime).isoformat(" ")
        return mtime


#### The following functions were taken from the gphoto python project
# https://github.com/jim-easterbrook/python-gphoto2


def list_files(camera, path="/"):
    result = []
    # get files
    for name, value in camera.folder_list_files(path):
        result.append(os.path.join(path, name))
    # read folders
    folders = []
    for name, value in camera.folder_list_folders(path):
        folders.append(name)
    # recurse over subfolders
    for name in folders:
        result.extend(list_files(camera, os.path.join(path, name)))
    return result


def get_file_info(camera, path):
    folder, name = os.path.split(path)
    return camera.file_get_info(folder, name)
