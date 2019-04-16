import scipy.io as sio 
import numpy as np 
import VMD 
from PyQt5.QtGui import QQuaternion, QVector3D
import copy 

def euler_to_quaternion(roll, pitch, yaw):
	qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
	qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
	qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)
	qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
	return qx, qy, qz, qw

def quaternion_to_euler(x, y, z, w):
	t0 = +2.0 * (w * x + y * z)
	t1 = +1.0 - 2.0 * (x * x + y * y)
	roll = np.atan2(t0, t1)
	t2 = +2.0 * (w * y - z * x)
	t2 = +1.0 if t2 > +1.0 else t2
	t2 = -1.0 if t2 < -1.0 else t2
	pitch = np.asin(t2)
	t3 = +2.0 * (w * z + x * y)
	t4 = +1.0 - 2.0 * (y * y + z * z)
	yaw = np.atan2(t3, t4)
	return yaw, pitch, roll

class poseFrame():
	def __init__(self, name, rotation):
		self.name = name + b'\x00'*(15-len(name))
		self.rotation = rotation.toVector4D()
	def get_vec(self):
		return self.rotation.x(), self.rotation.y(), self.rotation.z(), self.rotation.w()

def assign(item, frame):
	item['Rotation']['x'] = frame.get_vec()[0]
	item['Rotation']['y'] = frame.get_vec()[1]
	item['Rotation']['z'] = frame.get_vec()[2]
	item['Rotation']['w'] = frame.get_vec()[3]
	item['BoneName_byte'] = frame.name

def addOneMore(r):
	buff = r.bone_record[0]
	buff = copy.deepcopy(buff)
	r.bone_record.append(buff)
	return buff 

r = VMD.VMDReader('sample_reference.vmd')
r.bone_record = r.bone_record[:1]

joints = [[8,9],[9,10], [8,14],[14,15],[15,16], [8,11],[11,12],[12,13], [8,7],[7,0], [4,5],[5,6],[0,4], [0,1],[1,2],[2,3]]

time = 0
for i in range(586):
	time += 1
	pts = np.float32(sio.loadmat('./pred3d/%08d.mat'%i)['pts'])
	print(pts.shape)
	buf = []
	for i in range(17):
		buf.append(QVector3D(pts[i][0], -pts[i][1], pts[i][2]))
	pts = buf 

	# lowerbody 
	bonename = b'\x89\xba\x94\xbc\x90\x67'
	direction = pts[0] - pts[7]
	up = QVector3D.crossProduct(direction, (pts[4] - pts[1])).normalized()
	ori_lower = QQuaternion.fromDirection(direction, up)
	initial = QQuaternion.fromDirection(QVector3D(0,-1,0), QVector3D(0,0,1))
	rotation_lower = ori_lower * initial.inverted()
	frame_lower_body = poseFrame(bonename, rotation_lower)
	record = addOneMore(r)
	record['FrameTime'] = time
	assign(record, frame_lower_body)

	# upperbody
	bonename = b'\x8f\xe3\x94\xbc\x90\x67' 
	direction = pts[8] - pts[7]
	up = QVector3D.crossProduct(direction, (pts[14]-pts[11])).normalized()
	ori_upper = QQuaternion.fromDirection(direction, up)
	initial = QQuaternion.fromDirection(QVector3D(0,1,0), QVector3D(0,0,1))
	rotation_upper = ori_upper * initial.inverted()
	frame_upper_body = poseFrame(bonename, rotation_upper)
	record = addOneMore(r)
	record['FrameTime'] = time
	assign(record, frame_upper_body)

	

	# Fuck i dont want to use english
	# atama
	bonename = b'\x93\xaa'
	direction = pts[10] - pts[8]
	up = QVector3D.crossProduct( (pts[9] - pts[8]), (pts[10] - pts[9]))
	ori = QQuaternion.fromDirection(direction, up)
	initial = QQuaternion.fromDirection(QVector3D(0,1,0) , QVector3D(1,0,0))
	rotation = ori * initial.inverted()
	rotation = rotation_upper.inverted() * rotation
	frame_head = poseFrame(bonename, rotation)
	record = addOneMore(r)
	record['FrameTime'] = time
	assign(record, frame_head)

	# hidari ude 
	bonename = b'\x8d\xb6\x98\x72'
	direction = pts[12] - pts[11]
	up = QVector3D.crossProduct((pts[12] - pts[11]), (pts[13]-pts[12]))
	ori = QQuaternion.fromDirection(direction, up)
	initial = QQuaternion.fromDirection(QVector3D(1.0,-1,0), QVector3D(1,1.0,0))
	rotation = ori * initial.inverted()
	rotation_larm = rotation_upper.inverted() * rotation
	frame_hidariude = poseFrame(bonename, rotation_larm)
	record = addOneMore(r)
	record['FrameTime'] = time
	assign(record, frame_hidariude)

	# hidari hiji 
	bonename = b'\x8d\xb6\x82\xd0\x82\xb6'
	direction = pts[13] - pts[12]
	up = QVector3D.crossProduct((pts[12]-pts[11]), (pts[13]-pts[12]))
	ori = QQuaternion.fromDirection(direction, up)
	initial = QQuaternion.fromDirection(QVector3D(1.0,-1,0), QVector3D(1,1.0,0))
	rotation = ori * initial.inverted()
	rotation = rotation_larm.inverted() * rotation_upper.inverted() * rotation
	frame_hidarihiji = poseFrame(bonename, rotation)
	record = addOneMore(r)
	record['FrameTime'] = time
	assign(record, frame_hidarihiji)

	# migi ude 
	bonename = b'\x89\x45\x98\x72'
	direction = pts[15] - pts[14]
	up = QVector3D.crossProduct((pts[15]-pts[14]), (pts[16]-pts[15]))
	ori = QQuaternion.fromDirection(direction, up)
	initial = QQuaternion.fromDirection(QVector3D(-1.0,-1,0), QVector3D(1,-1.0,0))
	rotation = ori * initial.inverted()
	rotation_rarm = rotation_upper.inverted() * rotation
	frame_migiude = poseFrame(bonename, rotation_rarm)
	record = addOneMore(r)
	record['FrameTime'] = time
	assign(record, frame_migiude)

	# migi hiji 
	bonename = b'\x89\x45\x82\xd0\x82\xb6'
	direction = pts[16] - pts[15]
	up = QVector3D.crossProduct((pts[15]-pts[14]), (pts[16]-pts[15]))
	ori = QQuaternion.fromDirection(direction, up)
	initial = QQuaternion.fromDirection(QVector3D(-1.0,-1,0), QVector3D(1,-1.0,0))
	rotation = ori * initial.inverted()
	rotation = rotation_rarm.inverted() * rotation_upper.inverted() * rotation
	frame_migihiji = poseFrame(bonename, rotation)
	record = addOneMore(r)
	record['FrameTime'] = time
	assign(record, frame_migihiji)

	# hidari ashi 
	bonename = b'\x8d\xb6\x91\xab'
	direction = pts[5] - pts[4]
	up = QVector3D.crossProduct((pts[5]-pts[4]) , (pts[6]-pts[5]))
	ori = QQuaternion.fromDirection(direction, up)
	initial = QQuaternion.fromDirection(QVector3D(0,-1,0), QVector3D(-1,0,0))
	rotation = ori * initial.inverted()
	rotation_lleg = rotation_lower.inverted() * rotation 
	frame_hidariashi = poseFrame(bonename, rotation_lleg)
	record = addOneMore(r)
	record['FrameTime'] = time
	assign(record, frame_hidariashi)

	# hidari hiza 
	bonename = b'\x8d\xb6\x82\xd0\x82\xb4'
	direction = pts[6] - pts[5]
	up = QVector3D.crossProduct((pts[5]-pts[4]) , (pts[6]-pts[5]))
	ori = QQuaternion.fromDirection(direction, up)
	initial = QQuaternion.fromDirection(QVector3D(0,-1,0), QVector3D(-1,0,0))
	rotation = ori * initial.inverted()
	rotation = rotation_lleg.inverted() * rotation_lower.inverted() * rotation
	frame_hidarihiza = poseFrame(bonename, rotation)
	record = addOneMore(r)
	record['FrameTime'] = time
	assign(record, frame_hidarihiza)

	# migi ashi
	bonename = b'\x89\x45\x91\xab'
	direction = pts[2] - pts[1]
	up = QVector3D.crossProduct((pts[2]-pts[1]) , (pts[3]-pts[2]))
	ori = QQuaternion.fromDirection(direction, up)
	initial = QQuaternion.fromDirection(QVector3D(0,-1,0) , QVector3D(-1,0,0))
	rotation = ori * initial.inverted()
	rotation_rleg = rotation_lower.inverted() * rotation
	frame_migiashi = poseFrame(bonename, rotation_rleg)
	record = addOneMore(r)
	record['FrameTime'] = time
	assign(record, frame_migiashi)

	# migi hiza 
	bonename = b'\x89\x45\x82\xd0\x82\xb4'
	direction = pts[3] - pts[2]
	up = QVector3D.crossProduct((pts[2]-pts[1]) , (pts[3]-pts[2]))
	ori = QQuaternion.fromDirection(direction, up)
	initial = QQuaternion.fromDirection(QVector3D(0,-1,0) , QVector3D(-1,0,0))
	rotation = ori * initial.inverted()
	rotation = rotation_rleg.inverted() * rotation_lower.inverted() * rotation
	frame_migihiza = poseFrame(bonename, rotation)
	record = addOneMore(r)
	record['FrameTime'] = time
	assign(record, frame_migihiza)

r.bone_record = r.bone_record[1:]

w = VMD.VMDWriter(r)
w.write('output.vmd')
