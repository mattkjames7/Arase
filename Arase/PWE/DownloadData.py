from .. import Globals
import numpy as np
import DateTimeTools as TT
from ._GetCDFURL import _GetCDFURL
import os
import re
from ._ReadDataIndex import _ReadDataIndex
from ._UpdateDataIndex import _UpdateDataIndex
import RecarrayTools as RT

def DownloadData(subcomp,L,prod,StartYear=2016,EndYear=2019,Overwrite=False):
	'''
	Downloads Arase PWE data.

		Year: integer year.
		L: 2 or 3 integer
	
	'''
	#populate the list of dates to trace first
	yy = np.arange(StartYear,EndYear+1)
	mm = np.arange(12)
	n = yy.size*mm.size
	Years = np.zeros(n,dtype='int32')
	Months = np.arange(n,dtype='int32') % 12 + 1
	for i in range(0,yy.size):
		Years[i*12:(i+1)*12] = yy[i]
	
	#create output path if it doesn't exist
	outpath = Globals.DataPath+'PWE/{:s}/L{:01d}/{:s}/'.format(subcomp,L,prod)
	if not os.path.isdir(outpath):
		os.system('mkdir -pv '+outpath)
		
	if subcomp == 'wfc':
		#in this case we just download all of the text files
		urls,fnames = _GetCDFURL(0,0,subcomp,L,prod)
		nu = np.size(urls)
		for i in range(0,nu):
			os.system('wget '+urls[j]+' -O '+outpath+fnames[j])
		return 
		
	#loop through each remaining date and start downloading
	dp = re.compile('\d\d\d\d\d\d\d\d')
	vp = re.compile('v\d\d_\d\d')
	for i in range(0,n):
		print('Year {0}'.format(Years[i]))
		urls,fnames = _GetCDFURL(Years[i],Months[i],subcomp,L,prod)
		nu = np.size(urls)
		
		if nu > 0:
			idx = _ReadDataIndex(subcomp,L,prod)
			new_idx = np.recarray(nu,dtype=idx.dtype)
			new_idx.Date[:] = -1
			p = 0
			for j in range(0,nu):
				print('Downloading file {0} of {1} ({2})'.format(j+1,nu,fnames[j]))
				Date = np.int32(dp.search(fnames[j]).group())
				Ver	= np.int32((vp.search(fnames[j]).group()[1:]).replace('v','').replace('_',''))
				
				match = ((idx.Date == Date) & (idx.Version == Ver)).any()
				
				if (not match) or Overwrite:
					if not os.path.isfile(outpath+fnames[j]) or Overwrite:
						os.system('wget '+urls[j]+' -O '+outpath+fnames[j])

					new_idx.Date[p] = Date
					new_idx.FileName[p] = fnames[j]
					new_idx.Version[p] = Ver
					p+=1
					
			new_idx = new_idx[:p]
			
			#check for duplicates within new_idx (different versions)
			use = np.ones(p,dtype='bool')
			for j in range(0,p):
				match = np.where(new_idx.Date == new_idx.Date[j])[0]
				if match.size > 1:
					#compare versions
					mxVer = np.max(new_idx.Version[match])
					lose = np.where(new_idx.Version[match] != mxVer)[0]
					use[match[lose]] = False
			use = np.where(use)[0]
			new_idx = new_idx[use]
			p = new_idx.size
			
			#check for duplicates within old index
			usen = np.ones(p,dtype='bool')
			useo = np.ones(idx.size,dtype='bool')
				
			for j in range(0,p):
				match = np.where(idx.Date == new_idx.Date[j])[0]
				if match.size > 0:
					if idx.Version[match[0]] > new_idx.Version[j]:
						#old one is newer (unlikely)
						usen[j] = False
					else:
						#new one is newer
						useo[match[0]] = False

			usen = np.where(usen)[0]
			new_idx = new_idx[usen]
			useo = np.where(useo)[0]
			idx = idx[useo]					
			
			#join indices together and update file
			idx_out = RT.JoinRecarray(idx,new_idx)
			srt = np.argsort(idx_out.Date)
			idx_out = idx_out[srt]
			_UpdateDataIndex(idx_out,subcomp,L,prod)
			
			
