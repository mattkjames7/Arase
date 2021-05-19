import numpy as np
import os
import PyFileIO as pf

def SaveMirrorAlt(Date,path,AltN,AltS,Bm,B0,Overwrite=False):
	'''
	Save mirror altitudes and fields to go with the pitch angle 
	distribution data
	
	'''
	#create the output path
	outpath = path + '{:08d}/'.format(Date)
	if not os.path.isdir(outpath):
		os.system('mkdir -pv '+outpath)
		os.system('chmod 777 '+outpath)

	
	#loop through and save each one
	fname = outpath + 'Mirror.bin'
	if os.path.isfile(fname) and not Overwrite:
		return
	print('saving file: {:s}'.format(fname))
	f = open(fname,'wb')
	pf.ArrayToFile(AltN,'float32',f)
	pf.ArrayToFile(AltS,'float32',f)
	pf.ArrayToFile(Bm,'float32',f)
	pf.ArrayToFile(B0,'float32',f)

	f.close()

	#change permissions
	os.system('chmod 666 '+fname)
