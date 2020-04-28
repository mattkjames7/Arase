import numpy as np
from ._ReadCDF import _ReadCDF
from ..Tools.SpecCls import SpecCls
from ..Tools.CDFEpochToUT import CDFEpochToUT

def ReadEFD(Date):
	'''
	Reads the EFD part of PWE data.
	'''

	#List the fields to output
	fields = {	'spectra' : 'Spectra',
				'spectra_EvEv' : 'SpectraEvEv',
				'spectra_EuEu' : 'SpectraEvEv',
				'spectra_EuEv_re' : 'SpectraEvEvRe',
				'spectra_EuEv_im' : 'SpectraEvEvIm'}
				
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
		f = data[meta[k]['DEPEND_1']]
		if meta[k]['DEPEND_1'] == 'frequency':
			bw = data['band_width']
		else:
			bw = np.ones(f.size,dtype='float32')
		out[fields[k]] = SpecCls(out['Date'],out['ut'],out['Epoch'],f,spec,Meta=meta[k],dt=1.0,bw=bw)
		
	return out	
				
				
	
