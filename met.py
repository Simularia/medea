import pandas as pd




from factor import factor


def readmet(conf):
    met = pd.read_csv(conf['windinputfile'])
    columns = ['date', 'wd', 'ws']
    for i in conf['source']:
        for j in conf['species']:
            columns.append(str(i)+j)
    metout = pd.DataFrame([],columns=columns, index = range(1, len(met.index + 1)))
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
                metout.iloc[idx,str(i)+j] = fact
        metout.iloc[idx, 'date'] = date
        metout.iloc[idx, 'ws'] = ws
        metout.iloc[idx, 'wd'] = wd
    metout.to_csv(conf['windoutputfile'])
    return metout
