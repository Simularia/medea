###############################################################################
#
# Simularia s.r.l.
# via Sant'Antonio da Padova 12
# Torino, Italy
# www.simularia.it
# info@simularia.it
#
###############################################################################

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
        beta = pd.DataFrame(columns=['val'],
                    data = tab[conf['sources'][ind]['terrain']][met['stabclass']].to_list(),
                    index = met.index.values.tolist())
    else:
        beta = 0.55
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
        
    tmp = ((met['ws']*(met['z'].pow(beta['val']))/conf['sources'][ind]['height'])/vref)**gamma
    colname = str(conf['sources'][ind]['id']) + '_' + conf['sources'][ind]['species'][0]
    met.insert(len(met.columns), colname, round(tmp,2))
    return met

def scheme2(met, conf, ind):
    """Cumulus scheme to set emissions."""
    logger = logging.getLogger()
    logger.debug('{}'.format(scheme2.__doc__))
    sou = conf['sources'][ind]
    if set(sou['species']) != set(['PM25', 'PM10', 'PTS']):
        logger.info(f"Invalid species in source {sou['id']}: exit.")
        sys.exit()

    psba = np.array([0.2, 0.6, 0.9])
    ppsa = np.array([40.0, 48.0, 12.0])
    listpyr = ['xmax', 'xmin', 'ymax', 'ymin', 'height']
    pyramid = all(item in sou.keys() for item in listpyr) 
    listcon = ['radius', 'height']
    conical = all(item in sou.keys() for item in listcon)
    listflat = ['diameter', 'height']
    flat = all(item in sou.keys() for item in listflat)
    if pyramid:
        width = sou['xmax'] - sou['xmin']
        height = sou['ymax'] - sou['ymin']
        ap1 = math.sqrt((width / 5)**2 + sou['height']**2)
        ap2 = math.sqrt((height / 3)**2 + sou['height']**2)
        s = 8 * width * ap2 / 5 + 4 * height * ap1 / 3
        logger.debug(f"Source {sou['id']} has pyramid shape.")

    elif conical:
        r = sou['radius']
        h = sou['height']
        s = math.pi*r*math.sqrt(r**2 + h**2)
        logger.debug(f"Source {sou['id']} has conical shape.")

    elif flat:
        d = sou['diameter']
        h = sou['height']
        s = (math.pi/4)*d**2
        logger.debug(f"Source {sou['id']} has flat shape.")

    else:
        logger.info(f"Undefined shape of source {sou['id']}: exit.")
        sys.exit()


    # from wind speed to fastest mile
    a = 1.6
    b = 0.43
    fm = a*met['ws'] + b

    # roughness
    if 'roughness' in sou.keys():
        z0 = sou['roughness']
    else:
        z0 = 0.005

    # computing friction velocity
    ust = np.empty((len(fm), len(psba)))
    for idx, psbai in enumerate(psba):
        ust[:, idx] = 0.4*fm/np.log(25/z0)*psbai
    tfv = sou['tfv']*np.ones((len(fm), len(psba)))
    ust = np.where(ust > tfv, ust, tfv)

    # erosion potential
    p = np.zeros_like(ust)
    p = 58*(ust - tfv)**2 + 25*(ust - tfv)


    # parameter for PTS, PM25, PM10
    k25 = 0.075
    k10 = 0.5
    kpts = 1.0

    # building the emission
    ptot = np.sum(p*s*(ppsa/100.0)*10**6., axis = 1)


    # building species name for met dataframe
    pm25 = str(sou['id']) + '_' + 'PM25'
    pm10 = str(sou['id']) + '_' + 'PM10'
    pts = str(sou['id']) + '_' + 'PTS'

    met.insert(len(met.columns), pm25, np.around(k25*ptot*sou['mass'], 2))
    met.insert(len(met.columns), pm10, np.around(k10*ptot*sou['mass'], 2))
    met.insert(len(met.columns), pts, np.around(kpts*ptot*sou['mass'], 2))
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
