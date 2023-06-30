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
from datetime import datetime, timedelta
import logging

def pemtim(conf, met):
    """Modulate emission from existing pemtim."""

    logger = logging.getLogger()
    logger.debug('{}'.format(pemtim.__doc__))

    # opening pemspe and reading the number of species
    logger.debug(f"Reading pemspe file.")
    with open(conf['pemspe'], 'r') as ps:
        pemspe = [line.rstrip() for line in ps]

    nspe = int(pemspe[1])
    logger.debug(f"Number of species = {nspe}")

    # checking the species in pemspe/pemtim
    lspe = []
    for k in range(0, nspe):
        lspe.append(str(pemspe[3+k].split('*')[1].replace(" ", "")))
        logger.debug(f"Specie no. {k+1} is {lspe[k]}.")

    # checking configuration file species
    for spe in conf['species']:
        if spe not in lspe:
            logger.info(f"{spe} in configuration file,")
            logger.info(f"not present in pemtim/pemspe.") 
    # opening the input pemtim
    with open(conf['input'],'r') as file:
        lines = [line.rstrip() for line in file]
    # opening the output pemtim for writing
    output = open(conf['output'], 'w')
    # writing the pemtim header
    logger.debug(f"Writing the pemtim header.")
    for l in range(0,6):
        output.write(lines[l])
        output.write('\n')
    # building the reference date 
    pdate = [int(s) for s in lines[5].split() if s.isdigit()]
    refdate = datetime(2000+pdate[2], pdate[1], pdate[0],
                       pdate[3], pdate[4], pdate[5])
    logger.debug(f"Pemtim reference date is: {refdate}.")

    # reading the number of sources
    nsou = int(lines[1].split()[0])
    logger.debug(f"Number of sources = {nsou}")

    ind = 6
    logger.debug(f"Starting the loop on sources.")
    for isou in range(1, nsou+1):
        sou = int(lines[ind].split('#')[2])
        output.write(lines[ind]+'\n')
        ind += 1
        nper = int(lines[ind].split('#')[0])
        output.write(lines[ind]+'\n')
        ind += 1
        date = refdate

        for iper in range(1, nper+1):
            dl = lines[ind].split('#')
            hms = [int(s) for s in dl[2:5]]
            output.write(lines[ind]+'\n')
            metind = met.index[met['date']==date.strftime('%Y-%m-%dT%H:%M:%SZ')]
            date = date + timedelta(hours=hms[0])
            ind += 1
            if iper == 1:
                its = int(lines[ind].split('#')[5])
                if its == 2:
                    for j in range(0,3):
                        output.write(lines[ind+j]+'\n')
                    ind += 3
                else:
                    for j in range(0,2):
                        output.write(lines[ind+j]+'\n')
                    ind += 2
            # read and process all species
            for ispe in range(1, nspe+1): 
                spe = str(lines[ind].split('#')[1]).replace(" ", "")
                if sou in conf['sources'] and spe in conf['species']:
                    if iper == 1:
                        logger.debug(f"Source {sou} has to be rescaled")
                        logger.debug(f"on species {spe}.")
                    factor = met.iloc[metind][str(sou)+'_'+spe]
                    oldmass = float(lines[ind].split('#')[2])
                    newmass = factor*oldmass
                    dummy = int(lines[ind].split('#')[3])
                    output.write('{:3d}#{:<8s}#{:6.3E}#{:4d}#\n'
                            .format(ispe, spe, float(newmass.iloc[0]), dummy))
                else:
                    output.write(lines[ind]+'\n')
                ind += 1
    logger.debug(f"Output pemtim file written.")
    output.close()
    return
