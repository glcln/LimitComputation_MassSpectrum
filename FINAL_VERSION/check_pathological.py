from optparse import OptionParser
import subprocess
import array
from  array import array

import ROOT
from ROOT import *

import header
from header import WaitForJobs, make_smooth_graph, Inter
import tdrstyle, CMS_lumi
import os
import re

gStyle.SetOptStat(0)
gROOT.SetBatch(kTRUE)

parser = OptionParser()

def extract_mass(filename):
    match = re.search(r'Gluino(\d+)_\d+', filename)
    if match:
        return int(match.group(1))
    return None


# Initialize arrays to eventually store the points on the TGraph

tdrstyle.setTDRStyle()

def is_sorted(lst):
    return all(lst[i] <= lst[i + 1] for i in range(len(lst) - 1))

#iDir = '/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/limitTrees_tamas/tst_hybrid_tamas/'
iDir = '/opt/sbg/cms/ui3_data1/gcoulon/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/limitTrees_SR3_test_UnB_v4_Raph_withGoodSignals_hybrid_newSys/'
#iDir = './2DAlpha_CodeV46p8_1Dfrom2DNoExtrapol_ZPrimeTauPrimeOfficial/'
root_files = [f for f in os.listdir(iDir) if f.endswith('.root')]

#root_files = ["higgsCombine.Gluino1000_2018.HybridNew.all.mH120.root","higgsCombine.Gluino1400_2018.HybridNew.all.mH120.root","higgsCombine.Gluino1600_2018.HybridNew.all.mH120.root","higgsCombine.Gluino1800_2018.HybridNew.all.mH120.root","higgsCombine.Gluino2000_2018.HybridNew.all.mH120.root","higgsCombine.Gluino2200_2018.HybridNew.all.mH120.root","higgsCombine.Gluino2400_2018.HybridNew.all.mH120.root","higgsCombine.Gluino2600_2018.HybridNew.all.mH120.root"]

DumpAll = True
checkObs = True
for root_file in root_files:

    #if not 'pairStau'  in root_file:
    #    continue

    print("Running on {}".format(root_file)) 
    this_output = TFile.Open(iDir+root_file)
    if not this_output: 
        print("No root file opened")
        continue

    this_tree = this_output.Get('limit')
    quantiles = []
    limits = []
    limits_err = []
    if not this_tree: 
        print("No limit branch opened")
        continue
    for ievent in range(int(this_tree.GetEntries())):
        print("--  Branch limit opened")
        this_tree.GetEntry(ievent)
        if(round(this_tree.quantileExpected,2) == 0.16):
            quantiles.append(0.16)
            limits.append(this_tree.limit)
            limits_err.append(this_tree.limitErr)
        if(round(this_tree.quantileExpected,2) == 0.84):
            quantiles.append(0.84)
            limits.append(this_tree.limit)
            limits_err.append(this_tree.limitErr)
        if(this_tree.quantileExpected == 0.5):
            quantiles.append(0.5)
            limits.append(this_tree.limit)
            limits_err.append(this_tree.limitErr)
        if(this_tree.quantileExpected == -1):
            quantiles.append(-1)
            limits.append(this_tree.limit)
            limits_err.append(this_tree.limitErr)
        
        if(round(this_tree.quantileExpected,3) == 0.025):
            quantiles.append(0.025)
            limits.append(this_tree.limit)
            limits_err.append(this_tree.limitErr)
        if(round(this_tree.quantileExpected,3) == 0.975):
            quantiles.append(0.975)
            limits.append(this_tree.limit)
            limits_err.append(this_tree.limitErr)

    sorted_quantiles, sorted_limits, sorted_limits_err = zip(*sorted(zip(quantiles, limits,limits_err)))
    if(DumpAll):
        for i in range(len(sorted_quantiles)):
            print("Quantile {} | limit = {} +/- {}".format(sorted_quantiles[i],sorted_limits[i],sorted_limits_err[i]))
            print("Quantile {} | RelativeError = {}".format(sorted_quantiles[i],sorted_limits_err[i]/sorted_limits[i]))
    print("\n")
