import pandas as pd




from factor import factor


def readmet():
### non è giusto l'inserimento delle entrate del dataframe metout
    met = pd.read_csv(conf['windinputfile'])
    columns = ['date', 'wd', 'ws']
    for i in conf['source']:
        for j in conf['species']:
            columns.append(str(i)+j)
    metout = pd.DataFrame([],columns=columns)
    for idx in met.index:
        ws = met.iloc[idx, 'ws']
        date = met.iloc[idx, 'date']
        wd = met.iloc[idx, 'wd']
        for i in conf['source']:
            for j in conf['species']:
                ind = conf['source'].index(i)
                scheme = conf['scheme'][ind]
                height = conf['height'][ind]

                fact = computefactor(scheme, ws, height)
                metout[str(i)+j] = fact
        metout['date'] = date
        metout['ws'] = ws
        metout['wd'] = wd
        metout.loc[len(metout.index)] = ['Amy', 89, 93] 
    metout.to_csv(conf['windoutputfile'])