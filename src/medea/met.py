#
# SPDX-FileCopyrightText: 2023 Simularia s.r.l. <info@simualaria.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#

import logging
import sys
from datetime import datetime

import pandas as pd

from .factor import odour, scheme2, scheme3


def readmet(conf):
    """Read meteo file in input."""
    logger = logging.getLogger()
    logger.info("{}".format(readmet.__doc__))
    logger.info(f"Meteorological file is {conf["windInputFile"]}")
    try:
        mettype = str(conf["mettype"]).lower()
        logger.info(f"Meteo file type is {mettype}.")
    except Exception as e:
        logger.error(f"The error is {e}.")
        logger.error("Setting meteo type to default value: csv.")
        mettype = "csv"

    if mettype == "postbin":
        with open(conf["windInputFile"], "r") as file:
            lines = [line.rstrip() for line in file]
        metdata = [["none", -1.0, -1.0, -1.0] for x in range(len(lines))]
        for ind in range(0, len(lines)):
            line = lines[ind].split()
            dtl = [int(line[j].replace(".", "")) for j in range(2, 8)]
            date = datetime(2000 + dtl[2], dtl[1], dtl[0], dtl[3], dtl[4], dtl[5])
            datestr = date.strftime("%Y-%m-%dT%H:%M:%SZ")
            z = float(line[8])
            ws = float(line[9])
            wd = float(line[10])
            metdata[ind] = [datestr, ws, wd, z]
        met = pd.DataFrame(metdata, columns=["date", "ws", "wd", "z"])
        logger.debug("Read postbin meteo file.")
    else:
        try:
            # read input csv meteo file in a pandas dataframe
            met = pd.read_csv(conf["windInputFile"])
            if "stabclass" in met.keys():
                met = met.replace(
                    {
                        "stabclass": {
                            1: "A",
                            2: "B",
                            3: "C",
                            4: "D",
                            5: "E",
                            6: "F",
                            "a": "A",
                            "b": "B",
                            "c": "C",
                            "d": "D",
                            "e": "E",
                            "f": "F",
                        }
                    }
                )
            logger.info("Read csv meteo file.")
        except Exception as e:
            logger.error(f"Error reading {conf['windInputFile']}.")
            logger.error(f"{e}.")
            sys.exit()

    return met


def writemet(conf, met):
    """Write meteo file in output with rescaling factors."""
    logger = logging.getLogger()
    logger.info("{}".format(writemet.__doc__))

    logger.debug("Loop on selected sources to rescale emissions.")
    for ind, sou in enumerate(conf["sources"]):
        scheme = conf["sources"][ind]["scheme"]
        logger.debug(f"Source = {sou}, scheme = {scheme}.")

        if scheme == 1:
            met = odour(met, conf, ind)
        if scheme == 2:
            met = scheme2(met, conf, ind)
        if scheme == 3:
            met = scheme3(met, conf, ind)

    # write the output csv meteo and factor file
    logger.debug("Writing the output csv meteo and factor file.")
    met.to_csv(conf["windOutputFile"], index=False)

    return met
