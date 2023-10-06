#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2023 Simularia s.r.l. <info@simualaria.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#

import argparse
import logging
from pathlib import Path
from emifile import pemtim, calpuff, impact, aermod
from met import readmet, writemet
import tomli

__version__ = '1.0.0'


def check_mode(input):
    logger = logging.getLogger()
    logger.info('{}'.format(check_mode.__doc__))
    try:
        # Convert it into integer
        val = int(input)
        logger.info(f"mode is an integer number. mode = {val}")
    except ValueError:
        try:
            # Convert it into string
            val = str(input)
            val = val.lower()
            logger.info(f"mode is a string. mode = {val}")
        except ValueError:
            logger.info(f"mode is not a string or a number. mode = {val}")
    return val


def readconf(cFile):
    """Read toml configuration file."""

    logger = logging.getLogger()
    logger.info('{}'.format(readconf.__doc__))
    # Load the TOML data into a Python dictionary
    with open(cFile, 'rb') as f:
        conf = tomli.load(f)
    # debug information
    logger.debug("Configuration toml file dump:")
    for key in conf.keys():
        logger.debug(f"{key}: {conf[key]}")
    newsou = []
    for i, sou in enumerate(conf['sources']):
        if isinstance(sou['id'], list):
            ids = conf['sources'][i]['id']
            tmpsou = []
            for j in range(len(ids)):
                tmpsou.append(sou.copy())
            for k, id in enumerate(ids):
                tmpsou[k]['id'] = id
            newsou = newsou + tmpsou
    oldsou = []
    for i, sou in enumerate(conf['sources']):
        if not isinstance(sou['id'], list):
            oldsou.append(conf['sources'][i])
    conf['sources'] = []
    conf['sources'] = oldsou + newsou
    logger.debug("Configuration toml file read correctly.")
    return conf


def main():
    """
    MEDEA main
    """

    desc = "MEDEA: compute meteorolgy dependent emissions for dispersion models."
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
    fh = logging.FileHandler(filename="medea.log", mode="w")
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    logger.info("==========================")
    logger.info("========= MEDEA ==========")
    logger.info(f"Version {__version__}")
    logger.info("Licence: AGPL-3.0-or-later")
    logger.info("==========================")

    # Get path of input and output files
    cFile = Path(args.config)
    # read input configuration file
    logger.info("Reading input configuration file.")
    conf = readconf(cFile)
    # read meteorological file
    logger.info("Reading meteorological input file.")
    met = readmet(conf)
    # write meteorological file
    logger.info("Writing meteorological output file and")
    logger.info("computing new emission rescaling factor.")
    metout = writemet(conf, met)
    mode = check_mode(conf['mode'])

    if ((mode == 0) | (mode == 'spray')):
        # read and write pemtim file
        logger.info("Editing pemtim file.")
        pemtim(conf, metout)
        logger.info("Pemtim file edited.")

    if ((mode == 1) | (mode == 'calpuff')):
        # read and write calpuff file
        logger.info("Editing calpuff file.")
        calpuff(conf, metout)
        logger.info("Calpuff file edited.")

    if ((mode == 2) | (mode == 'impact')):
        # read and write impact file
        logger.info("Editing impact file.")
        impact(conf, metout)
        logger.info("Impact file edited.")

    if ((mode == 3) | (mode == 'aermod')):
        # read and write aermod file
        logger.info("Editing aermod file.")
        aermod(conf, metout)
        logger.info("Aermod file edited.")

    logger.info("End of program.")
    return


if __name__ == "__main__":

    main()
