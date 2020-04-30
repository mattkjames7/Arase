from .. import Globals
import numpy as np
from ..Tools.Downloading._DownloadData import _DownloadData

def DownloadData(subcomp,L,prod='',StartYear=2016,EndYear=2019,Overwrite=False):
	'''
	Downloads Arase PWE data.

	Inputs
	======
	subcomp : string
		Name of sub component of instrument: 'efd'|'hfa'|'ofa'
	L : int
		Level of data (2 or 3)
	prod : 
		Data product (depends on L and subcomp)
			efd	2	'E_spin'|'pot'|'spec'
			hfa	2	'high'|'low'|'monit'
			hfa	3	'' (no product needed)
			ofa	2	'complex'|'matrix'|'spec'
		
	
	'''

	url0 = 'https://ergsc.isee.nagoya-u.ac.jp/data/ergsc/satellite/erg/pwe/{:s}/l{:01d}/'.format(subcomp,L)

	if subcomp == 'hfa' and L == 2:
		url0 += 'spec/{:s}/'.format(prod)
	elif subcomp == 'hfa' and L == 3:
		pass
	elif subcomp == 'ofa' or subcomp == 'efd':
		url0 += '{:s}/'.format(prod)
	url0 += '{:04d}/{:02d}/'

	vfmt = ['v','_']

	if subcomp == 'hfa' and L == 3:
		idxfname = Globals.DataPath + 'PWE/Index-L{:01d}-{:s}.dat'.format(L,subcomp)
		datapath = Globals.DataPath + 'PWE/{:s}/L{:01d}/'.format(subcomp,L)
	else:	
		idxfname = Globals.DataPath + 'PWE/Index-L{:01d}-{:s}-{:s}.dat'.format(L,subcomp,prod)
		datapath = Globals.DataPath + 'PWE/{:s}/L{:01d}/{:s}/'.format(subcomp,L,prod)
		

	_DownloadData(url0,idxfname,datapath,StartYear,EndYear,vfmt,Overwrite)

			
