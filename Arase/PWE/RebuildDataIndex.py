import numpy as np
from .. import Globals
from ..Tools.Downloading._RebuildDataIndex import _RebuildDataIndex


def RebuildDataIndex(subcomp,L,prod):
	
	vfmt = ['v','_']

	if subcomp == 'hfa' and L == 3:
		idxfname = Globals.DataPath + 'PWE/Index-L{:01d}-{:s}.dat'.format(L,subcomp)
		datapath = Globals.DataPath + 'PWE/{:s}/L{:01d}/'.format(subcomp,L)
	else:	
		idxfname = Globals.DataPath + 'PWE/Index-L{:01d}-{:s}-{:s}.dat'.format(L,subcomp,prod)
		datapath = Globals.DataPath + 'PWE/{:s}/L{:01d}/{:s}/'.format(subcomp,L,prod)
		
	_RebuildDataIndex(datapath,idxfname,vfmt)
