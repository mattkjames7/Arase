import numpy as np
from .Read3D import Read3D
from ..MGF.ReadMGF import ReadMGF
from ..Tools.CDFEpochToUT import CDFEpochToUT
from scipy.interpolate import interp1d
from scipy.ndimage import uniform_filter
from ..Tools.CalculatePitchAngles import CalculatePitchAngles
from ..MGF.InterpObj import InterpObj


def GetPitchAngle(Date,data=None):
	'''
	Recreating the pitch angles seems to be a little dodgy.
	'''
	
	#read in the 3dflux level 2 data
	if data is None:
		data,meta = Read3D(Date)
	
	#get the elevation/angle data
	angles = data['FEDU_Angle_GSE']*np.pi/180.0
	
	#get the time and date
	date,time = CDFEpochToUT(data['Epoch'])
		
	#call the function to retrieve pitch angles
	alpha = CalculatePitchAngles(date,time,angles,None)

	return alpha
