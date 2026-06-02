"""

2022/10/03
create datacard from the mass distributions of signal in mass windows, and from the background prection using the Fpix mass reconstruction method.

Raphael Haberle

raphael.julien.haberle@cern.ch

"""

import ROOT as rt
import csv
import re
import sys
import collections
import os
#sys.path.append('/opt/sbg/cms/ui4_data1/rhaeberl/CMSSW_10_6_30/src/HSCPTreeAnalyzer/python')
from USE_DATE import USED_DATE, VERSION

sys.argv.append(' -b- ')



from collections import OrderedDict
import uproot

import scipy
import awkward
import numpy as np
import time

#from histo_utilities import std_color_list, create_TGraph, find_intersect


rt.gROOT.SetBatch(True)

import CMS_lumi, tdrstyle
a = tdrstyle.setTDRStyle()
CMS_lumi.writeExtraText = 0

def setColorAndMarkerGr(gr,a,b):
    gr.SetMarkerColor(a)
    gr.SetLineColor(a)
    gr.SetMarkerStyle(b)
    gr.SetMarkerSize(2)

def statErr(h1,name):
    statErr=h1.Clone()
    statErr.Reset()
    statErr.SetName(name)
    for i in range (1,statErr.GetNbinsX()):
        if h1.GetBinContent(i)>0:
            #print (i,statErr.GetBinError(i),statErr.GetBinContent(i),statErr.GetBinError(i)/statErr.GetBinContent(i))
            statErr.SetBinContent(i,h1.GetBinError(i)+h1.GetBinContent(i))
            #print i,h1.GetBinLowEdge(i), h1.GetBinError(i),h1.GetBinContent(i), h1.GetBinError(i)/h1.GetBinContent(i)
            #statErr.SetBinContent(i,statErr.GetBinError(i))
        if h1.GetBinContent(i)==0:
            statErr.SetBinContent(i,0)
    return statErr

def BiasCorrection(h1,a_,b_):
    h=h1.Clone()
    for i in range (0,h.GetNbinsX()+1):
        mass = h.GetBinLowEdge(i)
        if(mass<25): continue
        h.SetBinContent(i,h.GetBinContent(i)*(a_*mass+b_))
    return h


def make_datacard_hscp_combining2017and2018(outDataCardsDir,  modelName,rootName, signal2017, signal2018, bkg2017, bkg2018, observation2017, observation2018, shapeUp_2017, shapeDown_2017, shapeUp_2018, shapeDown_2018, shapeNames_unc,bkgShapes_unc,AddChannel,ScaleFactors,ExtDir,thresh):

    print("Making datacards, obs 2017 = {}, and obs 2018 = {}".format(observation2017,observation2018))
 
    text_file = open(outDataCardsDir+modelName+"_test1.txt", "w")
    if not AddChannel:
        text_file.write('imax {0} \n'.format(2))
        text_file.write('jmax {0} \n'.format(1))
        text_file.write('kmax * \n')
        text_file.write('--------------- \n')
        text_file.write('shapes * * MassShapeHistos_{}/{} $PROCESS_$CHANNEL $PROCESS_$CHANNEL_$SYSTEMATIC \n'.format(ExtDir,rootName))
        text_file.write('--------------- \n')
        text_file.write('bin \t  Ch2017 \t Ch2018 \n')
        #text_file.write('observation \t {0:6.2f} \t {0:6.2f} \n'.format(observation2017,observation2018))
        text_file.write('observation \t {} \t {} \n'.format(observation2017,observation2018))
        text_file.write('------------------------------ \n')
        text_file.write('bin \t Ch2017 \t Ch2017 \t Ch2018 \t Ch2018 \n')
        text_file.write('process \t signal \t background \t signal \t background \n')
        text_file.write('process \t 0 \t 1 \t 0 \t 1 \n')
        text_file.write('rate \t {} \t {} \t {} \t {} \n'.format(signal2017, bkg2017, signal2018, bkg2018,bkg2018,bkg2018))
        text_file.write('------------------------------ \n')
    
        ###Shape uncertainties 

          
        text_file.write('lumi \t lnN \t 1.016 \t - \t 1.016 \t - \n')
        for u in range(len(shapeNames_unc)):
            text_file.write('{} \t shape \t 1.0 \t - \t - \t - \n'.format(shapeNames_unc[u]))
            text_file.write('{} \t shape \t - \t - \t 1.0 \t - \n'.format(shapeNames_unc[u]))
        '''
        for binUnc in range(len(bkgShapes_unc)):
            text_file.write('{} \t shape \t - \t 1.0 \t - \t - \n'.format(bkgShapes_unc[binUnc]))
            text_file.write('{} \t shape \t - \t - \t - \t 1.0 \n'.format(bkgShapes_unc[binUnc]))
        '''
        '''
        for binUnc in range(1,28):
            binSys = "Bin"+str(binUnc)
            text_file.write('{} \t shape \t - \t 1.0 \t - \t - \n'.format(binSys))
            text_file.write('{} \t shape \t - \t - \t - \t 1.0 \n'.format(binSys))
        '''

        text_file.write('rateAllA rateParam Ch2017 background {}\n'.format(ScaleFactors[0]))
        text_file.write('rateAllB rateParam Ch2018 background {}\n'.format(ScaleFactors[1]))

        text_file.write('Ch2017 autoMCStats {}\n'.format(thresh))
        text_file.write('Ch2018 autoMCStats {}\n'.format(thresh))


    else:
        text_file.write('imax {0} \n'.format(4))
        text_file.write('jmax {0} \n'.format(1))
        text_file.write('kmax * \n')
        text_file.write('--------------- \n')
        text_file.write('shapes * * MassShapes_{}/{} $PROCESS_$CHANNEL $PROCESS_$CHANNEL_$SYSTEMATIC \n'.format(ExtDir,rootName))
        text_file.write('--------------- \n')
        text_file.write('bin \t  Ch2017_high_eta \t Ch2017_low_eta \t Ch2018_high_eta \t Ch2018_low_eta \n')
        #text_file.write('observation \t {0:6.2f} \t {0:6.2f} \n'.format(observation2017,observation2018))
        text_file.write('observation \t {} \t {} \t {} \t {} \n'.format(observation2017,observation2017,observation2018,observation2018))
        text_file.write('------------------------------ \n')
        text_file.write('bin \t Ch2017_high_eta \t Ch2017_high_eta \t Ch2017_low_eta \t Ch2017_low_eta \t Ch2018_high_eta \t Ch2018_high_eta \t Ch2018_low_eta \t Ch2018_low_eta \n')
        text_file.write('process \t signal \t background \t signal \t background \t signal \t background \t signal \t background \n')
        text_file.write('process \t 0 \t 1 \t 0 \t 1 \t 0 \t 1 \t 0 \t 1 \n')
        text_file.write('rate \t {} \t {} \t {} \t {} \t {} \t {} \t {} \t {} \n'.format(signal2017,signal2017, bkg2017,bkg2017, signal2018,signal2018, bkg2018,bkg2018))

        text_file.write('------------------------------ \n')
    
        ###Shape uncertainties 
                  
        for u in range(len(shapeNames_unc)):
            text_file.write('{} \t shape \t 1.0 \t - \t - \t - \t - \t - \t - \t - \n'.format(shapeNames_unc[u]))
            text_file.write('{} \t shape \t - \t - \t 1.0 \t - \t - \t - \t - \t - \n'.format(shapeNames_unc[u]))
            text_file.write('{} \t shape \t - \t - \t - \t - \t 1.0 \t - \t - \t - \n'.format(shapeNames_unc[u]))
            text_file.write('{} \t shape \t - \t - \t - \t - \t - \t - \t 1.0 \t - \n'.format(shapeNames_unc[u]))

        text_file.write('\n')
        text_file.write('rateLowA rateParam Ch2017_low_eta background {}\n'.format(ScaleFactors[0]))
        text_file.write('rateLowB rateParam Ch2018_low_eta background {}\n'.format(ScaleFactors[1]))
        text_file.write('rateHighA rateParam Ch2017_high_eta background {}\n'.format(ScaleFactors[2]))
        text_file.write('rateHighB rateParam Ch2018_high_eta background {}\n'.format(ScaleFactors[3]))


        text_file.write('Ch2017_low_eta autoMCStats {}\n'.format(thresh))
        text_file.write('Ch2017_high_eta autoMCStats {}\n'.format(thresh))
        text_file.write('Ch2018_low_eta autoMCStats {}\n'.format(thresh))
        text_file.write('Ch2018_high_eta autoMCStats {}\n'.format(thresh))


    text_file.close()

def totalUncertainy(unc,i=1):
    total=0
    for k,v in unc.items():
        if len(v)==2 and (i==0 or i==1):
            total+=pow(1-v[i],2)
        else:total+=pow(1-v[0],2)
    return np.sqrt(total)

def makeYieldFile(text_file_tex,modelName,bkg,bckg_up,bckg_down,signal,signal_up,signal_down):
    typeOfDisplay='.2E'
    text_file_tex.write('\n '+modelName+' & $'+str(format(bkg,typeOfDisplay))+'^{+'+str(format(bkg*bckg_up,typeOfDisplay))+'}_{-'+str(format(bkg*bckg_down,typeOfDisplay))+'}$ & $'+str(format(signal,typeOfDisplay))+'^{+'+str(format(signal*signal_up,typeOfDisplay))+'}_{-'+str(format(signal*signal_down,typeOfDisplay))+'}$ \\\\')
    text_file_tex.write('\n \hline')  
    

def fillH2(h2,targetMass,mean,stddev,s):
    for i in range(0,h2.GetNbinsX()+1):
        if (i!=h2.GetXaxis().FindBin(targetMass)): 
                continue
        else:
            for j in range(h2.GetYaxis().FindBin(mean-stddev),h2.GetYaxis().FindBin(mean+2*stddev)):
                if("Gluino" in s):
                    h2.SetBinContent(i,j,1)
                elif("pairStau" in s):
                    h2.SetBinContent(i,j,2)
                elif("Stop" in s):
                    h2.SetBinContent(i,j,3)

def pushSyst(syst1,syst2):
    syst1=abs(1-syst1)
    syst2=abs(1-syst2)
    res=max(syst1,syst2)
    return res*100



if __name__ == '__main__':


    fpath =OrderedDict()
    mass = OrderedDict()

    #if len(sys.argv) < 3:
        #print("Usage: python myscript.py <PTCUT> <SR#>")
        #exit()

    ptCUT = sys.argv[1]
    SR = sys.argv[2]
    version = VERSION
    print("Using version {}".format(version))

    testBin_ = False
    regionSignal=SR
    systSignal="Stau"

    #ExtDir = "pT100_SR1_V80p11_Ih4p35" 
    ExtDir = "pT100_SR1_V80p11_PrevisionRun3"
    print("Will run on {} region, with pt cut = {}".format(regionSignal, ptCUT))

    date = USED_DATE[:-1]
    dateName = date + "_EntireShape"

    thresh = 100000000

    print("Will create datacards from signals and data with code version {}, for SR = {}, and pT cut = {}".format(version,SR,ptCUT))

    text_file_tex = open('yieldDir/yield'+regionSignal+'_pT'+ptCUT+'_2017_'+dateName+'.tex', "w")
    text_file_tex.write('\n \\documentclass{article}')
    text_file_tex.write('\n \\begin{document}')
    text_file_tex.write('\n \\begin{center}')
    text_file_tex.write('\n \\begin{tabular}{ |l|c|c| } ')
    text_file_tex.write('\n \hline')
    text_file_tex.write('\n Yield '+regionSignal+' & Pred. & Signal \\\\')
    text_file_tex.write('\n \hline')
    text_file_tex.write('\n \hline')

    text_file_tex_2018 = open('yieldDir/yield'+regionSignal+'_pT'+ptCUT+'_2018_'+dateName+'.tex', "w")
    text_file_tex_2018.write('\n \\documentclass{article}')
    text_file_tex_2018.write('\n \\begin{document}')
    text_file_tex_2018.write('\n \\begin{center}')
    text_file_tex_2018.write('\n \\begin{tabular}{ |l|c|c| } ')
    text_file_tex_2018.write('\n \hline')
    text_file_tex_2018.write('\n Yield '+regionSignal+' & Pred. & Signal \\\\')
    text_file_tex_2018.write('\n \hline')
    text_file_tex_2018.write('\n \hline')

    # load root file
    pathSignal = "/opt/sbg/cms/ui3_data1/rhaeberl/HSCP_prod/V"+version+"/HSCPpairStau_V"+version+"/Merged_HSCPpairStau/"

    yearSignal='2018'
    ofileBase = rt.TFile("base.root","RECREATE")

    fpath['pairStau200_2018'] = 'HSCPpairStauM-200.root'
    fpath['pairStau247_2018'] = 'HSCPpairStauM-247.root'
    fpath['pairStau308_2018'] = 'HSCPpairStauM-308.root'
    fpath['pairStau432_2018'] = 'HSCPpairStauM-432.root'
    fpath['pairStau557_2018'] = 'HSCPpairStauM-557.root'
    fpath['pairStau651_2018'] = 'HSCPpairStauM-651.root'
    fpath['pairStau745_2018'] = 'HSCPpairStauM-745.root'
    fpath['pairStau871_2018'] = 'HSCPpairStauM-871.root'
    fpath['pairStau1029_2018'] = 'HSCPpairStauM-1029.root'

    fpath['DYcharge1e100_2018'] = 'HSCPDYcharge1eM-100.root'
    fpath['DYcharge1e200_2018'] = 'HSCPDYcharge1eM-200.root'
    fpath['DYcharge1e400_2018'] = 'HSCPDYcharge1eM-400.root'
    fpath['DYcharge1e500_2018'] = 'HSCPDYcharge1eM-500.root'
    fpath['DYcharge1e800_2018'] = 'HSCPDYcharge1eM-800.root'
    fpath['DYcharge1e1000_2018'] = 'HSCPDYcharge1eM-1000.root'
    fpath['DYcharge1e1800_2018'] = 'HSCPDYcharge1eM-1800.root'
    fpath['DYcharge1e2200_2018'] = 'HSCPDYcharge1eM-2200.root'
    fpath['DYcharge1e2600_2018'] = 'HSCPDYcharge1eM-2600.root'

    fpath['DYcharge2e100_2018'] = 'HSCPDYcharge2eM-100.root'
    fpath['DYcharge2e200_2018'] = 'HSCPDYcharge2eM-200.root'
    fpath['DYcharge2e400_2018'] = 'HSCPDYcharge2eM-400.root'
    fpath['DYcharge2e500_2018'] = 'HSCPDYcharge2eM-500.root'
    fpath['DYcharge2e1400_2018'] = 'HSCPDYcharge2eM-1400.root'
    fpath['DYcharge2e1800_2018'] = 'HSCPDYcharge2eM-1800.root'
    fpath['DYcharge2e2200_2018'] = 'HSCPDYcharge2eM-2200.root'
    fpath['DYcharge2e2600_2018'] = 'HSCPDYcharge2eM-2600.root'

    searchRegion=regionSignal

    ofileBase.cd()
       
    name = {
        'pairStau200_2018': '$\\tilde{\\tau}$ (M=200 GeV)',
        'pairStau247_2018': '$\\tilde{\\tau}$ (M=247 GeV)',
        'pairStau308_2018': '$\\tilde{\\tau}$ (M=308 GeV)',
        'pairStau432_2018': '$\\tilde{\\tau}$ (M=432 GeV)',
        'pairStau557_2018': '$\\tilde{\\tau}$ (M=557 GeV)',
        'pairStau651_2018': '$\\tilde{\\tau}$ (M=651 GeV)',
        'pairStau745_2018': '$\\tilde{\\tau}$ (M=745 GeV)',
        'pairStau871_2018': '$\\tilde{\\tau}$ (M=871 GeV)',
        'pairStau1029_2018': '$\\tilde{\\tau}$ (M=1029 GeV)',

        'DYcharge1e100_2018': "$\\tau'^{1e}$ (M=100 GeV)",
        'DYcharge1e200_2018': "$\\tau'^{1e}$ (M=200 GeV)",
        'DYcharge1e400_2018': "$\\tau'^{1e}$ (M=400 GeV)",
        'DYcharge1e500_2018': "$\\tau'^{1e}$ (M=500 GeV)",
        'DYcharge1e800_2018': "$\\tau'^{1e}$ (M=800 GeV)",
        'DYcharge1e1000_2018': "$\\tau'^{1e}$ (M=1000 GeV)",
        'DYcharge1e1800_2018': "$\\tau'^{1e}$ (M=1800 GeV)",
        'DYcharge1e2200_2018': "$\\tau'^{1e}$ (M=2200 GeV)",
        'DYcharge1e2600_2018': "$\\tau'^{1e}$ (M=2600 GeV)",

        'DYcharge2e100_2018': "$\\tau'^{2e}$ (M=100 GeV)",
        'DYcharge2e200_2018': "$\\tau'^{2e}$ (M=200 GeV)",
        'DYcharge2e400_2018': "$\\tau'^{2e}$ (M=400 GeV)",
        'DYcharge2e500_2018': "$\\tau'^{2e}$ (M=500 GeV)",
        'DYcharge2e1400_2018': "$\\tau'^{2e}$ (M=1400 GeV)",
        'DYcharge2e1800_2018': "$\\tau'^{2e}$ (M=1800 GeV)",
        'DYcharge2e2200_2018': "$\\tau'^{2e}$ (M=2200 GeV)",
        'DYcharge2e2600_2018': "$\\tau'^{2e}$ (M=2600 GeV)",
    }

    target={        
        'pairStau200_2018': 200,
        'pairStau247_2018': 247,
        'pairStau308_2018': 308,
        'pairStau432_2018': 432,
        'pairStau557_2018': 557,
        'pairStau651_2018': 651,
        'pairStau745_2018': 745,
        'pairStau871_2018': 871,
        'pairStau1029_2018': 1029,
        'DYcharge1e100_2018':100,
        'DYcharge1e200_2018':200,
        'DYcharge1e400_2018':400,
        'DYcharge1e500_2018':500,
        'DYcharge1e800_2018':800,
        'DYcharge1e1000_2018':1000,
        'DYcharge1e1800_2018':1800,
        'DYcharge1e2200_2018':2200,
        'DYcharge1e2600_2018':2600,
        'DYcharge2e100_2018':100,
        'DYcharge2e200_2018':200,
        'DYcharge2e400_2018':400,
        'DYcharge2e500_2018':500,
        'DYcharge2e1400_2018':1400,
        'DYcharge2e1800_2018':1800,
        'DYcharge2e2200_2018':2200,
        'DYcharge2e2600_2018':2600,

    }


    outDataCardsDir = "datacards_"+searchRegion+"_pt"+ ptCUT +"_" + dateName + "_PrevisionRun3/"
    #outDataCardsDir = "datacards_"+searchRegion+"_pt"+ ptCUT +"_" + dateName +"/"
    if os.path.exists(outDataCardsDir): 
        os.system("rm -rdf {0}".format(outDataCardsDir))

    os.system("mkdir -p {0}".format(outDataCardsDir))

    h2=rt.TH2F("h2",";Target Mass [GeV];Mass Window [GeV];[a.u.]",120,0,3000,400,0,4000)

    for signal,value in fpath.items():
        print signal
        ofileBase.cd()
        targetMass=target[signal]

        shapeNames_unc = ["pu","pT","trigger","fpix","muTrigger","muReco","muId","toferr"]
        numberBins = 27
        bkgShapes_unc = ["Bin{}".format(i) for i in range(1, numberBins + 1)]

        year2017 = "2017"
        year2018 = "2018"
        base_text_2017 = "signal_Ch{}_".format(year2017)
        base_text_2018 = "signal_Ch{}_".format(year2018)
        
        shapeDirecUp_2017 = [base_text_2017 + "{}".format(nameu) for nameu in shapeNames_unc]
        shapeDirecDown_2017 = [base_text_2017 + "{}".format(nameu) for nameu in shapeNames_unc]
  
        shapeDirecUp_2018 = [base_text_2018 + "{}".format(nameu) for nameu in shapeNames_unc] 
        shapeDirecDown_2018 = [base_text_2018 + "{}".format(nameu) for nameu in shapeNames_unc]

        '''
        last_two = value.split("_")[-3:-1]
        two_joined = '_'.join(last_two) + '.root'
        new = two_joined[7:].split("_")
        t1 = new[0][6:]+new[1]
        
        name_sig = "MassShapeHistos_pT" + ptCUT + "_"+searchRegion+ "_V" + version+ '/Histos_massShape_' + t1
        '''
        name_sig = "Histos_massShape_"+value

        pathSF = '/opt/sbg/cms/ui4_data1/rhaeberl/CMSSW_10_6_30/src/HSCPTreeAnalyzer/python/FINAL_BKG_PRED/V'+version+'/'+ date + '_pt' + ptCUT + '/'
        SF_txt = [pathSF+'2017_SF_CR_SRs_stau.txt', pathSF+'2018_SF_CR_SRs_stau.txt']
        year = ['2017','2018']

        ScaleFactors = []

        for idx_high,file_high in enumerate(SF_txt):
            with open(file_high, 'r') as file2:
                lines2 = file2.readlines()
                for line in lines2:
                    if searchRegion in line:
                        value = float(line.split(':')[1].strip())
                        print("Adding SF for high_ih channel in year {} and SR {} as : {}".format(year[idx_high],searchRegion,value))
                        ScaleFactors.append(value)

        print("Just before making datacards")
        #FIRST TRY

        make_datacard_hscp_combining2017and2018(outDataCardsDir,  signal,name_sig, -1, -1, -1, -1,-1,-1, shapeDirecUp_2017, shapeDirecDown_2017, shapeDirecUp_2018, shapeDirecDown_2018,shapeNames_unc,bkgShapes_unc,False,ScaleFactors,ExtDir,thresh)

        


    text_file_tex.write('\n \\end{tabular}')
    text_file_tex.write('\n \\end{center}')
    text_file_tex.write('\n \\end{document}')

    text_file_tex.close()
            

    text_file_tex_2018.write('\n \\end{tabular}')
    text_file_tex_2018.write('\n \\end{center}')
    text_file_tex_2018.write('\n \\end{document}')

    text_file_tex_2018.close()
            

    tdrstyle.setTDRStyle()
    CMS_lumi.cmsText     = "CMS"
    iPos = 0
    CMS_lumi.extraText = "Internal"
    CMS_lumi.writeExtraText=True

    if( iPos==0 ): CMS_lumi.relPosX = 0.12
    # CMS_lumi.CMS_lumi(c, 4, 0)
    CMS_lumi.lumi_13TeV  = "101 fb^{-1}"
    
        
    rt.gStyle.SetOptStat(0)
    c1=rt.TCanvas()
    h2.Draw("col")
    h2.GetXaxis().SetTitleSize(0.04)
    h2.GetYaxis().SetTitleSize(0.04)
    h2.GetXaxis().SetTitleOffset(1.5)
    h2.GetYaxis().SetTitleOffset(2)
    CMS_lumi.CMS_lumi(c1, 4, iPos)

    masswinPath = "mass_window_"+searchRegion +'_pt'+ ptCUT +"_"+dateName+ "/"
    if not os.path.exists(masswinPath):
        print("Directory does not exist. Creating directory...")
        os.makedirs(masswinPath)
        print("Directory created:", masswinPath)

    c1.SaveAs(masswinPath+ "h2_massWindow"+regionSignal+".root")
    c1.SaveAs(masswinPath+ "h2_massWindow"+regionSignal+".pdf")

    c2=rt.TCanvas("c","c",800,800)
    c2.SetGridx()
    c2.SetGridy()

    CMS_lumi.CMS_lumi(c2, 4, iPos)
    systPath = "systTargetMass_"+searchRegion +'_pt'+ ptCUT + "/"
    if not os.path.exists(systPath):
        print("Directory does not exist. Creating directory...")
        os.makedirs(systPath)
        print("Directory created:", systPath)
    c2.SaveAs(systPath + "systTargetMass_"+systSignal+"_"+regionSignal+".root")
    c2.SaveAs(systPath + "systTargetMass_"+systSignal+"_"+regionSignal+".pdf")
