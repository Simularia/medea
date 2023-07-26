# eolo usage

EOLO: compute wind-dependent emissions for spray.

positional arguments:
  config       Path to input configuration toml file.

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  Activate debug mode

## OUTLINE

- per i parametri di input vedere il file "config.toml"

- per i cumuli di polvere attualmente sono disponibili 
    3 forme: piramidali, coniche e piatte.

## IPOTESI

- il file meteo in input deve essere sempre fornito,
    anche se si sceglie l'algoritmo schema 3 che non necessita
    dei dati di vento: serve sempre almeno la data/ora
- il pemtim deve essere nel formato tipo quello in "./test/pemtim"
- il file calpuff deve essere nel formato come "./test/calpuffpolv"
- il file impact deve essere nel formato come  "./test/impact_input.csv"
- il file aermod deve essere nel formato come  "./test/aeremi.dat"
- la durata delle emissioni è oraria

## FILE DI TEST

Nella cartella test sono presenti alcuni file per i test dei 
vari formati:
- aeremi.dat per AERMOD
- calpuffpolv per CALPUFF
- impact_input.csv per IMPACT
- pemspe/pemtim per SPRAY
- windinput.csv per la meteorologia
