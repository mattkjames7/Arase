import numpy as np
from .Read3D import Read3D
from ..MGF.ReadMGF import ReadMGF
from scipy.interpolate import interp1d
from scipy.ndimage import uniform_filter
from ..Tools.CalculatePitchAngles import CalculatePitchAngles
from ..MGF.InterpObj import InterpObj
import DateTimeTools as TT

def GetPitchAngle(Date,data=None):
	'''
	Attempt to calculate the pitch angle for each element of the 3D
	fluxes. This should be contained in the level 3 3dflux data, but is 
	not available for all instruments yet (at least not publicly). 
	
	WARNING: These pitch angles may not line up exactly with level 3 ones,
	use with caution (they are usually within ~1 or 2 degrees).
	
	Inputs
	======
	Date : int32
		Date to calcualte pitch angles for
	data : None or dict
		If None, data will be loaded automatically, if data are already 
		in memory it would be quicker to set this keyword to save 
		reloading.
	
	Returns
	=======
	Array(s) of pitch angles

	'''
	
	#read in the 3dflux level 2 data
	if data is None:
		data,meta = Read3D(Date)
	
	#get the mag data interp objects
	mag = InterpObj(Date,Smooth=8)
	
	#get the elevation/angle data
	anglesl = data['FEDU_L_Angle_gse']*np.pi/180.0
	anglesh = data['FEDU_H_Angle_gse']*np.pi/180.0
	
	#get the time and date
	datel,timel = TT.CDFEpochtoDate(data['Epoch_L'])
	dateh,timeh = TT.CDFEpochtoDate(data['Epoch_H'])
		
	#call the function to retrieve pitch angles
	alphal = CalculatePitchAngles(datel,timel,anglesl,mag)
	alphah = CalculatePitchAngles(dateh,timeh,anglesh,mag)

	return alphal,alphah
