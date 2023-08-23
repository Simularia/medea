###############################################################################
#
# Simularia s.r.l.
# via Sant'Antonio da Padova 12
# Torino, Italy
# www.simularia.it
# info@simularia.it
#
###############################################################################

import pandas as pd
from factor import odour, scheme2, scheme3
import logging


def readmet(conf):
    """Read meteo file in input."""
    logger = logging.getLogger()
    logger.info('{}'.format(readmet.__doc__))

    # read input csv meteo file in a pandas dataframe
    met = pd.read_csv(conf['windinputfile'])
    if 'stabclass' in met.keys():
        met.replace({'stabclass' : { 1 : 'A', 2 : 'B', 3 : 'C',
                                     4 : 'D', 5 : 'E', 6 : 'F' ,
                                    'a' : 'A', 'b' : 'B', 'c' : 'C',
                                    'd' : 'D', 'e' : 'E', 'f' : 'F' }})

    return met


def writemet(conf, met):
    """Write meteo file in output with rescaling factors."""
    logger = logging.getLogger()
    logger.debug('{}'.format(writemet.__doc__))

    logger.debug("Loop on selected sources to rescale emissions.")
    for ind, sou in enumerate(conf['sources']):
        scheme = conf['sources'][ind]['scheme']
        logger.debug(f"Source = {sou}, scheme = {scheme}.")

        if scheme == 1:
            met = odour(met, conf, ind)
        if scheme == 2:
            met = scheme2(met, conf, ind)
        if scheme == 3:
            met = scheme3(met, conf, ind)

    # write the output csv meteo and factor file
    logger.debug("Writing the output csv meteo and factor file.")
    met.to_csv(conf['windoutputfile'], index=False)
    return met
