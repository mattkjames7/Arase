import numpy as np
import os
import PyFileIO as pf

def ReadMirrorAlt(Date,path):
	'''
	Read a PAD file
	
	'''	
	#get the file name
	fname = path + '{:08d}/'.format(Date) + 'Mirror.bin'

	#check it exists
	if not os.path.isfile(fname):
		print('File not found')
		return None
		
	#read the data
	f = open(fname,'rb')
	out = {}
	out['AltN'] = pf.ArrayFromFile('float32',f)
	out['AltS'] = pf.ArrayFromFile('float32',f)
	out['Bm'] = pf.ArrayFromFile('float32',f)
	out['B0'] = pf.ArrayFromFile('float32',f)

	f.close()
	return out
