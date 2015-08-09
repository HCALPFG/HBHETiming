
from xml.dom import minidom
import os

#choose = 1
choose = 2

if choose == 1:
	rbxDir = "output/DelaySetting_09August2015/delay/"
	ttcrxPath = "output/DelaySetting_09August2015/ttcrx.xml"
	outDirPath = "check/2015-August-09-DelaySetting.txt"
else:
	rbxDir = "Data/2015-july-14/"
	ttcrxPath = "Data/TTCrxPhaseDelayRBX_0x187_tunedHTRs_tuned_v19m_14July2015.xml"
	outDirPath = "check/2015-July-14-DelaySetting.txt"


outFile = open(outDirPath,"w")

brick_in_paths = [ rbxDir + "/" + p for p in os.listdir(rbxDir) if os.path.isfile(os.path.join(rbxDir,p)) and p.endswith(".xml") and not p.startswith(".") ]

delaySetting = {}
xmlFiles = {}
for brickPath in brick_in_paths:
	rbxName = brickPath.split("/")[-1].replace("_DELAY.xml","")
	xmlFiles[rbxName] = minidom.parse(brickPath)
	data = xmlFiles[rbxName].getElementsByTagName("Data")
	for datum in data:
		delaySetting[ ( rbxName,int(datum.getAttribute("qie")),int(datum.getAttribute("rm")),int(datum.getAttribute("card"))  ) ] = int(datum.childNodes[0].nodeValue)

ttcrxSetting = {}
ttcrxFile = minidom.parse(ttcrxPath)
data = ttcrxFile.getElementsByTagName("Data")
for datum in data:
	ttcrxSetting[str(datum.getAttribute("id"))] = datum.childNodes[0].nodeValue


for i,channel in enumerate(sorted(delaySetting)):
	total_delay = delaySetting[channel]+0.104*int(ttcrxSetting[channel[0]].split()[0])
	outFile.write("Line {0}".format(i) + " RBX: {0}, QIE: {1}, RM: {2}, Card: {3};".format(*channel)+" Delay: {0} ".format( delaySetting[channel] )+ "Total Delay: {0}".format(total_delay) + " ttcrx: " + ttcrxSetting[channel[0]] + "\n" )


outFile.close()
