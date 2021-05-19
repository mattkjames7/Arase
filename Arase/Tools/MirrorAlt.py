import numpy as np
from scipy.interpolate import interp1d

def _Gradient(x,y):
	
	dydx = (y[1:] - y[:-1])/(x[:1] - x[:-1])
	return dydx

def  _TraceAlt(S,R,B,z,Bm):
	Re = 6378.0
	
	#calculate the indices for northern and southern bits of the field line
	dRdS = _Gradient(S,R)
	zc = 0.5*(z[1:] + z[:-1])
	
	#north
	indn = np.where((dRdS < 0) & (zc > 0))[0]
	if indn.size > 0:
		indn = indn[-1]
		fn = interp1d(B[:indn][::-1],R[:indn][::-1],bounds_error=False,fill_value=np.nan)
		Rn = fn(Bm)
	else:
		Rn = np.zeros(Bm.size,dtype='float32') + np.nan
	
	
	
	inds = np.where((dRdS > 0) & (zc < 0))[0]
	if inds.size > 0:
		inds = inds[0]
		fs = interp1d(B[inds:],R[inds:],bounds_error=False,fill_value=np.nan)
		Rs = fs(Bm)
	else:
		Rs = np.zeros(Bm.size,dtype='float32') + np.nan

	#convert to altitude in km
	An = (Rn - 1.0)*Re
	As = (Rs - 1.0)*Re
	
	return An,As

def MirrorAlt(T,Bm):
	'''
	Calculate the mirror altitude in km for a bunch of traces.
	
	'''
	AltN = np.zeros(Bm.shape,dtype='float32') + np.nan
	AltS = np.zeros(Bm.shape,dtype='float32') + np.nan
	
	#loop through one trace at a time
	nT = T.n
	print('Calculating Mirror Altitudes')
	for i in range(0,nT):
		print('\rTrace {0} of {1}'.format(i+1,nT),end='')
		B = np.sqrt(T.Bx[i]**2 + T.By[i]**2 + T.Bz[i]**2)[:np.int32(T.nstep[i])]
		S = T.s[i][:np.int32(T.nstep[i])]
		R = T.R[i][:np.int32(T.nstep[i])]
		z = T.z[i][:np.int32(T.nstep[i])]
		AltN[i],AltS[i] = _TraceAlt(S,R,B,z,Bm[i])
	print()
		
	return AltN,AltS
	
	
