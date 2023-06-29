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


def odour(met, conf, ind):
    gamma = 0.5
    beta = 3
    vref = 0.3 
    tmp = ((met['ws']*(met['z']/conf['height'][ind])**beta)/vref)**gamma
    colname = str(conf['sources'][ind]) + '_' + conf['species'][0]
    met.insert(len(met.columns), colname, round(tmp,2))
    return met

def scheme2(met, conf, ind):


    return met


def scheme3(met, conf, ind):
    

    return met

