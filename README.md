# Documentazione EOLO

## Uso del programma eolo
Prima di usare eolo, occorre installare alcuni pacchetti python tramite virtual environment e attivare il virtual environment stesso:
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

## OUTLINE

Per i parametri di input vedere il file "config.toml"
    e la sezione [FILE DI CONFIGURAZIONE](#file-di-configurazione) più avanti


## IPOTESI

- Il [file meteo in input](#file-meteorologico-in-input) deve essere sempre fornito,
    anche se si sceglie l'algoritmo schema 3 che non necessita
    dei dati di vento: serve sempre almeno la data/ora;
- Nel caso SPRAY, il pemtim e pemspe devono essere nel formato tipo quelli in "./test/pemtim" e "./test/pemspe";
- Nel caso CALPUFF, il file calpuff deve essere nel formato come "./test/calpuffpolv";
- Nel caso IMPACT, il file impact deve essere nel formato come "./test/impact_input.csv";
- Nel caso AERMOD, il file aermod deve essere nel formato come "./test/aeremi.dat";
- La durata delle emissioni deve essere oraria.

## FILE DI TEST

Nella cartella `./test/` sono presenti alcuni file per i test dei 
vari formati:

- `aeremi.dat` per AERMOD;
- `calpuffpolv` per CALPUFF;
- `impact_input.csv` per IMPACT;
- `pemspe` e `pemtim` per SPRAY;
- `windinput.csv` per la meteorologia.

## FILE METEOROLOGICO IN INPUT

Il file meteorologico, specificato nel file di configurazione toml con il campo `windinputfile`, deve essere di tipo .csv con la data nel seguente formato:
```
date,ws,wd,stabclass,z
2019-01-01T00:00:00Z,4.32,111,B,10
```
Il parametro wd non è al momento utilizzato, i parametri z e stabclass sono utilizzati soltanto per lo schema 1, il parametro ws non è utilizzato nello schema 3.

Nota: il parametro date è sempre necessario. Ulteriori parametri necessari sono specificati nella descrizione degli [schemi](#formule-e-riferimenti).

## FILE METEOROLOGICO IN OUTPUT

Il file meteorologico in output, specificato nel file di configurazione toml con il campo `windoutputfile`, sarà di tipo .csv e contiene tutte le informazioni di input più i fattori moltiplicativi o masse (in funzione dello schema applicato), per tutte le sorgenti e specie definite nel file di configurazione.

## FILE DI CONFIGURAZIONE
Descrizione delle chiavi di configurazione:

- `input`: stringa del path al file di emissione in input (`="./test/pemtim"`)
- `output`: stringa del path al file di emissione in output (`="./test/pemtimout"`)
- `windinputfile`: stringa del path al file meteo in input (`="./test/met.csv"`)
- `windoutputfile`: stringa del path al file meteo e fattori emissione in output 
(`="./test/metout.csv"`)
- `mode`: (numero intero) modalità di eolo per la scelta del modello:
  - 0: spray
  - 1: calpuff
  - 2: impact
  - 3: aermod
- `pemspe`: stringa del path al file pemspe necessaria soltanto nel caso mode = 0 (spray)
- `sources`: è un toml inline table, cioè un array delimitato da `[...]`, e ogni elemento è un "dizionario", cioè elementi definiti da `{key1 = val1, key2 = val2, etc...}`,  che descrive una sorgente.
In particolare, la chiave `scheme` definisce l'algoritmo da applicare e a seconda dello schema specificato per la sorgente, i campi del dizionario possono variare.

Un esempio di valori di questo parametro toml è il seguente:
```
sources = [
    ### schema 1 - sorgente odorigena 
    { id = 1, scheme = 1, species = ["OU"], height = 5, 
      terrain = "rural", vref = 0.6},

    ### schema 2 - erosione cumulo di polveri con base dati vento disponibile
    # forma piramidale (xmin, xmax, ymin, ymax) 
    { id = 2, scheme = 2, species = ["PTS", "PM25", "PM10"], 
      height = 4, xmax = 5, xmin = 2, ymin = 2, ymax = 5, 
      mass = 2.5E+10, roughness = 0.005, tfv = 0.05},  
    # forma conica (radius)
    { id = 3, scheme = 2, species = ["PTS", "PM25", "PM10"], 
      height = 4, radius = 3, mass = 2.5E+10, roughness = 0.005, 
      tfv = 0.05},  
    # forma "piatta" (diameter) 
    { id = 4, scheme = 2, species = ["PTS", "PM25", "PM10"], 
      height = 4, diameter = 5, mass = 2.5E+10, roughness = 0.005,
      tfv = 0.05},  

    ### schema 3 - erosione cumulo di polveri con base dati vento non disponibile
    { id = 5, scheme = 3, species = ["PTS", "PM25", "PM10"], 
      height = 4, radius = 3.6, movh = 4} 
]
```
Descrizione dei campi **obbligatori** descrittivi delle sorgenti **comuni** a tutti i vari schemi:
- `id`: stringa identificativa della sorgente nei file di emissione in input;
- `scheme`: = {1,2,3} numero intero che identifica lo [schema](#formule-e-riferimenti):
  - 1 = schema per sorgenti odorigene,
  - 2 = schema per sorgenti cumuli di polveri con base dati di vento disponibile,
  - 3 = schema per sorgenti cumuli di polveri con base dati di vento non disponibile;
- `species`: array di stringhe identificative delle specie trattate;
- `height`: altezza della sorgente in metri.

Descrizione dei campi **specifici** per ciascun schema:
- [schema 1](#schema-1---odori):
  - `terrain`: {"rural", "urban"} tipologia terreno (**opzionale**)
  - `vref`: velocità (m/s) di riferimento del fattore emissivo presente nel file di emissione in input (**opzionale**, default = 0.3)

- [schema 2](#schema-2---cumuli-di-polveri-con-luso-dei-dati-di-vento):
  - `mass`: massa in mcg del cumulo di polveri (**obbligatorio**);
  - `tfv`: velocità (m/s) d'attrito di soglia (**obbligatorio**);
  - `roughness`: lunghezza di rugosità (m) (**opzionale**, default = 0.005);
  - geometria della sorgente (**obbligatorio**):
    - piramide: `xmin`, `xmax`, `ymin`, `ymax`, coordinate (m) orizzontali del cumulo piramidale;
    - conica: `radius`, raggio (m) del cono;
    - piatto: `diameter`, diametro (m) del cumulo piatto.

- [schema 3](#schema-3---cumuli-polveri-senza-luso-dei-dati-di-vento):
  - `radius`: raggio (m) equivalente del cumulo (**obbligatorio**);
  - `movh`: numero di movimentazioni orarie del cumulo (**obbligatorio**).

## FORMULE E RIFERIMENTI

### Schema 1 - Odori
Fattore moltiplicativo del SOER:

$$f = \left( \dfrac{w_s \left(\frac{z}{h}\right)^{\beta}}{v_{\text{ref}}}\right)^{\gamma}$$

dove $w_s$ è la wind speed, $\gamma = 0.5$, $z$ (m) è la quota a cui è riferita la velocità del vento, $h$ è l'altezza (m) della sorgente, $\beta$ è un parametro calcolato a partire dal tipo di terreno e dalla classe di stabilità specificata nel file input meteorologico. Se manca almeno un parametro tra tipo di terreno e classe di stabilità, allora il valore di default di $\beta$ è 0.55, altrimenti è calcolato in accordo con la seguente tabella:

|tipo terreno/classe stabilità|A|B|C|D|E|F|
|:---|---|---|---|---|---|---|
|rural| 0.07 | 0.07 | 0.1 | 0.15 | 0.35 | 0.55 |
|urban| 0.15 | 0.15 | 0.2 | 0.25 | 0.3 | 0.3 |



- Riferimento bibliografico: Bellasio, R.; Bianconi, R. A Heuristic Method for Modeling Odor Emissions from Open Roof Rectangular Tanks. Atmosphere 2022, 13, 367. https://doi.org/10.3390/atmos13030367


### Schema 2 - Cumuli di polveri con l'uso dei dati di vento
Algoritmo di calcolo secondo la metodologia EPA AP-42 è il seguente:

- Calcolo del fastest mile a partire dalla wind speed:
$$f_m = 1.6 w_s + 0.43$$


- La superficie viene calcolata a seconda della forma del cumulo:

  1) sorgente piramidale
  
  $$S = \dfrac{8}{5} (x_{max}-x_{min}) \sqrt{\left(\dfrac{ (x_{max}-x_{min})}{5}\right)^2 + h^2}  + \dfrac{4}{3}(y_{max}-y_{min}) \sqrt{\left( \dfrac{(y_{max}-y_{min})}{3}\right) ^2 + h^2}$$
  
  dove $h$ è l'altezza del cumulo, $x_{min},x_{max},y_{min},y_{max}$ sono le dimensione orizzontali del cumulo.

  2) sorgente conica
  
  $$S = \pi r \sqrt(r^2 + h^2)$$

  3) sorgente piatta
  
  $$S = \dfrac{\pi}{4} d^2 $$

- Calcolo della velocità di attrito:

  $$u_1^* = \max \left(0.4 \dfrac{f_m}{\log \frac{25}{z_0}} 0.2, u^*_{thr}\right)$$

  $$u_2^* = \max \left(0.4 \dfrac{f_m}{\log \frac{25}{z_0}} 0.6, u^*_{thr}\right)$$
  
  $$u_3^* = \max \left(0.4 \dfrac{f_m}{\log \frac{25}{z_0}} 0.9, u^*_{thr}\right)$$

dove $z_0$ è la rugosità, $u^*_{thr}$ è la velocità d'attrito di soglia, entrambe impostate nel file di configurazione.

- Calcolo del potenziale erosivo:

$$P_1 = 58 (u_1^* - u^*_{thr})^2 + 25*(u_1^* - u^*_{thr})$$

$$P_2 = 58 (u_2^* - u^*_{thr})^2 + 25*(u_2^* - u^*_{thr})$$

$$P_3 = 58 (u_3^* - u^*_{thr})^2 + 25*(u_3^* - u^*_{thr})$$


- Calcolo massa oraria emessa:

$$e_{r} = k \dfrac{40 P_1 + 48 P_2 + 12 P_3}{100} 10^6$$

con $k = 0.075$ per il pm25, $k = 0.5$ per il pm10, $k = 1$ per le pts.

- Riferimento bibliografico: https://www.epa.gov/air-emissions-factors-and-quantification/ap-42-compilation-air-emissions-factors AP-42: Compilation of Air Emissions Factors, Sezione 13.2.5 Industrial Wind Erosion

### Schema 3 - Cumuli polveri senza l'uso dei dati di vento
L'algoritmo secondo la metodologia ARPA Toscana semplificata è sintetizzato dalla seguente formula:

$$e_{r} = 10^9  e_{f} S m_{h}$$

- $e_{r}$ è l'emission rate (o massa oraria emessa) effettivo da mettere nel file di emissione.
- $e_{f}$ è il fattore emissivo del generico inquinante:
- se $\dfrac{h}{2r} > 0.2$, cioè nel caso di cumuli alti, per il pm25, $= 1.26 \cdot 10^{-6}$, per il pm10, $= 7.9 \cdot 10^{-6}$, per le pts, $= 1.6 \cdot 10^{-5}$,
- se $\dfrac{h}{2r} \le 0.2$, cioè nel caso di cumuli bassi, per il pm25, $= 3.8 \cdot 10^{-5}$, per il pm10, $= 2.5 \cdot 10^{-4}$, per le pts, $= 5.1 \cdot 10^{-4}$.
- $S = \pi r \sqrt(r^2 + h^2)$ è la superficie del cumulo di forma conica, dove $h$ è l'altezza ed $r$ è il raggio.
- $m_{h}$ sono il numero di movimentazioni orarie del cumulo.

- Riferimento bibliografico: Sezione 1.4 "EROSIONE DEL VENTO DAI CUMULI" del documento "LINEE GUIDA PER LA VALUTAZIONE DELLE EMISSIONI DI POLVERI PROVENIENTI DA ATTIVITÀ DI PRODUZIONE, MANIPOLAZIONE, TRASPORTO, CARICO O STOCCAGGIO DI MATERIALI POLVERULENTI", di ARPA TOSCANA

## Generazione del README.pdf
Per generare il documento pdf di questo manuale, digitare sul terminale il seguente comando:
```{sh}
$ pandoc --to=pdf README.md -V geometry:margin=25mm -o README.pdf
```