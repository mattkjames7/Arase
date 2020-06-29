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
	
	#get the mag data interp objects
	mag = InterpObj(Date,Smooth=8)
	
	#get the elevation/angle data
	anglesl = data2['FEDU_L_Angle_gse']*np.pi/180.0
	anglesh = data2['FEDU_H_Angle_gse']*np.pi/180.0
	
	#get the time and date
	datel,timel = CDFEpochToUT(data2['Epoch_L'])
	dateh,timeh = CDFEpochToUT(data2['Epoch_H'])
		
	#call the function to retrieve pitch angles
	alphal = CalculatePitchAngles(datel,timel,anglesl,mag)
	alphah = CalculatePitchAngles(dateh,timeh,anglesh,mag)

	return alphal,alphah
