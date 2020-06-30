import numpy as np
from .Read3D import Read3D
from .GetPitchAngle import GetPitchAngle
from ..Tools.ContUT import ContUT
from ..Tools.CDFEpochToUT import CDFEpochToUT
from scipy.stats import binned_statistic

def CalculatePADs(Date,na=18,Verbose=True):
	
	#for HEP we should average over each sector
	
	#this is the output dictionary
	out = {}
	
	#read the 3D data in
	data,meta = Read3D(Date)
	

	#calculate alpha
	alphaL,alphaH = GetPitchAngle(Date,data=data)

	#list the fields used for high and low parts of the data
	fields = { 	'eFluxL' : ('Epoch_L','FEDU_L_Energy','FEDU_L',alphaL,'sctno_L'),
				'eFluxH' : ('Epoch_H','FEDU_H_Energy','FEDU_H',alphaH,'sctno_H')}
	
	#loop through them both
	for ff in list(fields.keys()):
		print(ff)
		ftime,fenergy,fflux,alpha,fsect =  fields[ff]
		
		#find sector start and end times
		sect = data[fsect]
		i0 = np.where(sect == 0)[0]
		i1 = np.where(sect == 15)[0] + 1
		ni = i0.size
		
		#combine epochs
		epoch = data[ftime][i0] + 4000000000
		
	
		#determine the size of the output arrays
		nt = ni
		ne = data[fenergy].shape[1]
		
		#get the dates/times
		Date,ut = CDFEpochToUT(epoch)
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
		bad = np.where(FLUX <= 0)
		FLUX[bad] = np.nan
		for i in range(0,nt):
			if Verbose:
				print('\r{:6.2f}%'.format(100.0*(i+1)/nt),end='')
			for j in range(0,ne):
				a = alpha[i0[i]:i1[i]].flatten()
				f = FLUX[i0[i]:i1[i],j].flatten()
				good = np.where(np.isfinite(f))[0]
				if good.size > 0:
					flux[i,j],_,_ = binned_statistic(a[good],f[good],statistic='mean',bins=Alpha)
		if Verbose:
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
