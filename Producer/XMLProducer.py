import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

class XMLProducer(object):
	def __init__(self):
		self.xmlData = {}

	def produce(self,delaySetting,brickCreationTag,brickCreationStamp,ttcrxTag,ttcrxFileName,outDirPath):
		if not os.path.isdir(outDirPath):
			os.mkdir(outDirPath,0755)
			os.mkdir(outDirPath+"/delay",0755)

		chDelaySetting,RBXDelaySetting = delaySetting.getAdjustSetting()

		for channel,adjustDelay in chDelaySetting.iteritems():
			if channel[0] not in self.xmlData:
				self.xmlData[channel[0]] = []
			self.xmlData[channel[0]].append((channel[1],channel[2],channel[3],adjustDelay))

		for RBX,channelData in self.xmlData.iteritems():
			channelData.sort()

		# Produce xml for each RBX
		for RBX,channelData in self.xmlData.iteritems():
			brick = ET.Element("CFGBrick")
			ET.SubElement(brick,"Parameter",name="RBX",type="string").text = RBX
			ET.SubElement(brick,"Parameter",name="INFOTYPE",type="string").text = "DELAY"
			ET.SubElement(brick,"Parameter",name="CREATIONTAG",type="string").text = brickCreationTag
			ET.SubElement(brick,"Parameter",name="CREATIONSTAMP",type="string").text = brickCreationStamp
			for channelDatum in channelData:
				ET.SubElement(brick,"Data",elements="1",encoding="dec",rm=str(channelDatum[1]),card=str(channelDatum[2]),qie=str(channelDatum[0])).text = str(int(channelDatum[3]))
			tree = ET.ElementTree(brick)
			xmlFile = open(outDirPath+"delay/"+RBX+"_DELAY.xml","w")
			xmlFile.write(minidom.parseString(ET.tostring(brick)).toprettyxml())
			xmlFile.close()

		# Produce TTcrx File	
		ttcrx = ET.Element("CFGBrickSet")
		bricks = ET.SubElement(ttcrx,"CFGBrick")
		ET.SubElement(bricks,"Parameter",name="BOARD",type="string").text = "RBX"
		ET.SubElement(bricks,"Parameter",name="TAG",type="string").text = ttcrxTag
		ET.SubElement(bricks,"Parameter",name="DATACLASS",type="string").text = "TTCRXPHASE"
		for rbxName,delay in RBXDelaySetting.iteritems():
			ET.SubElement(bricks,"Data",elements="3",encoding="dec",id=rbxName).text = RBXDelaySetting[rbxName]
		ttcrxFile = open(outDirPath+ttcrxFileName,"w")
		ttcrxFile.write(minidom.parseString(ET.tostring(ttcrx)).toprettyxml())
		ttcrxFile.close()


