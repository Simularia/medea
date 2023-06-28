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
from factor import computefactor


def readmet(conf):
    """Read meteo file in input."""
    # read input csv meteo file in a pandas dataframe
    met = pd.read_csv(conf['windinputfile'])
    return met


def writemet(conf, met):
    """Write meteo file in output with rescaling factors."""
    # build output meteo and factor dataframe
    columns = ['date', 'wd', 'ws']
    for i in conf['source']:
        for j in conf['species']:
            columns.append(str(i)+j)
    metout = pd.DataFrame([],columns=columns, index = range(1, len(met.index + 1)))

    # loop on all the deadlines
    for idx in met.index:
        ws = met.iloc[idx, 'ws']
        date = met.iloc[idx, 'date']
        wd = met.iloc[idx, 'wd']
        # for each combination of source and species
        # compute the rescaling factor
        for i in conf['source']:
            for j in conf['species']:
                ind = conf['source'].index(i)
                scheme = conf['scheme'][ind]
                height = conf['height'][ind]
                fact = computefactor(scheme, ws, height)
                metout.iloc[idx,str(i)+j] = fact
        metout.iloc[idx, 'date'] = date
        metout.iloc[idx, 'ws'] = ws
        metout.iloc[idx, 'wd'] = wd
    # write the output csv meteo and factor file
    metout.to_csv(conf['windoutputfile'])
    return metout
