import numpy as np
from .ReadCDF import ReadCDF
from ..Tools.PSpecCls import PSpecCls
from ..Tools.CDFEpochToUT import CDFEpochToUT
from ..Tools.ListDates import ListDates

def ReadOmni(Date,KeV=True,JoinBins=False):
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
		if JoinBins:
			mean = np.nanmean(emid,axis=0)
			
			srt = np.argsort(mean)
			le = np.log10(emid[:,srt])
			
			emm = 0.5*(le[:,1:] + le[:,:-1])
			
			ew00 = np.abs(le[:,0]-emm[:,0])
			ew01 = np.abs(le[:,1:]-emm)
			ew0 = np.append(ew00.reshape([-1,1]),ew01,axis=1)
			ew11 = np.abs(le[:,-1]-emm[:,-1])
			ew10 = np.abs(le[:,:-1]-emm)
			ew1 = np.append(ew10,ew11.reshape([-1,1]),axis=1)
			ew = ew0 + ew1
			print(le[0])
			print(ew[0])
			
			ew[:,srt] = 10**ew

		else:
			ew = sEnergy[:,1,:] - sEnergy[:,0,:]


		#replace bad data
		s = data['FEDO']
		bad = np.where(s < 0)
		s[bad] = np.nan
		if KeV:
			s = s*1000.0
		
			#plot labels
			ylabel = 'Energy (keV)'
			zlabel = 'Flux\n((s cm$^{2}$ sr keV)$^{-1}$)'
		else:
			
			#plot labels
			ylabel = 'Energy (eV)'
			zlabel = 'Flux\n((s cm$^{2}$ sr keV)$^{-1}$)'
		

		#now to store the spectra
		if out['eFlux'] is None:
			out['eFlux'] = PSpecCls(SpecType='e',ylabel=ylabel,zlabel=zlabel,ylog=True,zlog=True)
		out['eFlux'].AddData(sDate,sut,sEpoch,emid,s,Meta=meta['FEDO'],ew=ew,Label='LEPe')
			
	

	return out
