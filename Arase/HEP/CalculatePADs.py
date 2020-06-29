import numpy as np
from .Read3D import Read3D
from .GetPitchAngle import GetPitchAngle
from ..Tools.ContUT import ContUT
from ..Tools.CDFEpochToUT import CDFEpochToUT
from scipy.stats import binned_statistic

def CalculatePADs(Date,na=18):
	
	#for HEP we should average over a small range in time
	
	#this is the output dictionary
	out = {}
	
	#read the 3D data in
	data,meta = Read3D(Date)
	

	#calculate alpha
	alphaL,alphaH = GetPitchAngle(Date,data=data)

	#list the fields used for high and low parts of the data
	fields = { 	'eFluxL' : ('Epoch_L','FEDU_L_Energy','FEDU_L',alphaL),
				'eFluxH' : ('Epoch_H','FEDU_H_Energy','FEDU_H',alphaH)}
	
	#loop through them both
	for ff in list(fields.keys()):
		print(ff)
		ftime,fenergy,fflux,alpha =  fields[ff]
	
		#determine the size of the output arrays
		nt = data[ftime].size
		ne = data[fenergy].shape[1]
		
		#get the dates/times
		Date,ut = CDFEpochToUT(data[ftime])
		utc = ContUT(Date,ut)
		
		#get the energy arrays (shape: (nt,ne))
		EMin = data[fenergy][0,:]
		EMax = data[fenergy][1,:]
		
		#get the alpha limits
		Alpha = np.linspace(0.0,180.0,na+1)

		#create 3D array for fluxes
		flux = np.zeros((nt,ne,na),dtype='float32') + np.nan
		
		
		#loop through each dimension (slow!)
		FLUX = data[fflux]
		bad = np.where(FLUX < 0)
		FLUX[bad] = np.nan
		for i in range(0,nt):
			print('\r{:6.2f}%'.format(100.0*(i+1)/nt),end='')
			for j in range(0,ne):
				a = alpha[i].flatten()
				f = FLUX[i,j].flatten()
				good = np.where(np.isfinite(f))[0]
				if good.size > 0:
					flux[i,j],_,_ = binned_statistic(a[good],f[good],statistic='mean',bins=Alpha)
		print()		
		
		tmp = {}
		tmp['Date'] = Date
		tmp['ut'] = ut
		tmp['utc'] = utc
		tmp['Emin'] = EMin
		tmp['Emax'] = EMax
		tmp['Alpha'] = Alpha
		tmp['Flux'] = flux
		
		out[ff] = tmp
	
	return out
