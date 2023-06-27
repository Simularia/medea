import pandas as pd
from datetime import datetime 

def pemtim(conf, metout):
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

    return