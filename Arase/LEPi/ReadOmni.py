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
		'Energy' : Energy bins
		'H+Flux' : SpecCls object, contains proton fluxes
		'He+Flux' : SpecCls object, contains helium ion fluxes
		'O+Flux' : SpecCls object, contains oxygen ion fluxes
		
	For more information about the SpecCls object, see Arase.Tools.SpecCls 
		

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
		data,meta = _ReadCDF(date,2,'omniflux')		

		if data is None:
			continue
		
		
		#get the time 
		sEpoch = data['Epoch']
		sDate,sut = CDFEpochToUT(sEpoch)



		#replace bad data
		fields = {	'FPDO' : 	('H+','Energy (keV)',r'Omni H$^+$ flux (1/keV-sr-s-cm$^2$)','H'),
					'FHEDO' : 	('He+','Energy (keV)',r'Omni He$^+$ flux (1/keV-sr-s-cm$^2$)','He'),
					'FODO' : 	('O+','Energy (keV)',r'Omni O$^+$ flux (1/keV-sr-s-cm$^2$)','O'),}
		
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
			
			#now to store the spectra
			if out[kspec] is None:
				out[kspec] = SpecCls(SpecType=spectype,ylabel=ylabel,zlabel=zlabel,ScaleType='positive',ylog=True,zlog=True)
			out[kspec].AddData(sDate,sut,sEpoch,ke,s,Meta=meta[k],Label='LEPi')
			

	return out	
