import os 
from .. import Globals
import PyFileIO as pf

def _UpdateDataIndex(idx,L):
	'''
	Updates the data index file.
	
	Input:
		idx: numpy.recarray containing the file names.
	'''
	
	fname = Globals.DataPath+'Pos/PosIndex-L{:01d}.dat'.format(L)
	pf.WriteASCIIData(fname,idx)
