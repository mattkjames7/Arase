import numpy as np
from .ReadCDF import ReadCDF
from ..Tools.PSpecCls import PSpecCls
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
		'H+Flux' : PSpecCls object, contains proton fluxes
		'He+Flux' : PSpecCls object, contains helium ion fluxes
		'O+Flux' : PSpecCls object, contains oxygen ion fluxes
		
	For more information about the PSpecCls object, see Arase.Tools.PSpecCls 
		

	'''		


	#get a list of the dates to load		
	if np.size(Date) == 1:
		dates = np.array([Date])
	elif np.size(Date) == 2:
		dates = ListDates(Date[0],Date[1])
	else:
		dates = np.array([Date]).flatten()
		
	out = {	'H+Flux' : None,
			'He+Flux' : None,
			'O+Flux' : None}


	#loop through dates
	for date in dates:	
				
					
		#read the CDF file
		data,meta = ReadCDF(date,2,'omniflux')		

		if data is None:
			continue
		
		
		#get the time 
		sEpoch = data['Epoch']
		sDate,sut = CDFEpochToUT(sEpoch)



		#replace bad data
		fields = {	'FPDO' : 	('H+','Energy (keV)',r'H$^+$ flux (keV/(s cm$^{2}$ sr keV))','H'),
					'FHEDO' : 	('He+','Energy (keV)',r'He$^+$ flux (keV/(s cm$^{2}$ sr keV))','He'),
					'FODO' : 	('O+','Energy (keV)',r'O$^+$ flux (keV/(s cm$^{2}$ sr keV))','O'),}
		
		for k in list(fields.keys()):
			s = data[k]
			bad = np.where(s < 0)
			s[bad] = np.nan
			
			#get the base field name
			kout,ylabel,zlabel,spectype = fields[k]
			
			#output spectra fields name
			kspec = kout + 'Flux'
			
			#energy field name
			ke_cdf = k + '_Energy'
			
			#get the energy bins
			ke = data[ke_cdf]
			
			#convert spectra to energy flux
			s = s*ke
			
			#now to store the spectra
			if out[kspec] is None:
				out[kspec] = PSpecCls(SpecType=spectype,ylabel=ylabel,zlabel=zlabel,ScaleType='positive',ylog=True,zlog=True)
			out[kspec].AddData(sDate,sut,sEpoch,ke,s,Meta=meta[k],Label='LEPi')
			

	return out	
