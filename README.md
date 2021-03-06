# Arase
A module for downloading and reading Arase spacecraft data.

## Installation

Install from PyPI:

```bash
pip3 install Arase --user
```

or

```bash
python3 -m pip install Arase --user
```

Set the `ARASE_PATH` variable by placing the following at the end of `~/.bashrc`:

```bash
export ARASE_PATH=/path/to/arase/data
```

## Downloading Data

Most instrument data can be downloaded using the `DownloadData` function
contained in the instruments submodule, e.g.:

```python
Arase.XXX.DownloadData(L,prod,Date=Date,Overwrite=Overwrite)
```

where `XXX` can be replaced with the instrument names: `HEP`, `LEPe`, `LEPi`, `MEPe`, `MEPi`, 
`MGF` or `XEP`. `L` is an integer and `prod` is a string which correspond to the
level and data product provided by the instrument, repsectively (see the table in "Current
Progress"). `Date` determines the range of dates to download data for.  The `Date` keyword can be a single date, a list of specific dates to download, or a 2 element list defining the start and end dates (by default `Date = [20170101,20200101]`). `Overwrite` will force the routine to overwrite existing data.

This method will work for PWE data:

```python
Arase.PWE.DownloadData(subcomp,L,prod,Date=Date,Overwrite=Overwrite)
```

where `subcomp` is the sub-component of the instrument (see table below).

To download the position data:

```python
Arase.Pos.DownloadData(prod,Date=Date,Overwrite=Overwrite)
```

where prod is either `'l3'` or `'def'`. The `'def'` option is needed for
position-related functions elsewhere in the `Arase` module.

## Position and tracing

1. Download position data:

```python
Arase.Pos.DownloadData('def')
```

2.  Convert to a binary format (this allows for quicker reading):

```python
Arase.Pos.ConvertPos()
```

3. Save field traces

```python
Arase.Pos.SaveFieldTraces(Model=Model,StartDate=StartDate,EndDate=EndDate)
```

where Model is either `'T89'`, `'T96'`, `'T01'` or `'TS05'` (`'T96'` by default).
`StartDate` and `EndDate` are the start and end dates to perform traces for,
both are integers of the format yyymmdd.

4. To read the position data :

```python
pos = Arase.Pos.GetPos()
```

To read the traces:

```python
tr = Arase.Pos.ReadFieldTraces(Date)
```

## Reading Data

### MGF data

```python
data = Arase.MGF.ReadMGF(Date)
```

This returns a `numpy.recarray` object which contains the time-series data. The `Date` argument may be a single date, a list of dates or a 2 element `list` of dates defining the start and end date to load. 

### Particle Omni-directional Spectra 

```python
data = Arase.LEPe.ReadOmni(Date)
```

For other instruments, replace `LEPe` with one of the following: `LEPi`,
`MEPe`, `MEPi`, `HEP` or `XEP`. `data` is a dictionary which will contain
dates, times, energy bins and instances of the `Arase.Tools.PSpecCls` object. The `PSpecCls`
object contains all of the spectral information stored within it, and is 
usually identified by the dictionary key containing `'Flux'`. The `PSpecCls`
object has an in-built method for plotting the spectrograms, e.g.:

```python
data['eFlux'].Plot()
```

will plot the electron flux spectrogram from the LEPe data loaded above. 
To list the keys of a dictionary, use `list(data.keys())`

### Combined Particle Spectra

Two functions are available which will load the data for multiple instruments
at the same time.

For electrons:

```python
E = Arase.Electrons.ReadOmni(Date)
```

and for ions:

```python
H,He,O = Arase.Ions.ReadOmni(Date)
```

where `E`, `H`, `He` and `O` are all instances of `SpecCls`. 

![alt text](Electrons.png)

### Single Spectra

The `SpecCls` object has the ability to return single spectra, e.g.:

```python
import Arase
import matplotlib.pyplot as plt

#read in the electrons - this should work with and SpecCls object
spec = Arase.Electrons.ReadOmni(Date)

#for the energy bins and particle flux data
e,dJdE,_ = spec.GetSpectrum(Date,ut)

#for velocity and phase space density
v,f,_ = spec.GetSpectrum(Date,ut,xparam='V',yparam='PSD')

#or to plot
plt.figure(figsize=(8,4))
ax0 = spec.PlotSpectrum(Date,ut,xparam='E',yparam='Flux',Split=True,fig=plt,maps=[2,1,0,0])
ax1 = spec.PlotSpectrum(Date,ut,xparam='V',yparam='PSD',Split=True,fig=plt,maps=[2,1,1,0])
plt.tight_layout()

#for more information, read the docstrings:
spec.GetSpectrum?
spec.PlotSpectrum?
```

![](Spectrum.png)





###	3D Particle Spectra

These data are not currently placed into an object like `PSpecCls`, for instruments which provide 3D spectra, there is a function `Read3D` which will simply read the CDF file for a given date, and list all of the data and corresponding metadata into
two dictionaries, e.g.:

```python
data,meta = Arase.LEPe.Read3D(Date)
```



### Pitch Angle Distributions

For particle instruments with 3D flux data, there is a method to convert these to pitch angle distributions (PADs). The PADs are calculated using the MGF data and the elevation/azimuth angles of the instruments in GSE coordinates where provided in the level 2 `3dflux` data products. It was possible to compare this mehod to the angles provided by the level 3 `3dflux` product from the MEPe instrument and almost all pitch angles were within about 1-2 degrees. **WARNING: these data should be used with caution - they may not be correct.** 

To store the PADs:

```python
import Arase
Arase.LEPe.SavePADs(Date,na=18,Overwrite=False,DownloadMissingData=True,DeleteNewData=True,Verbose=True)
```

The above code will bin up the 3D LEPe fluxes from a single date into `na` pitch angle bins (always in the range 0 to 180 degrees). The `Overwrite` keyword will force the overwriting of previously created PAD files. `DownloadMissingData` will download any missing `3dflux` data and MGF data. `DeleteNewData` will delete the newly downloaded `3dflux` data after creating the PAD data because some of the `3dflux` files are > 500 MB.

To read PADs:

```python
pad = Arase.LEPe.ReadPAD(Date,SpecType,ReturnSpecObject=True)
```

This will read the PAD spectra from a single date for a given SpecType (e.g. `'eFlux'` or `'H+Flux'`, depending on the instrument). The returned object will either be a `dict` containing just the data if `ReturnSpecObject=False`, or a `Arase.Tools.PSpecPADCls` object if  `ReturnSpecObject=True`. The `PSpecPADCls` object allows the plotting of spectrograms, 1D spectra and 2D spectra.

For a spectrogram of a specific pitch angle bin:

```python
pad = Arase.MEPe.ReadPAD(20180101,'eFlux')
pad.PlotSpectrogram(Bin=5)
```

![PADSpectrogram.png](PADSpectrogram.png)



Or a 1D spectrum

```python
pad.PlotSpectrum1D(12.0,Bin=5,xparam='V',yparam='PSD')
```

![PAD1DSpectrum](PAD1DSpectrum.png)

Or a 2D spectrum:

```python
pad.PlotSpectrum2D(12.0,xparam='V',zparam='PSD')
```

![PAD2DSpectrum](PAD2DSpectrum.png)



## Current progress


| Instrument | Subcomponent | Level | Product  | Download |   Read   |   Plot   |
| :--------: | :----------: | :---: | :------: | :------: | :------: | :------: |
|    HEP     |              |   2   | omniflux | &#10004; | &#10004; | &#10004; |
|    LEPe    |              |   2   | omniflux | &#10004; | &#10004; | &#10004; |
|    LEPe    |              |   2   |  3dflux  | &#10004; | &#10033; | &#10006; |
|    LEPi    |              |   2   | omniflux | &#10004; | &#10004; | &#10004; |
|    LEPi    |              |   2   |  3dflux  | &#10004; | &#10033; | &#10006; |
|    MEPe    |              |   2   | omniflux | &#10004; | &#10004; | &#10004; |
|    MEPe    |              |   2   |  3dflux  | &#10004; | &#10033; | &#10033; |
|    MEPe    |              |   3   |  3dflux  | &#10004; | &#10033; | &#10006; |
|    MEPi    |              |   2   | omniflux | &#10004; | &#10004; | &#10004; |
|    MEPi    |              |   2   |  3dflux  | &#10004; | &#10033; | &#10004; |
|    MEPi    |              |   3   |  3dflux  | &#10004; | &#10033; | &#10006; |
|    MGF     |              |   2   |   8sec   | &#10004; | &#10004; | &#10006; |
|    PWE     |     efd      |   2   |   spec   | &#10004; | &#10004; | &#10004; |
|    PWE     |     hfa      |   2   |   high   | &#10004; | &#10004; | &#10004; |
|    PWE     |     hfa      |   2   |   low    | &#10004; | &#10004; | &#10004; |
|    PWE     |     hfa      |   3   |          | &#10004; | &#10004; | &#10006; |
|    PWE     |     ofa      |   2   | complex  | &#10013; | &#10006; | &#10006; |
|    PWE     |     ofa      |   2   |  matrix  | &#10013; | &#10006; | &#10006; |
|    PWE     |     ofa      |   2   |   spec   | &#10004; | &#10006; | &#10006; |
|    XEP     |              |   2   | omniflux | &#10004; | &#10004; | &#10004; |

* &#10004; - Works
* &#10006; - Not working yet. In the case of 3D data, a `SpecCls3D` object needs to be written. For MGF and level 3 hfa data, it's a simple case of plotting a line.
* &#10013; - Probably works, but have no access to the data to be able to test it.
* &#10033; - Currently 3D spectra can only be read into dictionaries as a `SpecCls3D` object is needed.

