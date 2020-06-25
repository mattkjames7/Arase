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
		If Date is a single integer - one date is loaded.
		If Date is a 2-element tuple or list, all dates from Date[0] to
		Date[1] are loaded.
		If Date contains > 2 elements, all dates within the list will
		be loaded.
			
	Returns
	=======
	data : dict
		Contains the following fields:
		'EpochL' : CDF epoch
		'EpochH' : CDF epoch
		'DateL' : Date
		'DateH' : Date
		'utL' : UT (hours from beginning of the day)
		'utH' : UT (hours from beginning of the day)
		'EnergyL' : Energy bins
		'EnergyH' : Energy bins
		'eFluxL' : SpecCls object, contains electron fluxes
		'eFluxH' : SpecCls object, contains electron fluxes
		
	For more information about the SpecCls object, see Arase.Tools.SpecCls 
		

	'''	
	#get a list of the dates to load		
	if np.size(Date) == 1:
		dates = np.array([Date])
	elif np.size(Date) == 2:
		dates = ListDates(Date[0],Date[1])
	else:
		dates = np.array([Date]).flatten()
		
	out = {	'eFluxL' : None,
			'eFluxH' : None}

	#loop through dates
	for date in dates:	
				
		#read the CDF file
		data,meta = _ReadCDF(date,2,'omniflux')		

		if data is None:
			continue
		
		
		#get the time 
		sEpochL = data['Epoch_L']
		sDateL,sutL = CDFEpochToUT(sEpochL)
		sEpochH = data['Epoch_H']
		sDateH,sutH = CDFEpochToUT(sEpochH)
		
		#the energy arrays
		sEnergyL = data['FEDO_L_Energy']
		sEnergyH = data['FEDO_H_Energy']
		
		#get the midpoints
		eL = np.mean(sEnergyL,axis=0)
		eH = np.mean(sEnergyH,axis=0)
		
		#replace bad data
		L = data['FEDO_L']
		bad = np.where(L < 0)
		L[bad] = np.nan
		
		H = data['FEDO_H']
		bad = np.where(H < 0)
		H[bad] = np.nan
		
		#labels
		zlabelH = 'Omni-directional flux of HEP-H (1/keV-sr-s-cm$^2$)'
		zlabelL = 'Omni-directional flux of HEP-L (1/keV-sr-s-cm$^2$)'
		ylabelH = 'Energy (keV)'
		ylabelL = 'Energy (keV)'
		
		
		#now to store the spectra
		if out['eFluxL'] is None:
			out['eFluxL'] = SpecCls(SpecType='e',ylabel=ylabelL,zlabel=zlabelL,ylog=True,zlog=True,ScaleType='positive')
		out['eFluxL'].AddData(sDateL,sutL,sEpochL,eL,L,bw=None,dt=None,Meta=meta['FEDO_L'],Label='HEP-L')
		
		if out['eFluxH'] is None:
			out['eFluxH'] = SpecCls(SpecType='e',ylabel=ylabelH,zlabel=zlabelH,ylog=True,zlog=True,ScaleType='positive')
		out['eFluxH'].AddData(sDateH,sutH,sEpochH,eH,H,bw=None,dt=None,Meta=meta['FEDO_H'],Label='HEP-H')
			
	return out	
