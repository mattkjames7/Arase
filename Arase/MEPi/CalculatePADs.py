import numpy as np
from .Read3D import Read3D
from .GetPitchAngle import GetPitchAngle
from ..Tools.ContUT import ContUT
from ..Tools.CDFEpochToUT import CDFEpochToUT
from scipy.stats import binned_statistic

def CalculatePADs(Date,na=18):
	
	#for HEP we should average over each sector
	
	#this is the output dictionary
	out = {}
	
	#read the 3D data in
	data,meta = Read3D(Date)
	

	#calculate alpha
	alpha = GetPitchAngle(Date,data=data)

	#list the fields used for high and low parts of the data
	fields = { 	'H+Flux' : ('FPDU_Energy','FPEDU'),
				'He+Flux' : ('FHEDU_Energy','FHEEDU'),
				'He++Flux' : ('FHE2DU_Energy','FHE2EDU'),
				'O++Flux' : ('FOPPDU_Energy','FOPPEDU'),
				'O+Flux' : ('FODU_Energy','FOEDU'),
				'O2+Flux' : ('FO2PDU_Energy','FO2PEDU')}
	
	#loop through them both
	for ff in list(fields.keys()):
		print(ff)
		fenergy,fflux =  fields[ff]
		
	
		#determine the size of the output arrays
		nt = data['epoch'].size
		ne = data[fenergy].size
		
		#get the dates/times
		Date,ut = CDFEpochToUT(data['epoch'])
		utc = ContUT(Date,ut)
		
		#get the energy arrays (shape: (nt,ne))
		Emid = data[fenergy]
		lE = np.log10(Emid)
		dE = np.abs(lE[1:] - lE[:-1])
		lEmin = np.append(lE[0]-dE[0]/2.0,lE[1:]-dE/2.0)
		lEmax = np.append(lE[:-1]+dE/2.0,lE[-1]+dE[-1]/2.0,)

		EMin = 10**lEmin
		EMax = 10**lEmax
		
		#get the alpha limits
		Alpha = np.linspace(0.0,180.0,na+1)

		#create 3D array for fluxes
		flux = np.zeros((nt,ne,na),dtype='float32') + np.nan
		
		
		#loop through each dimension (slow!)
		FLUX = data[fflux]
		bad = np.where(FLUX <= 0)
		FLUX[bad] = np.nan
		for i in range(0,nt):
			print('\r{:6.2f}%'.format(100.0*(i+1)/nt),end='')
			for j in range(0,ne):
				a = alpha[i].flatten()
				f = FLUX[i,:,j].flatten()
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