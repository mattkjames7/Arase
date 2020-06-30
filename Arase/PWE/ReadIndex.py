import numpy as np
from ..Tools.Downloading._ReadDataIndex import _ReadDataIndex
from .. import Globals

def ReadIndex(subcomp,L,prod):
	'''
	
	'''
	if subcomp == 'hfa' and L == 3:
		idxfname = Globals.DataPath + 'PWE/Index-L{:01d}-{:s}.dat'.format(L,subcomp)
		datapath = Globals.DataPath + 'PWE/{:s}/L{:01d}/'.format(subcomp,L)
	else:	
		idxfname = Globals.DataPath + 'PWE/Index-L{:01d}-{:s}-{:s}.dat'.format(L,subcomp,prod)
		datapath = Globals.DataPath + 'PWE/{:s}/L{:01d}/{:s}/'.format(subcomp,L,prod)
	
	return _ReadDataIndex(idxfname)
