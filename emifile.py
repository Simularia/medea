###############################################################################
#
# Simularia s.r.l.
# via Sant'Antonio da Padova 12
# Torino, Italy
# www.simularia.it
# info@simularia.it
#
###############################################################################
from datetime import datetime, timedelta
import logging
import sys
import pandas as pd


def pemtim(conf, met):
    """Modulate emission from existing pemtim."""
    logger = logging.getLogger()
    logger.debug('{}'.format(pemtim.__doc__))

    # opening pemspe and reading the number of species
    logger.debug("Reading pemspe file.")
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
    for sou in conf['sources']:
        for spe in sou['species']:
            if spe not in lspe:
                logger.info(f"{spe} in source = {sou['id']} in the")
                logger.info("configuration file,")
                logger.info("not present in pemtim/pemspe.")
                logger.info("Exit: end procedure.")
                sys.exit()
    # collecting all sources involved in config.toml
    lsou = []
    for k in range(0, len(conf['sources'])):
        lsou.append(conf['sources'][k]['id'])

    # opening the input pemtim
    with open(conf['input'], 'r') as file:
        lines = [line.rstrip() for line in file]
    # opening the output pemtim for writing
    output = open(conf['output'], 'w')
    # writing the pemtim header
    logger.debug("Writing the pemtim header.")
    for i in range(0, 6):
        output.write(lines[i] + '\n')
    # building the reference date
    pdate = [int(s) for s in lines[5].split() if s.isdigit()]
    refdate = datetime(2000+pdate[2], pdate[1], pdate[0],
                       pdate[3], pdate[4], pdate[5])
    logger.debug(f"Pemtim reference date is: {refdate}.")

    # reading the number of sources
    nsou = int(lines[1].split()[0])
    logger.debug(f"Number of sources = {nsou}")

    ind = 6
    logger.debug("Starting the loop on sources.")
    for isou in range(1, nsou+1):
        sou = int(lines[ind].split('#')[2])
        output.write(lines[ind]+'\n')
        ind += 1
        nper = int(lines[ind].split('#')[0])
        output.write(lines[ind]+'\n')
        ind += 1
        date = refdate

        iconfsou = lsou.index(sou)

        scheme = conf['sources'][iconfsou]['scheme']

        for iper in range(1, nper+1):
            dl = lines[ind].split('#')
            hms = [int(s) for s in dl[2:5]]
            output.write(lines[ind]+'\n')
            metind = met.index[met['date'] ==
                               date.strftime('%Y-%m-%dT%H:%M:%SZ')]
            date = date + timedelta(hours=hms[0])
            ind += 1
            if iper == 1:
                its = int(lines[ind].split('#')[5])
                if its == 2:
                    for j in range(0, 3):
                        output.write(lines[ind+j]+'\n')
                    ind += 3
                else:
                    for j in range(0, 2):
                        output.write(lines[ind+j]+'\n')
                    ind += 2
            # read and process all species
            for ispe in range(1, nspe+1):
                spe = str(lines[ind].split('#')[1]).replace(" ", "")
                if sou in lsou and spe in conf['sources'][iconfsou]['species']:
                    if iper == 1:
                        logger.debug(f"Source {sou} has to be rescaled")
                        logger.debug(f"on species {spe}.")
                    factor = met.iloc[metind][str(sou)+'_'+spe]
                    if scheme == 1:
                        oldmass = float(lines[ind].split('#')[2])
                        newmass = oldmass*factor._values
                    if (scheme == 2) | (scheme == 3):
                        newmass = factor._values
                    dummy = int(lines[ind].split('#')[3])
                    s2w = '{:3d}#{:<8s}#{:6.3E}#{:4d}#\n'
                    output.write(s2w.format(ispe, spe,
                                            float(newmass.iloc[0]), dummy))
                else:
                    output.write(lines[ind]+'\n')
                ind += 1
    file.close()
    output.close()
    logger.debug("Output pemtim file written.")
    return


def calpuff(conf, met):
    """Modulate emission from existing calpuff emissions input."""
    logger = logging.getLogger()
    logger.debug('{}'.format(calpuff.__doc__))

    # opening the input calpuff emissions input
    with open(conf['input'], 'r') as file:
        lines = [line.rstrip() for line in file]
    # opening the output file for writing
    output = open(conf['output'], 'w')

    # collecting all sources involved in config.toml
    lsou = []
    for k in range(0, len(conf['sources'])):
        lsou.append(conf['sources'][k]['id'])

    # read source and species information
    ncomm = int(lines[1])
    proj = str(lines[ncomm].split(' ')[0])
    if proj in ["TTM", "LCC", "LAZA"]:
        ncomm = ncomm + 1
    nsou = int(lines[ncomm + 8].split(' ')[0])
    nspe = int(lines[ncomm + 8].split(' ')[1])
    lspe = [s.replace("'", "") for s in lines[ncomm + 9].split(" ")]

    # search the time-variant part of the file
    flag = 0
    for i in range(ncomm+10, len(lines)):
        if lines[i][0] == "'":
            flag += 1
        if flag == (nsou + 1):
            start = i
            break
    # write the header information
    logger.debug("Writing the header part of file.")
    for i in range(0, start-1):
        output.write(lines[i] + '\n')
    logger.debug("Writing the time-variant part of file.")
    for ind in range(start - 1, len(lines), nsou + 1):
        pdate = [int(s) for s in lines[ind].split() if s.isdigit()]
        date = datetime(pdate[0], 1, 1,
                        pdate[2], 0, pdate[3]) + timedelta(days=(pdate[1] - 1))
        metind = met.index[met['date'] == date.strftime('%Y-%m-%dT%H:%M:%SZ')]
        output.write(lines[ind] + '\n')
        for sou in range(0, nsou):
            ind = ind + 1
            namesou = str(lines[ind][0:15].split("'")[1])
            line = lines[ind][16:].split(' ')
            if namesou in lsou:
                newspe = []
                iconfsou = lsou.index(namesou)
                scheme = conf['sources'][iconfsou]['scheme']
                for s in range(0, nspe):
                    factor = met.iloc[metind][namesou+'_'+lspe[s]]
                    if scheme == 1:
                        oldmass = float(line[5+s])
                        newmass = oldmass*factor._values
                    if (scheme == 2) | (scheme == 3):
                        newmass = factor._values
                    newspe.append(newmass)
                # write the source information
                fstr = "{:<15s} {:3.2f} {:1.2f} {:1.1f} {:1.1f}"
                output.write(fstr.format(lines[ind][0:15],
                                         float(line[-nspe-4]),
                                         float(line[-nspe-3]),
                                         float(line[-nspe-2]),
                                         float(line[-nspe-1])))
                # for each species write the modified emission
                for i in range(0, nspe):
                    output.write(" {:1.7E}".format(float(newspe[i])))
                output.write("\n")
            else:
                # otherwise write the line without modifications
                output.write(lines[ind] + '\n')
    # closing input and output files
    output.close()
    file.close()
    logger.debug("Output calpuff file written.")
    return


def impact(conf, met):
    """Modulate emission from existing impact emissions input."""
    logger = logging.getLogger()
    logger.debug('{}'.format(impact.__doc__))

    # opening the input impact emissions input
    file = pd.DataFrame(pd.read_csv(conf['input'], sep=";"))

    lsout = []
    # collecting all sources involved in config.toml
    lsou = []
    for k in range(0, len(conf['sources'])):
        lsou.append(conf['sources'][k]['id'])
    # configuration file species
    cspe = []
    for sou in conf['sources']:
        for spe in sou['species']:
            cspe.append(spe)
    # reading each lines of input
    for index, row in file.iterrows():
        date = datetime.strptime(row['DATEDEB'], '%d-%m-%Y %H:%M:%S')
        metind = met.index[met['date'] ==
                           date.strftime('%Y-%m-%dT%H:%M:%SZ')]
        sou = row['SRCEID']
        if sou in lsou:
            iconfsou = lsou.index(sou)
            scheme = conf['sources'][iconfsou]['scheme']
            for spe in cspe:
                factor = met.iloc[metind][str(sou)+'_'+spe]
                qspe = 'Q_' + spe
                if scheme == 1:
                    oldmass = float(row[qspe])
                    newmass = oldmass*factor._values
                if (scheme == 2) | (scheme == 3):
                    newmass = factor._values
                row[qspe] = newmass
        lsout.append(row)

    output = pd.DataFrame(lsout)
    # writing output csv file
    output.to_csv(conf['output'], index=False, sep=";")
    return


def aermod(conf, met):
    """Modulate emission from existing aermod emissions input."""
    logger = logging.getLogger()
    logger.debug('{}'.format(aermod.__doc__))

    # opening the input aermod emissions input
    with open(conf['input'], 'r') as file:
        lines = [line.rstrip() for line in file]
    # opening the output file for writing
    output = open(conf['output'], 'w')

    # collecting all sources involved in config.toml
    lsou = []
    for k in range(0, len(conf['sources'])):
        lsou.append(conf['sources'][k]['id'])

    s2w = '{:2s} {:8s} {:2d} {:>2d} {:>2d} {:>2d} {:<7s} '
    ns = len(lines[0].split()) - 7
    # processing each line of the emission file
    for ind in range(0, len(lines)):
        line = lines[ind].split()
        sou = str(line[6])
        # if the source has to be processed
        if sou in lsou:
            # build datetime from emission file line
            date = datetime(year=2000 + int(line[2]),
                            month=int(line[3]),
                            day=int(line[4]),
                            hour=(int(line[5]) - 1),
                            minute=0, second=0)
            date = date + timedelta(hours=1)
            # find the corresponding emission factor
            metind = met.index[met['date'] ==
                               date.strftime('%Y-%m-%dT%H:%M:%SZ')]
            iconfsou = lsou.index(sou)
            scheme = conf['sources'][iconfsou]['scheme']
            spe = conf['sources'][iconfsou]['species'][0]
            factor = met.iloc[metind][str(sou)+'_'+spe]
            if scheme == 1:
                oldmass = float(line[7])
                newmass = oldmass*factor._values
            if (scheme == 2) | (scheme == 3):
                newmass = factor._values
            newline = line
            newline[7] = newmass.item(0)
        else:
            # in this case the line does not change
            newline = line
        # writing the new line or simply copy the
        # existing one
        output.write(s2w.format(newline[0], newline[1],
                                int(newline[2]),
                                int(newline[3]),
                                int(newline[4]),
                                int(newline[5]),
                                newline[6]))
        output.write('{:>6.3f} '.format(newline[7]))
        # formatting the elements after the emission rate
        for i in range(1, ns):
            output.write('{:>6.3f} '.format(float(newline[7+i])))
        # windows end-of-line \r\n, for linux/mac set \n
        output.write('\r\n')
    # closing input and output files
    output.close()
    file.close()
    logger.debug("Output calpuff file written.")
    return
