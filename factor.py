#
# SPDX-FileCopyrightText: 2023 Simularia s.r.l. <info@simualaria.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#

import logging
import pandas as pd
import numpy as np
import sys
import math


def odour(met, conf, ind):
    """Odour scheme for rescaling emissions."""
    logger = logging.getLogger()
    logger.debug('{}'.format(odour.__doc__))

    gamma = 0.5
    dt = {'rural': [0.07, 0.07, 0.1, 0.15, 0.35, 0.55],
          'urban': [0.15, 0.15, 0.2, 0.25, 0.3, 0.3]}

    tab = pd.DataFrame(data=dt, index=["A", "B", "C", "D", "E", "F"])
    if 'terrain' in conf['sources'][ind].keys() and 'stabclass' in met.keys():
        logger.debug("Terrain type and stability class information")
        logger.debug("are available: computing beta.")
        beta = pd.DataFrame(
            columns=['val'],
            data=tab[conf['sources'][ind]['terrain']][met['stabclass']]
            .to_list(),
            index=met.index.values.tolist())
    else:
        beta = 0.55  # default value
        logger.debug("Terrain type or stability class information")
        logger.debug(f"are missing: default beta value = {beta}.")
    if 'vref' in conf['sources'][ind].keys():
        vref = conf['sources'][ind]['vref']
        logger.debug("Reference velocity available from the")
        logger.debug("configuration toml file.")
    else:
        vref = 0.3
        logger.debug("Reference velocity not available from the")
        logger.debug(f"configuration toml file: {vref} default value.")
    rat = met['z']/conf['sources'][ind]['height']
    tmp = (met['ws']*(rat.pow(beta['val']))/vref)**gamma
    colname = str(conf['sources'][ind]['id']) + '_' + \
        conf['sources'][ind]['species'][0]
    met.insert(len(met.columns), colname, round(tmp, 2))
    return met

def sympar(sym, alpha):
    if sym:
        ppsa = np.array([40.0, 48.0, 12.0, 0.0])       
    if (not sym):
        ppsa = np.empty((len(alpha), 4), dtype=float)
        for ind in range(0, len(alpha)):
            val = alpha[ind]
            if (val>=0.0) and (val<=20.0):
                ppsa[ind, :] = np.array([36.0, 50.0, 14.0, 0.0])
            if (val>20.0) and (val<=40.0):
                ppsa[ind, :] = np.array([31.0, 51.0, 15.0, 3.0])
            if (val>40.0) and (val<=90.0):
                ppsa[ind, :] = np.array([28.0, 54.0, 14.0, 4.0])
    return ppsa
    
def inc2alpha(input):

    if input>360.0:
        input = input - 360.0
    if input<0.0:
        input = input + 360.0
    if input>=270.0:
        alpha = input - 270.0
    if input<270.0 and input>180:
        alpha = 270 - input
    if input<=180.0 and input>90:
        alpha = input - 90.0
    if input<90.0:
        alpha = 90.0 - input
    return alpha

def scheme2(met, conf, ind):
    """Cumulus scheme to set emissions."""
    logger = logging.getLogger()
    logger.debug('{}'.format(scheme2.__doc__))
    sou = conf['sources'][ind]
    if set(sou['species']) != set(['PM25', 'PM10', 'PTS']):
        logger.info(f"Invalid species in source {sou['id']}: exit.")
        sys.exit()

    listpyr = ['major', 'minor', 'angle', 'height']
    pyramid = all(item in sou.keys() for item in listpyr)
    listcon = ['radius', 'height']
    conical = all(item in sou.keys() for item in listcon)

    if ((pyramid + conical) != 1):
        logger.info(f"Undefined shape of source {sou['id']}: exit.")
        sys.exit()

    if pyramid:
        major = sou['major']
        minor = sou['minor']
        ap1 = math.sqrt((major / 5)**2 + sou['height']**2)
        ap2 = math.sqrt((minor / 3)**2 + sou['height']**2)
        s = 8 * major * ap2 / 5 + 4 * minor * ap1 / 3
        base = minor
        if (abs(sou['angle']) > 90.0):
            logger.info(f"Bad definition of angle {sou['angle']}: exit.")
            sys.exit()
        # computing angle to select EPA case
        if sou['angle']<0.0:
            ainc = (met['wd'] - (-90.0 - sou['angle']))
        else:
            ainc = (met['wd'] - (90.0 - sou['angle']))

        alpha = ainc.apply(inc2alpha)
        ppsa = sympar(False, alpha.to_numpy())
        logger.debug(f"Source {sou['id']} has pyramid shape.")

    elif conical:
        r = sou['radius']
        h = sou['height']
        s = math.pi*r*math.sqrt(r**2 + h**2)
        base = 2*r
        ppsa = sympar(True, 1.0)
        ppsa = np.repeat(a = ppsa, repeats = len(met['ws']), axis=0)
        logger.debug(f"Source {sou['id']} has conical shape.")

    else:
        logger.info(f"Undefined shape of source {sou['id']}: exit.")
        sys.exit()

    if sou['height']/base <= 0.2:
        psba = [1, 1, 1, 1]
    else:
        psba = [0.2, 0.6, 0.9, 1.1]

    # roughness in cm to meters
    if 'roughness' in sou.keys():
        z0 = sou['roughness']/100.0
    else:
        z0 = 0.005

    # scale wind speed to 10 m height
    ws10 = met['ws']*(np.log(10.0/z0))/(np.log(met['z']/z0))

    # from wind speed to fastest mile
    a = 1.6
    b = 0.43
    fm = a*ws10 + b

    # computing friction velocity
    ust = np.empty((len(fm), len(psba)))
    for idx, psbai in enumerate(psba):
        ust[:, idx] = 0.4*fm/np.log(0.25/z0)*psbai
    tfv = sou['tfv']*np.ones((len(fm), len(psba)))
    ust = np.where(ust > tfv, ust, tfv)

    # erosion potential
    p = np.zeros_like(ust)
    p = 58*(ust - tfv)**2 + 25*(ust - tfv)

    # parameter for PTS, PM25, PM10
    k25 = 0.075
    k10 = 0.5
    kpts = 1.0

    # building the emission in mcg
    ptot = np.zeros(len(p[:,0]), float)
    for ind in range(0, len(p)):
        ptot[ind] = np.dot(p[ind, :],ppsa[ind, :])*(s/100.0)*10**6.

    # building species name for met dataframe
    pm25 = str(sou['id']) + '_' + 'PM25'
    pm10 = str(sou['id']) + '_' + 'PM10'
    pts = str(sou['id']) + '_' + 'PTS'

    met.insert(len(met.columns), pm25, np.around(k25*ptot, 2))
    met.insert(len(met.columns), pm10, np.around(k10*ptot, 2))
    met.insert(len(met.columns), pts, np.around(kpts*ptot, 2))
    return met


def scheme3(met, conf, ind):
    """Cumulus scheme to set emissions in absence of wind data."""
    logger = logging.getLogger()
    logger.debug('{}'.format(scheme2.__doc__))
    sou = conf['sources'][ind]
    if set(sou['species']) != set(['PM25', 'PM10', 'PTS']):
        logger.info(f"Invalid species in source {sou['id']}: exit.")
        sys.exit()

    listnw = ['radius', 'height', 'movh']
    conic = all(item in sou.keys() for item in listnw)
    if conic:
        r = sou['radius']
        h = sou['height']
        s = math.pi*r*math.sqrt(r**2 + h**2)
        movh = sou['movh']
    else:
        logger.info(f"Missing parameters in source {sou['id']}: exit.")
        sys.exit()

    if (h/(2*r) > 0.2):
        logger.debug("High mounds case.")
        efpm25 = 1.26E-06
        efpm10 = 7.9E-06
        efpts = 1.6E-05
    else:
        logger.debug("Low mounds case.")
        efpm25 = 3.8E-05
        efpm10 = 2.5E-04
        efpts = 5.1E-04

    epm25 = (10**9)*efpm25*s*movh
    epm10 = (10**9)*efpm10*s*movh
    epts = (10**9)*efpts*s*movh
    # building species name for met dataframe
    pm25 = str(sou['id']) + '_' + 'PM25'
    pm10 = str(sou['id']) + '_' + 'PM10'
    pts = str(sou['id']) + '_' + 'PTS'

    met.insert(len(met.columns), pm25, np.around(epm25, 2))
    met.insert(len(met.columns), pm10, np.around(epm10, 2))
    met.insert(len(met.columns), pts, np.around(epts, 2))

    return met
