# eolo usage

EOLO: compute wind-dependent emissions for dispersion models.

positional arguments:
  config       Path to input configuration toml file.

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  Activate debug mode

## OUTLINE

- per i parametri di input vedere il file "config.toml"
    e la sezione FILE DI CONFIGURAZIONE più avanti

- per i cumuli di polvere (schema 2) attualmente sono disponibili 
    3 forme: piramidali, coniche e piatte.

## IPOTESI

- il file meteo in input deve essere sempre fornito,
    anche se si sceglie l'algoritmo schema 3 che non necessita
    dei dati di vento: serve sempre almeno la data/ora
- il pemtim deve essere nel formato tipo quello in "./test/pemtim"
- il file calpuff deve essere nel formato come "./test/calpuffpolv"
- il file impact deve essere nel formato come "./test/impact_input.csv"
- il file aermod deve essere nel formato come "./test/aeremi.dat"
- la durata delle emissioni è oraria

## FILE DI TEST

Nella cartella test sono presenti alcuni file per i test dei 
vari formati:
- aeremi.dat per AERMOD
- calpuffpolv per CALPUFF
- impact_input.csv per IMPACT
- pemspe/pemtim per SPRAY
- windinput.csv per la meteorologia

## FILE METEOROLOGICO IN INPUT

Il file meteorologico (windinputfile) è di tipo .csv
con almeno la data nel seguente formato:
date,ws,wd,stabclass,z
2019-01-01T00:00:00Z,4.32,111,B,10
Il parametro wd non è al momento utilizzato,
i parametri z e stabclass sono utilizzati soltanto per lo schema 1,
il parametro ws non è utilizzato nello schema 3.

## FILE METEOROLOGICO E FATTORI EMISSIONE IN OUTPUT

Il file meteorologico in output con fattori emissivi (windoutputfile)
è di tipo .csv e contiene tutte le informazioni di windinputfile
più tutti i fattori emissione per tutte le sorgenti e specie
specificate nel file fi configurazione.
## FILE DI CONFIGURAZIONE

- input: stringa del path al file di emissione in input
- output: stringa del path al file di emissione in output
- pemspe: stringa del path al file pemspe nel caso mode = 0 (spray)
- windinputfile: stringa del path al file meteo in input
- windoutputfile: stringa del path al file meteo e fattori emissione in output
- mode: modalità di eolo per lavorare con file di 
        0: spray
        1: calpuff
        2: impact
        3: aermod
- sources: è un toml inline table, cioé un array, i cui elementi sono
           delimitati da [], e ogni elemento è un "dizionario", cioè
           elementi definiti da {key1 = val1, key2 = val2, etc...}.
           In particolare, a seconda dello schema per la sorgente 
           specificata, i campi del dizionario possono variare.
           Un esempio di valori di questo parametro toml è il seguente:
sources = [
    # sorgente odorigena
    { id = 1, scheme = 1, species = ["OU"], height = 5, terrain = "rural", vref = 0.6},
    # erosione cumulo di polveri con base dati vento disponibile 
    # forma piramidale (xmin, xmax, ymin, ymax)
    { id = 2, scheme = 2, species = ["PTS", "PM25", "PM10"], height = 4, xmax = 5, xmin = 2, ymin = 2, ymax = 5, mass = 2.5E+10, roughness = 0.005, tfv = 0.05},  
    # forma conica (radius)
    { id = 3, scheme = 2, species = ["PTS", "PM25", "PM10"], height = 4, radius = 3, mass = 2.5E+10, roughness = 0.005, tfv = 0.05},  
    # forma "piatta" (diameter) 
    { id = 4, scheme = 2, species = ["PTS", "PM25", "PM10"], height = 4, diameter = 5, mass = 2.5E+10, roughness = 0.005, tfv = 0.05},  
    # erosione cumulo di polveri con base dati vento non disponibile (radius è il raggio equivalente)
    { id = 5, scheme = 3, species = ["PTS", "PM25", "PM10"], height = 4, radius = 3.6, movh = 4} 
]

mass in microgrammi
roughness in metri
(radius, diameter, xmax, xmin, ymax, ymin, height) in metri
movh numero movimentazioni all'ora
tfv threshold friction velocity in metri al secondo
vref velocità di riferimento per il fattore emissivo odorigeno in metri al secondo
terrain = "rural" o "urban"

## FORMULE E RIFERIMENTI

Schema 1 - odori
Formula per fattore moltiplicativo
```math
f = \left( \dfrac{w_s \left(\frac{z}{h}\right)^{\beta}}{v_{\text{ref}}}\right)^{\gamma}
```
dove $w_s$ è la wind speed, $z$ è la quota a cui è riferita la velocità
del vento, $\beta$ è un parametro calcolato a partire dal tipo di terreno
e dalla classe di stabilità.
Riferimento bibliografico:
Bellasio, R.; Bianconi, R. A
Heuristic Method for Modeling Odor
Emissions from Open Roof
Rectangular Tanks. Atmosphere 2022,
13, 367. https://doi.org/10.3390/
atmos13030367


Schema 2 - cumuli polveri


$f_m = 1.6 w_s + 0.43$ è il fastest mile

La superficie viene calcolata a seconda della forma del cumulo:
1) piramidale
  $$S = \dfrac{8}{5} (x_{max}-x_{min}) \sqrt{\left(\dfrac{ (x_{max}-x_{min})}{5}\right)^2 + h^2}  + \dfrac{4}{3}(y_{max}-y_{min}) \sqrt{\left( \dfrac{(y_{max}-y_{min})}{3}\right) ^2 + h^2}$$
2) conica
  $$S = \pi r \sqrt(r^2 + h^2)$$
3) piatta
  $$S = \dfrac{\pi}{4} d^2 $$

Calcolo della velocità di attrito:
$$ u_1^* = \max(0.4 \dfrac{f_m}{\log \frac{25}{z0}} 0.2, u^*_{thr}) $$
$$ u_2^* = \max(0.4 \dfrac{f_m}{\log \frac{25}{z0}} 0.6, u^*_{thr}) $$
$$ u_3^* = \max(0.4 \dfrac{f_m}{\log \frac{25}{z0}} 0.9, u^*_{thr}) $$

Calcolo del potenziale erosivo:
$$P_1 = 58 (u_1^* - u^*_{thr})^2 + 25*(u_1^* - u^*_{thr}) $$
$$P_2 = 58 (u_2^* - u^*_{thr})^2 + 25*(u_2^* - u^*_{thr}) $$
$$P_3 = 58 (u_3^* - u^*_{thr})^2 + 25*(u_3^* - u^*_{thr}) $$

Calcolo massa oraria emessa:
$$ e_{r} = k \dfrac{40 P_1 + 48 P_2 + 12 P_3}{100} 10^6 $$
$k = 0.075$ per il pm25, $k = 0.5$ per il pm10, $k = 1$ per le pts.

Riferimento bibliografico:
https://www.epa.gov/air-emissions-factors-and-quantification/ap-42-compilation-air-emissions-factors
AP-42: Compilation of Air Emissions Factors 
Sezione 13.2.5 Industrial Wind Erosion

Schema 3 - cumuli polveri senza l'uso dei dati di vento

```math
e_{r} = 10^9  e_{f} S m_{h}
```
$e_{r}$ è l'emission rate (o massa oraria emessa) effettivo da mettere nel file di emissione.
$e_{f}$ è il fattore emissivo del generico inquinante:
se $h/(2*r) > 0.2$, cioè nel caso di cumuli alti,
per il pm25, = 1.26E-06, per il pm10, = 7.9E-06, per le pts, = 1.6E-05,
altrimenti 
per il pm25, = 3.8E-05, per il pm10, = 2.5E-04, per le pts, = 5.1E-04.
$S = \pi r \sqrt(r^2 + h^2)$ è la superficie del cumulo di forma conica,
dove $h$ è l'altezza ed $r$ è il raggio.
$m_{h}$ sono il numero di movimentazioni orarie del cumulo.

Riferimento bibliografico:
Sezione 1.4 "EROSIONE DEL VENTO DAI CUMULI" del documento
LINEE GUIDA PER LA VALUTAZIONE DELLE EMISSIONI DI
POLVERI PROVENIENTI DA ATTIVITÀ DI PRODUZIONE,
MANIPOLAZIONE, TRASPORTO, CARICO O STOCCAGGIO DI
MATERIALI POLVERULENTI, di ARPA TOSCANA




