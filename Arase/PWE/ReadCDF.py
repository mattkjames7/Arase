import numpy as np
import os
import pysatCDF
from .. import Globals
from ._ReadDataIndex import _ReadDataIndex

def ReadCDF(Date,subcomp,L,prod,ReturnCDF=False):
	'''
	Reads the CDF file containing the position of Arase.
	
	
	
	'''
	#read the data index
	idx = _ReadDataIndex(subcomp,L,prod)

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
	fpath = Globals.DataPath+'PWE/{:s}/L{:01d}/{:s}/'.format(subcomp,L,prod)
	fname = fpath + fname
	
	#check file exists
	if not os.path.isfile(fname):
		print('Index is broken: Update the data index')
		return None
		
	#read the file
	try:
		print(fname)
		cdf = pysatCDF.CDF(fname)
		if ReturnCDF:
			return cdf
		else:
			data = cdf.data
			meta = cdf.meta
			return data,meta
	except:
		print('Reading CDF file failed')
		return None
	
