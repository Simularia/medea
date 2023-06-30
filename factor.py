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

def odour(met, conf, ind):
    """Odour scheme for rescaling emissions."""

    logger = logging.getLogger()
    logger.debug('{}'.format(odour.__doc__))

    gamma = 0.5
    dt = {'rural': [0.07, 0.07, 0.1, 0.15, 0.35, 0.55], 
          'urban': [0.15, 0.15, 0.2, 0.25, 0.3, 0.3]}

    tab = pd.DataFrame(data=dt, index=["A", "B", "C", "D", "E", "F"])
    if 'terrain' in conf.keys() and 'stabclass' in met.keys():
        logger.debug(f"Terrain type and stability class information")
        logger.debug(f"are available: computing beta.")
        beta = pd.DataFrame(columns=['val'],
                    data = tab[conf['terrain']][met['stabclass']].to_list(),
                    index = met.index.values.tolist())
    else:
        # valore default beta?
        beta = 0.2
        logger.debug(f"Terrain type or stability class information")
        logger.debug(f"are missing: default beta value = {beta}.")
    if 'vref' in conf.keys():
        vref = conf['vref']
        logger.debug(f"Reference velocity available from the")
        logger.debug(f"configuration toml file.")
    else:
        vref = 0.3 
        logger.debug(f"Reference velocity not available from the")
        logger.debug(f"configuration toml file: {vref} default value.")
        
    tmp = ((met['ws']*(met['z'].pow(beta['val']))/conf['height'][ind])/vref)**gamma
    colname = str(conf['sources'][ind]) + '_' + conf['species'][0]
    met.insert(len(met.columns), colname, round(tmp,2))
    return met

def scheme2(met, conf, ind):


    return met


def scheme3(met, conf, ind):
    

    return met

