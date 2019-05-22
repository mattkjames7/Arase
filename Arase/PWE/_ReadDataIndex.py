from .. import Globals
import numpy as np
import PyFileIO as pf
import os

def _ReadDataIndex(subcomp,L,prod):
	'''
	Reads index file containing a list of all of the dates with their
	associated data file name (so that we can pick the version 
	automatically).
	'''
	#define the dtype
	dtype = [('Date','int32'),('FileName','object'),('Version','int16')]
	
	#find the file
	fname = Globals.DataPath+'PWE/Index-L{:01d}-{:s}-{:s}.dat'.format(L,subcomp,prod)
	
	#check it exists
	if not os.path.isfile(fname):
		return np.recarray(0,dtype=dtype)
		
	#read the index file
	try:
		data = pf.ReadASCIIData(fname,True,dtype=dtype)
	except:
		return np.recarray(0,dtype=dtype)
		
	return data
