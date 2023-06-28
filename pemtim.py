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

def pemtim(conf, metout):
    """Modulate emission from existing pemtim."""
    # opening pemspe and reading the number of species
    with open(conf['pemspe'],'r') as ps:
        pemspe = [line.rstrip() for line in ps]

    nspe = int(pemspe[1].split())
    # opening the input pemtim
    with open(conf['input'],'r') as file:
        lines = [line.rstrip() for line in file]
    # opening the output pemtim for writing
    output = open(conf['output'], 'w')
    for l in range(0,6):
        output.write(lines[l])
        output.write('\n')
    pdate = [int(s) for s in lines[5].split() if s.isdigit()]
    refdate = datetime(2000+pdate[2], pdate[1], pdate[0],
                       pdate[3], pdate[4], pdate[5])
    nsou = int(lines[1].split()[0])
    ind = 6
    for isou in range(1, nsou+1):

        sou = int(lines[ind].split('#')[2])
        output.write(lines[ind]+'\n')
        ind += 1
        nper = int(lines[ind].split('#')[0])
        output.write(lines[ind]+'\n')
        ind += 1
        date = refdate

        for iper in range(1, nper+1):
            hms = [int(s) for s in lines[ind].split('#') if s.isdigit()]
            output.write(lines[ind]+'\n')
            metind = metout.index[metout['date']==date.strftime('%Y-%m-%dT%H:%M:%SZ')]
            date = date + timedelta(hour=hms[0])
            ind += 1
            if iper == 1:
                its = int(lines[ind].split('#')[5])
                if its == 2:
                    for j in range(0,3):
                        output.write(lines[ind+j]+'\n')
                        ind += 3
                else
                    for j in range(0,2):
                        output.write(lines[ind+j]+'\n')
                        ind += 2
            # read and process all species
            for ispe in range(1, nspe+1): 
                spe = str(lines[ind].split('#')[1])
                if sou in conf['source'] and spe in conf['species']:
                    factor = metout.iloc[metind, str(sou)+spe]
                    oldmass = float(lines[ind].split('#')[2])
                    newmass = factor*oldmass
                    dummy = str(lines[ind].split('#')[3])
                    output.write('{:3d}#{:<8s}#{:6.3E}#{:4d}#\n'
                            .format(ispe, spe, newmass, dummy))
                ind += 1


    return
