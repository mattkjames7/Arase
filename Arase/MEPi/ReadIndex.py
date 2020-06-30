import numpy as np
from ..Tools.Downloading._ReadDataIndex import _ReadDataIndex
from .. import Globals

def ReadIndex(L,prod):
	'''
	
	'''
	idxfname = Globals.DataPath + 'MEPi/Index-L{:01d}-{:s}.dat'.format(L,prod)
	return _ReadDataIndex(idxfname)
