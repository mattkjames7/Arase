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
	fields = {	'FPDO' : 'Hp',
				'FHEDO' : 'Hep',
				'FODO' : 'Op'}
	
	for k in list(fields.keys()):
		s = data[k]
		bad = np.where(s < 0)
		s[bad] = np.nan
		
		kout = fields[k]
		
		out['Energy'+kout] = data[k+'_Energy']
		
		
		#now to store the spectra
		out[kout+'Flux'] = SpecCls(out['Date'],out['ut'],out['Epoch'],out['Energy'+kout],s,Meta=meta[k])
	


	

	

	return out	
