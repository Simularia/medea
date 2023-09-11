# EOLO Documentation

## How to use eolo
First of all, some python packages are required: these can be installed via a virtual environment as following:
```{sh}
$ virtualenv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```
After that one can use it:

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

## Hypothesis

- The meteorological input file is required in all possible eolo use configuration, at least it must contain the datetime of each deadline for emission:
- In the SPRAY case, pemtim and pemspe input files must be provided in the format specified in "./test/pemtim" and "./test/pemspe";
- In the CALPUFF case, calpuff input file must be provided in the format specified in "./test/calpuffpolv";
- In the IMPACT case, impact input file must be provided in the format specified in "./test/impact_input.csv";
- In the AERMOD case, aermod input file must be provided in the format specified in "./test/aeremi.dat";
- The emission duration of must be hourly.

## Test files

In the `./test/` folder some input files are provided as examples in all four formats and for meteorology:

- `aeremi.dat` for AERMOD;
- `calpuffpolv` for CALPUFF;
- `impact_input.csv` for IMPACT;
- `pemspe` and `pemtim` for SPRAY;
- `windinput.csv` and `postbin.dat` for meteorology.

## Meteorological input file
The meteorological file, specified in the toml configuration file with the field `windInputFile`, can be in the form '.csv' with datetime in the following format:
```
date,ws,wd,stabclass,z
2019-01-01T00:00:00Z,4.32,111,B,10
```
or in the 'postbin' format: in the latter case, the field `mettype` has to be filled up with the string `postbin` in the toml configuration file.
The z (wind field sensor height) and stabclass (stability class, specified with letters A,B,C,D,E,F or numbers 1,2,3,4,5,6) parameters are employed only with scheme number 1, while ws (wind speed) and wd (wind direction) are not needed with the scheme number 3.
Note: date parameter is always necessary. Further necessary parameters are specified in the scheme description.


## Meteorological output file

Output meteorological file, specified in the toml configuration file with the key `windOutputFile`, will be in the '.csv' format and it will contain all input information and all the computed emission factor or emission values (according to the selected scheme), for all specified sources and species defined in the same configuration file.

## Configuration file
The configuration file is in the toml format (see https://toml.io/en/): an example of this file is `config.toml`.
The keys of this toml file are described in the following:

- `input`: string containing the path to the input emission file (`="./test/pemtim"`)
- `output`: string containing the path to the output emission file (`="./test/pemtimout"`)
- `windInputFile`: string containing the path to the input meteo file (`="./test/met.csv"` or `="postbin.dat`)
- `mettype`: string containing the type of the input meteo file:
  - = 'postbin' : it tries to read a postbin file.
  - = 'csv' : it tries to read a .csv file.
  - by default (by omitting the field or filling it with an invalid value) it tries to read a .csv file.
- `windOutputFile`: string containing the path to the input meteo file and emission information of each source and species  (`="./test/metout.csv"`)
- `mode`: (integer number or string) eolo mode for the model choice:
  - 0: spray
  - 1: calpuff
  - 2: impact
  - 3: aermod
- `pemspe`: string containing the path to the pemspe file: it is needed only in spray mode (mode = 0)
- `sources`: it is a toml inline table, that is an array delimited by `[{...}, {...}, {...}]`, and each element is a "dictionary", in this form `{key1 = val1, key2 = val2, etc...}`, that describes a source. The key `scheme` defines the algorithm to apply to a source. The keys of a source's dictionary can be different as will be shown in the following.
An example of values of this parameter is shown below:

```
sources = [
    ### scheme 1 - odour source 
    { id = 1, scheme = 1, species = ["OU"], height = 5, 
      terrain = "rural", vref = 0.6},

    ### scheme 2 - wind erosion of dust cumulus with available data
    # pyramidal shape (2 sides and an angle)
    { id = 2, scheme = 2, species = ["PTS", "PM25", "PM10"], 
      height = 4, major = 5, minor = 3, angle = 15, 
      roughness = 0.5, tfv = 0.05},  
    # conical shape (radius)
    { id = 3, scheme = 2, species = ["PTS", "PM25", "PM10"], 
      height = 4, radius = 3, roughness = 0.005, 
      tfv = 0.05},   

    ### scheme 3 -  wind erosion of dust cumulus with no available data
    { id = 4, scheme = 3, species = ["PTS", "PM25", "PM10"], 
      height = 4, radius = 3.6, movh = 4} 
]
```
Details on the **mandatory** and **common** keys that are common to all scheme:
- `id`: identifier string or number in the input emission file (it can also be a list, e.g. [1, 'source1', 'source 2']);
- `scheme`: = {1,2,3} integer number that identifies the [scheme](#employed-formulas-and-bibliographical-references)
  - 1 = scheme for odour sources,
  - 2 = scheme for dust cumulus with available wind data,
  - 3 = scheme for dust cumulus with no available wind data;
- `species`: array of strings that identify the involved species;
- `height`: source height in meters.

Description of **specific** keys for each scheme:
- [scheme 1](#scheme-1---odour):
  - `terrain`: {"rural", "urban"} terrain type (**optional**)
  - `vref`: reference velocity (m/s) of the emission factor used to estimate the emission in the input file (**optional**, default = 0.3)

- [scheme 2](#scheme-2---wind-erosion-of-dust-cumulus-with-available-wind-data)):
  - `tfv`: threshold friction velocity (m/s) (**mandatory**);
  - `roughness`: rugosity or roughness length (cm) (**optional**, default = 0.5);
  - source geometry (**mandatory**):
    - pyramid: `major`, `minor`, `angle`, sides of the base rectangle (m) and angle between the major side and the x-axis (anticlockwise, range -90°,+90°);
    - conic: `radius`, cone radius (m).

- [scheme 3](#scheme-3---wind-erosion-of-dust-cumulus-with-no-available-wind-data):
  - `radius`: equivalent cumulus radius (m) (**mandatory**);
  - `movh`: hourly movement of cumulus number (**mandatory**).

**Note**: geometrical information in the config.toml will not substitute those present in the emission file and no compatibility control is performed between the two file.
## Employed formulas and bibliographical references

### Scheme 1 - Odour
SOER Multiplicative factor:

$$f = \left( \dfrac{w_s \left(\frac{z}{h}\right)^{\beta}}{v_{\text{ref}}}\right)^{\gamma}$$

where $w_s$ is the wind speed, $\gamma = 0.5$, $z$ (m) is height at which the wind velocity is referred to, $h$ is the source height (m), $\beta$ is a parameter computed starting from the terrain type and the stability class specified in the input meteo file. If at least, one parameter between the terrain type or the stability class, then the default value of $\beta$ is 0.55, otherwise is computed according to the following table:

|terrain type/stability class|A|B|C|D|E|F|
|:---|---|---|---|---|---|---|
|rural| 0.07 | 0.07 | 0.1 | 0.15 | 0.35 | 0.55 |
|urban| 0.15 | 0.15 | 0.2 | 0.25 | 0.3 | 0.3 |

- Reference: Bellasio, R.; Bianconi, R. A Heuristic Method for Modeling Odor Emissions from Open Roof Rectangular Tanks. Atmosphere 2022, 13, 367. https://doi.org/10.3390/atmos13030367

### Scheme 2 - wind erosion of dust cumulus with available wind data
The algorithm according to the EPA AP-42 methodology is the following:

- Computation of the wind at 10 meters (1000 cm):
  $$ w_s = w_s(z)\dfrac{\log(1000/z_0)}{\log(z/z_0)} $$
  where $z_0$ is the roughness length (cm) and $z$ is the height at which the wind data are referred to.

- Computation of fastest mile starting from wind speed:
$$f_m = 1.6 w_s + 0.43$$


- Cumulus surface is computed according to its shape:

  1) pyramid shaped source
  
  $$S = \dfrac{8}{5} l_{major} \sqrt{\left(\dfrac{ l_{major}}{5}\right)^2 + h^2}  + \dfrac{4}{3}l_{minor} \sqrt{\left( \dfrac{l_{minor}}{3}\right) ^2 + h^2}$$
  
  where $h$ is the cumulus height, $l_{major}, l_{minor}$ are the horizontal dimensions.

  2) conical shaped source
  
  $$S = \pi r \sqrt(r^2 + h^2)$$


- Computation of friction velocity:

  $$u_1^* = \max \left(0.4 \dfrac{f_m}{\log \frac{25}{z_0}} 0.2, u^*_{thr}\right)$$

  $$u_2^* = \max \left(0.4 \dfrac{f_m}{\log \frac{25}{z_0}} 0.6, u^*_{thr}\right)$$
  
  $$u_3^* = \max \left(0.4 \dfrac{f_m}{\log \frac{25}{z_0}} 0.9, u^*_{thr}\right)$$

  $$u_4^* = \max \left(0.4 \dfrac{f_m}{\log \frac{25}{z_0}} 1.1, u^*_{thr}\right)$$

  $$u_5^* = \max \left(0.4 \dfrac{f_m}{\log \frac{25}{z_0}}, u^*_{thr}\right)$$

where $z_0$ is the roughness lenght (cm), $u^*_{thr}$ is the threshold friction velocity, both set in the configuration file.

- Computation of erosion potential:

$$P_i = 58 (u_i^* - u^*_{thr})^2 + 25(u_i^* - u^*_{thr}), i = 1,2,3,4,5$$


- Computation of hourly emitted mass (mcg):

  a) if $\dfrac{h}{base} \le 0.2$:
  $$e_{r} = k S P_5  10^6$$

  b) if $\dfrac{h}{base} > 0.2$:

    1) if the shape of cumulus is symmetric (conical)

    $$e_{r} = k S \dfrac{40 P_1 + 48 P_2 + 12 P_3 + 0P_4}{100} 10^6$$

    2) if the shape of cumulus is asymmetric and the wind direction w.r.t. the orientation of the cumulus is between [0°,20°]:
    $$e_{r} = k S \dfrac{36 P_1 + 50 P_2 + 14 P_3 + 0P_4}{100} 10^6$$
    3) if the shape of cumulus is asymmetric and the wind direction w.r.t. the orientation of the cumulus is between (20°,40°]:
    $$e_{r} = k S \dfrac{31 P_1 + 51 P_2 + 15 P_3 + 3P_4}{100} 10^6$$
    4) if the shape of cumulus is asymmetric and the wind direction w.r.t. the orientation of the cumulus is between (40°,90°]:
    $$e_{r} = k S \dfrac{28 P_1 + 54 P_2 + 14 P_3 + 4P_4}{100} 10^6$$

with $k = 0.075$ for PM25, $k = 0.5$ for PM10, $k = 1$ for PTS.

- References: 
  - https://www.epa.gov/air-emissions-factors-and-quantification/ap-42-compilation-air-emissions-factors AP-42: Compilation of Air Emissions Factors, Sezione 13.2.5 Industrial Wind Erosion
  - Davis, F. K., and H. Newstein, 1968: The variation of gust factors and mean wind speed with height. J. Appl. Meteor., 7, 372–378

### Scheme 3 - wind erosion of dust cumulus with no available wind data
The algorithm proposed in the simplified methodology of ARPA Toscana is summarized with the following formula:

$$e_{r} = 10^9  e_{f} S m_{h}$$

- $e_{r}$ is the emission rate (in mcg) (or hourly emitted pollutant mass) that will go in the output emission file.
- $e_{f}$ is the pollutant emitted value:
  1) if $\dfrac{h}{2r} > 0.2$, that is the high cumulus case, for the PM25, $= 1.26 \cdot 10^{-6}$, for the PM10, $= 7.9 \cdot 10^{-6}$, for the PTS, $= 1.6 \cdot 10^{-5}$,
  2) se $\dfrac{h}{2r} \le 0.2$, that is the low cumulus case, for the PM25, $= 3.8 \cdot 10^{-5}$, for the PM10, $= 2.5 \cdot 10^{-4}$, for the PTS, $= 5.1 \cdot 10^{-4}$.
- $S = \pi r \sqrt(r^2 + h^2)$ is the conical shape cumulus surface, where $h$ is the height and $r$ is the radius.
- $m_{h}$ is the number of hourly movement of cumulus.

- Reference: Sezione 1.4 "EROSIONE DEL VENTO DAI CUMULI" del documento "LINEE GUIDA PER LA VALUTAZIONE DELLE EMISSIONI DI POLVERI PROVENIENTI DA ATTIVITÀ DI PRODUZIONE, MANIPOLAZIONE, TRASPORTO, CARICO O STOCCAGGIO DI MATERIALI POLVERULENTI", di ARPA TOSCANA

## Generate PDF manual starting from this readme
To generate the pdf manual, one can simply type this command on the terminal:
```{sh}
$ pandoc --to=pdf README.md -V geometry:margin=25mm -o README.pdf
```