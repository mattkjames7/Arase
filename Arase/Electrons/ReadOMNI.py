import numpy as np
from ..LEPe._ReadCDF import _ReadCDF as LEPCDF 
from ..MEPe._ReadCDF import _ReadCDF as MEPCDF 
from ..HEP._ReadCDF import _ReadCDF as HEPCDF 
from ..XEP._ReadCDF import _ReadCDF as XEPCDF 
from ..Tools.SpecCls import SpecCls
from ..Tools.CDFEpochToUT import CDFEpochToUT

def ReadOMNI(Date,Instruments=['LEPe','MEPe','HEP','XEP']):
	'''
	Get a SpecCls object containing all of the electron data in one place.
	
	'''

	ylabel = 'Energy (keV)'
	zlabel = 'Omni-directional Electron Flux (cm$^{-2}$ s$^{-1}$ sr$^{-1}$ keV$^{-1}$)'
	
	Dates = []
	ut = []
	Epoch = []
	Energy = []
	Spec = []
	BW = []
	
	if 'LEP' in Instruments or 'LEPe' in Instruments:
		#Add LEP spectra
		
		data,meta = LEPCDF(Date,2,'omniflux')	

		if not data is None:
			e = data['Epoch']
			d,t = CDFEpochToUT(e)
			energy = data['FEDO_Energy']/1000.0
			emid = np.mean(energy,axis=1)
			bw = energy[:,1,:] - energy[:,0,:]
			s = data['FEDO']*1000.0
			bad = np.where(s < 0)
			s[bad] = np.nan
			
			Dates.append(d)
			ut.append(t)
			Epoch.append(e)
			Energy.append(emid)
			Spec.append(s)
			BW.append(bw)
			
			
			
	if 'MEP' in Instruments or 'MEPe' in Instruments:
		#Add MEP spectra
		
		data,meta = MEPCDF(Date,2,'omniflux')	

		if not data is None:
			e = data['epoch']
			d,t = CDFEpochToUT(e)
			energy = data['FEDO_Energy']
			emid = energy
			bw = None
			s = data['FEDO']
			bad = np.where(s < 0)
			s[bad] = np.nan
			
			Dates.append(d)
			ut.append(t)
			Epoch.append(e)
			Energy.append(emid)
			Spec.append(s)
			BW.append(bw)
			
	if 'HEP' in Instruments:
		#Add HEP spectra
		
		data,meta = HEPCDF(Date,2,'omniflux')	

		if not data is None:
			e = data['Epoch_L']
			d,t = CDFEpochToUT(e)
			energy = data['FEDO_L_Energy']
			emid = np.mean(energy,axis=1)
			bw = energy[:,1,:] - energy[:,0,:]
			s = data['FEDO_L']
			bad = np.where(s < 0)
			s[bad] = np.nan
			
			Dates.append(d)
			ut.append(t)
			Epoch.append(e)
			Energy.append(emid)
			Spec.append(s)
			BW.append(None)
			
			e = data['Epoch_H']
			d,t = CDFEpochToUT(e)
			energy = data['FEDO_H_Energy']
			emid = np.mean(energy,axis=1)
			bw = energy[:,1,:] - energy[:,0,:]
			s = data['FEDO_H']
			bad = np.where(s < 0)
			s[bad] = np.nan
			
			Dates.append(d)
			ut.append(t)
			Epoch.append(e)
			Energy.append(emid)
			Spec.append(s)
			BW.append(None)
			
	if 'XEP' in Instruments:
		#Add XEP spectra
		
		data,meta = XEPCDF(Date,2,'omniflux')	

		if not data is None:
			e = data['Epoch']
			d,t = CDFEpochToUT(e)
			energy = data['FEDO_SSD_Energy']
			emid = np.mean(energy,axis=1)
			bw = energy[:,1,:] - energy[:,0,:]
			s = data['FEDO_SSD']
			bad = np.where(s < 0)
			s[bad] = np.nan
			
			Dates.append(d)
			ut.append(t)
			Epoch.append(e)
			Energy.append(emid)
			Spec.append(s)
			BW.append(bw)
			
	return SpecCls(Dates,ut,Epoch,Energy,Spec,bw=BW,ylabel=ylabel,zlabel=zlabel,ylog=ylog,zlog=zlog,ScaleType='positive')
