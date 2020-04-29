import numpy as np
from .. import Globals
from ..Tools.Downloading._RebuildDataIndex import _RebuildDataIndex


def RebuildDataIndex(L,prod):
	
	vfmt = ['v','.']
	idxfname = Globals.DataPath + 'MGF/Index-L{:01d}-{:s}.dat'.format(L,prod)
	datapath = Globals.DataPath + 'MGF/l{:01d}/{:s}/'.format(L,prod)
	
	_RebuildDataIndex(datapath,idxfname,vfmt)
