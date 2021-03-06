import numpy as np
import matplotlib.pyplot as plt
from .. import LEPi,MEPi
from ..Tools.PlotLabel import PlotLabel

def StackPlot(Date,ut=[0.0,24.0],Instruments=['MEPi','LEPi'],Species='H+',
	figsize=(8,6),yparam='E',zparam='Flux',scale=None,TickFreq='auto',PosAxis=True):
	'''
	Plot electron data with each intrument on a separate panel.
	
	Inputs
	======
	Date : int
		Date(s) to load/plot
	ut : float
		2-element list contining the start and end times in hours from
		the beginning of the day.
	Instruments : str
		List of instrument strings to plot.
		default: ['MEPi','LEPi']
	Species : str
		Species to plot: 'H+'|'He+'|'O+'
	figsize : tuple
		2-element tuple containing the size of the figure to be created
	PSD : bool
		If True, phase space density is plotted as opposed to differential
		energy flux.
	scale : list
		2-element list - use this to set the limits of the colour scale.
	
	
	'''

	#load the data
	Ldata = {}
	Mdata = {}

	if 'LEPi' in Instruments:
		Ldata = LEPi.ReadOmni(Date)
	if 'MEPi' in Instruments:
		Mdata = MEPi.ReadOmni(Date)


	#count the number of plots, load data objects into a list
	datamap = { 'LEPi' : Ldata.get(Species+'Flux',None),
				'MEPi' : Mdata.get(Species+'Flux',None)}
	keys = list(datamap.keys())
	data = []
	labels = []
	n = 0
	for I in Instruments:
		if I in keys:
			d = datamap[I]
			if not d is None:
				data.append(d)
				labels.append(I)
				n += 1
			
	
	
	#create the figure
	fig = plt.figure(figsize=figsize)
	ax = []
	
	#plot each one
	for i in range(0,n):
		if i == n-1:
			nox = False
		else:
			nox = True
		a = data[i].Plot(Date,ut=ut,fig=plt,maps=[1,n,0,i],nox=nox,yparam=yparam,zparam=zparam,scale=scale,TickFreq=TickFreq,PosAxis=PosAxis)
		ax.append(a)
		
	#remove space 
	plt.tight_layout()
	plt.subplots_adjust(hspace = 0.02)
	
	#add plot labels
	let = ['(a)','(b)','(c)','(d)','(e)']
	for i in range(0,n):
		PlotLabel(ax[i],let[i]+' '+labels[i],x=0.02,y=0.9,ha='left')
		

	return fig,data
