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
	
	#the energy arrays
	out['Energy'] = data['FEDO_Energy']
	emid = np.mean(out['Energy'],axis=1)
	bw = out['Energy'][:,1,:] - out['Energy'][:,0,:]
	out['bw'] = bw
	out['emid'] = emid

	#replace bad data
	s = data['FEDO']
	bad = np.where(s < 0)
	s[bad] = np.nan
	
	#plot labels
	ylabel = 'Energy (eV)'
	zlabel = 'Omni-directional number flux (#/s-cm2-sr-eV)'
	
	
	#now to store the spectra
	out['eFlux'] = SpecCls(out['Date'],out['ut'],out['Epoch'],emid,s,Meta=meta['FEDO'],bw=bw,ylabel=ylabel,zlabel=zlabel,ylog=True,zlog=True)
		
	return out	
