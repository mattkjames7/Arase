import numpy as np
from ._ReadCDF import _ReadCDF
from ..Tools.SpecCls import SpecCls
from ..Tools.CDFEpochToUT import CDFEpochToUT
from ..Tools.ListDates import ListDates

def ReadOmni(Date):
	'''
	Reads the level 2 omniflux data product for a given date.
	
	Inputs
	======
	Date : int
		Integer date in the format yyyymmdd
	
	Returns
	=======
	data : dict
		Contains the following fields:
		'Epoch' : CDF epoch
		'Date' : Date
		'ut' : UT (hours from beginning of the day)
		'EnergySSD' : SSD Energy bins
		'EnergyGSO' : GSO Energy bins
		'eFluxSSD' : SpecCls object, contains SSD electron fluxes
		'eFluxGSO' : SpecCls object, contains GSO electron fluxes
		
	For more information about the SpecCls object, see Arase.Tools.SpecCls 
		

	'''		
	#get a list of the dates to load		
	if np.size(Date) == 1:
		dates = np.array([Date])
	elif np.size(Date) == 2:
		dates = ListDates(Date[0],Date[1])
	else:
		dates = np.array([Date]).flatten()
		
	out = {	'eFluxSSD' : None,
			'eFluxGSO' : None}

	#loop through dates
	for date in dates:					
		
		#read the CDF file
		data,meta = _ReadCDF(date,2,'omniflux')		
		

		if data is None:
			continue
		
		#get the time 
		sEpoch = data['Epoch']
		sDate,sut = CDFEpochToUT(sEpoch)
		
		#the energy arrays
		sEnergySSD = data['FEDO_SSD_Energy']
		sEnergyGSO = data['FEDO_GSO_Energy']
		
		#get the midpoints
		essd = np.mean(sEnergySSD,axis=0)
		egso = np.mean(sEnergyGSO,axis=0)
		
		#replace bad data
		ssd = data['FEDO_SSD']
		bad = np.where(ssd < 0)
		ssd[bad] = np.nan
		
		gso = data['FEDO_GSO']
		bad = np.where(gso < 0)
		gso[bad] = np.nan
		
		#plot labels
		zlabelS = 'Omni-directional flux of XEP SSD (1/keV-sr-s-cm$^2$)'
		ylabelS = 'Energy (keV)'
		zlabelG = 'Omni-directional flux of XEP GSO (1/keV-sr-s-cm$^2$)'
		ylabelG = 'Energy (keV)'
		
		
		#now to store the spectra
		if out['eFluxSSD'] is None:
			out['eFluxSSD'] = SpecCls(SpecType='e',ylabel=ylabelS,zlabel=zlabelS,ylog=True,zlog=True,ScaleType='positive')
		out['eFluxSSD'].AddData(sDate,sut,sEpoch,essd,ssd,Meta=meta['FEDO_SSD'],Label='XEP')
		if out['eFluxGSO'] is None:
			out['eFluxGSO'] = SpecCls(SpecType='e',ylabel=ylabelG,zlabel=zlabelG,ylog=True,zlog=True,ScaleType='positive')
		out['eFluxGSO'].AddData(sDate,sut,sEpoch,egso,gso,Meta=meta['FEDO_GSO'],Label='XEP')
			
	return out	
