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

import argparse
import logging
from pathlib import Path
from pemtim import pemtim
from met import readmet, writemet
import tomli

__version__ = '0.0.1'


def readconf(cFile):
    """Read toml configuration file."""

    logger = logging.getLogger()
    logger.info('{}'.format(readconf.__doc__))
    # Load the TOML data into a Python dictionary
    with open(cFile, 'rb') as f:
        conf = tomli.load(f)
    # debug information
    logger.debug(f"Configuration toml file dump:")
    for key in conf.keys():
        logger.debug(f"{key}: {conf[key]}")
    logger.debug(f"Configuration toml file read correctly.")

    return conf


def main():
    """
    EOLO main
    """

    desc = "EOLO: compute wind-dependent emissions for spray."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('config',
                        type=str,
                        help="Path to input configuration toml file.")
    parser.add_argument('-d',
                        '--debug',
                        help="Activate debug mode",
                        action='store_true')
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
    cFile = Path(args.config)

    # read input configuration file
    logger.info(f"Reading input configuration file.")
    conf = readconf(cFile)
    # read meteorological file
    logger.info(f"Reading meteorological input file.")
    met = readmet(conf)
    # write meteorological file
    logger.info(f"Writing meteorological input file and")
    logger.info(f"computing new emission rescaling factor.")
    metout = writemet(conf, met)
    # read and write pemtim file
    logger.info(f"Editing pemtim file.")
    pemtim(conf, metout)
    logger.info(f"End of program.")

    return

# Execute script as a standalone application
if __name__ == "__main__":
    main()

