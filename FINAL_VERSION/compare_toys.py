from optparse import OptionParser
import subprocess
import array
from  array import array

import ROOT
from ROOT import *

import header
from header import WaitForJobs, make_smooth_graph, Inter
import tdrstyle, CMS_lumi

gStyle.SetOptStat(0)
gROOT.SetBatch(kTRUE)

parser = OptionParser()



# Initialize arrays to eventually store the points on the TGraph

tdrstyle.setTDRStyle()



#ext = "doublebkg"
ext = "lowSys"
ext = "v2"
#ext = "v1"
iDir = '/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/tst_hybrid_'+ext
iDir = '/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/tst_hybrid_'+ext



#this_output = TFile.Open(iDir+"/higgsCombine.gmsbStau1029_2018.HybridNew.all.mH120.root")
#this_output = TFile.Open(iDir+"/higgsCombine.Gluino1600_2018nominalBkg_obs1.HybridNew.all.mH120.root")
#this_output = TFile.Open(iDir+"/higgsCombine.tauPrime2e-600-ZPrimeSSM-3000_2018.HybridNew.all.mH120.root")
#this_output = TFile.Open(iDir+'/higgsCombinetest500toy_dy2e1tev.HybridNew.mH120.quant0.500.root')
if not this_output: exit()
this_tree = this_output.Get('limit')
for ievent in range(int(this_tree.GetEntries())):
    this_tree.GetEntry(ievent)
    print("Quantile {} has r = {} and rErr = {}".format(this_tree.quantileExpected,this_tree.limit*0.00887,this_tree.limitErr*0.00887))         
    '''
    if this_tree.quantileExpected == 0.5:
        print("At expected median , limit = {}, error = {}".format(this_tree.limit,this_tree.limitErr))
    if this_tree.quantileExpected == -1:
        print("Observed , limit = {}, error = {}".format(this_tree.limit,this_tree.limitErr))
    '''


