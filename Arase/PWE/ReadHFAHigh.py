import numpy as np
from ._ReadCDF import _ReadCDF
from ..Tools.SpecCls import SpecCls
from ..Tools.CDFEpochToUT import CDFEpochToUT

def ReadHFAHigh(Date):
	
	#List the fields to output
	fields = {	'spectra_eu' : 'SpectraEu',
				'spectra_ev' : 'SpectraEv',
				'spectra_bgamma' : 'SpectraBgamma',
				'spectra_esum' : 'SpectraEsum',
				'spectra_er' : 'SpectraEr',
				'spectra_el' : 'SpectraEl',
				'spectra_e_mix' : 'SpectraEmix',
				'spectra_e_ar' : 'SpectraEAR',
				'spectra_eu_ev' : 'SpectraEuEv',
				'spectra_eu_bg' : 'SpectraEuBgamma',
				'spectra_ev_bg' : 'SpectraEvBgamma'}
				
	#read the CDF file
	data,meta = _ReadCDF(Date,'hfa',2,'high')		
	
	#output dict
	out = {}
	
	#get the time 
	out['Epoch'] = data['Epoch']
	out['Date'],out['ut'] = CDFEpochToUT(out['Epoch'])
	
	#the frequency arrays
	out['F'] = data['freq_spec']
			
	#now to store the spectra
	for k in list(fields.keys()):
		spec = data[k]
		out[fields[k]] = SpecCls(out['Date'],out['ut'],out['Epoch'],out['F'],spec,Meta=meta[k])
		
	return out	
