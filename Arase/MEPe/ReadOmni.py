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
	out['Epoch'] = data['epoch']
	out['Date'],out['ut'] = CDFEpochToUT(out['Epoch'])
	
	#the energy arrays
	out['Energy'] = data['FEDO_Energy']
	

	#replace bad data
	s = data['FEDO']
	bad = np.where(s < 0)
	s[bad] = np.nan
	
	#plot labels
	ylabel = 'Energy (keV)'
	zlabel = 'Omni-directional Electron Flux (cm$^{-2}$ s$^{-1}$ sr$^{-1}$ keV$^{-1}$)'
	
	
	#now to store the spectra
	out['eFlux'] = SpecCls(out['Date'],out['ut'],out['Epoch'],out['Energy'],s,Meta=meta['FEDO'],ylabel=ylabel,zlabel=zlabel,ylog=True,zlog=True)
		
	return out	
