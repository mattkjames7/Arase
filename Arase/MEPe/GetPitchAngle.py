import numpy as np
from .Read3D import Read3D
from ..MGF.ReadMGF import ReadMGF
from ..Tools.CDFEpochToUT import CDFEpochToUT
from scipy.interpolate import interp1d
from scipy.ndimage import uniform_filter
from ..Tools.CalculatePitchAngles import CalculatePitchAngles
from ..MGF.InterpObj import InterpObj


# Field			Description				Dimension
# ------------------------------------------------------
# epoch			Time					nt
# FEDU_Energy		Centre of energy bin	ne = 16
# FEDU_APDno		APD detector index		na = 16
# FEDU_Sector		Spin sector number		ns = 32
# FEDU			Diff number flux		(nt,ns,ne,ns)
# FEEDU			Diff energy flux		(nt,ns,ne,ns)
# FEDU_Angle_gse	Direction of FEDU (GSE)	(nt,2(elevation,azimuth),na,ns)
# FEDU_alpha		Pitch angle				(nt,ns,ne,na)



def GetPitchAngle(Date):
	'''
	Recreating the pitch angles seems to be a little dodgy.
	'''
	
	#read in the 3dflux level 2 data
	data2,meta2 = Read3D(Date,2)
	#read in the 3dflux level 3 data
	#data3,meta3 = Read3D(Date,3)
	
	#get the elevation/angle data
	angles = data2['FEDU_Angle_gse']*np.pi/180.0
	
	#get the time and date
	date,time = CDFEpochToUT(data2['epoch'])
		
	#call the function to retrieve pitch angles
	alpha = CalculatePitchAngles(date,time,angles,None)

	#get the original, average over the energy bin directions
	#alpha0 = data3['FEDU_alpha']
	#alpha0 = np.nanmean(alpha0,axis=2)
	
	#transpose the new alpha such that the dimensions are in the same
	#order as the  original
	alpha = np.transpose(alpha,(0,2,1))
	
	
	return alpha#,alpha0
