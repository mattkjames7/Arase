import os

#try and find the ARASE_PATH variable - this is where data will be stored
ModulePath = os.path.dirname(__file__)+'/'
try:
	DataPath = os.getenv('ARASE_PATH')+'/'
except:
	print('Please set ARASE_PATH environment variable')
	DataPath = ''
