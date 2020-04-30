import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from .ContUT import ContUT
from .DTPlotLabel import DTPlotLabel

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


class SpecCls(object):
	def __init__(self,Date,ut,Epoch,Freq,Spec,**kwargs):
		#store the input variables
		self.Date = Date
		self.ut = ut
		self.Epoch = Epoch
		self.Freq = Freq
		self.Spec = Spec
		
		#and the keywords
		self.Meta = kwargs.get('Meta',defargs['Meta'])
		dt = kwargs.get('dt',defargs['dt'])
		bw = kwargs.get('bw',defargs['bw'])
		self.xlabel = kwargs.get('xlabel',defargs['xlabel'])
		self.ylabel = kwargs.get('ylabel',defargs['ylabel'])
		self.zlabel = kwargs.get('zlabel',defargs['zlabel'])
		self._ylog = kwargs.get('ylog',defargs['ylog'])
		self._zlog = kwargs.get('zlog',defargs['zlog'])
		self._ScaleType = kwargs.get('ScaleType',defargs['ScaleType'])
		self._nStd = kwargs.get('nStd',defargs['nStd'])
		
		#calculate continuous time axis
		if isinstance(self.ut,list):
			n = len(self.ut)
			self.utc = []
			for i in range(0,n):
				self.utc.append(ContUT(self.Date[i],self.ut[i]))
		else:
			self.utc = ContUT(self.Date,self.ut)
		
		#set the interval between each measurement (assuming ut is start 
		#of interval and that ut + dt is the end
		if dt is None:
			if isinstance(ut,list):
				n = len(ut)
				self.dt = []
				for i in range(0,n):
					dt = (ut[i][1:] - ut[i][:-1])
					u,c = np.unique(dt,return_counts=True)
					self.dt.append(u[np.where(c == c.max())[0][0]])
			else:
				dt = (ut[1:] - ut[:-1])
				u,c = np.unique(dt,return_counts=True)
				self.dt = u[np.where(c == c.max())[0][0]]
		elif np.size(dt) == 1 and not isinstance(dt,list):
			if isinstance(ut,list):
				n = len(ut)
				self.dt = []
				for i in range(0,n):
					self.dt.append(dt)
			else:
				self.dt = dt
		else:
			self.dt = dt
		
		
		#set the bandwidth
		if bw is None:
			#if bandwidth is None, then we must calculate it from the fequencies
			if isinstance(Freq,list):
				n = len(Freq)
				self.bw = []
				for i in range(0,n):
					df = Freq[i][1:] - Freq[i][:-1]
					df = np.concatenate(([df[0]],df,[df[1]]))/2.0
					self.bw.append(df[1:] + df[:-1])
			else:
				df = Freq[1:] - Freq[:-1]
				df = np.concatenate(([df[0]],df,[df[1]]))/2.0
				self.bw = df[1:] + df[:-1]
		elif np.size(bw) == 1 and not isinstance(bw,list):
			if isinstance(self.Freq,list):
				n = len(self.Freq)
				self.bw = []
				for i in range(0,n):
					self.bw.append(np.zeros(self.Freq[i].size,dtype='float32') + bw)
			else:
				self.bw = np.zeros(self.Freq.size,dtype='float32') + bw		
		else:
			self.bw = bw
			
		self._CalculateTimeLimits() 
		self._CalculateFrequencyLimits()
		self._CalculateScale()
		
	def Plot(self,fig=None,maps=[1,1,0,0],ylog=None,scale=None,zlog=None):
		#create the plot
		if fig is None:
			fig = plt
			fig.figure()
		ax = fig.subplot2grid((maps[1],maps[0]),(maps[3],maps[2]))
		
		#set axis limits
		ax.set_xlim(self._utlim)
		if ylog is None:
			ylog = self._ylog
		if ylog:
			ax.set_yscale('log')
			ax.set_ylim(self._logflim)
		else:
			ax.set_ylim(self._flim)
			
		#and labels
		ax.set_xlabel(self.xlabel)
		ax.set_ylabel(self.ylabel)
			
		#get color scale
		if zlog is None:
			zlog = self._zlog
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
		if isinstance(self.Epoch,list):
			n = len(self.Epoch)
			for i in range(0,n):
				tmp = self._PlotSpectrogram(ax,i,scale,norm)
				if i == 0:
					sm = tmp
		else:
			sm = self._PlotSpectrogram(ax,-1,scale,norm)

		#sort the UT axis out
		if isinstance(self.utc,list):
			
			tdate = np.concatenate(self.Date)
			tutc = np.concatenate(self.utc)
			srt = np.argsort(tutc)
			tdate = tdate[srt]
			tutc = tutc[srt]
		else:
			tdate = self.Date
			tutc = self.utc

		DTPlotLabel(ax,tutc,tdate)


		#colorbar
		divider = make_axes_locatable(ax)
		cax = divider.append_axes("right", size="5%", pad=0.05)

		cbar = fig.colorbar(sm,cax=cax) 
		cbar.set_label(self.zlabel)		
		return ax

	def _PlotSpectrogram(self,ax,I,scale,norm):
		'''
		This will plot a single spectrogram (multiple may be stored in
		this object at any one time
		
		'''
		#get the appropriate data
		if I == -1:
			#we just have a single spectrum to worry about
			Date = self.Date
			utc = self.utc
			ut = self.ut
			dt = self.dt
			f = self.Freq
			bw = self.bw
			Spec = self.Spec
		else:
			#select one of the spectra
			Date = self.Date[I]
			utc = self.utc[I]
			ut = self.ut[I]
			if isinstance(self.dt,list):
				dt = self.dt[I]
			else:
				dt = self.dt
			f = self.Freq[I]
			if isinstance(self.bw,list):
				bw = self.bw[I]
			else:
				bw = self.bw
			Spec = self.Spec[I]		
		
		#get the frequency band limits
		bad = np.where(np.isnan(f))
		f[bad] = 0.0
		f0 = f - 0.5*bw
		f1 = f + 0.5*bw

		#get the ut array limits
		if np.size(dt) == 1:
			dt = np.zeros(ut.size,dtype='float32') + dt
		t0 = utc
		t1 = utc + dt
		
		
		#look for gaps in ut
		if len(f.shape) > 1:
			isgap = ((utc[1:] - utc[:-1]) > 1.1*dt[:-1]) | ((f[1:,:] - f[:-1,:]) != 0).any(axis=1)
			nf = f.shape[1]
		else:
			isgap = (utc[1:] - utc[:-1]) > 1.1*dt[:-1]
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
		
		cmap = plt.cm.get_cmap('gnuplot')
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
		
		#check if ut is a list or a single array
		tislist = isinstance(self.utc,list)
		dislist = isinstance(self.dt,list)
		
		#one of three situations should be allowed here:
		#1. both ut and dt are just single arrays
		#2. ut is a list of arrays, sharing one single dt array
		#3. Both ut and dt are lists of arrays
		if not tislist and not dislist:
			#both single arrays
			utlim = [np.nanmin(self.utc),np.nanmax(self.utc + self.dt)]
		elif tislist and not dislist:
			#shared dt array
		
			#loop through each array
			n = len(self.utc)
			for i in range(0,n):
				mn = np.nanmin(self.utc[i])
				mx = np.nanmax(self.utc[i] + self.dt)
				if mn < utlim[0]:
					utlim[0] = mn
				if mx > utlim[1]:
					utlim[1] = mx
		elif tislist and dislist:
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
		
		#check if ut is a list or a single array
		fislist = isinstance(self.Freq,list)
		bislist = isinstance(self.bw,list)
		
		#one of three situations should be allowed here:
		#1. both F and bw are just single arrays
		#2. F is a list of arrays, sharing one single bw array
		#3. Both F and bw are lists of arrays
		if not fislist and not bislist:
			#both single arrays
			f0 = self.Freq - self.bw/2.0
			f1 = self.Freq + self.bw/2.0
			
			flim = [np.nanmin(f0),np.nanmax(f1)]
			lf0 = np.log10(f0)
			lf1 = np.log10(f1)
			bad = np.where(self.Freq <= 0.0)
			lf0[bad] = np.nan
			lf1[bad] = np.nan
			
			logflim = 10**np.array([np.nanmin(lf0),np.nanmax(lf1)])
			
			
		elif fislist and not bislist:
			#shared bw array

					
			#loop through each array
			n = len(self.Freq)
			for i in range(0,n):
				f0 = self.Freq[i] - self.bw/2.0
				f1 = self.Freq[i] + self.bw/2.0
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

		elif fislist and bislist:
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
		self._logflim = logflim
		
	def _CalculateScale(self):
		'''
		Calculate the default scale limits for the plot.
		
		'''
		scale = [np.inf,-np.inf]
		logscale = [np.inf,-np.inf]
		
		if isinstance(self.Spec,list):
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
		else:
			ls = np.log10(self.Spec)
			bad = np.where(self.Spec <= 0)
			ls[bad] = np.nan
			if self._ScaleType == 'std':
				#calculate the default limits using the standard deviation
				mu = np.nanmean(self.Spec)
				std = np.std(self.Spec)
				
				lmu = np.nanmean(ls)
				lstd = np.std(ls)
				
				scale = [mu - self._nStd*std, mu + self._nStd*std]
				logscale = 10**np.array([lmu - self._nStd*lstd, lmu + self._nStd*lstd])
			elif self._ScaleType == 'positive':
				#calculate the scale based on all values being positive 
				std = np.sqrt((1.0/np.sum(self.Spec.size))*np.nansum((self.Spec)**2))
				lstd = np.sqrt(((1.0/np.sum(np.isfinite(ls))))*np.nansum((ls)**2))
				
				scale = [0.0,std*self._nStd]
				logscale = 10**np.array([np.nanmin(ls),lstd*self._nStd])
				
			else:
				#absolute range
				scale = [np.nanmin(self.Spec),np.nanmax(self.Spec)]
				logscale = 10**np.array([np.nanmin(ls),np.nanmax(ls)])
		
		self._scale = scale
		self._logscale = logscale
