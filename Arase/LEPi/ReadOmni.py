import numpy as np
from ._ReadCDF import _ReadCDF
from ..Tools.SpecCls import SpecCls
from ..Tools.CDFEpochToUT import CDFEpochToUT

def ReadOmni(Date):
	
				
	#read the CDF file
	data,meta = _ReadCDF(Date,2,'omniflux')		
	
	#output dict
	out = {}
	
	#get the time 
	out['Epoch'] = data['Epoch']
	out['Date'],out['ut'] = CDFEpochToUT(out['Epoch'])



	#replace bad data
	fields = {	'FPDO' : 	('H+','Energy (keV)',r'Omni H$^+$ flux (1/keV-sr-s-cm$^2$)'),
				'FHEDO' : 	('He+','Energy (keV)',r'Omni He$^+$ flux (1/keV-sr-s-cm$^2$)'),
				'FODO' : 	('O+','Energy (keV)',r'Omni O$^+$ flux (1/keV-sr-s-cm$^2$)'),}
	
	for k in list(fields.keys()):
		s = data[k]
		bad = np.where(s < 0)
		s[bad] = np.nan
		
		#get the base field name
		kout,ylabel,zlabel = fields[k]
		
		#output spectra fields name
		kspec = kout + 'Flux'
		
		#energy field name
		ke = 'Energy' + kout
		ke_cdf = k + '_Energy'
		
		#get the energy bins
		out[ke] = data[ke_cdf]
		
		#now to store the spectra
		out[kspec] = SpecCls(out['Date'],out['ut'],out['Epoch'],out[ke],s,Meta=meta[k],ylabel=ylabel,zlabel=zlabel,ScaleType='positive',ylog=True,zlog=True)
		

	return out	
