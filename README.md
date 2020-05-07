# Arase
A module for downloading and reading Arase spacecraft data.

## Current progress


| Instrument | Subcomponent | Level    | Product  | Download | Read     | Plot     |
|:----------:|:------------:|:--------:|:--------:|:--------:|:--------:|:--------:|
| HEP        |              | 2        | omniflux | &#10004; | &#10004; | &#10004; |
| LEPe       |              | 2        | omniflux | &#10004; | &#10004; | &#10004; |
| LEPe       |              | 2        | 3dflux   | &#10004; | &#10033; | &#10006; |
| LEPi       |              | 2        | omniflux | &#10004; | &#10004; | &#10004; |
| LEPi       |              | 2        | 3dflux   | &#10004; | &#10033; | &#10006; |
| MEPe       |              | 2        | omniflux | &#10004; | &#10004; | &#10004; |
| MEPe       |              | 2        | 3dflux   | &#10004; | &#10033; | &#10033; |
| MEPe       |              | 3        | 3dflux   | &#10013; | &#10033; | &#10006; |
| MEPi       |              | 2        | omniflux | &#10004; | &#10004; | &#10004; |
| MEPi       |              | 2        | 3dflux   | &#10004; | &#10033; | &#10004; |
| MEPi       |              | 3        | 3dflux   | &#10013; | &#10033; | &#10006; |
| MGF        |              | 2        | 8sec     | &#10004; | &#10004; | &#10006; |
| PWE        | efd          | 2        | spec     | &#10004; | &#10004; | &#10004; |
| PWE        | hfa          | 2        | high     | &#10004; | &#10004; | &#10004; |
| PWE        | hfa          | 2        | low      | &#10004; | &#10004; | &#10004; |
| PWE        | hfa          | 3        |          | &#10013; | &#10004; | &#10006; |
| PWE        | ofa          | 2        | complex  | &#10013; | &#10006; | &#10006; |
| PWE        | ofa          | 2        | matrix   | &#10013; | &#10006; | &#10006; |
| PWE        | ofa          | 2        | spec     | &#10004; | &#10006; | &#10006; |
| XEP        |              | 2        | omniflux | &#10004; | &#10004; | &#10004; |

* &#10004; - Works
* &#10006; - Not working yet. In the case of 3D data, a `SpecCls3D` object needs to be written. For MGF and level 3 hfa data, it's a simple case of plotting a line.
* &#10013; - Probably works, but have no access to the data to be able to test it.
* &#10033; - Currently 3D spectra can only be read into dictionaries as a `SpecCls3D` object is needed.
