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
				self.channel_EtaPhiCoord[(ieta,iphi,depth)] = ""
				self.map[(ieta,iphi,depth)] = (rbx,qie,rm,cand)
				self.inverse_map[ (rbx,qie,rm,cand) ] = (ieta,iphi,depth)
			elif subDet.endswith("M"):
				self.channel_EtaPhiCoord[(ieta*-1,iphi,depth)] = ""
				self.map[(ieta*-1,iphi,depth)] = (rbx,qie,rm,cand)
				self.inverse_map[ (rbx,qie,rm,cand) ] = (ieta*-1,iphi,depth)

			self.channel_RBXCoord[(rbx,qie,rm,cand)] = ""

	def __iter__(self):
		return iter(self.channel_RBXCoord)

	def cleanUp(self):
		self._file.close()

	def getRBXCoords(self,ieta,iphi,depth):
		if (ieta,iphi,depth) in self.map:
			return self.map[(ieta,iphi,depth)]
		else:
			raise RuntimeError,"Can't find (ieta,iphi,depth,subDet) in the emap for HCAL"

