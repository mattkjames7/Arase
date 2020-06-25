import numpy as np
from ._ReadCDF import _ReadCDF
from ..Tools.SpecCls import SpecCls
from ..Tools.CDFEpochToUT import CDFEpochToUT
from ..Tools.ListDates import ListDates

def ReadHFAHigh(Date):
	'''
	Reads the level 2 high HFA data.
	
	Inputs
	======
	Date : int
		Integer date in the format yyyymmdd
	
	Returns
	=======
	data : dict
		Contains the following fields:
		'EpochH' : CDF epoch
		'DateH' : Date
		'utH' : UT (hours from beginning of the day)
		'FH' : Frequency bins
		'EpochL' : CDF epoch
		'DateL' : Date
		'utL' : UT (hours from beginning of the day)
		'FL' : Frequency bins
		'SpectraEu' : SpecCls object, contains Spectra
		'SpectraEv' : SpecCls object, contains Spectra
		'SpectraBgamma' : SpecCls object, contains Spectra
		'SpectraEsum' : SpecCls object, contains Spectra
		'SpectraEr' : SpecCls object, contains Spectra
		'SpectraEl' : SpecCls object, contains Spectra
		'SpectraEmix' : SpecCls object, contains Spectra
		'SpectraEAR' : SpecCls object, contains Spectra
		
	For more information about the SpecCls object, see Arase.Tools.SpecCls 
		

	'''		
	#List the fields to output
	fields = {	'spectra_eu' : 		('SpectraEu','Frequency, $f$ (kHz)','Power spectra $E_u^2$ (mV$^2$/m$^2$/Hz)'),
				'spectra_ev' : 		('SpectraEv','Frequency, $f$ (kHz)','Power spectra $E_v^2$ (mV$^2$/m$^2$/Hz)'),
				'spectra_bgamma' : 	('SpectraBgamma','Frequency, $f$ (kHz)','Power spectra $B_{\gamma}^2$ (pT$^2$/Hz)'),
				'spectra_esum' : 	('SpectraEsum','Frequency, $f$ (kHz)','Power spectra $E_u^2 + E_v^2$ (mV$^2$/m$^2$/Hz)'),
				'spectra_er' : 		('SpectraEr','Frequency, $f$ (kHz)','Power spectra $E_{right}^2$ (mV$^2$/m$^2$/Hz)'),
				'spectra_el' : 		('SpectraEl','Frequency, $f$ (kHz)','Power spectra $E_{left}^2$ (mV$^2$/m$^2$/Hz)'),
				'spectra_e_mix' : 	('SpectraEmix','Frequency, $f$ (kHz)','Power spectra $E_u^2$ or $E_v^2$ or $E_u^2 + E_v^2$ (mV$^2$/m$^2$/Hz)'),
				'spectra_e_ar' : 	('SpectraEAR','Frequency, $f$ (kHz)','Spectra Axial Ratio LH:-1/RH:+1'),}
				

	#get a list of the dates to load		
	if np.size(Date) == 1:
		dates = np.array([Date])
	elif np.size(Date) == 2:
		dates = ListDates(Date[0],Date[1])
	else:
		dates = np.array([Date]).flatten()
		
	out = {	'SpectraEu' : None,
			'SpectraEv' : None,
			'SpectraBgamma' : None,
			'SpectraEsum' : None,
			'SpectraEr' : None,
			'SpectraEl' : None,
			'SpectraEmix' : None,
			'SpectraEAR' : None}


	#loop through dates
	for date in dates:	


		#read the CDF file
		data,meta = _ReadCDF(date,'hfa',2,'high')		
		
		if data is None:
			continue
		
		#get the time 
		sEpoch = data['Epoch']
		sDate,sut = CDFEpochToUT(sEpoch)
		
		#the frequency arrays
		sF = data['freq_spec']
				
		#now to store the spectra
		for k in list(fields.keys()):
			spec = data[k]

			field,ylabel,zlabel = fields[k]
			if k == 'spectra_e_ar':
				ScaleType = 'range'
			else:
				ScaleType = 'positive'
			bad = np.where(spec == -999.9)
			spec[bad] = np.nan
			if out[field] is None:
				out[field] = SpecCls(SpecType='freq',ylabel=ylabel,zlabel=zlabel,ScaleType=ScaleType,zlog=True)
			out[field].AddData(sDate,sut,sEpoch,sF,spec,Meta=meta[k],dt=data['time_step']/3600.0)
		
	return out	
