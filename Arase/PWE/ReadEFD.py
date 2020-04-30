import numpy as np
from ._ReadCDF import _ReadCDF
from ..Tools.SpecCls import SpecCls
from ..Tools.CDFEpochToUT import CDFEpochToUT

def ReadEFD(Date):
	'''
	Reads the EFD part of PWE data.
	'''

	#List the fields to output
	fields = {	'spectra' : 		('Spectra','Frequency, $f$ (Hz)',r'EFD spectrum, $E_v$ ((mV/m)$^2$/Hz)'),
				'spectra_EvEv' : 	('SpectraEvEv','Frequency, $f$ (Hz)',r'EFD spectrum, $\Re(E_v)^2+\Im(E_v)^2$ ((mV/m)$^2$/Hz)'),
				'spectra_EuEu' : 	('SpectraEuEu','Frequency, $f$ (Hz)',r'EFD spectrum, $\Re(E_u)^2+\Im(E_u)^2$ ((mV/m)$^2$/Hz)'),
				'spectra_EuEv_re' : ('SpectraEuEvRe','Frequency, $f$ (Hz)',r'EFD spectrum, $\Re(E_u)\Re(E_v)+\Im(E_u)\Im(E_v)$ ((mV/m)$^2$/Hz)'),
				'spectra_EuEv_im' : ('SpectraEuEvIm','Frequency, $f$ (Hz)',r'EFD spectrum, $\Re(E_u)\Im(E_v)+\Im(E_u)\Re(E_v)$ ((mV/m)$^2$/Hz)'),}
				
	#read the CDF file
	data,meta = _ReadCDF(Date,'efd',2,'spec')		
	
	#output dict
	out = {}
	
	#get the time 
	out['Epoch'] = data['Epoch']
	out['Date'],out['ut'] = CDFEpochToUT(out['Epoch'])
	
	#the frequency arrays
	out['F'] = data['frequency']
	out['F100'] = data['frequency_100hz']
			
	#now to store the spectra
	for k in list(fields.keys()):
		spec = data[k]
		bad = np.where(spec < 0)
		spec[bad] = np.nan
		field,ylabel,zlabel = fields[k]
		f = data[meta[k]['DEPEND_1']]
		if meta[k]['DEPEND_1'] == 'frequency':
			bw = data['band_width']
		else:
			bw = np.ones(f.size,dtype='float32')
		out[field] = SpecCls(out['Date'],out['ut'],out['Epoch'],f,spec,Meta=meta[k],dt=1.0,bw=bw,ylabel=ylabel,zlabel=zlabel,ScaleType='positive')
		
	return out	
				
				
	
