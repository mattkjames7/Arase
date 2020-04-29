import numpy as np
from ._ReadCDF import _ReadCDF
from ..Tools.SpecCls import SpecCls
from ..Tools.CDFEpochToUT import CDFEpochToUT

def ReadOmni(Date):
	
	#List the fields to output
	fields = {	'FEDO_SSD' : 'SpectraSSD',
				'FEDO_GSO' : 'SpectraGSO'}
				
	#read the CDF file
	data,meta = _ReadCDF(Date,2,'omniflux')		
	
	#output dict
	out = {}
	
	#get the time 
	out['Epoch'] = data['Epoch']
	out['Date'],out['ut'] = CDFEpochToUT(out['Epoch'])
	
	#the energy arrays
	out['EnergySSD'] = data['FEDO_SSD_Energy']
	out['EnergyGSO'] = data['FEDO_GSO_Energy']
	
	#get the midpoints
	essd = np.mean(out['EnergySSD'],axis=0)
	egso = np.mean(out['EnergyGSO'],axis=0)
	
	#replace bad data
	ssd = data['FEDO_SSD']
	bad = np.where(ssd < 0)
	ssd[bad] = np.nan
	
	gso = data['FEDO_GSO']
	bad = np.where(gso < 0)
	gso[bad] = np.nan
	
	#now to store the spectra
	out['SpectraSSD'] = SpecCls(out['Date'],out['ut'],out['Epoch'],essd,ssd,Meta=meta['FEDO_SSD'])
	out['SpectraGSO'] = SpecCls(out['Date'],out['ut'],out['Epoch'],egso,gso,Meta=meta['FEDO_GSO'])
		
	return out	
