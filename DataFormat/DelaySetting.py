from Emap import Emap
import ROOT as r
import os
from xml.dom import minidom

class DelaySetting(object):
	"""a class to read DelaySetting from TH2 and XML"""
	def __init__(self,mapFileName,subDetList):
	
		self.subDetList = subDetList
		self.emap = Emap(mapFileName,self.subDetList)

		# Default Setting
		self.CalibRM_number = 5
		self.HF_CalibRM_number = 4
		self.brick_min_delay = 0
		self.brick_max_delay = 24
		self.brick_width = 25
		self.ttcrx_min_delay = 0
		self.ttcrx_max_delay = 225
		self.ttcrx_step_time_ns = 1.56
		self.ttcrx_step_value = 15

	def readDelayFromXML(self,rbxDir,ttcrxFile):
		self.currentRBXSetting = {}
		self.currentChSetting = {}
		self.xmlFiles = {}

		brick_in_paths = [ rbxDir + "/" + p for p in os.listdir(rbxDir) if os.path.isfile(os.path.join(rbxDir,p)) and p.endswith(".xml") and not p.startswith(".") ]

		for brickPath in brick_in_paths:
			rbxName = brickPath.split("/")[-1].replace("_DELAY.xml","")
			self.xmlFiles[rbxName] = minidom.parse(brickPath)
			data = self.xmlFiles[rbxName].getElementsByTagName("Data")
			for datum in data:
				self.currentChSetting[ ( rbxName,int(datum.getAttribute("qie")),int(datum.getAttribute("rm")),int(datum.getAttribute("card"))  ) ] = int(datum.childNodes[0].nodeValue)

		ttcrxFile = minidom.parse(ttcrxFile)
		ttcrxData = ttcrxFile.getElementsByTagName("Data")
		for datum in ttcrxData:
			self.currentRBXSetting[str(datum.getAttribute("id"))] = datum.childNodes[0].nodeValue

	def readDelayFromTXT(self,fileName):
		textFile = open(fileName,'r')
		self.addSetting = {}
		for line in textFile:
			if line[0] == "#": continue
			fieldList = line.split()

			# Default Input txt format, comment out because of different format for 20150809 textfile
			ieta = int(fieldList[0])
			iphi = int(fieldList[1])
			depth = int(fieldList[2])
			delay = float(fieldList[3])

			#print "Notice the adjustment file is read in a different way!"
			#ieta = int(fieldList[2])
			#iphi = int(fieldList[1])
			#depth = int(fieldList[0])
			#delay = float(fieldList[3])

			self.addSetting[self.getRBXCoords(ieta,iphi,depth)] = round(delay)


	def adjustTiming(self):
		if hasattr(self,"currentRBXSetting") and hasattr(self,"currentChSetting") and hasattr(self,"addSetting"):
			self.adjustChSetting = {}
			self.adjustRBXSetting = {}

			# Loop over each RBX
			for rbxName,RBXDelay in self.currentRBXSetting.iteritems():

				successShift = False
				
				goodChannels = {(coord[1],coord[2],coord[3]):True for coord in self.currentChSetting if coord[0] == rbxName}
				allDelayForOneRBX = {(coord[1],coord[2],coord[3]):delay for coord,delay in self.currentChSetting.iteritems() if coord[0] == rbxName}
				if rbxName[:2] not in self.subDetList:
					self.adjustRBXSetting[rbxName] = self.currentRBXSetting[rbxName]
					for coord,delay in allDelayForOneRBX.iteritems():
						self.adjustChSetting[(rbxName,coord[0],coord[1],coord[2])] = delay
					continue

				# Loop over each channel and check if there is out of bound
				for channelCoord,currentDelay in allDelayForOneRBX.iteritems():

					# Do nothing for calibration channel
					if self.isCalibChannel(rbxName,channelCoord[1]): continue

					if (rbxName,channelCoord[0],channelCoord[1],channelCoord[2]) not in self.addSetting:
						#print "Missing info to adjust setting for the channel ",(rbxName,channelCoord[0],channelCoord[1],channelCoord[2]), " or ", self.inverse_map[(rbxName,channelCoord[0],channelCoord[1],channelCoord[2])]
						#print "Will not adjust setting of this channel"
						self.addSetting[(rbxName,channelCoord[0],channelCoord[1],channelCoord[2])] = 0.
						continue
					if (self.addSetting[(rbxName,channelCoord[0],channelCoord[1],channelCoord[2])] + currentDelay > self.brick_max_delay) or  (self.addSetting[(rbxName,channelCoord[0],channelCoord[1],channelCoord[2])] + currentDelay < self.brick_min_delay):  		
					 	goodChannels[channelCoord] = False

				# Adjust timing according to if there is out of bound
				if False in goodChannels.values():
					listBadChannels = []
					print "Interplay with TTCrx..."
					print "List of bad channels:"
					print "=============================="
					for channelCoord,isGood in goodChannels.iteritems():
						if not isGood:
							print "RBX: {0}, QIE: {1}, RM: {2}, Card: {3};".format(rbxName,*channelCoord)+" Current Delay: {0}, Request Delay: {1}".format(allDelayForOneRBX[channelCoord],self.addSetting[(rbxName,channelCoord[0],channelCoord[1],channelCoord[2])] )
							listBadChannels.append(channelCoord)
					print  "=============================="
	
					for badChannel in listBadChannels:
						if successShift: continue
						requiredShift = self.addSetting[(rbxName,badChannel[0],badChannel[1],badChannel[2])] + allDelayForOneRBX[badChannel]
						if requiredShift > 0:
							delay_for_ttcrx_ns = requiredShift - self.brick_max_delay
						else:
							delay_for_ttcrx_ns = requiredShift - self.brick_min_delay
						delay_for_ttcrx_nk = int(round(float(delay_for_ttcrx_ns) / self.ttcrx_step_time_ns) - .5) + (float(delay_for_ttcrx_ns) / self.ttcrx_step_time_ns > 0)
						delay_for_ttcrx_k = delay_for_ttcrx_nk*self.ttcrx_step_value
	
						# Check if this delay for ttcrx is compatible with the rest
						testAdjust = {otherChannel: allDelayForOneRBX[otherChannel]-delay_for_ttcrx_ns + self.addSetting[(rbxName,otherChannel[0],otherChannel[1],otherChannel[2])]   for otherChannel in allDelayForOneRBX  if otherChannel != badChannel and not self.isCalibChannel(rbxName,otherChannel[1])}
						successShift = all([(adjustShiftWithTTcrx >= self.brick_min_delay) and (adjustShiftWithTTcrx <= self.brick_max_delay) for goodChannel,adjustShiftWithTTcrx in testAdjust.iteritems()  ])
						if successShift:
							for coord,currentDelay in allDelayForOneRBX.iteritems():
								if not self.isCalibChannel(rbxName,coord[1]):
									self.adjustChSetting[(rbxName,coord[0],coord[1],coord[2])] = currentDelay+self.addSetting[(rbxName,coord[0],coord[1],coord[2])]-int(round(delay_for_ttcrx_ns))
								else:
									self.adjustChSetting[(rbxName,coord[0],coord[1],coord[2])] = 0
							delay_for_ttcrx = int(self.currentRBXSetting[rbxName].split(" ")[0]) + delay_for_ttcrx_k
							self.adjustRBXSetting[rbxName] = " ".join([str(int(delay_for_ttcrx)),self.currentRBXSetting[rbxName].split(" ")[1],self.currentRBXSetting[rbxName].split(" ")[2]])


				else:
					for coord,currentDelay in allDelayForOneRBX.iteritems():
						if not self.isCalibChannel(rbxName,coord[1]):
							self.adjustChSetting[(rbxName,coord[0],coord[1],coord[2])] = currentDelay+self.addSetting[(rbxName,coord[0],coord[1],coord[2])]
						else:
							self.adjustChSetting[(rbxName,coord[0],coord[1],coord[2])] = 0
					self.adjustRBXSetting[rbxName] = self.currentRBXSetting[rbxName]
					successShift = True

				if not successShift:
					print "WARNING! Illegal delays have been requested! The current setting can't accomodate the required changes. Setting the delay setting to max or min ({0} or {1}) instead".format(self.brick_max_delay,self.brick_min_delay)
					for coord, currentDelay in allDelayForOneRBX.iteritems():	
						if coord not in listBadChannels and coord[1] != self.HF_CalibRM_number:
							self.adjustChSetting[(rbxName,coord[0],coord[1],coord[2])] = currentDelay+self.addSetting[(rbxName,coord[0],coord[1],coord[2])]
						elif coord in listBadChannels:
							print "RBX: {0}, QIE: {1}, RM: {2}, Card: {3};".format(rbxName,*coord)+ "Current Delay: {0}, Request Delay: {1} ".format(currentDelay,self.addSetting[(rbxName,coord[0],coord[1],coord[2])])
							if (currentDelay+self.addSetting[(rbxName,coord[0],coord[1],coord[2])] > self.brick_max_delay):
								self.adjustChSetting[(rbxName,coord[0],coord[1],coord[2])] =  self.brick_max_delay
								print "Set to {0}".format(self.brick_max_delay)
							elif (currentDelay+self.addSetting[rbxname,coord[0],coord[1],coord[2]] < self.brick_min_delay):
								self.adjustChSetting[(rbxName,coord[0],coord[1],coord[2])] =  self.brick_min_delay
								print "Set to {0}".format(self.brick_min_delay)
						elif self.isCalibChannel(rbxName,coord[1]):
							self.adjustRBXSetting[rbxName] = 0
						self.adjustRBXSetting[rbxName] = self.currentRBXSetting[rbxName]



		else:
			raise RuntimeError,"Delay Setting for RBX, channel or relative change not set"
	
	
	def getAdjustSetting(self):
		return self.adjustChSetting,self.adjustRBXSetting



	def __str__(self):
		# print delay setting for each channel, each line for each channel
		return "\n".join(["ieta: %s, iphi: %s, depth: %s, det: %s, delay: %s"%(coords[0],coords[1],coords[2],coords[3],delay)+", RBX: {0}, QIE: {1}, RM: {2}, Cand: {3}".format(*self.getRBXCoords(*coords)) for coords,delay in self._EtaPhiSetting.iteritems() ])

	def cleanUp(self):
		super(DelaySetting,self).cleanUp()
		for depth,file in self._files.iteritems():
			file.Close()

	def getRBXCoords(self,ieta,iphi,depth):
		return self.emap.getRBXCoords(ieta,iphi,depth)

	def isCalibChannel(self,rbx,rm):
		return (rbx.startswith("HF") and rm == self.HF_CalibRM_number) or ((rbx.startswith("HO") or rbx.startswith("HB") or rbx.startswith("HE")) and rm == self.CalibRM_number)

	
