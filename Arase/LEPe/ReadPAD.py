import numpy as np
from ..Tools.ReadPAD import ReadPAD as RPAD
from .. import Globals

def ReadPAD(Date,SpecType):
	'''
	Date : int
		Date to download data for in format yyyymmdd
		If single date - only data from that one day will be fetched
		If 2-element array - dates from Date[0] to Date[1] will be downloaded
		If > 2 elements - this is treated as a specific list of dates to download
	SpecType : str
		'eFlux'
	
	'''

	path = Globals.DataPath + 'LEPe/PAD/'
	
	return RPAD(Date,path,SpecType)
