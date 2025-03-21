<!-- 
 SPDX-FileCopyrightText: 2023 Simularia s.r.l. <info@simualaria.it>

 SPDX-License-Identifier: AGPL-3.0-or-later
-->

# MEDEA - Meteorology Dependent Emission Algorithms

[![DOI](https://zenodo.org/badge/699299175.svg)](https://zenodo.org/badge/latestdoi/699299175)

## Table of contents

- [Introduction](#introduction)
- [Install `MEDEA`](#install-medea)
- [How to use `MEDEA`](#how-to-use-medea)
- [Configuration file](#configuration-file)
- [Working hypotheses](#working-hypotheses)
- [Meteorological input file](#meteorological-input-file)
- [Meteorological output file](#meteorological-output-file)
- [Test files](#test-files)
- [Algorithms and bibliographical references](#algorithms-and-bibliographical-references)
  - [Scheme 1 – Odour](#scheme-1-odour)
  - [Scheme 2 – Dust emission by wind erosion of piles](#scheme-2-dust-emission-by-wind-erosion-of-piles)
  - [Scheme 3 – Simplified dust emission by wind erosion of piles](#scheme-3-simplified-dust-emission-by-wind-erosion-of-piles)
- [Contacts, questions and contributions](#contacts-questions-and-contributions)
- [License](#licence)

## Introduction

`MEDEA` is a command line tool to compute **meteorology dependent emission** files for many atmospheric pollution dispersion models. 
Emissions are computed according to different schemes suitable for **odour** and **particulate matter** modelling.

Three emission schemes are currently available:
- odour emission;
- dust emission by wind erosion of piles;
- simplified dust emission by wind erosion of piles.
See [below](#algorithms-and-bibliographical-references) for a description of the relevant algorithms and for bibliographical references.

The atmospheric dispersion models currently supported by `MEDEA` are:
- CALPUFF
- AERMOD
- ARIA-Impact
- SPRAY.


## Install `MEDEA`

`MEDEA` is currently available only as a source distribution from GitHub.
The preferred way to install it, is by `pipx`.
It will install `medea` and its dependencies in an isolated environment and it will make the tool available in your $PATH.

- Download the source files from the GitHub [repository](https://github.com/simularia/medea).
- Install the command line tool with [pipx](https://pipx.pypa.io/stable/):
```sh
$ cd /path/to/medea/
$ pipx install .

```
For development, use standard [editable installs](https://setuptools.pypa.io/en/latest/userguide/development_mode.html):
```sh
$ cd /path/to/medea
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install --editable .
```

## How to use `MEDEA`

`medea` is a command line tool with many operational modes. Every aspect of its functionality is specified in the [configuration file](#configuration-file).
The included help, shows how to use the tool:

```sh
$ medea -h
usage: medea [-h] [-d] config

MEDEA: compute meteorology dependent emissions for dispersion models.

positional arguments:
  config       Path to input configuration toml file.

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  Activate debug mode
```


## Configuration file

An example of configuration file `config.toml` is included in the repository in the `./tests/` subfolder. The file is in [*toml*](https://toml.io/en/) format and the required keys are described hereafter:

- **mode**: string (or integer) to select the dispersion model. Allowed values are:
  - "spray" (or 0);
  - "calpuff" (or 1);
  - "impact" (or 2);
  - "aermod" (or 3).

  Example:
  ```toml
  mode = "calpuff"
  ```

- **input**: path to _input emission_ file. Example:
  ```toml
  input = "./path/to/emission_input.csv"
  ```

- **output**: path to _output emission_ file. Example:
  ```toml
  output ="./path/to/emission_output"
  ```

- **windInputFile**: path to _input meteo_ file. Example:
  ```toml
  windInputFile ="./path/to/meteo.csv"
  ```

- **mettype**: (string) _type_ to input meteo file (default: *csv* file):
  - "csv" (*csv* file type);
  - "postbin" (*postbin* file type).

  Example:
  ```toml
  mettype = "csv"
  ```
  
- **windOutputFile**: path to _output meteorological_ file where meteo and emission information for each source and species are saved. Example:
  ```toml
  windOutputFile = "./path/to/meteo_emissions.csv"
  ```

- **pemspe**: path to the *pemspe* file (needed only in "spray" mode). Example:
  ```toml
  pemspe = "./path/to/pemspe"
  ```

- **sources**: a *toml* inline table (i.e. an array delimited by `[{...}, {...}, {...}]`). Each element is a dictionary, in the form of `{key1 = val1, key2 = val2, etc...}`, that describes a source. The `scheme` key defines the algorithm to apply to the given source. The keys of a source's dictionary can be different as shown in the following example:
  ```sh
  sources = [
      ### scheme 1 - odour source 
      { id = 1, scheme = 1, species = ["OU"], height = 5, 
        terrain = "rural", vref = 0.6},

      ### scheme 2 - dust emitted by wind erosion of piles with available data
      # asymmetric shape (2 sides and an angle)
      { id = 2, scheme = 2, species = ["PTS", "PM25", "PM10"], 
        height = 4, major = 5, minor = 3, angle = 15, 
        roughness = 0.5, tfv = 0.05},  
      # conical shape (radius)
      { id = 3, scheme = 2, species = ["PTS", "PM25", "PM10"], 
        height = 4, radius = 3, roughness = 0.005, 
        tfv = 0.05},   

      ### scheme 3 - simplified dust emission by wind erosion of piles
      { id = 4, scheme = 3, species = ["PTS", "PM25", "PM10"], 
        height = 4, radius = 3.6, movh = 4} 
  ]
  ```

Details on the **mandatory** keys for sources, that are **common** to all the schemes:

- **id**: identifier string or number in the input emission file (it can also be a list, e.g. `[1, 'source1', 'source 2']`);

- **scheme**: integer number that identifies the emission [scheme](#algorithms-and-bibliographical-references):
  - 1 = odour sources,
  - 2 = dust emission by wind erosion of piles, with available wind data,
  - 3 = simplified dust emissions by wind erosion of piles, with no available wind data;

- **species**: array of strings that identify the involved species;

- **height**: source height in meters.

Description of scheme **specific** keys:

- [scheme 1](#scheme-1-odour) (odour):
  - **terrain**: optional string with terrain type (one of `{"rural", "urban"}`);
  - **vref**: reference velocity (m/s) of the emission factor used to estimate the input emission (optional, default = 0.3).

- [scheme 2](#scheme-2-dust-emission-by-wind-erosion-of-piles) (dust):
  - **tfv**: threshold friction velocity (m/s), (mandatory);
  - **roughness**: rugosity or roughness length (cm) (optional, default = 0.5);
  - Mandatory source geometry:
    - Asymmetric pile shaped as a trapezoidal prism:
      1. **major** (m): length of the major side of the base rectangle on which the pile rests on the ground.  
      2. **minor** (m): length of the minor side of the base rectangle on which the pile rests on the ground.  
      3. **angle** (°): angle between the major side and the x-axis on the ground, measured anticlockwise with a range of -90° to +90°.  
    - Conic pile:
      1. **radius** (m): cone radius.

- [scheme 3](#scheme-3-simplified-dust-emission-by-wind-erosion-of-piles) (simplified dust):
  - **radius**: equivalent conic pile radius (m) (mandatory);
  - **movh**: number of hourly disturbances of the erodible surface (mandatory).

**Nota Bene**: geometrical information specified in the configuration file does not overwrite the one provided in the emission file, and no validation is performed to ensure compatibility between the two files.


## Working hypotheses

Working hypotheses for`MEDEA` are hereafter summarised:

1. The *meteorological input* file is always required. It must contain at least all the deadlines included in the emission file;
2. In the `spray` model case, pemtim and pemspe input files must be provided in the format specified in `./tests/pemtim` and `./tests/pemspe`;
3. In the `calpuff` model case, calpuff input file must be provided in the format specified in `./tests/calpuffpolv`;
4. In the `impact` model case, impact input file must be provided in the format specified in `./tests/impact_input.csv`;
5. In the `aermod` model case, aermod input file must be provided in the format specified in `./tests/aeremi.dat`;
6. Only hourly emissions are allowed.


## Meteorological input file

The meteorological file is specified in the configuration file with the `windInputFile` key.
Currently, two formats are recognised:

- *csv*, with deadlines formatted as in the following:
  ```
  date,ws,wd,stabclass,z
  2019-01-01T00:00:00Z,4.32,111,B,10
  ```

- *postbin*, test file format. In this case, the field `mettype = "postbin"` must be added to the configuration file.

The parameters `z` (wind field sensor height) and `stabclass` (stability class, specified with letters [A, B, C, D, E, F, G] or numbers [1, 2, 3, 4, 5, 6]) are only used by [scheme 1](#scheme-1-odour) (odour emission), while `ws` (wind speed) and `wd` (wind direction) are not needed by the [scheme 3](#scheme-3-simplified-dust-emission-by-wind-erosion-of-piles) (simplified dust emission by wind erosion).

Note: the `date` parameter is always necessary. Further mandatory parameters are specified in the following schemes description.


## Meteorological output file

Output meteorological file, specified in the toml configuration file with the key `windOutputFile`, will always be in the *csv* format and it will contain all input information plus all the computed emission factor or emission values (according to the selected scheme), for all specified sources and species defined in the same configuration file.

In the case of [scheme 1](#scheme-1-odour), the meteorological output file includes the hourly correction factors for each source.


## Test files

In the `./tests/` folder some input emission files are provided as examples for all four models and for the meteorology:

- `pemspe` and `pemtim` for `SPRAY`;
- `calpuffpolv` for `CALPUFF`;
- `impact_input.csv` for `IMPACT`;
- `aeremi.dat` for `AERMOD`;
- `windinput.csv` and `postbin.dat` for meteorology.


## Algorithms and bibliographical references


### Scheme 1: Odour

Odour emission correction factor:

$$f = \left( \frac{w_s \left(\frac{h}{z}\right)^{\beta}}{v_{\text{ref}}}\right)^{\gamma}$$

where $w_s$ is the wind speed provided by the meteorological model or the anemometer (as written in the meteorological input file), $z$ (m) is the reference height for the wind velocity, $h$ is the source height (m), $\gamma = 0.5$  as reported in some guidelines and $\beta$ is a parameter dependent on the terrain type and the stability class specified in the input meteorological file. If either the terrain type or the stability class is missing, then the default value of $\beta$ is set to 0.55, otherwise it is chosen according to the following table:

| Terrain type / Stability class | A    | B    | C   | D    | E    | F    |
|:-------------------------------|------|------|-----|------|------|------|
| rural                          | 0.07 | 0.07 | 0.1 | 0.15 | 0.35 | 0.55 |
| urban                          | 0.15 | 0.15 | 0.2 | 0.25 | 0.3  | 0.3  |

Reference:
- Bellasio, R.; Bianconi, R. A Heuristic Method for Modeling Odor Emissions from Open Roof Rectangular Tanks. Atmosphere 2022, 13, 367. https://doi.org/10.3390/atmos13030367


### Scheme 2: Dust emission by wind erosion of piles 

Dust emission by wind erosion of storage piles is estimated according to the EPA AP-42 Sec. 13.2.5 ("Industrial wind erosion") methodology, hereafter summarized:

- Computation of the wind at 10 meters:

$$w_s = w_s(z) \frac{\log(10/z_0)}{\log(z/z_0)}$$

where $z_0$ is the roughness length and $z$ is the height at which the wind data are referred to.

- Computation of fastest mile starting from wind speed:

$$f_m = 1.6 w_s + 0.43$$

- Pile exposed surface is computed according to its shape:

  1) Trapezoidal prism shaped source

    $$S = \frac{h (T + l_{minor})}{2} + l_{obl} l_{major} + T l_{major} + l_{obl} l_{major}+ \frac{h (T + l_{minor})}{2}$$
  
  where $T = l_{minor} / 2 - h$ is the top side of the trapezoid section, $l_{obl}$ is the oblique side of the trapezoid section, $h$ is the pile height, $l_{major}, l_{minor}$ are the horizontal dimensions.

  2) Conical shaped source:
  
  $$S = \pi r \sqrt{r^2 + h^2}$$

- Computation of the friction velocities applied to the pile sub-areas:

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

  a) If $\frac{h}{base} \le 0.2$ (low pile):

  $$e_{r} = k  S  P_5  10^6$$

  b) If $\frac{h}{base} > 0.2$ (high pile):

    1) if the shape of pile is symmetric (conical)

    $$e_{r} = k S \frac{40 P_1 + 48 P_2 + 12 P_3 + 0P_4}{100} 10^6$$

    2) if the shape of pile is asymmetric and the wind direction w.r.t. the orientation of the pile is between [0°,20°]:
    $$e_{r} = k S \frac{36 P_1 + 50 P_2 + 14 P_3 + 0P_4}{100} 10^6$$

    3) if the shape of pile is asymmetric and the wind direction w.r.t. the orientation of the pile is between (20°,40°]:
    $$e_{r} = k S \frac{31 P_1 + 51 P_2 + 15 P_3 + 3P_4}{100} 10^6$$

    4) if the shape of pile is asymmetric and the wind direction w.r.t. the orientation of the pile is between (40°,90°]:
    $$e_{r} = k S \frac{28 P_1 + 54 P_2 + 14 P_3 + 4P_4}{100} 10^6$$

with $k$ multiplier depending on particle size: $k = 0.075$ for PM25; $k = 0.5$ for PM10; $k = 1$ for PTS.

References: 

- EPA AP-42: Compilation of Air Emissions Factors, [Section 13.2.5 Industrial Wind Erosion](https://www.epa.gov/air-emissions-factors-and-quantification/ap-42-fifth-edition-volume-i-chapter-13-miscellaneous-0).

- Davis, F. K., and H. Newstein, 1968: The variation of gust factors with mean wind speed and with height. J. Appl. Meteor., 7, 372–378 [https://doi.org/10.1175/1520-0450(1968)007<0372:TVOGFW>2.0.CO;2](https://doi.org/10.1175/1520-0450\(1968\)007%3C0372:TVOGFW%3E2.0.CO;2)


### Scheme 3: Simplified dust emission by wind erosion of piles

Simplified dust emission by wind erosion of storage piles, without wind speed time series, is estimated according to the methodology proposed by of ARPA Toscana and summarised by the following expression:

$$ e_r = e_f \cdot S \cdot \mathrm{mov}_h $$

where:

- $e_{r}$ is the emission rate (or hourly emitted pollutant mass, in kg/h). In the output emission file the emission will be written as µg/h;

- $e_{f}$ is the pollutant emitted value (in kg/m^2):

  1) if $\frac{h}{2r} > 0.2$, that is the high pile case: $e_f = 1.26 \cdot 10^{-6}$ for PM25; $e_f = 7.9 \cdot 10^{-6}$ for PM10; $e_f = 1.6 \cdot 10^{-5}$ for PTS;

  2) if $\frac{h}{2r} \le 0.2$, that is the low pile case: $e_f = 3.8 \cdot 10^{-5}$ for PM25; $e_f = 2.5 \cdot 10^{-4}$ for PM10; $e_f = 5.1 \cdot 10^{-4}$ for PTS.

- $S = \pi r \sqrt{r^2 + h^2}$ is the surface of the conical shaped pile, where $h$ is the height and $r$ is the radius;

- $\mathrm{mov}_{h}$ is the number of hourly movements occurring on the erodible surface;

The simplified methodology is based on EPA AP-42 Sec. 13.2.5 with a standardized wind speed distribution.

Reference:

- [ARPA Toscana, 2010: Linee guida per intervenire sulle attività che producono polveri](https://www.arpat.toscana.it/documentazione/catalogo-pubblicazioni-arpat/linee-guida-per-intervenire-sulle-attivita-che-producono-polveri), Section 1.4 *Erosione del vento dai cumuli*, in italian.


## Contacts, questions and contributions

`medea` was initially developed at [Simularia](https://www.simularia.it) by [Massimiliano Romana](https://github.com/mromanasimularia).
The current maintainer is Giuseppe Carlino.

**Bug fixing** and **feature requests**: please [submit and issue](https://github.com/simularia/medea/issues/new).
Contributions should be addressed with [pull requests](https://github.com/Simularia/medea/pulls).
For any other request, find us on [email](mailto:info@simularia.it).


## Licence

`medea` is [free software](https://fsfe.org/freesoftware/freesoftware.en.html) whose copyright holder is [Simularia s.r.l.](https://www.simularia.it) and it is distributed under the GNU Affero General Public License v3.0 or later. See [the LICENSE file](./LICENSES/AGPL-3.0-or-later.txt) for more information.


