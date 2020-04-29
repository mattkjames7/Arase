from .. import Globals
import numpy as np
from ..Tools.Downloading._DownloadData import _DownloadData


def DownloadData(L,prod,StartYear=2016,EndYear=2019,Overwrite=False):
	'''
	Downloads Arase MGF data.

		Year: integer year.
	
	'''

	url0 = 'https://ergsc.isee.nagoya-u.ac.jp/data/ergsc/satellite/erg/xep/l{:01d}/{:s}/'.format(L,prod) + '{:04d}/{:02d}/'
	vfmt = ['v','_']
	idxfname = Globals.DataPath + 'XEP/Index-L{:01d}-{:s}.dat'.format(L,prod)
	datapath = Globals.DataPath + 'XEP/l{:01d}/{:s}/'.format(L,prod)
	
	_DownloadData(url0,idxfname,datapath,StartYear,EndYear,vfmt,Overwrite)

