# !/usr/bin/python3
# -*- coding:utf-8 -*-

"""
Useful stuff.

2021, Technische Universität München, Ludwig Kürzinger
"""

import logging
from threading import Timer, Lock
import os
import time
import shutil
from netifaces import interfaces, ifaddresses, AF_INET

# mothpi-specific
from mothpi.display import Epaper, paint_simple_text_output


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
    """Reboot. Try it out."""
    logging.warning("Rebooting.")
    message = paint_simple_text_output(output_string="rebooting...")
    Epaper.display(message)
    time.sleep(1)
    os.system("sudo reboot")


def is_disk_full(path):
    """Check if the disk is full."""
    total, used, free = shutil.disk_usage(path)
    mib = 1000 * 1000
    if free < (50 * mib):
        return True
    else:
        return False


def get_disk_free_capacity(path):
    """Estimate number of free pictures slots in disk space."""
    total, used, free = shutil.disk_usage(path)
    mib = 1000 * 1000
    free -= 50 * mib
    if free <= 0:
        free = 0
    free /= 5 * mib  # how many 5MiB pics fit into the remaining space?
    return int(free)


def get_ip_addresses() -> dict:
    """Return dictionary of IP addresses as {interface: [ip1, ip2]}."""
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
