import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from DataFormat.DelaySetting import DelaySetting
from Producer.XMLProducer import XMLProducer


inputBrickPath = "Data/2015-july-14/"
inputTTCRXPath = "Data/TTCrxPhaseDelayRBX_0x187_tunedHTRs_tuned_v19m_14July2015.xml"
mapPath = "Data/2015-may-4_HCALmapHBEF_G_uHTR.txt"
adjustFile = "Data/20150809_HBHE_AdjustTiming_List.txt"

outputPath = "output/DelaySetting_09August2015/"

delaySetting = DelaySetting(mapPath,["HB","HE"])
delaySetting.readDelayFromXML(inputBrickPath,inputTTCRXPath)
delaySetting.readDelayFromTXT(adjustFile)
delaySetting.adjustTiming()
producer = XMLProducer()
producer.produce(delaySetting,"2015-august-09_HCAL_Delays","09-08-15","All30","ttcrx.xml",outputPath)
