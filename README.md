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

