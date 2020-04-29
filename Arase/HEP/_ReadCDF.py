import numpy as np
import os
from .. import Globals
from ..Tools.Downloading._ReadDataIndex import _ReadDataIndex
from ..Tools.ReadCDF import ReadCDF

def _ReadCDF(Date,L,prod):
	'''
	Reads the CDF file containing the position of Arase.
	
	
	
	'''
	
	idxfname = Globals.DataPath + 'HEP/Index-L{:01d}-{:s}.dat'.format(L,prod)
	datapath = Globals.DataPath + 'HEP/l{:01d}/{:s}/'.format(L,prod)
	
	#read the data index
	idx = _ReadDataIndex(idxfname)

	#check the index for the appropriate date
	use = np.where(idx.Date == Date)[0]
	if use.size == 0:
		print('Date not found, run Arase.Pos.DownloadData() to check for updates.')
		return None
	idx = idx[use]
	mx = np.where(idx.Version  == np.max(idx.Version))[0]
	mx = mx[0]
	
	#get the file name
	fname = idx[mx].FileName
	
	#path
	fname = datapath + fname
	
	#check file exists
	if not os.path.isfile(fname):
		print('Index is broken: Update the data index')
		return None
		
	#read the file
	return ReadCDF(fname)
