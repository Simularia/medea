#
# SPDX-FileCopyrightText: 2023 Simularia s.r.l. <info@simualaria.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
import argparse
import logging
import sys
from importlib.metadata import version
from pathlib import Path

import tomllib

from .emifile import aermod, calpuff, impact, pemtim
from .met import readmet, writemet


def check_model(input):
    """ Check input model """
    logger = logging.getLogger()
    logger.debug("{}".format(check_model.__doc__))

    # List of valid models
    valid_models = ["spray", "calpuff", "impact", "aermod"]
    
    try:
        # Convert it into integer
        val = int(input)
        logger.debug(f"mode = {val} is an integer number.")

        # Convert to string
        if val == 0:
            model = "spray"
        elif val == 1:
            model = "calpuff"
        elif val == 2:
            model = "impact"
        elif val == 3:
            model = "aermod"
        else:
            pass
    except ValueError:
        # Convert it into string
        model = str(input)
        model = model.lower()
        logger.debug(f"mode = {model} is a string.")
    finally:
        # Check if model is valid
        if model not in valid_models:
            raise ValueError(f"Invalid model: {model}. Allowed models are {valid_models}")
        else:
            logger.debug(f"Model {model} is valid.")

    return model


def readconf(cFile):
    """Read toml configuration file."""
    logger = logging.getLogger()
    logger.info("{}".format(readconf.__doc__))

    # Load the TOML data into a Python dictionary
    with open(cFile, "rb") as f:
        conf = tomllib.load(f)

    # debug information
    logger.debug("Configuration toml file dump (key: value):")
    for key in conf.keys():
        logger.debug(f"{key}: {conf[key]}")

    newsou = []
    for i, sou in enumerate(conf["sources"]):
        if isinstance(sou["id"], list):
            ids = conf["sources"][i]["id"]
            tmpsou = []
            for j in range(len(ids)):
                tmpsou.append(sou.copy())
            for k, id in enumerate(ids):
                tmpsou[k]["id"] = id
            newsou = newsou + tmpsou
    oldsou = []
    for i, sou in enumerate(conf["sources"]):
        if not isinstance(sou["id"], list):
            oldsou.append(conf["sources"][i])
    conf["sources"] = []
    conf["sources"] = oldsou + newsou
    logger.debug("Reading configuration file completed.")

    # Validate schemes
    logger.debug("Validating sources schemes")
    valid_schemes = [1, 2, 3]
    for i, sou in enumerate(conf["sources"]):
        try:
            scheme = sou["scheme"]
        except Exception as e:
            raise Exception(f"Error reading scheme for source {i}. Error message: {e}.")
        if scheme not in valid_schemes:
            raise ValueError(f"Invalid scheme \"{scheme}\" for source {sou["id"]}. Allowed schemes are {valid_schemes}")

    return conf


def medea():
    """
    MEDEA main
    """

    desc = "MEDEA: compute meteorolgy dependent emissions for dispersion models."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument(
        "config", type=str, help="Path to input configuration toml file."
    )
    parser.add_argument(
        "-d", "--debug", help="Activate debug mode", action="store_true"
    )
    args = parser.parse_args()

    # Create Logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if args.debug:
        logger.setLevel(logging.DEBUG)

    # Logging format
    formatter = logging.Formatter(
        "*** %(levelname)-7.7s – %(asctime)s – %(module)s – %(funcName)s – %(message)s"
    )

    # Create console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Create log file handler (always debug level)
    fh = logging.FileHandler(filename="medea.log", mode="w")
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    logger.info("==========================")
    logger.info("medea")
    logger.info(f"Version {version("medea")}")
    logger.info("Licence: AGPL-3.0-or-later")
    logger.info("==========================")

    # read input configuration file
    try:
        logger.info("Reading input configuration file.")
        cFile = Path(args.config)
        conf = readconf(cFile)
    except Exception as e:
        logger.error(f"{e}")
        sys.exit()

    # read meteorological file
    try:
        logger.info("Reading meteorological input file.")
        met = readmet(conf)
    except Exception as e:
        logger.error(f"{e}")
        sys.exit()

    # write meteorological file
    try:
        logger.info("Writing meteorological output file and")
        logger.info("computing new emission rescaling factor.")
        metout = writemet(conf, met)
    except Exception as e:
        logger.error(f"{e}")
        sys.exit()

    # Get mode and check its validity
    try:
        mode = check_model(conf["mode"])
    except Exception as e:
        logger.error(f"{e}")
        sys.exit()

    # read and write emission files
    logger.info(f"Editing emission file for {mode}")
    if mode == "spray":
        pemtim(conf, metout)
    elif mode == "calpuff":
        calpuff(conf, metout)
    elif mode == "impact":
        impact(conf, metout)
    elif mode == "aermod":
        aermod(conf, metout)
    else:
        logger.error("No model has been recognized.")
        sys.exit()
    logger.info("Emission file edited.")

    logger.info("End of program.")
    return
