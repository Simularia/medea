#!/usr/bin/env python3
###############################################################################
#
# Simularia s.r.l.
# via Sant'Antonio da Padova 12
# Torino, Italy
# www.simularia.it
# info@simularia.it
#
###############################################################################

import toml
import pandas as pd
import argparse
import logging
from pathlib import Path, PurePath
from datetime import datetime, timedelta
from pemtim import pemtim
from met import readmet, writemet

__version__ = '0.0.1'


def readconf(cFile):
    """Read toml configuration file."""

    logger = logging.getLogger()
    logger.info('{}'.format(readconf.__doc__))
    # Load the TOML data into a Python dictionary
    with open(cFile) as f:
        conf = toml.load(f)

    return conf


def main():
    """
    EOLO main
    """

    desc = "EOLO: compute wind-dependent emissions for spray."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-d',
                        '--debug',
                        help="Activate debug mode",
                        action='store_true')
    parser.add_argument('-c',
                        type=str,
                        help='Path to input configuration toml file.')

    args = parser.parse_args()

    # Logging format
    formatter = logging.Formatter(
        '*** %(levelname)-7.7s - %(asctime)s - %(module)-19.19s ' +
        '- %(funcName)-19.19s - %(message)s')
    # Create Logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if (args.debug):
        logger.setLevel(logging.DEBUG)

    # Create console handler and set level to debug if needed
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    if (args.debug):
        ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    # Create log file handler
    fh = logging.FileHandler(filename="eolo.log", mode="w")
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    logger.info("======================")
    logger.info("======= EOLO =========")
    logger.info(f"Version {__version__}")
    logger.info("======================")

    # Get path of input and output files
    debug = args.debug
    cFile = Path(args.c)

    # read input configuration file
    conf = readconf(cFile)
    # read meteorological file
    met = readmet(conf)
    # write meteorological file
    metout = writemet(conf, met)
    # read and write pemtim file
    pemtim(conf, metout)

    return

# Execute script as a standalone application
if __name__ == "__main__":
    main()

