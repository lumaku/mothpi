# !/usr/bin/python3
# -*- coding:utf-8 -*-

"""
Mothpi

Usage:
    - Run this file from bash

2021, Technische Universität München, Ludwig Kürzinger
"""

import logging
import argparse
from mothpi.mp import MothPi
import systemd.daemon
import time
from pathlib import Path
from utils import reboot


def get_parser():
    """Obtain an argument-parser for the script interface."""
    parser = argparse.ArgumentParser(
        description="Mothpi main software",
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


def main():
    # Initialize
    parser = get_parser()
    args = parser.parse_args()
    logger = logging.getLogger()
    logger.setLevel(args.log_level)
    formatter = logging.Formatter("(%(module)s:%(lineno)d) %(levelname)s: %(message)s")
    logger.handlers[0].setFormatter(formatter)

    # Set up Mothpi
    mothpi = MothPi(configuration=args.config)

    # Systemd service notification
    # https://github.com/torfsen/python-systemd-tutorial
    systemd.daemon.notify("READY=1")
    logging.info("Ready.")

    try:
        mothpi.serve()
        while True:
            time.sleep(10000)
    finally:
        logging.info(" -- Shutting down")
        # Stop all processes and wait until completion (with timeout)
        mothpi.stop_service()
        logging.info("The End!")


if __name__ == "__main__":
    main()
