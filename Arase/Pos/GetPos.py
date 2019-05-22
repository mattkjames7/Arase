from .. import Globals
import RecarrayTools as RT

def GetPos():
	'''
	Reads the binary files containing positional information about RBSP.

	Input:
		sc: 'a' or 'b'
		
	Returns:
		numpy.recarray
	'''
		
	if Globals.Pos is None:
		fname = Globals.DataPath+'Pos/pos.bin'
		Globals.Pos = RT.ReadRecarray(fname,Globals.PosDtype)
		
	return Globals.Pos
