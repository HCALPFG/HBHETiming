import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from DataFormat.DelaySetting import DelaySetting
from Producer.XMLProducer import XMLProducer


inputBrickPath = "Data/2016-april-11/"
inputTTCRXPath = "Data/TTCrxPhaseDelayRBX_0x187_tunedHTRs_tuned_v19m_11April2016.xml"
mapPath = "Data/2016-april-22_HCALmapHBEF_G_uHTR.txt"
adjustFile = "Data/20160422_HF_AdjustTiming_List.txt"

outputPath = "output/DelaySetting_22April2016/"

delaySetting = DelaySetting(mapPath,["HF"])
delaySetting.readDelayFromXML(inputBrickPath,inputTTCRXPath)
delaySetting.readDelayFromTXT(adjustFile)
delaySetting.adjustTiming()
producer = XMLProducer()
producer.produce(delaySetting,"2016-april-22_HCAL_Delays","22-04-16","All30","ttcrx.xml",outputPath)
