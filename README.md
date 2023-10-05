<!-- 
 SPDX-FileCopyrightText: 2023 Simularia s.r.l. <info@simualaria.it>

 SPDX-License-Identifier: AGPL-3.0-or-later
-->

# MEDEA - Meteorological Dependent Emission Algorithms

[![DOI](https://zenodo.org/badge/699299175.svg)](https://zenodo.org/badge/latestdoi/699299175)

## Introduction

Use `medea` to compute **meteorological dependent emission** input files for many atmospheric pollution dispersion models. 
Emissions are computed according to different schemes suitable for **odour** and **particulate matter** modelling.
See [below](#algorithms-and-bibliographical-references) for a description of the relevant algorithms and for bibliographical references.

The tool currently works with the following atmospheric dispersion models: CALPUFF, ARIA-IMPACT, SPRAY, AERMOD.

To generate a *PDF* document from this file, type this command in the terminal:

```{sh}
$ pandoc --to=pdf README.md -V geometry:margin=25mm -o README.pdf
```


## How to use medea

In order to run `medea`, some python packages are required. These can be installed inside a virtual environment as in the following:

```{sh}
$ virtualenv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

The included help, shows how to use the tool:
```{sh}
(venv) $ ./medea.py -h
usage: medea.py [-h] [-d] config

MEDEA: compute wind-dependent emissions for dispersion models.

positional arguments:
  config       Path to input configuration toml file.

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  Activate debug mode
```

## Configuration file

The configuration file is in [*toml*](https://toml.io/en/) format. An example `config.toml` is included in the repository.
The keys of configuration file are described in the following:

- `input`: string containing the path to the input emission file (`="./test/pemtim"`);
- `output`: string containing the path to the output emission file (`="./test/pemtimout"`);
- `windInputFile`: string containing the path to the input meteo file (`="./test/met.csv"` or `="postbin.dat"`);
- `mettype`: string containing the type of the input meteo file:
  - = "postbin" : it tries to read a *postbin* file.
  - = "csv" : it tries to read a *csv* file.
  - by default (by omitting the field or filling it with an invalid value) it tries to read a *csv* file.
- `windOutputFile`: string containing the path to the output file where meteo and emission information for each source and species are saved (`="./test/metout.csv"`);
- `mode`: (integer number or string) medea mode for the model choice:
  - 0 or "spray" ⟶ spray;
  - 1 or "calpuff" ⟶ calpuff;
  - 2 or "impact" ⟶ impact;
  - 3 or "aermod" ⟶ aermod.
- `pemspe`: string containing the path to the pemspe file: it is needed only in spray mode (mode = 0)
- `sources`: it is a *toml* inline table, that is an array delimited by `[{...}, {...}, {...}]`, and each element is a "dictionary", in this form `{key1 = val1, key2 = val2, etc...}`, that describes a source. The key `scheme` defines the algorithm to apply to a source. The keys of a source's dictionary can be different as shown in the following example:

```
sources = [
    ### scheme 1 - odour source 
    { id = 1, scheme = 1, species = ["OU"], height = 5, 
      terrain = "rural", vref = 0.6},

    ### scheme 2 - wind erosion of dust cumulus with available data
    # asymmetric shape (2 sides and an angle)
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
Details on the **mandatory** keys that are **common** to all the schemes:

- `id`: identifier string or number in the input emission file (it can also be a list, e.g. [1, 'source1', 'source 2']);
- `scheme`: = {1,2,3} integer number that identifies the [scheme](#algorithms-and-bibliographical-references):
  - 1 = scheme for odour sources,
  - 2 = scheme for dust cumulus with available wind data,
  - 3 = scheme for dust cumulus with no available wind data;
- `species`: array of strings that identify the involved species;
- `height`: source height in meters.

Description of **specific** keys for each scheme:

- [scheme 1](#scheme-1---odour):
  - `terrain`: {"rural", "urban"} terrain type (**optional**)
  - `vref`: reference velocity (m/s) of the emission factor used to estimate the emission in the input file (**optional**, default = 0.3)

- [scheme 2](#scheme-2---wind-erosion-of-dust-cumulus-with-available-wind-data):
  - `tfv`: threshold friction velocity (m/s) (**mandatory**);
  - `roughness`: rugosity or roughness length (cm) (**optional**, default = 0.5);
  - source geometry (**mandatory**):
    - asymmetric (trapezoidal prism): `major`, `minor`, `angle`, sides of the base rectangle (m) and angle between the major side and the x-axis (anticlockwise, range -90°,+90°);
    - conic: `radius`, cone radius (m).

- [scheme 3](#scheme-3---wind-erosion-of-dust-cumulus-with-no-wind-data-available):
  - `radius`: equivalent cumulus radius (m) (**mandatory**);
  - `movh`: hourly movement of cumulus number (**mandatory**).

**Note**: geometrical information in the `config.toml` will not substitute that present in the emission file and no compatibility control is performed between the two files.


## Working hypothesis

Working hypotheses for`medea` are hereafter summarised:

- The meteorological input file is always required. It must contain at least all the deadlines included in the emission file;
- In the SPRAY model case, pemtim and pemspe input files must be provided in the format specified in `./test/pemtim` and `./test/pemspe`;
- In the CALPUFF model case, calpuff input file must be provided in the format specified in `./test/calpuffpolv`;
- In the IMPACT model case, impact input file must be provided in the format specified in `./test/impact_input.csv`;
- In the AERMOD model case, aermod input file must be provided in the format specified in `./test/aeremi.dat`;
- Only hourly emissions are allowed.


## Meteorological input file

The meteorological file is specified in the configuration file with the `windInputFile` key.
Currently, two formats are recognised:

1. A *csv* file with deadlines formatted as in the following:
    ```
    date,ws,wd,stabclass,z
    2019-01-01T00:00:00Z,4.32,111,B,10
    ```
2. A text file in the *postbin* format. In this case, the field `mettype` has to be filled up with the string `postbin` in the toml configuration file.

The `z` (wind field sensor height) and `stabclass` (stability class, specified with letters A, B, C, D, E, F+G or numbers 1, 2, 3, 4, 5, 6) parameters are employed only with scheme number 1, while `ws` (wind speed) and `wd` (wind direction) are not needed by the scheme number 3.

Note: the `date` parameter is always necessary. Further mandatory parameters are specified in the scheme description.


## Meteorological output file

Output meteorological file, specified in the toml configuration file with the key `windOutputFile`, will always be in the *csv* format and it will contain all input information and all the computed emission factor or emission values (according to the selected scheme), for all specified sources and species defined in the same configuration file.

In the case of [scheme 1](#scheme-1---odour), the meteorological output file includes the hourly correction factors for each source.


## Test files

In the `./test/` folder some input emission files are provided as examples for all four models and for the meteorology:

- `pemspe` and `pemtim` for SPRAY;
- `calpuffpolv` for CALPUFF;
- `impact_input.csv` for IMPACT;
- `aeremi.dat` for AERMOD;
- `windinput.csv` and `postbin.dat` for meteorology.


## Algorithms and bibliographical references


### Scheme 1 - Odour

Odour emission correction factor:

$$f = \left( \frac{w_s \left(\frac{h}{z}\right)^{\beta}}{v_{\text{ref}}}\right)^{\gamma}$$

where $w_s$ is the wind speed provided by the meteorological model or the anemometer (as written in the meteorological input file), $z$ (m) is the reference height for the wind velocity, $h$ is the source height (m), $\gamma = 0.5$  as reported in some guidelines and $\beta$ is a parameter dependent on the terrain type and the stability class specified in the input meteorological file. If either the terrain type or the stability class is missing, then the default value of $\beta$ is set to 0.55, otherwise it is chosen according to the following table:

| Terrain type / Stability class | A    | B    | C   | D    | E    | F    |
|:-------------------------------|------|------|-----|------|------|------|
| rural                          | 0.07 | 0.07 | 0.1 | 0.15 | 0.35 | 0.55 |
| urban                          | 0.15 | 0.15 | 0.2 | 0.25 | 0.3  | 0.3  |

Reference:
- Bellasio, R.; Bianconi, R. A Heuristic Method for Modeling Odor Emissions from Open Roof Rectangular Tanks. Atmosphere 2022, 13, 367. https://doi.org/10.3390/atmos13030367


### Scheme 2 - Wind erosion of dust cumulus with available wind data

The algorithm according to the EPA AP-42 methodology is here summarized:

- Computation of the wind at 10 meters:

$$w_s = w_s(z) \frac{\log(10/z_0)}{\log(z/z_0)}$$

where $z_0$ is the roughness length and $z$ is the height at which the wind data are referred to.

- Computation of fastest mile starting from wind speed:

$$f_m = 1.6 w_s + 0.43$$

- Cumulus exposed surface is computed according to its shape:

  1) Trapezoidal prism shaped source

    $$S = \frac{h (T + l_{minor})}{2} + l_{obl} l_{major} + T l_{major} + l_{obl} l_{major}+ \frac{h (T + l_{minor})}{2}$$
  
  where $T = l_{minor} / 2 - h$ is the top side of the trapezoid section, $l_{obl}$ is the oblique side of the trapezoid section, $h$ is the cumulus height, $l_{major}, l_{minor}$ are the horizontal dimensions.

  2) Conical shaped source:
  
  $$S = \pi r \sqrt{r^2 + h^2}$$

- Computation of the friction velocities applied to the cumulus sub-areas:

  $$u_1^* = \max \left(0.4 \frac{f_m}{\log \frac{25}{z_0}} 0.2, u^*_{thr}\right)$$

  $$u_2^* = \max \left(0.4 \frac{f_m}{\log \frac{25}{z_0}} 0.6, u^*_{thr}\right)$$
  
  $$u_3^* = \max \left(0.4 \frac{f_m}{\log \frac{25}{z_0}} 0.9, u^*_{thr}\right)$$

  $$u_4^* = \max \left(0.4 \frac{f_m}{\log \frac{25}{z_0}} 1.1, u^*_{thr}\right)$$

  $$u_5^* = \max \left(0.4 \frac{f_m}{\log \frac{25}{z_0}}, u^*_{thr}\right)$$

where $z_0$ is the roughness length, $u^*_{thr}$ is the threshold friction velocity, both set in the configuration file.

- Computation of the erosion potential for each sub-area:

    $$P_i = 58 \cdot \left( u^*_i - u^*_{thr} \right)^{2} + 25 \cdot \left( u_i^* - u^*_{thr} \right)$$

  with $i = 1, 2, 3, 4, 5$.

- Computation of hourly emitted mass (µg/h):

  a) If $\frac{h}{base} \le 0.2$ (low cumulus):

  $$e_{r} = k  S  P_5  10^6$$

  b) If $\frac{h}{base} > 0.2$ (high cumulus):

    1) if the shape of cumulus is symmetric (conical)

    $$e_{r} = k S \frac{40 P_1 + 48 P_2 + 12 P_3 + 0P_4}{100} 10^6$$

    2) if the shape of cumulus is asymmetric and the wind direction w.r.t. the orientation of the cumulus is between [0°,20°]:
    $$e_{r} = k S \frac{36 P_1 + 50 P_2 + 14 P_3 + 0P_4}{100} 10^6$$

    3) if the shape of cumulus is asymmetric and the wind direction w.r.t. the orientation of the cumulus is between (20°,40°]:
    $$e_{r} = k S \frac{31 P_1 + 51 P_2 + 15 P_3 + 3P_4}{100} 10^6$$

    4) if the shape of cumulus is asymmetric and the wind direction w.r.t. the orientation of the cumulus is between (40°,90°]:
    $$e_{r} = k S \frac{28 P_1 + 54 P_2 + 14 P_3 + 4P_4}{100} 10^6$$

with $k$ multiplier depending on particle size: $k = 0.075$ for PM25; $k = 0.5$ for PM10; $k = 1$ for PTS.

References: 

- EPA AP-42: Compilation of Air Emissions Factors, [Section 13.2.5 Industrial Wind Erosion](https://www.epa.gov/air-emissions-factors-and-quantification/ap-42-fifth-edition-volume-i-chapter-13-miscellaneous-0).

- Davis, F. K., and H. Newstein, 1968: The variation of gust factors with mean wind speed and with height. J. Appl. Meteor., 7, 372–378 [https://doi.org/10.1175/1520-0450(1968)007<0372:TVOGFW>2.0.CO;2](https://doi.org/10.1175/1520-0450\(1968\)007%3C0372:TVOGFW%3E2.0.CO;2)


### Scheme 3 - Wind erosion of dust cumulus with no wind data available

The algorithm proposed in the simplified methodology of ARPA Toscana is summarized with the following formula:

$$ e_r = e_f S \mathrm{mov}_h $$

where:

- $e_{r}$ is the emission rate (or hourly emitted pollutant mass, in kg/h). In the output emission file the emission will be written as µg/h;

- $e_{f}$ is the pollutant emitted value (in kg/m^2):

  1) if $\frac{h}{2r} > 0.2$, that is the high cumulus case: $e_f = 1.26 \cdot 10^{-6}$ for PM25; $e_f = 7.9 \cdot 10^{-6}$ for PM10; $e_f = 1.6 \cdot 10^{-5}$ for PTS;

  2) if $\frac{h}{2r} \le 0.2$, that is the low cumulus case: $e_f = 3.8 \cdot 10^{-5}$ for PM25; $e_f = 2.5 \cdot 10^{-4}$ for PM10; $e_f = 5.1 \cdot 10^{-4}$ for PTS.

- $S = \pi r \sqrt{r^2 + h^2}$ is the surface of the conical shaped cumulus, where $h$ is the height and $r$ is the radius;

- $\mathrm{mov}_{h}$ is the number of hourly movements occurring on the cumulus;

Reference:

- [ARPA Toscana, 2010: Linee guida per intervenire sulle attività che producono polveri](https://www.arpat.toscana.it/documentazione/catalogo-pubblicazioni-arpat/linee-guida-per-intervenire-sulle-attivita-che-producono-polveri), Section 1.4 *Erosione del vento dai cumuli*, in italian.


## Contacts, questions and contributions

`medea` is developed at [Simularia](https://www.simularia.it) by [Massimiliano Romana](https://github.com/mromanasimularia) (maintainer) and Giuseppe Carlino.

**Bug fixing** and **feature requests**: please [submit and issue](https://github.com/simularia/medea/issues/new).
Contributions should be addressed with [pull requests](https://github.com/Simularia/medea/pulls).
For any other request, find us on [email](mailto:info@simularia.it).


## Licence

`medea` is [free software](https://fsfe.org/freesoftware/freesoftware.en.html) whose copyright holder is [Simularia s.r.l.](https://www.simularia.it) and it is distributed under the GNU Affero General Public License v3.0 or later. See [the LICENCE file](./LICENSES/AGPL-3.0-or-later.txt) for more information.


