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
	out['Epoch'] = data['epoch']
	out['Date'],out['ut'] = CDFEpochToUT(out['Epoch'])
	out['EpochTOF'] = data['epoch_tof']
	out['DateTOF'],out['utTOF'] = CDFEpochToUT(out['EpochTOF'])
	
	#the energy arrays
	out['Energy'] = data['FIDO_Energy']
	

	#replace bad data
	fields = {	'FPDO' : 'HpFlux',
				'FHE2DO' : 'HeppFlux',
				'FHEDO' : 'HepFlux',
				'FOPPDO' : 'OppFlux',
				'FODO' : 'OpFlux',
				'FO2PDO' : 'O2pFlux',
				'FPDO_tof' : 'HpFluxTOF',
				'FHE2DO_tof' : 'HeppFluxTOF',
				'FHEDO_tof' : 'HepFluxTOF',
				'FOPPDO_tof' : 'OppFluxTOF',
				'FODO_tof' : 'OpFluxTOF',
				'FO2PDO_tof' : 'O2pFluxTOF' }
	
	for k in list(fields.keys()):
		s = data[k]
		bad = np.where(s < 0)
		s[bad] = np.nan
		
		#now to store the spectra
		if '_tof' in k:
			out[fields[k]] = SpecCls(out['Date'],out['ut'],out['Epoch'],out['Energy'],s,Meta=meta[k])
		else:
			out[fields[k]] = SpecCls(out['DateTOF'],out['utTOF'],out['EpochTOF'],out['Energy'],s,Meta=meta[k])
			
	return out	
