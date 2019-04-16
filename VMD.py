import numpy as np 
from functools import reduce 
import struct

class VMDReader():
	def __init__(self, fname):
		f = open(fname , 'rb')
		array = bytes(reduce(lambda x,y:x+y, list(f)))
		versioninfo = array[:30].decode('ascii')
		print(versioninfo)
		# modelname = array[30:50].decode('shift-JIS')
		# print(modelname)
		keyframe_num = struct.unpack("<I", array[50: 54])[0]
		print(keyframe_num)

		current_index = 54

		bone_record = []
		for i in range(keyframe_num):
			buff = {}
			buff['BoneName'] = array[current_index: current_index+15].split(bytes([0]))[0].decode('shift-JIS')
			# print(buff['BoneName'])
			buff['BoneName_byte'] = array[current_index: current_index+15]
			buff['FrameTime'] = struct.unpack("<I", array[current_index+15: current_index+19])[0]
			buff['Position'] = {'x': struct.unpack("<f", array[current_index+19: current_index+23])[0],
							'y': struct.unpack("<f", array[current_index+23: current_index+27])[0],
							'z': struct.unpack("<f", array[current_index+27: current_index+31])[0]}
			buff['Rotation'] = {"x": struct.unpack("<f", array[current_index+31: current_index+35])[0],
								"y": struct.unpack("<f", array[current_index+35: current_index+39])[0],
								"z": struct.unpack("<f", array[current_index+39: current_index+43])[0],
								"w": struct.unpack("<f", array[current_index+43: current_index+47])[0]}

			buff['Curve'] = {"x":(array[current_index+47], array[current_index+51], array[current_index+55], array[current_index+59]),
							"y":(array[current_index+63], array[current_index+67], array[current_index+71], array[current_index+75]),
							"z":(array[current_index+79], array[current_index+83], array[current_index+87], array[current_index+91]),
							"r":(array[current_index+95], array[current_index+99], array[current_index+103], array[current_index+107])}

			bone_record.append(buff)
			current_index += 111

		self.bone_record = bone_record
		self.version_byte = array[:30]
		self.model_name_byte = array[30:50]
		self.postfix = array[current_index:]

def get_curve(c):
	res = bytearray()
	x = c['x']
	y = c['y']
	z = c['z']
	r = c['r']
	for item in [x,y,z,r]:
		for i in range(4):
			res += struct.pack('<I', item[i])
	return res 

def get_rotation(r):
	res = bytearray()
	x = r['x']
	y = r['y']
	z = r['z']
	w = r['w']
	for i in [x,y,z,w]:
		res += struct.pack('<f', i)
	return res 

def get_position(p):
	res = bytearray()
	x = p['x']
	y = p['y']
	z = p['z']
	for i in [x,y,z]:
		res += struct.pack('<f', i)
	return res 

class VMDWriter():
	def __init__(self, data):
		self.data = data 

	def write(self, fname):
		def get_data(dt, pattern):
			return struct.pack(pattern, dt)

		f = open(fname, 'wb')
		data = self.data 

		# version info & model name
		f.write(data.version_byte)
		f.write(data.model_name_byte)

		# write num bone frame
		length = len(data.bone_record)
		f.write( get_data(length,'<I') )

		# recursively write record 
		for rec in data.bone_record:
			f.write(rec['BoneName_byte']) # bone name
			f.write(get_data(rec['FrameTime'], '<I')) # frame time
			f.write(get_position(rec['Position'])) # position
			f.write(get_rotation(rec['Rotation'])) # rotation
			f.write(get_curve(rec['Curve'])) # curve 

		f.write(data.postfix)
		f.close()


if __name__=='__main__':
	r = VMDReader('ddd.vmd')
	r.bone_record = r.bone_record[-1:]
	print(r.bone_record)

	# w = VMDWriter(r)
	# w.write('abc.vmd')
