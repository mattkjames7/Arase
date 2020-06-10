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
from .FitMaxwellianDist import FitMaxwellianDistCts,FitMaxwellianDist
from .FitKappaDist import FitKappaDistCts,FitKappaDist
from .KappaDist import KappaDist
from .MaxwellBoltzmannDist import MaxwellBoltzmannDist

defargs = {	'Meta' : None,
			'dt' : None,
			'bw' : None,
			'xlabel' : 'UT',
			'ylabel' : 'Frequency, $f$',
			'zlabel' : '',
			'ylog' : False,
			'zlog' : False, 
			'ScaleType' : 'range',
			'nStd' : 2}

amu = 1.6605e-27

ParticleMass = { 	'e' : 9.10938356e-31,
					'H' : 1.6726219e-27,
					'He' : 4.002602*amu,
					'O' : 15.999*amu,
					'O2' : 15.999*amu*2}

class SpecCls(object):
	def __init__(self,SpecType='freq',**kwargs):
		'''
		An object for storing and plotting spectral data,
		
		See SpecCls.Plot, SpecCls.PlotSpectrum and SpecCls.GetSpectrum
		for more information.
		
		Inputs
		=====
		SpecType : str
			'freq'|'e'|'H'|'He'|'O'|'O2'
		xlabel : str
			Label for x-axis
		ylabel : str
			Label for y-axis
		zlabel : str
			Label for color scale
		ylog : bool
			True for logarithmic y-axis
		zlog : bool
			True for logarithmic color scale
		
		'''
		
		#create lists to store the input variables
		self.Date = []
		self.ut = []
		self.Epoch = []
		self.Freq = []
		self.Spec = []
		self.utc = []
		self.bw = []
		self.dt = []
		self.Meta = []
		self.Label = []
		self.V = []
		self.Vbw = []
		self.PSD = []
		self.Mass = ParticleMass.get(SpecType,0.0)
		self.n = 0
		self.SpecType = SpecType
		
		#and the keywords
		self.xlabel = kwargs.get('xlabel',defargs['xlabel'])
		self.ylabel = kwargs.get('ylabel',defargs['ylabel'])
		self.zlabel = kwargs.get('zlabel',defargs['zlabel'])
		self._ylog = kwargs.get('ylog',defargs['ylog'])
		self._zlog = kwargs.get('zlog',defargs['zlog'])
		self._ScaleType = kwargs.get('ScaleType',defargs['ScaleType'])
		self._nStd = kwargs.get('nStd',defargs['nStd'])
		
			

	
	def _ProcessBW(self,bw,Freq):
		
		if bw is None:
			#if bandwidth is None, then we must calculate it from the fequencies
			df = Freq[1:] - Freq[:-1]
			df = np.concatenate(([df[0]],df,[df[1]]))/2.0
			bw = df[1:] + df[:-1]	
		elif np.size(bw) == 1:
			#if it is a single value, then turn it into an array the same size as Freq
			bw = np.zeros(Freq.shape,dtype='float32') + bw	
		
		return bw
		
	def _ProcessDT(self,dt,ut):
		#set the interval between each measurement (assuming ut is start 
		#of interval and that ut + dt is the end
		if dt is None:
			dt = (ut[1:] - ut[:-1])
			u,c = np.unique(dt,return_counts=True)
			dt = u[np.where(c == c.max())[0][0]]
		
		#convert it to an array the same length as ut
		dt = np.zeros(ut.size,dtype='float32') + dt
		return dt
		
	def _CalculatePSD(self,Spec,Energy,dE):
		e = 1.6022e-19
		V = np.sqrt(np.float64(e*2000.0*Energy)/self.Mass)
		V0 = np.sqrt(np.float64(e*2000.0*(Energy-dE/2.0)/self.Mass))
		V1 = np.sqrt(np.float64(e*2000.0*(Energy+dE/2.0)/self.Mass))
		self.V.append(V)
		self.Vbw.append(V1-V0)
		
		psd =  np.float64(Spec)*(np.float64(self.Mass)/(V**2)) * np.float64(10.0/e)
		self.PSD.append(psd)
		
		
					
	
	def AddData(self,Date,ut,Epoch,Freq,Spec,bw=None,dt=None,Meta=None,Label=''):
		'''
		Adds data to the object
		
		Inputs
		======
		Date : int
			Array of dates in format yyyymmdd
		ut : float
			Array of times since beginning of the day
		Epoch : float
			CDF epoch 
		Freq : float
			Either an array of frequencies or energies depending upon the
			type of spectrum
		Spec : float
			2D array containing the spectral data, shape (nt,nf) where
			nt is ut.size and nf is Freq.size
		bw : None or float
			Width of the energy/frequency bins
		dt : None or float
			duration of each spectrum
		Meta : dict
			Meta data from CDF - not used
		Label : str
			String containing a plot label if desired
		'''

		#store the input variables by appending to the existing lists
		self.Date.append(Date)
		self.ut.append(ut)
		self.Epoch.append(Epoch)
		self.Freq.append(Freq)
		self.Spec.append(Spec)		
		self.Meta.append(Meta)
		self.Label.append(Label)

	
		#get the bandwidth in the appropriate format
		self.bw.append(self._ProcessBW(bw,Freq))

		if self.SpecType != 'freq':
			self._CalculatePSD(Spec,Freq,self.bw[-1])
		
		#calculate continuous time axis
		self.utc.append(ContUT(Date,ut))
		
		#calculate dt
		self.dt.append(self._ProcessDT(dt,ut))

		#calculate the new time, frequency and z scale limits
		self._CalculateTimeLimits() 
		self._CalculateFrequencyLimits()
		self._CalculateScale()
		if self.SpecType != 'freq':
			self._CalculateVLimits()
			self._CalculatePSDScale()
		
		#add to the total count of spectrograms stored
		self.n += 1
	
	def _GetSpectrum(self,I,sutc,dutc,Method,PSD):
	
		#get the appropriate data
		l = self.Label[I]
		utc = self.utc[I]
		if PSD and self.SpecType != 'freq':
			f = self.V[I]
			Spec = self.PSD[I]		
		else:
			f = self.Freq[I]
			Spec = self.Spec[I]		
		
		#find the nearest
		dt = np.abs(utc - sutc)
		near = np.where(dt == dt.min())[0][0]
		
		#check if the nearest is within dutc
		if dt[near] > dutc:
			return [],[],[]
			
		
		#check if we are past the end of the time series, or Method is nearest
		if (Method == 'nearest') or (sutc < utc[0]) or (sutc > utc[-1]):
			s = Spec[near,:]
			if len(f.shape) == 2:
				e = f[near,:]
			else:
				e = f
			
		else:
			#in this case we need to find the two surrounding neighbours
			#and interpolate between them
			bef = np.where(utc <= sutc)[0][-1]
			aft = np.where(utc > sutc)[0][0]
			
			s0 = Spec[bef,:]
			s1 = Spec[aft,:]
			
			if len(f.shape) == 2:
				e0 = f[near,:]
				e1 = f[near,:]
			else:
				e0 = f
				e1 = f
			
			dx = utc[aft] - utc[bef]
			ds = s1 - s0
			de = e1 - e0
			
			dsdx = ds/dx
			dedx = de/dx
			
			dt = sutc - utc[bef]
			
			s = s0 + dt*dsdx
			e = e0 + dt*dedx
		
		
		#remove rubbish
		good = np.where(e > 0)[0]
		e = e[good]
		s = s[good]
			
		#sort by e
		srt = np.argsort(e)
		e = e[srt]
		s = s[srt]
		return e,s,l

	
	def GetSpectrum(self,Date,ut,Method='nearest',Maxdt=60.0,Split=False,PSD=False):
		'''
		This method will return a spectrum from a given time.
		
		Inputs
		======
		Date : int
			Date in format yyyymmdd
		ut : float
			Time in hours since beginning of the day
		Method : str
			'nearest'|'interpolate' - will find the nearest spectrum to
			the time specified time, or will interpolate between two 
			surrounding spectra.
		Maxdt : float
			Maximum difference in time between the specified time and the
			time of the spectra in seconds.
		Split : bool
			If True, the spectra will be returned as a list, if False,
			they will be combined to form a single spectrum.
		PSD : bool
			If True and this is not a frequency spectrum, then phase
			space density will be returned
		
		Returns
		=======
		freq : float/list
			Array(s) of frequencies or energies
		spec : float/list
			Array(s) containing specral data
		labs : list
			List of plot labels
		
		'''
	
		#convert to continuous time
		utc = ContUT(np.array([Date]),np.array([ut]))[0]
		dutc = Maxdt/3600.0
		
		#create the objects to store spectra and energy/frequency bins
		spec = []
		freq = []
		labs = []
		
		#get the spectra for each element in  self.Spec
		for i in range(0,self.n):
			e,s,l = self._GetSpectrum(i,utc,dutc,Method,PSD)
			if len(s) > 0:
				spec.append(s)
				freq.append(e)
				labs.append(l)
			
		#combine if necessary
		if not Split:
			spec = np.concatenate(spec)
			freq = np.concatenate(freq)
			srt = np.argsort(freq)
			spec = spec[srt]
			freq = freq[srt]
			
		return freq,spec,labs
		
	def PlotSpectrum(self,Date,ut,Method='nearest',Maxdt=60.0,Split=False,
		fig=None,maps=[1,1,0,0],color=None,xlog=True,ylog=None,PSD=False,
		FitKappa=False,FitMaxwellian=False):
		'''
		This method will plot a spectrum from a given time.
		
		Inputs
		======
		Date : int
			Date in format yyyymmdd
		ut : float
			Time in hours since beginning of the day
		Method : str
			'nearest'|'interpolate' - will find the nearest spectrum to
			the time specified time, or will interpolate between two 
			surrounding spectra.
		Maxdt : float
			Maximum difference in time between the specified time and the
			time of the spectra in seconds.
		Split : bool
			If True, the spectra will be returned as a list, if False,
			they will be combined to form a single spectrum.
		PSD : bool
			If True and this is not a frequency spectrum, then phase
			space density will be plotted
		fig : None, matplotlib.pyplot or matplotlib.pyplot.Axes instance
			If None - a new plot is created
			If an instance of pyplot then a new Axes is created on an existing plot
			If Axes instance, then plotting is done on existing Axes
		maps : list
			[xmaps,ymaps,xmap,ymap] controls position of subplot
		xlog : bool
			if True, x-axis is logarithmic
		ylog : bool
			If True, y-axis is logarithmic
		FitMaxwellian : bool or str
			If True - the PSD will be used to fit a Maxwellian 
			distribution, if 'counts' then the counts will be used 
			instead.
		FitKappa : bool or str
			If True - the PSD will be used to fit a Kappa
			distribution, if 'counts' then the counts will be used 
			instead.			
		
				
		'''	
		
		#get the spectra
		freq,spec,labs = self.GetSpectrum(Date,ut,Method,Maxdt,Split,PSD)
		
		
		#create the figure
		if fig is None:
			fig = plt
			fig.figure()
		if hasattr(fig,'Axes'):	
			ax = fig.subplot2grid((maps[1],maps[0]),(maps[3],maps[2]))
		else:
			ax = fig	
			
		#plot
		if Split:
			if not color is None:
				nc = len(color)
			for i in range(0,len(spec)):
				if color is None:
					ax.plot(freq[i],spec[i],label=labs[i])
				else:
					ax.plot(freq[i],spec[i],color=color[i % nc],label=labs[i])
			
		else:
			ax.plot(freq,spec,color=color)

		#set the x-axis scale
		if xlog is None:
			xlog = self._ylog
		if xlog:
			ax.set_xscale('log')
		
		#set the y-axis scale
		if ylog is None:
			ylog = self._zlog
		if ylog:
			ax.set_yscale('log')
			
		#set the axis labels
		if PSD:
			ax.set_xlabel('V (m s$^{-1}$)')
			ax.set_ylabel('PSD (s$^3$ m$^{-6}$)')
		else:
			ax.set_xlabel(self.ylabel)
			ax.set_ylabel(self.zlabel)


		if (not FitKappa is False) or (not FitMaxwellian is False):
			ylim = ax.get_ylim()
			ax.set_ylim(ylim)
			
			
			#get the combined spectra
			v,spec,labs = self.GetSpectrum(Date,ut,Method,Maxdt,False,True)
			e = 1.6022e-19
			E = 0.5*self.Mass*(v**2)/(e*1000)
			
			#convert to counts
			C = PSDtoCounts(v,spec,self.Mass)

			#fit spectrum
			if (not FitKappa is False):
				if FitKappa is 'counts':
					nk,Tk,K,statk = FitKappaDistCts(v,C,1.0e5,1.0e6,self.Mass,Verbose=True)
				else:
					nk,Tk,K,statk = FitKappaDist(v,spec,1.0e5,1.0e6,self.Mass,Verbose=True)
				fk = KappaDist(nk,v,Tk,self.Mass,K)
				if not PSD:
					fk = PSDtoFlux(v,fk,self.Mass)
					ax.plot(E,fk,color='pink',linestyle='--',label=r'Kappa Fit: $n_{\kappa}$=' + '{:5.2f}'.format(nk/1e6)+r' cm$^{-3}$,'+'\n'+'$T_{\kappa}$='+'{:5.2f}'.format(Tk/1e6)+r' MK, $\kappa$='+'{:5.1f}'.format(K))
				else:
					ax.plot(v,fk,color='pink',linestyle='--',label=r'Kappa Fit: $n_{\kappa}$=' + '{:5.2f}'.format(nk/1e6)+r' cm$^{-3}$,'+'\n'+'$T_{\kappa}$='+'{:5.2f}'.format(Tk/1e6)+r' MK, $\kappa$='+'{:5.1f}'.format(K))
			if (not FitMaxwellian is False):
				if FitMaxwellian is 'counts':
					nm,Tm,statm = FitMaxwellianDistCts(v,C,1.0e5,1.0e6,self.Mass)
				else:
					nm,Tm,statm = FitMaxwellianDist(v,spec,1.0e5,1.0e6,self.Mass,Verbose=True)
				fm = MaxwellBoltzmannDist(nm,v,Tm,self.Mass)
				if not PSD:
					fm = PSDtoFlux(v,fm,self.Mass)
					ax.plot(E,fm,color='blue',linestyle='--',label=r'M-B Fit: $n$=' + '{:5.2f}'.format(nm/1e6)+r' cm$^{-3}$,'+'\n'+'$T$='+'{:5.2f}'.format(Tm/1e6)+r' MK')
				else:
					ax.plot(v,fm,color='blue',linestyle='--',label=r'M-B Fit: $n$=' + '{:5.2f}'.format(nm/1e6)+r' cm$^{-3}$,'+'\n'+'$T$='+'{:5.2f}'.format(Tm/1e6)+r' MK')

		ax.legend(fontsize=8)
			
		return ax
				
		
	def Plot(self,fig=None,maps=[1,1,0,0],ylog=None,scale=None,zlog=None,
			cmap='gnuplot',PSD=False):
		'''
		Plots the spectrogram
		
		Inputs
		======
		PSD : bool
			If True and this is not a frequency spectrum, then phase
			space density will be plotted
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
		
		'''
		
		
		
		#create the plot
		if fig is None:
			fig = plt
			fig.figure()
		ax = fig.subplot2grid((maps[1],maps[0]),(maps[3],maps[2]))
		
		#set axis limits
		ax.set_xlim(self._utlim)
		if ylog is None:
			ylog = self._ylog
		if PSD and not self.SpecType == 'freq':
			if ylog:
				ax.set_yscale('log')
				ax.set_ylim(self._logvlim)
			else:
				ax.set_ylim(self._vlim)
		else:
			if ylog:
				ax.set_yscale('log')
				ax.set_ylim(self._logflim)
			else:
				ax.set_ylim(self._flim)
			
		#and labels
		ax.set_xlabel(self.xlabel)
		if PSD and self.SpecType != 'freq':
			ax.set_ylabel('V (m s$^{-1}$)')
		else:
			ax.set_ylabel(self.ylabel)
			
		#get color scale
		if zlog is None:
			zlog = self._zlog
		if PSD and not self.SpecType == 'freq':
			if scale is None:
				if zlog:
					scale = self._psdlogscale
				else:
					scale = self._psdscale
		else:
			if scale is None:
				if zlog:
					scale = self._logscale
				else:
					scale = self._scale
		if zlog:
			norm = colors.LogNorm()
		else:
			norm = colors.Normalize()
			
		#create plots
		for i in range(0,self.n):
			tmp = self._PlotSpectrogram(ax,i,scale,norm,cmap,PSD)
			if i == 0:
				sm = tmp

		#sort the UT axis out
		tdate = np.concatenate(self.Date)
		tutc = np.concatenate(self.utc)
		srt = np.argsort(tutc)
		tdate = tdate[srt]
		tutc = tutc[srt]
		DTPlotLabel(ax,tutc,tdate)


		#colorbar
		divider = make_axes_locatable(ax)
		cax = divider.append_axes("right", size="2.5%", pad=0.05)

		cbar = fig.colorbar(sm,cax=cax) 
		if PSD and self.SpecType != 'freq':
			cbar.set_label('PSD (s$^3$ m$^{-6}$)')		
		else:
			cbar.set_label(self.zlabel)		
		return ax

	def _PlotSpectrogram(self,ax,I,scale,norm,cmap,PSD):
		'''
		This will plot a single spectrogram (multiple may be stored in
		this object at any one time
		
		'''
		#get the appropriate data
		Date = self.Date[I]
		utc = self.utc[I]
		ut = self.ut[I]
		dt = self.dt[I]
		bw = self.bw[I]
		
		if PSD and self.SpecType != 'freq':
			bw = self.Vbw[I]
			f = self.V[I]
			Spec = self.PSD[I]		
		else:
			bw = self.bw[I]
			f = self.Freq[I]
			Spec = self.Spec[I]	
		
		#get the frequency band limits
		bad = np.where(np.isnan(f))
		f[bad] = 0.0
		f0 = f - 0.5*bw
		f1 = f + 0.5*bw

		#get the ut array limits
		t0 = utc
		t1 = utc + dt
		
		
		#look for gaps in ut
		if len(f.shape) > 1:
			#isgap = ((utc[1:] - utc[:-1]) > 1.1*dt[:-1]) | ((f[1:,:] - f[:-1,:]) != 0).any(axis=1)
			#minor fudge here
			isgap = ((utc[1:] - utc[:-1]) > 60.0/3600.0) | ((f[1:,:] - f[:-1,:]) != 0).any(axis=1)
			nf = f.shape[1]
		else:
			#isgap = (utc[1:] - utc[:-1]) > 1.1*dt[:-1]
			isgap = (utc[1:] - utc[:-1]) > 60.0/3600.0
			nf = f.size
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
			st = Spec[i0[i]:i1[i]]
			for j in range(0,nf):				
				if len(f.shape) > 1:
					ftmp = np.array([f0[i0[i],j],f1[i0[i],j]])
				else:
					ftmp = np.array([f0[j],f1[j]])
				if np.isfinite(ftmp).all():
					#plot each row of frequency
					tg,fg = np.meshgrid(ttmp,ftmp)
					
					s = np.array([st[:,j]])
					
					sm = ax.pcolormesh(tg,fg,s,cmap=cmap,norm=norm,vmin=scale[0],vmax=scale[1])
			
		return sm
		
	def _CalculateTimeLimits(self):
		'''
		Loop through all of the stored spectra and find the time limits.
		
		'''
		#initialize time limits
		utlim = [np.inf,-np.inf]
		
		#loop through each array
		n = len(self.utc)
		for i in range(0,n):
			mn = np.nanmin(self.utc[i])
			mx = np.nanmax(self.utc[i] + self.dt[i])
			if mn < utlim[0]:
				utlim[0] = mn
			if mx > utlim[1]:
				utlim[1] = mx
		self._utlim = utlim
		
	def _CalculateFrequencyLimits(self):
		'''
		Loop through all of the stored spectra and work out the frequency
		range to plot.
		
		'''
		#initialize frequency limits
		flim = [0.0,-np.inf]
		logflim = [np.inf,-np.inf]
		

		#loop through each array
		n = len(self.Freq)
		for i in range(0,n):
			f0 = self.Freq[i] - self.bw[i]/2.0
			f1 = self.Freq[i] + self.bw[i]/2.0
			mn = np.nanmin(f0)
			mx = np.nanmax(f1)
			if mn < flim[0]:
				flim[0] = mn
			if mx > flim[1]:
				flim[1] = mx
			lf0 = np.log10(f0)
			lf1 = np.log10(f1)
			bad = np.where(self.Freq[i] <= 0.0)
			lf0[bad] = np.nan
			lf1[bad] = np.nan

			lmn = np.nanmin(lf0)
			lmx = np.nanmax(lf1)
			if lmn < logflim[0]:
				logflim[0] = lmn
			if lmx > logflim[1]:
				logflim[1] = lmx

		self._flim = flim
		self._logflim = 10**np.array(logflim)


	def _CalculateVLimits(self):
		'''
		Loop through all of the stored spectra and work out the frequency
		range to plot.
		
		'''
		#initialize frequency limits
		vlim = [0.0,-np.inf]
		logvlim = [np.inf,-np.inf]
		

		#loop through each array
		n = len(self.V)
		for i in range(0,n):
			f0 = self.V[i] - self.Vbw[i]/2.0
			f1 = self.V[i] + self.Vbw[i]/2.0
			mn = np.nanmin(f0)
			mx = np.nanmax(f1)
			if mn < vlim[0]:
				vlim[0] = mn
			if mx > vlim[1]:
				vlim[1] = mx
			lf0 = np.log10(f0)
			lf1 = np.log10(f1)
			bad = np.where(self.V[i] <= 0.0)
			lf0[bad] = np.nan
			lf1[bad] = np.nan

			lmn = np.nanmin(lf0)
			lmx = np.nanmax(lf1)
			if lmn < logvlim[0]:
				logvlim[0] = lmn
			if lmx > logvlim[1]:
				logvlim[1] = lmx

		self._vlim = vlim
		self._logvlim = 10**np.array(logvlim)


		
	def _CalculateScale(self):
		'''
		Calculate the default scale limits for the plot.
		
		'''
		scale = [np.inf,-np.inf]
		logscale = [np.inf,-np.inf]
		
		n = len(self.Spec)
		for i in range(0,n):
			ls = np.log10(self.Spec[i])
			bad = np.where(self.Spec[i] <= 0)
			ls[bad] = np.nan
				
			if self._ScaleType == 'std':
				mu = np.nanmean(self.Spec[i])
				std = np.std(self.Spec[i])
				
				lmu = np.nanmean(ls)
				lstd = np.std(ls)
					
				tmpscale = [mu - self._nStd*std, mu + self._nStd*std]
				tmplogscale = 10**np.array([lmu - self._nStd*lstd, lmu + self._nStd*lstd])					
				
			elif self._ScaleType == 'positive':
				#calculate the scale based on all values being positive 
				std = np.sqrt((1.0/np.sum(self.Spec[i].size))*np.nansum((self.Spec[i])**2))
				lstd = np.sqrt(((1.0/np.sum(np.isfinite(ls))))*np.nansum((ls)**2))
					
				tmpscale = [0.0,std*self._nStd]
				tmplogscale = 10**np.array([np.nanmin(ls),lstd*self._nStd])			
			else:
				#absolute range
				tmpscale = [np.nanmin(self.Spec[i]),np.nanmax(self.Spec[i])]
				tmplogscale = 10**np.array([np.nanmin(ls),np.nanmax(ls)])


			if tmpscale[0] < scale[0]:
				scale[0] = tmpscale[0]
			if tmpscale[1] > scale[1]:
				scale[1] = tmpscale[1]
			
			if tmplogscale[0] < logscale[0]:
				logscale[0] = tmplogscale[0]
			if tmplogscale[1] > logscale[1]:
				logscale[1] = tmplogscale[1]
	
		
		self._scale = scale
		self._logscale = logscale
	
	def _CalculatePSDScale(self):
		'''
		Calculate the default scale limits for the plot.
		
		'''
		scale = [np.inf,-np.inf]
		logscale = [np.inf,-np.inf]
		
		n = len(self.PSD)
		for i in range(0,n):
			ls = np.log10(self.PSD[i])
			bad = np.where(self.PSD[i] <= 0)
			ls[bad] = np.nan
				
			if self._ScaleType == 'std':
				mu = np.nanmean(self.PSD[i])
				std = np.std(self.PSD[i])
				
				lmu = np.nanmean(ls)
				lstd = np.std(ls)
					
				tmpscale = [mu - self._nStd*std, mu + self._nStd*std]
				tmplogscale = 10**np.array([lmu - self._nStd*lstd, lmu + self._nStd*lstd])					
				
			elif self._ScaleType == 'positive':
				#calculate the scale based on all values being positive 
				std = np.sqrt((1.0/np.sum(self.Spec[i].size))*np.nansum((self.PSD[i])**2))
				lstd = np.sqrt(((1.0/np.sum(np.isfinite(ls))))*np.nansum((ls)**2))
					
				tmpscale = [0.0,std*self._nStd]
				tmplogscale = 10**np.array([np.nanmin(ls),lstd*self._nStd])			
			else:
				#absolute range
				tmpscale = [np.nanmin(self.PSD[i]),np.nanmax(self.PSD[i])]
				tmplogscale = 10**np.array([np.nanmin(ls),np.nanmax(ls)])


			if tmpscale[0] < scale[0]:
				scale[0] = tmpscale[0]
			if tmpscale[1] > scale[1]:
				scale[1] = tmpscale[1]
			
			if tmplogscale[0] < logscale[0]:
				logscale[0] = tmplogscale[0]
			if tmplogscale[1] > logscale[1]:
				logscale[1] = tmplogscale[1]
	
		
		self._psdscale = scale
		self._psdlogscale = logscale
