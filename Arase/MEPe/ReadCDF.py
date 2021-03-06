import numpy as np
import os
from .. import Globals
from ..Tools.Downloading._ReadDataIndex import _ReadDataIndex
from ..Tools.ReadCDF import ReadCDF as RCDF

def ReadCDF(Date,L,prod):
	'''
	Reads the CDF file containing Arase MEPe data.

	Inputs
	======
	Date : int
		Integer date in the format yyyymmdd
	L : int
		Level of data to download
	prod : str
		Data product to download


	Available data products
	=======================
	L		prod
	2		'omniflux'
	2		'3dflux'
	3		'3dflux'
	
	Returns
	=======
	data : dict
		Dictionary containing the data for each variable stored within 
		the CDF file.
	meta : dict
		Dictionary containing the metadata for each variable in the data
		dictionary.
		
	'''
	
	idxfname = Globals.DataPath + 'MEPe/Index-L{:01d}-{:s}.dat'.format(L,prod)
	datapath = Globals.DataPath + 'MEPe/l{:01d}/{:s}/'.format(L,prod)
	
	#read the data index
	idx = _ReadDataIndex(idxfname)

	#check the index for the appropriate date
	use = np.where(idx.Date == Date)[0]
	if use.size == 0:
		print('Date not found, run Arase.Pos.DownloadData() to check for updates.')
		return None,None
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
		return None,None
		
	#read the file
	return RCDF(fname)
