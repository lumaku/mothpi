# !/usr/bin/python3
# -*- coding:utf-8 -*-

"""
Mothpi - a tool for biodiversity monitoring of moths.
Usually combined with a moth scanner, see:
https://visammod.vision.in.tum.de/

--
2021, Technische Universität München, Ludwig Kürzinger
"""

import logging
import argparse
import systemd.daemon
import time
from mothpi.mp import MothPi


def get_parser():
    """Obtain an argument-parser for the script interface."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--log_level",
        type=lambda x: x.upper(),
        default="INFO",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"),
        help="The verbosity level of logging",
    )
    parser.add_argument(
        "--app",
        dest="app",
        action=argparse.BooleanOptionalAction,
        help="Also open a web interface",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Change the port of the web app",
    )
    parser.set_defaults(app=True)
    return parser


def main():
    """Main function of mothpi.

    This function starts the Mothpi program, and, if configured,
    opens the web interface.

    Also, if Mothpi is configured to run as a systemd service, it sends the
    READY signal.
    """
    # Initialize
    parser = get_parser()
    args = parser.parse_args()
    logger = logging.getLogger()
    logger.setLevel(args.log_level)
    formatter = logging.Formatter("(%(module)s:%(lineno)d) %(levelname)s: %(message)s")
    logger.handlers[0].setFormatter(formatter)

    # Set up Mothpi
    mothpi = MothPi()

    # if needed, start web interface
    if args.app:
        from mothpi.app import create_app

        port = args.port
        logging.info(f"Starting web app on port {port}.")
        create_app().run(host="0.0.0.0", port=port)

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
