import numpy as np
from ._ReadCDF import _ReadCDF
from ..Tools.SpecCls import SpecCls
from ..Tools.CDFEpochToUT import CDFEpochToUT

def ReadHFA(Date):
	
	#List the fields to output
	fields = {	'spectra_eu' : 		('SpectraEu','Frequency, $f$ (kHz)','Power spectra $E_u^2$ (mV$^2$/m$^2$/Hz)'),
				'spectra_ev' : 		('SpectraEv','Frequency, $f$ (kHz)','Power spectra $E_v^2$ (mV$^2$/m$^2$/Hz)'),
				'spectra_bgamma' : 	('SpectraBgamma','Frequency, $f$ (kHz)','Power spectra $B_{\gamma}^2$ (pT$^2$/Hz)'),
				'spectra_esum' : 	('SpectraEsum','Frequency, $f$ (kHz)','Power spectra $E_u^2 + E_v^2$ (mV$^2$/m$^2$/Hz)'),
				'spectra_er' : 		('SpectraEr','Frequency, $f$ (kHz)','Power spectra $E_{right}^2$ (mV$^2$/m$^2$/Hz)'),
				'spectra_el' : 		('SpectraEl','Frequency, $f$ (kHz)','Power spectra $E_{left}^2$ (mV$^2$/m$^2$/Hz)'),
				'spectra_e_mix' : 	('SpectraEmix','Frequency, $f$ (kHz)','Power spectra $E_u^2$ or $E_v^2$ or $E_u^2 + E_v^2$ (mV$^2$/m$^2$/Hz)'),
				'spectra_e_ar' : 	('SpectraEAR','Frequency, $f$ (kHz)','Spectra Axial Ratio LH:-1/RH:+1'),}

				
	#read the CDF file
	datah,metah = _ReadCDF(Date,'hfa',2,'high')		
	datal,metal = _ReadCDF(Date,'hfa',2,'low')		
	
	if datah is None and datal is None:
		print('No data for this date')
		return {}
	
	#output dict
	out = {}
	
	#get the time and the frequency arrays
	if not datah is None:
		out['EpochH'] = datah['Epoch']
		out['DateH'],out['utH'] = CDFEpochToUT(out['EpochH'])
		out['FH'] = datah['freq_spec']
	if not datal is None:
		out['EpochL'] = datal['Epoch']
		out['DateL'],out['utL'] = CDFEpochToUT(out['EpochL'])
		out['FL'] = datal['freq_spec']
	

			
	#now to store the spectra
	for k in list(fields.keys()):
		

		field,ylabel,zlabel = fields[k]
		if k == 'spectra_e_ar':
			ScaleType = 'range'
		else:
			ScaleType = 'positive'
		spech = datah[k]
		bad = np.where(spech == -999.9)
		spech[bad] = np.nan
		specl = datal[k]
		bad = np.where(specl == -999.9)
		specl[bad] = np.nan


		spec = []
		date = []
		ut = [] 
		epoch = []
		f = []
		meta = []
		dt = []
		if not datah is None:
			spec.append(spech)
			date.append(out['DateH'])
			ut.append(out['utH'])
			epoch.append(out['EpochH'])
			f.append(out['FH'])
			meta.append(metah[k])
			dt.append(datah['time_step']/3600.0)
		if not datal is None:
			spec.append(specl)
			date.append(out['DateL'])
			ut.append(out['utL'])
			epoch.append(out['EpochL'])
			f.append(out['FL'])
			meta.append(metal[k])
			dt.append(datal['time_step']/3600.0)
			
		out[field] = SpecCls(date,ut,epoch,f,spec,Meta=meta,dt=dt,ylabel=ylabel,zlabel=zlabel,ScaleType=ScaleType)
		
	return out	
