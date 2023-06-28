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

def computefactor(scheme, ws, height):
    """Computing rescaling factor for wind-dependant pemtim emission."""
    
    logger = logging.getLogger()
    logger.info('{}'.format(computefactor.__doc__))
    
    match scheme:
        case 1:
            factor = 2
            # odour
            # inserire formula per l'odore
        case 2:
            factor = 3
            # cumuli alti?
        case 3:
            factor = 4
            # cumuli bassi?

    return factor
