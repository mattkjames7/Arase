from .. import Globals 
import time
import os
import numpy as np

def _GetCDFURL(Date,L):
	'''
	Retrieves the url(s) of the cdf file to be downloaded.
	
	Inputs:
		Date: 32-bit integer date with format yyyymmdd.
		L: Level of the data 2 or 3 (integer)
		
	Returns:
		urls,fnames
	'''
	#first let's get the url which will contain the link to the cdf file
	yy = Date // 10000
	mm = (Date % 10000) // 100
	dd = Date % 100
	
	urls = ['https://ergsc.isee.nagoya-u.ac.jp/data/ergsc/satellite/erg/orb/def/{:04d}/'.format(yy),
			'https://ergsc.isee.nagoya-u.ac.jp/data/ergsc/satellite/erg/orb/l3/2016/tmp/',
			'https://ergsc.isee.nagoya-u.ac.jp/data/ergsc/satellite/erg/orb/l3/{:04d}/'.format(yy)]
			
	if L == 2:
		url = urls[0]
	elif L == 3 and yy == 2016:
		url = urls[1]
	else:
		url = urls[2]
	
	#set up a temporary file/path 
	tmppath = Globals.DataPath+'tmp/'
	if not os.path.isdir(tmppath):
		os.system('mkdir -pv '+tmppath)
	tmpfname = tmppath + '{:17.7f}.tmp'.format(time.time())
	
	#wget the file
	os.system('wget '+url+' -O '+tmpfname)
	
	#read it
	f = open(tmpfname,'r')
	lines = f.readlines()
	n = np.size(lines)
	f.close()
	#delete it
	#os.system('rm -v '+tmpfname)
	
	
	#now search for the line with the substring '.cdf"'
	datestr = '{:08d}'.format(Date)
	urls = []
	fnames = []
	for i in range(0,n):
		if '.cdf"' in lines[i] and datestr in lines[i]:
			s = lines[i].replace('<a','"').replace('</a>','"').replace('>','"').split('"')
			for ss in s:
				if '.cdf' in ss and not 'http' in ss:
					urls.append(url+ss)
					fnames.append(ss)
					break
					
	return urls,fnames
	
