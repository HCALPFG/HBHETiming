import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from DataFormat.DelaySetting import DelaySetting
from Producer.XMLProducer import XMLProducer


inputBrickPath = "/afs/cern.ch/work/k/klo/hcal/PromptAnalysis/HFPhaseScan/DelayByChannel/Data/2015-july-14/"
inputTTCRXPath = "/afs/cern.ch/work/k/klo/hcal/PromptAnalysis/HFPhaseScan/DelayByChannel/Data/TTCrxPhaseDelayRBX_0x187_tunedHTRs_tuned_v19m_14July2015.xml"
mapPath = "/afs/cern.ch/work/k/klo/hcal/PromptAnalysis/HFPhaseScan/DelayByChannel/Data/2015-may-4_HCALmapHBEF_G_uHTR.txt"
adjustFile = "/afs/cern.ch/work/k/klo/hcal/PromptAnalysis/HFPhaseScan/DelayByChannel/Data/AdjustSetting_07082015.txt"

# relativeTimingPath = "/afs/cern.ch/work/k/klo/hcal/PromptAnalysis/HFPhaseScan/DelayByChannel/Data/20150608_HFRelativeTiming.txt"
# relativeTimingPath = {"depth1":("Data/20150528_RelativeTimeShift.root","shift_depth1"),"depth2":("Data/20150528_RelativeTimeShift.root","shift_depth2")}
outputPath = "output/DelaySetting_09August2015/"

delaySetting = DelaySetting(mapPath)
delaySetting.readDelayFromXML(inputBrickPath,inputTTCRXPath)
delaySetting.readDelayFromTXT(adjustFile)
delaySetting.adjustTiming()
producer = XMLProducer()
producer.produce(delaySetting,"2015-august-07_HCAL_Delays","07-08-15","All30","ttcrx.xml",outputPath)
