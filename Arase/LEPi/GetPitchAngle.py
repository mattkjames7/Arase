import numpy as np
from .Read3D import Read3D
from ..MGF.ReadMGF import ReadMGF
from ..Tools.CDFEpochToUT import CDFEpochToUT
from scipy.interpolate import interp1d
from scipy.ndimage import uniform_filter
from ..Tools.CalculatePitchAngles import CalculatePitchAngles
from ..MGF.InterpObj import InterpObj


def GetPitchAngle(Date):
	'''
	Recreating the pitch angles seems to be a little dodgy.
	'''
	
	#read in the 3dflux level 2 data
	data2,meta2 = Read3D(Date)
	
	#get the elevation/angle data
	angles = data2['FIDU_Angle_gse']*np.pi/180.0
	
	#get the time and date
	date,time = CDFEpochToUT(data2['Epoch'])
		
	#call the function to retrieve pitch angles
	alpha = CalculatePitchAngles(date,time,angles,None)

	return alpha#,alpha0
