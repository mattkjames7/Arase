from .. import Globals
import numpy as np
import PyFileIO as pf
import os

def _ReadDataIndex(L):
	'''
	Reads index file containing a list of all of the dates with their
	associated data file name (so that we can pick the version 
	automatically).
	'''
	#define the dtype
	dtype = [('Date','int32'),('FileName','object'),('Version','int8')]
	
	#find the file
	fname = Globals.DataPath+'Pos/PosIndex-L{:01d}.dat'.format(L)
	
	#check it exists
	if not os.path.isfile(fname):
		return np.recarray(0,dtype=dtype)
		
	#read the index file
	data = pf.ReadASCIIData(fname,True,dtype=dtype)
	
	return data
