import os 
from .. import Globals
import PyFileIO as pf

def _UpdateDataIndex(idx,subcomp,L,prod):
	'''
	Updates the data index file.
	
	Input:
		idx: numpy.recarray containing the file names.
	'''
	
	fname = Globals.DataPath+'PWE/Index-L{:01d}-{:s}-{:s}.dat'.format(L,subcomp,prod)
	pf.WriteASCIIData(fname,idx)
