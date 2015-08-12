import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from DataFormat.DelaySetting import DelaySetting
from Producer.XMLProducer import XMLProducer


inputBrickPath = "Data/2015-august-09/"
inputTTCRXPath = "Data/TTCrxPhaseDelayRBX_0x187_tunedHTRs_tuned_v19m_09August2015.xml"
mapPath = "Data/2015-may-4_HCALmapHBEF_G_uHTR.txt"
adjustFile = "Data/20150812_HF_AdjustTiming_List.txt"

outputPath = "output/DelaySetting_12August2015/"

delaySetting = DelaySetting(mapPath,["HF"])
delaySetting.readDelayFromXML(inputBrickPath,inputTTCRXPath)
delaySetting.readDelayFromTXT(adjustFile)
delaySetting.adjustTiming()
producer = XMLProducer()
producer.produce(delaySetting,"2015-august-12_HCAL_Delays","12-08-15","All30","TTCrxPhaseDelayRBX_0x187_tunedHTRs_tuned_v19m_12August2015.xml",outputPath)
