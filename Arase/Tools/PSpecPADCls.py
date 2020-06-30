import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from .ContUT import ContUT
from .DTPlotLabel import DTPlotLabel
from scipy.interpolate import interp1d
from .PSDtoCounts import PSDtoCounts
from .PSDtoFlux import PSDtoFlux
from .CountstoFlux import CountstoFlux
from .CountstoPSD import CountstoPSD
from scipy.stats import mode

defargs = {	'Meta' : None,
			'dt' : None,
			'ew' : None,
			'tlabel' : 'UT',
			'elabel' : '$E$ (keV)',
			'vlabel' : '$V$ (m s$^{-1}$)',
			'alabel' : r'Pitch Angle, $\alpha$ ($^{\circ}$)',
			'flabel' : '',
			'plabel' : 'PSD (s$^3$ m$^{-6}$)',
			'elog' : True,
			'vlog' : True,
			'flog' : True, 
			'plog' : True, 
			'ScaleType' : 'range',
			'nStd' : 2}

amu = 1.6605e-27

ParticleMass = { 	'e' : 9.10938356e-31,
					'H' : 1.6726219e-27,
					'He' : 4.002602*amu,
					'O' : 15.999*amu,
					'O2' : 15.999*amu*2}

class PSpecPADCls(object):
	def __init__(self,PADSpec,SpecType='e',**kwargs):
		'''
		An object for storing and plotting particle spectral data.
		
		See SpecCls.Plot, SpecCls.PlotSpectrum and SpecCls.GetSpectrum
		for more information.
		
		Inputs
		=====
		SpecType : str
			'e'|'H'|'He'|'O'|'O2'
		xlabel : str
			Label for x-axis
		ylabel : str
			Label for Energy
		zlabel : str
			Label for pitch angle
		clabel : str
			Label for color scale
		ylog : bool
			True for logarithmic y-axis
		clog : bool
			True for logarithmic color scale
		
		'''
		
		#create lists to store the input variables
		self.Mass = ParticleMass.get(SpecType,9.10938356e-31)
		self.n = 0
		self.SpecType = SpecType

		#store the input variables by appending to the existing lists
		self.Date = PADSpec['Date']
		self.ut = PADSpec['ut']
		self.utc = PADSpec['utc']
		self.Emax = PADSpec['Emin']
		self.Emin = PADSpec['Emax']
		self.Alpha = PADSpec['Alpha']
		self.Flux = PADSpec['Flux']

	
		#Process the energy bins
		self._ProcessEnergy()

		#get phase space density
		self._CalculatePSD()
		
		#calculate dt
		self._ProcessDT()


		
		
		#and the keywords
		self.tlabel = kwargs.get('tlabel',defargs['tlabel'])
		self.elabel = kwargs.get('elabel',defargs['elabel'])
		self.vlabel = kwargs.get('vlabel',defargs['vlabel'])
		self.alabel = kwargs.get('alabel',defargs['alabel'])
		self.flabel = kwargs.get('flabel',defargs['flabel'])
		self.plabel = kwargs.get('plabel',defargs['plabel'])
		self._elog = kwargs.get('elog',defargs['elog'])
		self._elog = kwargs.get('vlog',defargs['vlog'])
		self._flog = kwargs.get('flog',defargs['flog'])
		self._plog = kwargs.get('plog',defargs['plog'])
		self._ScaleType = kwargs.get('ScaleType',defargs['ScaleType'])
		self._nStd = kwargs.get('nStd',defargs['nStd'])
		
		#calculate the new time, energy and z scale limits
		self._CalculateTimeLimits() 
		self._CalculateEnergyLimits()
		self._CalculateScale()
		self._CalculateVLimits()
		self._CalculatePSDScale()		

	
	def _ProcessEnergy(self):
		'''
		Process the energy bins
		
		'''
		
		#calculate the middle (logarithmically)
		lemin = np.log10(self.Emin)
		lemax = np.log10(self.Emax)
		self.Emid = 10.0**(0.5*(lemin + lemax))

		
		
	def _ProcessDT(self):
		#set the interval between each measurement (assuming ut is start 
		#of interval and that ut + dt is the end
		dt = (self.utc[1:] - self.utc[:-1])
		self.dt = np.append(dt,dt[-1]).clip(max=8.0/3600.0)
		

	def _CalculatePSD(self):
		e = 1.6022e-19
		self.V = np.sqrt(np.float64(e*2000.0*self.Emid)/self.Mass)
		self.V0 = np.sqrt(np.float64(e*2000.0*(self.Emin)/self.Mass))
		self.V1 = np.sqrt(np.float64(e*2000.0*(self.Emax)/self.Mass))

		psd = np.zeros(self.Flux.shape,dtype='float64')
		if np.size(self.V.shape) == 1: 
			nv = self.V.size
			for i in range(0,nv):
				psd[:,i,:] =  np.float64(self.Flux[:,i,:])*(np.float64(self.Mass)/(self.V[i]**2)) * np.float64(10.0/e)
		else:
			nv = self.V.shape[-1]
			for i in range(0,nv):
				psd[:,i,:] =  (np.float64(self.Flux[:,i,:].T)*(np.float64(self.Mass)/(self.V[:,i]**2)) * np.float64(10.0/e)).T
		self.PSD = psd
			
	
	
	# def _GetSpectrum(self,I,sutc,dutc,Method,PSD):
	
		# #get the appropriate data
		# l = self.Label[I]
		# utc = self.utc[I]
		# if PSD:
			# f = self.V[I]
			# Spec = self.PSD[I]		
		# else:
			# f = self.Energy[I]
			# Spec = self.Spec[I]		
		
		# #find the nearest
		# dt = np.abs(utc - sutc)
		# near = np.where(dt == dt.min())[0][0]
		
		# #check if the nearest is within dutc
		# if dt[near] > dutc:
			# return [],[],[]
			
		
		# #check if we are past the end of the time series, or Method is nearest
		# if (Method == 'nearest') or (sutc < utc[0]) or (sutc > utc[-1]):
			# s = Spec[near,:]
			# if len(f.shape) == 2:
				# e = f[near,:]
			# else:
				# e = f
			
		# else:
			# #in this case we need to find the two surrounding neighbours
			# #and interpolate between them
			# bef = np.where(utc <= sutc)[0][-1]
			# aft = np.where(utc > sutc)[0][0]
			
			# s0 = Spec[bef,:]
			# s1 = Spec[aft,:]
			
			# if len(f.shape) == 2:
				# e0 = f[near,:]
				# e1 = f[near,:]
			# else:
				# e0 = f
				# e1 = f
			
			# dx = utc[aft] - utc[bef]
			# ds = s1 - s0
			# de = e1 - e0
			
			# dsdx = ds/dx
			# dedx = de/dx
			
			# dt = sutc - utc[bef]
			
			# s = s0 + dt*dsdx
			# e = e0 + dt*dedx
		
		
		# #remove rubbish
		# good = np.where(e > 0)[0]
		# e = e[good]
		# s = s[good]
			
		# #sort by e
		# srt = np.argsort(e)
		# e = e[srt]
		# s = s[srt]
		# return e,s,l

	
	# def GetSpectrum(self,Date,ut,Method='nearest',Maxdt=60.0,Split=False,PSD=False):
		# '''
		# This method will return a spectrum from a given time.
		
		# Inputs
		# ======
		# Date : int
			# Date in format yyyymmdd
		# ut : float
			# Time in hours since beginning of the day
		# Method : str
			# 'nearest'|'interpolate' - will find the nearest spectrum to
			# the time specified time, or will interpolate between two 
			# surrounding spectra.
		# Maxdt : float
			# Maximum difference in time between the specified time and the
			# time of the spectra in seconds.
		# Split : bool
			# If True, the spectra will be returned as a list, if False,
			# they will be combined to form a single spectrum.
		# PSD : bool
			# If True then phase space density will be returned
		
		# Returns
		# =======
		# energy : float/list
			# Array(s) of energies
		# spec : float/list
			# Array(s) containing specral data
		# labs : list
			# List of plot labels
		
		# '''
	
		# #convert to continuous time
		# utc = ContUT(np.array([Date]),np.array([ut]))[0]
		# dutc = Maxdt/3600.0
		
		# #create the objects to store spectra and energy bins
		# spec = []
		# energy = []
		# labs = []
		
		# #get the spectra for each element in  self.Spec
		# for i in range(0,self.n):
			# e,s,l = self._GetSpectrum(i,utc,dutc,Method,PSD)
			# if len(s) > 0:
				# spec.append(s)
				# energy.append(e)
				# labs.append(l)
			
		# #combine if necessary
		# if not Split:
			# spec = np.concatenate(spec)
			# energy = np.concatenate(energy)
			# srt = np.argsort(energy)
			# spec = spec[srt]
			# energy = energy[srt]
			
		# return energy,spec,labs
		
	# def PlotSpectrum(self,Date,ut,Method='nearest',Maxdt=60.0,Split=False,
		# fig=None,maps=[1,1,0,0],color=None,xlog=True,ylog=None,PSD=False,
		# FitKappa=False,FitMaxwellian=False,nox=False,noy=False):
		# '''
		# This method will plot a spectrum from a given time.
		
		# Inputs
		# ======
		# Date : int
			# Date in format yyyymmdd
		# ut : float
			# Time in hours since beginning of the day
		# Method : str
			# 'nearest'|'interpolate' - will find the nearest spectrum to
			# the time specified time, or will interpolate between two 
			# surrounding spectra.
		# Maxdt : float
			# Maximum difference in time between the specified time and the
			# time of the spectra in seconds.
		# Split : bool
			# If True, the spectra will be returned as a list, if False,
			# they will be combined to form a single spectrum.
		# PSD : bool
			# If True then phase space density will be plotted
		# fig : None, matplotlib.pyplot or matplotlib.pyplot.Axes instance
			# If None - a new plot is created
			# If an instance of pyplot then a new Axes is created on an existing plot
			# If Axes instance, then plotting is done on existing Axes
		# maps : list
			# [xmaps,ymaps,xmap,ymap] controls position of subplot
		# xlog : bool
			# if True, x-axis is logarithmic
		# ylog : bool
			# If True, y-axis is logarithmic
		# FitMaxwellian : bool or str
			# If True - the PSD will be used to fit a Maxwellian 
			# distribution, if 'counts' then the counts will be used 
			# instead.
		# FitKappa : bool or str
			# If True - the PSD will be used to fit a Kappa
			# distribution, if 'counts' then the counts will be used 
			# instead.			
		
				
		# '''	
		
		# #get the spectra
		# energy,spec,labs = self.GetSpectrum(Date,ut,Method,Maxdt,Split,PSD)
		
		
		# #create the figure
		# if fig is None:
			# fig = plt
			# fig.figure()
		# if hasattr(fig,'Axes'):	
			# ax = fig.subplot2grid((maps[1],maps[0]),(maps[3],maps[2]))
		# else:
			# ax = fig	
			
		# #plot
		# if Split:
			# if not color is None:
				# nc = len(color)
			# for i in range(0,len(spec)):
				# if color is None:
					# ax.plot(energy[i],spec[i],label=labs[i],marker='.')
				# else:
					# ax.plot(energy[i],spec[i],color=color[i % nc],label=labs[i],marker='.')
			
		# else:
			# ax.plot(energy,spec,color=color,marker='.')

		# #set the x-axis scale
		# if xlog is None:
			# xlog = self._ylog
		# if xlog:
			# ax.set_xscale('log')
		
		# #set the y-axis scale
		# if ylog is None:
			# ylog = self._zlog
		# if ylog:
			# ax.set_yscale('log')
			
		# #set the axis labels
		# if PSD:
			# ax.set_xlabel('V (m s$^{-1}$)')
			# ax.set_ylabel('PSD (s$^3$ m$^{-6}$)')
		# else:
			# ax.set_xlabel(self.ylabel)
			# ax.set_ylabel(self.zlabel)
			
		# #turn axes off when needed
		# if nox:
			# ax.set_xlabel('')
			# ax.xaxis.set_ticks([])
		# if noy:
			# ax.set_ylabel('')
			# ax.yaxis.set_ticks([])


		# if (not FitKappa is False) or (not FitMaxwellian is False):
			# ylim = ax.get_ylim()
			# ax.set_ylim(ylim)
			
			
			# #get the combined spectra
			# v,spec,labs = self.GetSpectrum(Date,ut,Method,Maxdt,False,True)
			# e = 1.6022e-19
			# E = 0.5*self.Mass*(v**2)/(e*1000)
			
			# #convert to counts
			# C = PSDtoCounts(v,spec,self.Mass)

			# #fit spectrum
			# if (not FitKappa is False):
				# if FitKappa is 'counts':
					# nk,Tk,K,statk = FitKappaDistCts(v,C,1.0e5,1.0e6,self.Mass,Verbose=True)
				# else:
					# nk,Tk,K,statk = FitKappaDist(v,spec,1.0e5,1.0e6,self.Mass,Verbose=True)
				# fk = KappaDist(nk,v,Tk,self.Mass,K)
				# if not PSD:
					# fk = PSDtoFlux(v,fk,self.Mass)
					# ax.plot(E,fk,color='pink',linestyle='--',label=r'Kappa Fit: $n_{\kappa}$=' + '{:5.2f}'.format(nk/1e6)+r' cm$^{-3}$,'+'\n'+'$T_{\kappa}$='+'{:5.2f}'.format(Tk/1e6)+r' MK, $\kappa$='+'{:5.1f}'.format(K))
				# else:
					# ax.plot(v,fk,color='pink',linestyle='--',label=r'Kappa Fit: $n_{\kappa}$=' + '{:5.2f}'.format(nk/1e6)+r' cm$^{-3}$,'+'\n'+'$T_{\kappa}$='+'{:5.2f}'.format(Tk/1e6)+r' MK, $\kappa$='+'{:5.1f}'.format(K))
			# if (not FitMaxwellian is False):
				# if FitMaxwellian is 'counts':
					# nm,Tm,statm = FitMaxwellianDistCts(v,C,1.0e5,1.0e6,self.Mass)
				# else:
					# nm,Tm,statm = FitMaxwellianDist(v,spec,1.0e5,1.0e6,self.Mass,Verbose=True)
				# fm = MaxwellBoltzmannDist(nm,v,Tm,self.Mass)
				# if not PSD:
					# fm = PSDtoFlux(v,fm,self.Mass)
					# ax.plot(E,fm,color='blue',linestyle='--',label=r'M-B Fit: $n$=' + '{:5.2f}'.format(nm/1e6)+r' cm$^{-3}$,'+'\n'+'$T$='+'{:5.2f}'.format(Tm/1e6)+r' MK')
				# else:
					# ax.plot(v,fm,color='blue',linestyle='--',label=r'M-B Fit: $n$=' + '{:5.2f}'.format(nm/1e6)+r' cm$^{-3}$,'+'\n'+'$T$='+'{:5.2f}'.format(Tm/1e6)+r' MK')

		# ax.legend(fontsize=8)
			
		# return ax
				
		
	def PlotSpectrogram(self,Bin,ut=None,fig=None,maps=[1,1,0,0],
			yparam='E',zparam='Flux',ylog=None,scale=None,zlog=None,
			cmap='gnuplot',nox=False,noy=False):
		'''
		Plots the spectrogram
		
		Inputs
		======
		Date : int32
			This, along with 'ut' controls the time limits of the plot,
			either set as a single date in the format yyyymmdd, or if 
			plotting over multiple days then set a 2 element tuple/list/
			numpy.ndarray with the start and end dates. If set to None 
			(default) then the time axis limits will be calculated 
			automatically.
		ut : list/tuple
			2-element start and end times for the plot, where each 
			element is the time in hours sinsce the start fo the day,
			e.g. 17:30 == 17.5.
		PSD : bool
			If True then phase space density will be plotted
		fig : None, matplotlib.pyplot or matplotlib.pyplot.Axes instance
			If None - a new plot is created
			If an instance of pyplot then a new Axes is created on an existing plot
			If Axes instance, then plotting is done on existing Axes
		maps : list
			[xmaps,ymaps,xmap,ymap] controls position of subplot
		xlog : bool
			if True, color scale is logarithmic
		ylog : bool
			If True, y-axis is logarithmic
		cmap : str
			String containing the name of the colomap to use
		scale : list
			2-element list or tuple containing the minimum and maximum
			extents of the color scale
		nox : bool
			If True, no labels or tick marks are drawn for the x-axis
		noy : bool
			If True, no labels or tick marks are drawn for the y-axis
		'''
		
		
		
		#create the plot
		if fig is None:
			fig = plt
			fig.figure()
		ax = fig.subplot2grid((maps[1],maps[0]),(maps[3],maps[2]))
		
		#set time axis limits
		if ut is None:
			ax.set_xlim(self._utlim)
		else:
			Date = mode(self.Date)[0][0]
			utclim = ContUT(np.array([Date,Date]),np.array(ut))
			ax.set_xlim(utclim)
			
		#get the yparameter stuff
		if yparam == 'E':
			title = r'$\alpha$ Bin {:d} ({:4.1f} - {:4.1f}'.format(Bin,self.Alpha[Bin],self.Alpha[Bin+1])+'$^{\circ}$)'
			if ylog is None:
				ylog = self._elog
			ax.set_ylim(self._elim)
			y0 = self.Emin
			y1 = self.Emax
			ax.set_ylabel(self.elabel)
		elif yparam == 'V':
			title = r'$\alpha$ Bin {:d} ({:4.1f} - {:4.1f}'.format(Bin,self.Alpha[Bin],self.Alpha[Bin+1])+'$^{\circ}$)'
			if ylog is None:
				ylog = self._elog
			ax.set_ylim(self._vlim)
			y0 = self.V0
			y1 = self.V1
			ax.set_ylabel(self.vlabel)
		elif yparam == 'alpha':
			title = '$E$/$V$ Bin {:d}'.format(Bin)
			ylog = False
			ax.set_ylim([0.0,180.0])
			y0 = self.Alpha[:-1]
			y1 = self.Alpha[1:]
			ax.set_ylabel(self.alabel)
		else:
			return			
		if ylog:
			ax.set_yscale('log')
		ax.set_xlabel(self.tlabel)
		ax.set_title(title)
	
		#turn axes off when needed
		if nox:
			ax.set_xlabel('')
			ax.xaxis.set_ticks([])
		if noy:
			ax.set_ylabel('')
			ax.yaxis.set_ticks([])

		#get z stuff
		if zparam == 'Flux':
			if yparam == 'alpha':
				z = self.Flux[:,:,Bin]
			else:
				z = self.Flux[:,Bin,:]
			
			zlabel = self.flabel
			if zlog is None:
				zlog = self._flog
			if scale is None:
				scale = self._scale
		elif zparam == 'PSD':
			if yparam == 'alpha':
				z = self.PSD[:,:,Bin]
			else:
				z = self.PSD[:,Bin,:]
			zlabel = self.plabel
			if zlog is None:
				zlog = self._plog
			if scale is None:
				scale = self._psdscale
			
		#get color scale
		if zlog:
			norm = colors.LogNorm()
		else:
			norm = colors.Normalize()
			
		#create plots
		sm = self._PlotSpectrogram(ax,y0,y1,z,scale,norm,cmap)

		#sort the UT axis out
		DTPlotLabel(ax,self.utc,self.Date)
		

		#colorbar
		divider = make_axes_locatable(ax)
		cax = divider.append_axes("right", size="2.5%", pad=0.05)

		cbar = fig.colorbar(sm,cax=cax) 
		cbar.set_label(zlabel)		
		return ax

	def _PlotSpectrogram(self,ax,y0,y1,z,scale,norm,cmap):
		'''
		This will plot a single spectrogram
		
		'''
		#get the y ranges for each row of data
		bad = np.where(np.isnan(y0) | np.isnan(y1))
		y0[bad] = 0.0
		y1[bad] = 0.0

		#get the ut array limits
		t0 = self.utc
		t1 = self.utc + self.dt
		utc = self.utc
		
		#look for gaps in ut
		if len(y0.shape) > 1:

			isgap = ((utc[1:] - utc[:-1]) > 60.0/3600.0) | (((y0[1:,:] - y0[:-1,:]) != 0) | ((y0[1:,:] - y0[:-1,:]) != 0)).any(axis=1)
			ne = y0.shape[1]
		else:
			#isgap = (utc[1:] - utc[:-1]) > 1.1*dt[:-1]
			isgap = (utc[1:] - utc[:-1]) > 60.0/3600.0
			ne = y0.size
		gaps = np.where(isgap)[0] + 1
		if gaps.size == 0:
			#no gaps
			i0 = [0]
			i1 = [utc.size]
		else:
			#lots of gaps
			i0 = np.append(0,gaps)
			i1 = np.append(gaps,utc.size)
		ng = np.size(i0)

		#loop through each continuous block of utc
		for i in range(0,ng):
			ttmp = np.append(t0[i0[i]:i1[i]-1],t1[i1[i]-1])
			st = z[i0[i]:i1[i]]
			for j in range(0,ne):				
				if len(y0.shape) > 1:
					etmp = np.array([y0[i0[i],j],y1[i0[i],j]])
				else:
					etmp = np.array([y0[j],y1[j]])
				if np.isfinite(etmp).all():
					#plot each row of energy
					tg,eg = np.meshgrid(ttmp,etmp)
					
					s = np.array([st[:,j]])
					
					sm = ax.pcolormesh(tg,eg,s,cmap=cmap,norm=norm,vmin=scale[0],vmax=scale[1])
			
		return sm
		
	def _CalculateTimeLimits(self):
		'''
		Loop through all of the stored spectra and find the time limits.
		
		'''
		#initialize time limits
		self._utlim = [np.nanmin(self.utc),np.nanmax(self.utc)]
		
		
	def _CalculateEnergyLimits(self):
		'''
		Loop through all of the stored spectra and work out the energy
		range to plot.
		
		'''

		goodmin = np.where((self.Emin > 0) & np.isfinite(self.Emin))
		goodmax = np.where((self.Emax > 0) & np.isfinite(self.Emax))

		self._elim = [np.nanmin(self.Emin[goodmin]),np.nanmax(self.Emax[goodmax])]


	def _CalculateVLimits(self):
		'''
		Loop through all of the stored spectra and work out the velocity
		range to plot.
		
		'''
		goodmin = np.where((self.V0 > 0) & np.isfinite(self.V0))
		goodmax = np.where((self.V1 > 0) & np.isfinite(self.V1))

		self._vlim = [np.nanmin(self.V0[goodmin]),np.nanmax(self.V1[goodmax])]


		
	def _CalculateScale(self):
		'''
		Calculate the default scale limits for the plot.
		
		'''
		ls = np.log10(self.Flux)
		bad = np.where(self.Flux <= 0)
		ls[bad] = np.nan
				
		if self._ScaleType == 'std':
			mu = np.nanmean(self.Flux)
			std = np.std(self.Flux)
			
			lmu = np.nanmean(ls)
			lstd = np.std(ls)
				
			tmpscale = [mu - self._nStd*std, mu + self._nStd*std]
			tmplogscale = 10**np.array([lmu - self._nStd*lstd, lmu + self._nStd*lstd])					
			
		elif self._ScaleType == 'positive':
			#calculate the scale based on all values being positive 
			std = np.sqrt((1.0/np.sum(self.Flux.size))*np.nansum((self.Flux)**2))
			lstd = np.sqrt(((1.0/np.sum(np.isfinite(ls))))*np.nansum((ls)**2))
				
			tmpscale = [0.0,std*self._nStd]
			tmplogscale = 10**np.array([np.nanmin(ls),lstd*self._nStd])			
		else:
			#absolute range
			tmpscale = [np.nanmin(self.Flux),np.nanmax(self.Flux)]
			tmplogscale = 10**np.array([np.nanmin(ls),np.nanmax(ls)])


	
		self._scale = tmpscale
		self._logscale = tmplogscale
	
	def _CalculatePSDScale(self):
		'''
		Calculate the default scale limits for the plot.
		
		'''

		ls = np.log10(self.PSD)
		bad = np.where(self.PSD <= 0)
		ls[bad] = np.nan
				
		if self._ScaleType == 'std':
			mu = np.nanmean(self.PSD)
			std = np.std(self.PSD)
			
			lmu = np.nanmean(ls)
			lstd = np.std(ls)
				
			tmpscale = [mu - self._nStd*std, mu + self._nStd*std]
			tmplogscale = 10**np.array([lmu - self._nStd*lstd, lmu + self._nStd*lstd])					
			
		elif self._ScaleType == 'positive':
			#calculate the scale based on all values being positive 
			std = np.sqrt((1.0/np.sum(self.Flux.size))*np.nansum((self.PSD)**2))
			lstd = np.sqrt(((1.0/np.sum(np.isfinite(ls))))*np.nansum((ls)**2))
				
			tmpscale = [0.0,std*self._nStd]
			tmplogscale = 10**np.array([np.nanmin(ls),lstd*self._nStd])			
		else:
			#absolute range
			tmpscale = [np.nanmin(self.PSD),np.nanmax(self.PSD)]
			tmplogscale = 10**np.array([np.nanmin(ls),np.nanmax(ls)])


		
		self._psdscale = tmpscale
		self._psdlogscale = tmplogscale
