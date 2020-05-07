import numpy as np
from ._ReadCDF import _ReadCDF
from ..Tools.SpecCls import SpecCls
from ..Tools.CDFEpochToUT import CDFEpochToUT

def Read3D(Date):
	'''
	Reads the level 2 3dflux data product for a given date.
	
	Inputs
	======
	Date : int
		Integer date in the format yyyymmdd
	
	Returns
	=======
	data : dict
		Dictionary containing the data for each variable stored within 
		the CDF file.
	meta : dict
		Dictionary containing the metadata for each variable in the data
		dictionary.
		
	NOTE: In future, the data and meta dicts may be replaced by an object
	similar to that returned from ReadOmni.	
	'''
				
	#read the CDF file
	data,meta = _ReadCDF(Date,2,'3dflux')		
	
	# #output dict
	# out = {}
	
	# #get the time 
	# out['EpochL'] = data['Epoch_L']
	# out['DateL'],out['utL'] = CDFEpochToUT(out['EpochL'])
	# out['EpochH'] = data['Epoch_H']
	# out['DateH'],out['utH'] = CDFEpochToUT(out['EpochH'])
	
	# #the energy arrays
	# out['EnergyL'] = data['FEDO_L_Energy']
	# out['EnergyH'] = data['FEDO_H_Energy']
	
	# #get the midpoints
	# eL = np.mean(out['EnergyL'],axis=0)
	# eH = np.mean(out['EnergyH'],axis=0)
	
	# #replace bad data
	# L = data['FEDO_L']
	# bad = np.where(L < 0)
	# L[bad] = np.nan
	
	# H = data['FEDO_H']
	# bad = np.where(H < 0)
	# H[bad] = np.nan
	
	# #now to store the spectra
	# out['SpectraL'] = SpecCls(out['DateL'],out['utL'],out['EpochL'],eL,L,Meta=meta['FEDO_L'])
	# out['SpectraH'] = SpecCls(out['DateH'],out['utH'],out['EpochH'],eH,H,Meta=meta['FEDO_H'])
		
	data['Epoch'] = data['Epoch']
	data['Date'],data['ut'] = CDFEpochToUT(data['Epoch'])

	return data,meta