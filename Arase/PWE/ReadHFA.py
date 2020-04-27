import numpy as np
from ._ReadCDF import _ReadCDF
from ..Tools.SpecCls import SpecCls
from ..Tools.CDFEpochToUT import CDFEpochToUT

def ReadHFA(Date):
	
	#List the fields to output
	fields = {	'spectra_eu' : 'SpectraEu',
				'spectra_ev' : 'SpectraEv',
				'spectra_bgamma' : 'SpectraBgamma',
				'spectra_esum' : 'SpectraEsum',
				'spectra_er' : 'SpectraEr',
				'spectra_el' : 'SpectraEl',
				'spectra_e_mix' : 'SpectraEmix',
				'spectra_e_ar' : 'SpectraEAR',
				'spectra_eu_ev' : 'SpectraEuEv',
				'spectra_eu_bg' : 'SpectraEuBgamma',
				'spectra_ev_bg' : 'SpectraEvBgamma'}
				
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
		spec = []
		date = []
		ut = [] 
		epoch = []
		f = []
		meta = []
		if not datah is None:
			spec.append(datah[k])
			date.append(out['DateH'])
			ut.append(out['utH'])
			epoch.append(out['EpochH'])
			f.append(out['FH'])
			meta.append(metah[k])
		if not datal is None:
			spec.append(datal[k])
			date.append(out['DateL'])
			ut.append(out['utL'])
			epoch.append(out['EpochL'])
			f.append(out['FL'])
			meta.append(metal[k])
			
		out[fields[k]] = SpecCls(date,ut,epoch,f,spec,Meta=meta)
		
	return out	
