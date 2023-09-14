<!-- 
 SPDX-FileCopyrightText: 2023 Simularia s.r.l. <info@simualaria.it>

 SPDX-License-Identifier: AGPL-3.0-or-later
-->

# EOLO

## Introduzione

Usa `eolo` per calcolare l'input emissivo dipendente dal vento per diversi modelli di dispersione atmosferica.
Questo strumento funziona con i modelli di dispersione in atmosfera CALPUFF, AERMOD, ARIA-IMPACT e SPRAY. Le emissioni sono calcolate secondo diversi schemi adatti per simulazioni numeriche sia di odore che di qualità dell'aria.

Nella [sezione](#algoritmi-e-riferimenti-bibliografici) dedicata sono riportati la descrizione degli algoritmi utilizzati e le referenze bibliografiche.


## Uso del codice eolo

Prima di usare eolo, occorre installare alcuni moduli python tramite virtual environment e attivare il virtual environment stesso:

```{sh}
$ virtualenv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

Dopodiché si può procedere con l'uso:

```{sh}
(venv) $ ./eolo.py -h
usage: eolo.py [-h] [-d] config

EOLO: compute wind-dependent emissions for dispersion models.

positional arguments:
  config       Path to input configuration toml file.

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  Activate debug mode
```

## File di configurazione

Il file di configurazione è in formato [*toml*](https://toml.io/). Un esempio di configurazione è contenuto nel file `config.toml` incluso in questo repository.

Le chiavi di configurazione sono descritte di seguito:

- `input`: stringa con il percorso al file di emissione in input (`="./test/pemtim"`);
- `output`: stringa con il percorso al file di emissione in output (`="./test/pemtimout"`);
- `windInputFile`: stringa con il percorso al file meteo in input (`="./test/met.csv"` o `="postbin.dat"`);
- `mettype`: stringa che indica il tipo di file meteorologico da leggere:
  - =  "postbin" : legge un file di tipo postbin;
  - = "csv" : legge un file di tipo .csv;
  - di default tenta di leggere un file di tipo .csv;
- `windOutputFile`: stringa con il percorso al file meteo e fattori emissione in output (`="./test/metout.csv"`);
- `mode`: (numero intero o stringa del modello) modalità di eolo per la scelta del modello:
  - 0: spray;
  - 1: calpuff;
  - 2: impact;
  - 3: aermod;
- `pemspe`: stringa con il percorso al file pemspe necessaria soltanto nel caso mode = 0 (spray);
- `sources`: è un toml inline table, cioè un array delimitato da `[...]`, e ogni elemento è un *dizionario*, cioè elementi definiti da `{key1 = val1, key2 = val2, etc...}`, che descrive una sorgente.
In particolare, la chiave `scheme` definisce l'algoritmo da applicare e, a seconda dello schema specificato per la sorgente, i campi del dizionario possono variare.

Un esempio di valori di questo parametro *toml* è il seguente:
```
sources = [
    ### schema 1 - sorgente odorigena 
    { id = 1, scheme = 1, species = ["OU"], height = 5, 
      terrain = "rural", vref = 0.6},

    ### schema 2 - erosione cumulo di polveri con base dati vento disponibile
    # forma piramidale (lati e angolo)
    { id = 2, scheme = 2, species = ["PTS", "PM25", "PM10"], 
      height = 4, major = 5, minor = 3, angle = 15, 
      roughness = 0.5, tfv = 0.05},  
    # forma conica (radius)
    { id = 3, scheme = 2, species = ["PTS", "PM25", "PM10"], 
      height = 4, radius = 3, roughness = 0.005, 
      tfv = 0.05},   

    ### schema 3 - erosione cumulo di polveri con base dati vento non disponibile
    { id = 4, scheme = 3, species = ["PTS", "PM25", "PM10"], 
      height = 4, radius = 3.6, movh = 4} 
]
```
Descrizione dei campi **obbligatori** descrittivi delle sorgenti, **comuni** a tutti i vari schemi:

- `id`: stringa o numero identificativa della sorgente nei file di emissione in input (puà essere anche una lista, come ad esempio: [1, 'source1', 'source 2']);
- `scheme`: = {1,2,3} numero intero che identifica lo [schema](#algoritmi-e-riferimenti-bibliografici):
  - 1 = schema per sorgenti odorigene;
  - 2 = schema per sorgenti cumuli di polveri con base dati di vento disponibile;
  - 3 = schema per sorgenti cumuli di polveri con base dati di vento non disponibile;
- `species`: array di stringhe identificative delle specie trattate;
- `height`: altezza del cumulo in metri.

Descrizione dei campi **specifici** per ciascun schema:

- [schema 1](#schema-1---odori):
  - `terrain`: {"rural", "urban"} tipologia terreno (**opzionale**);
  - `vref`: velocità (m/s) di riferimento del fattore emissivo usato per la stima dell'emissione nel file di input (**opzionale**, default = 0.3);

- [schema 2](#schema-2---cumuli-di-polveri-con-luso-dei-dati-di-vento):
  - `tfv`: velocità (m/s) d'attrito di soglia (**obbligatorio**);
  - `roughness`: lunghezza di rugosità (cm) (**opzionale**, default = 0.5);
  - geometria della sorgente (**obbligatorio**):
    - piramide: `major`, `minor`, `angle`, lati del rettangolo alla base (m) e angolo del lato lungo rispetto all'asse x (senso antiorario, range -90°,+90°);
    - conica: `radius`, raggio (m) del cono.

- [schema 3](#schema-3---cumuli-polveri-senza-luso-dei-dati-di-vento):
  - `radius`: raggio (m) equivalente del cumulo (**obbligatorio**);
  - `movh`: numero di movimentazioni orarie del cumulo (**obbligatorio**).

**Nota**: le informazioni geometriche presenti nel file di configurazione non sostituiranno quelle presenti nel file di emissione e tra le due non viene eseguito alcun tipo di controllo di compatibilità.


## Ipotesi

- Il [file meteo](#file-meteorologico-in-input) in input deve essere sempre fornito, anche se si sceglie l'algoritmo schema 3 che non necessita dei dati di vento: serve sempre almeno la data/ora;
- Nel caso SPRAY, il pemtim e pemspe devono essere nel formato tipo quelli in "./test/pemtim" e "./test/pemspe";
- Nel caso CALPUFF, il file calpuff deve essere nel formato come "./test/calpuffpolv";
- Nel caso IMPACT, il file impact deve essere nel formato come "./test/impact_input.csv";
- Nel caso AERMOD, il file aermod deve essere nel formato come "./test/aeremi.dat";
- La durata delle emissioni deve essere oraria.


## File di test

Nella cartella `./test/` sono presenti alcuni file per i test dei 
vari formati:

- `aeremi.dat` per AERMOD;
- `calpuffpolv` per CALPUFF;
- `impact_input.csv` per IMPACT;
- `pemspe` e `pemtim` per SPRAY;
- `windinput.csv` e `postbin.dat` per la meteorologia.


## File meteorologico in input

Il file meteorologico, specificato nel file di configurazione *toml* con il campo `windInputFile`, può essere di tipo *csv* con la data nel seguente formato:
    ```
    date,ws,wd,stabclass,z
    2019-01-01T00:00:00Z,4.32,111,B,10
    ```
oppure nel formato *postbin*: in quest'ultimo caso dovrà essere specificato il parametro `mettype` nel file di configurazione.

I parametri `z` (altezza a cui è riferita la velocità del vento) e `stabclass` (classe di stabilità, con lettere A, B, C, D, E, F oppure numeri 1, 2, 3, 4, 5, 6) sono utilizzati soltanto per lo schema 1, i parametro `ws` (intensità del vento) e `wd` (direzione del vento) non sono utilizzati nello schema 3.

Nota: il parametro `date` è sempre necessario. Ulteriori parametri necessari sono specificati nella descrizione degli [schemi](#algoritmi-e-riferimenti-bibliografici).


## File meteorologico in output

Il file meteorologico in output, specificato nel file di configurazione *toml* con il campo `windOutputFile`, sarà di tipo *csv* e contiene tutte le informazioni di input più i fattori moltiplicativi o masse (in funzione dello schema applicato), per tutte le sorgenti e specie definite nel file di configurazione.


## Algoritmi e riferimenti bibliografici


### Schema 1 - Odori
Fattore moltiplicativo del SOER:

$$f = \left( \frac{w_s \left(\frac{z}{h}\right)^{\beta}}{v_{\text{ref}}}\right)^{\gamma}$$

dove $w_s$ è la intensità del vento, $\gamma = 0.5$, $z$ (m) è la quota a cui è riferita la velocità del vento, $h$ è l'altezza (m) della sorgente, $\beta$ è un parametro calcolato a partire dal tipo di terreno e dalla classe di stabilità specificata nel file input meteorologico. Se manca almeno un parametro tra tipo di terreno e classe di stabilità, allora il valore di default di $\beta$ è 0.55, altrimenti è determinato con la seguente tabella:

|Tipo terreno / Classe di stabilità|A|B|C|D|E|F|
|:---|---|---|---|---|---|---|
|rural| 0.07 | 0.07 | 0.1 | 0.15 | 0.35 | 0.55 |
|urban| 0.15 | 0.15 | 0.2 | 0.25 | 0.3 | 0.3 |


Riferimento bibliografico:
- Bellasio, R.; Bianconi, R. A Heuristic Method for Modeling Odor Emissions from Open Roof Rectangular Tanks. Atmosphere 2022, 13, 367. https://doi.org/10.3390/atmos13030367


### Schema 2 - Cumuli di polveri con l'uso dei dati di vento
L'algoritmo di calcolo secondo la metodologia EPA AP-42 è il seguente:

- Calcolo del vento a 10 metri (1000 cm):

  $$ w_s = w_s(z)\frac{\log(1000/z_0)}{\log(z/z_0)} $$

  dove $z_0$ è la lunghezza di rugosità in cm e $z$ è la quota a cui sono riferiti i dati di vento.

- Calcolo del fastest mile a partire dalla intensità del vento $w_s$:

$$f_m = 1.6 w_s + 0.43$$

- La superficie viene calcolata a seconda della forma del cumulo:

  1) sorgente piramidale:
  $$S = \frac{8}{5} l_{major} \sqrt{\left(\frac{ l_{major}}{5}\right)^2 + h^2}  + \frac{4}{3}l_{minor} \sqrt{\left( \frac{l_{minor}}{3}\right) ^2 + h^2}$$
  
  dove $h$ è l'altezza del cumulo, $l_{major}, l_{minor}$ sono le dimensioni orizzontali del cumulo.

  2) sorgente conica
  $$S = \pi r \sqrt{r^2 + h^2}$$


- Calcolo della velocità di attrito:

  $$u_1^* = \max \left(0.4 \frac{f_m}{\log \frac{25}{z_0}} 0.2, u^*_{thr}\right)$$

  $$u_2^* = \max \left(0.4 \frac{f_m}{\log \frac{25}{z_0}} 0.6, u^*_{thr}\right)$$
  
  $$u_3^* = \max \left(0.4 \frac{f_m}{\log \frac{25}{z_0}} 0.9, u^*_{thr}\right)$$

  $$u_4^* = \max \left(0.4 \frac{f_m}{\log \frac{25}{z_0}} 1.1, u^*_{thr}\right)$$

  $$u_5^* = \max \left(0.4 \frac{f_m}{\log \frac{25}{z_0}}, u^*_{thr}\right)$$

dove $z_0$ è la rugosità (in cm), $u^*_{thr}$ è la velocità d'attrito di soglia, entrambe impostate nel file di configurazione.

- Calcolo del potenziale erosivo:

$$P_i = 58 (u_i^{*} - u^{*}_{thr})^2 + 25(u_i^{*} - u^{*}_{thr})$$

dove $i = 1,2,3,4,5$.


- Calcolo massa oraria emessa in mcg:

  a) se $\frac{h}{base} \le 0.2$:
  $$e_{r} = k S P_5  10^6$$

  b) se $\frac{h}{base} > 0.2$:

    1) se la forma del cumulo è simmetrica (conica)

    $$e_{r} = k S \frac{40 P_1 + 48 P_2 + 12 P_3 + 0P_4}{100} 10^6$$

    2) se la forma del cumulo è asimmetrica con vento incidente tra [0°,20°]:

    $$e_{r} = k S \frac{36 P_1 + 50 P_2 + 14 P_3 + 0P_4}{100} 10^6$$
    3) se la forma del cumulo è asimmetrica con vento incidente tra (20°,40°]:
    $$e_{r} = k S \frac{31 P_1 + 51 P_2 + 15 P_3 + 3P_4}{100} 10^6$$
    4) se la forma del cumulo è asimmetrica con vento incidente tra (40°,90°]:
    $$e_{r} = k S \frac{28 P_1 + 54 P_2 + 14 P_3 + 4P_4}{100} 10^6$$

con $k = 0.075$ per il PM25, $k = 0.5$ per il PM10, $k = 1$ per le PTS.

Riferimenti bibliografici: 

- EPA AP-42: Compilation of Air Emissions Factors, Sezione 13.2.5 Industrial Wind Erosion: https://www.epa.gov/air-emissions-factors-and-quantification/ap-42-compilation-air-emissions-factors

- Davis, F. K., and H. Newstein, 1968: The variation of gust factors and mean wind speed with height. J. Appl. Meteor., 7, 372–378


### Schema 3 - Cumuli polveri senza l'uso dei dati di vento

L'algoritmo implementa la metodologia semplificata di ARPA Toscana (basato su EPA AP-42) è sintetizzato dalla seguente formula:

$$e_{r} = 10^9  e_{f} S m_{h}$$

dove:

- $e_{r}$ è la massa oraria emessa (in mcg/ora) effettiva da scrivere nel file di emissione;
- $e_{f}$ è il valore di emissione dell' inquinante:
  1. se $\frac{h}{2r} > 0.2$, cioè nel caso di cumuli alti, per il PM25, $= 1.26 \cdot 10^{-6}$, per il PM10, $= 7.9 \cdot 10^{-6}$, per le PTS, $= 1.6 \cdot 10^{-5}$,
  2. se $\frac{h}{2r} \le 0.2$, cioè nel caso di cumuli bassi, per il PM25, $= 3.8 \cdot 10^{-5}$, per il PM10, $= 2.5 \cdot 10^{-4}$, per le PTS, $= 5.1 \cdot 10^{-4}$.

- $S = \pi r \sqrt{r^2 + h^2}$ è la superficie del cumulo di forma conica, dove $h$ è l'altezza ed $r$ è il raggio.

- $m_{h}$ è il numero di movimentazioni orarie del cumulo.

Riferimento bibliografico:

- Sezione 1.4 "Erosione del vento dai cumuli" del documento "Linee guida per la valutazione delle emissioni di polveri provenienti da attività di produzione, manipolazione, trasporto, carico o stoccaggio di materiali polverulenti", di Arpa Toscana.


## Generazione del README.pdf

Per generare il documento *pdf* di questo manuale, digitare sul terminale il seguente comando:
```{sh}
$ pandoc --to=pdf README_ita.md -V geometry:margin=25mm -o README_ita.pdf
```

## Autori

`eolo` è sviluppato e mantenuto da Massimiliano Romana presso [Simularia](https://www.simularia.it).

## Licenza

`eolo` è un [software libero](https://fsfe.org/freesoftware/freesoftware.en.html) il cui copyright è di [Simularia s.r.l.](https://www.simularia.it) ed è distribuito con licenza GNU Affero General Public License v3.0 o successivi.

