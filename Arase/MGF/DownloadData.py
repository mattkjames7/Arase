from .. import Globals
import numpy as np
from ..Tools.Downloading._DownloadData import _DownloadData

def DownloadData(L,prod,StartYear=2016,EndYear=2019,Overwrite=False):
	'''
	Downloads Arase MGF data. This routine will look for newer versions
	of existing data too.

	Inputs
	======
	L : int
		Level of data to download
	prod : str
		Data product to download
	StartYear : int
		Year to start search for new data
	EndYear : int
		Last year to search for data
	Overwrite : bool
		Overwrites existing data if True
		
		
	Available data products
	=======================
	L		prod
	2		'8sec'
	
	'''

	url0 = 'https://ergsc.isee.nagoya-u.ac.jp/data/ergsc/satellite/erg/mgf/l{:01d}/{:s}/'.format(L,prod) + '{:04d}/{:02d}/'
	vfmt = ['v','.']
	idxfname = Globals.DataPath + 'MGF/Index-L{:01d}-{:s}.dat'.format(L,prod)
	datapath = Globals.DataPath + 'MGF/l{:01d}/{:s}/'.format(L,prod)
	
	_DownloadData(url0,idxfname,datapath,StartYear,EndYear,vfmt,Overwrite)
