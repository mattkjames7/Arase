import numpy as np
from .ReadCDF import ReadCDF
from ..Tools.PSpecCls import PSpecCls
from ..Tools.CDFEpochToUT import CDFEpochToUT
from ..Tools.ListDates import ListDates

def ReadOmni(Date,KeV=True):
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
	Kev : bool
		Converts units to be KeV instead of eV
	
	Returns
	=======
	data : dict
		Contains the following fields:
		'eFlux' : PSpecCls object, contains electron fluxes
		
	For more information about the PSpecCls object, see Arase.Tools.PSpecCls 
		

	'''		
	
	#get a list of the dates to load		
	if np.size(Date) == 1:
		dates = np.array([Date])
	elif np.size(Date) == 2:
		dates = ListDates(Date[0],Date[1])
	else:
		dates = np.array([Date]).flatten()
		
	out = {	'eFlux' : None}

	#loop through dates
	for date in dates:	
				
		#read the CDF file
		data,meta = ReadCDF(date,2,'omniflux')		

		if data is None:
			continue
		

		#get the time 
		sEpoch = data['Epoch']
		sDate,sut = CDFEpochToUT(sEpoch)
		
		#the energy arrays
		sEnergy = data['FEDO_Energy']
		if KeV:
			sEnergy = sEnergy/1000.0
		emid = 10**np.mean(np.log10(sEnergy),axis=1)
		ew = sEnergy[:,1,:] - sEnergy[:,0,:]


		#replace bad data
		s = data['FEDO']
		bad = np.where(s < 0)
		s[bad] = np.nan
		if KeV:
			s = s*1000.0
		
			#plot labels
			ylabel = 'Energy (keV)'
			zlabel = 'Energy Flux\n(keV/(s cm$^{2}$ sr keV))'
		else:
			
			#plot labels
			ylabel = 'Energy (eV)'
			zlabel = 'Energy Flux\n(keV/(s cm$^{2}$ sr eV))'
		
		#convert to differential energy flux
		s = s*emid
		
		#now to store the spectra
		if out['eFlux'] is None:
			out['eFlux'] = PSpecCls(SpecType='e',ylabel=ylabel,zlabel=zlabel,ylog=True,zlog=True)
		out['eFlux'].AddData(sDate,sut,sEpoch,emid,s,Meta=meta['FEDO'],ew=ew,Label='LEPe')
			
	

	return out
