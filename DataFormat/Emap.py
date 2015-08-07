from copy import deepcopy

class Emap(object):
	"""Map for channels in HCAL"""
	def __init__(self,mapFileName):
		self._file = open(mapFileName)

		self.channel_EtaPhiCoord = {}
		self.map = {}
		self.inverse_map = {}
		self.channel_RBXCoord = {}

		for line in self._file:
			if line[0] == "#": continue
			fieldList = line.split()
			ieta = int(fieldList[2])
			iphi = int(fieldList[3])
			depth = int(fieldList[5])
			subDet = fieldList[7][:3]	
			rbx = fieldList[7]
			qie = int(fieldList[12])
			rm = int(fieldList[9])
			cand = int(fieldList[11])
			if subDet.endswith("P"):
				self.channel_EtaPhiCoord[(ieta,iphi,depth,subDet)] = ""
				self.map[(ieta,iphi,depth,subDet)] = (rbx,qie,rm,cand)
				self.inverse_map[ (rbx,qie,rm,cand) ] = (ieta,iphi,depth,subDet)
			elif subDet.endswith("M"):
				self.channel_EtaPhiCoord[(ieta*-1,iphi,depth,subDet)] = ""
				self.map[(ieta*-1,iphi,depth,subDet)] = (rbx,qie,rm,cand)
				self.inverse_map[ (rbx,qie,rm,cand) ] = (ieta*-1,iphi,depth,subDet)

			self.channel_RBXCoord[(rbx,qie,rm,cand)] = ""

	def __iter__(self):
		return iter(self.channel_RBXCoord)

	def cleanUp(self):
		self._file.close()

	def getRBXCoords(self,ieta,iphi,depth,subDet):
		if (ieta,iphi,depth,subDet) in self.map:
			return self.map[(ieta,iphi,depth,subDet)]
		else:
			raise RuntimeError,"Can't find (ieta,iphi,depth,subDet) in the emap for HCAL"

