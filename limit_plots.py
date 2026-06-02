import ROOT as rt
# import root_numpy as rtnp
import csv
import re
import sys
import collections
import os
sys.argv.append(' -b- ')

from collections import OrderedDict
import uproot
import numpy as np
from histo_utilities import std_color_list, create_TGraph, find_intersect,make_smooth_graph

rt.gROOT.SetBatch(True)

import CMS_lumi, tdrstyle
a = tdrstyle.setTDRStyle()
CMS_lumi.writeExtraText = 0

tdrstyle.setTDRStyle()

print(sys.version)


odirectory = 'limit_plots_dir'
os.system('mkdir -p ' + odirectory)
ofile_name = odirectory +"/Asymptotic_"+labelSignal+"_"+labelSR

searchRegion='SR3'
labelSR=searchRegion+'_ReRunGael'

#labelSignal="ppStau"
#labelSignal="gluino"
#labelSignal="stop"
#labelSignal="DYQ1"
#labelSignal="DYQ2"

intersect_bool=True

xsec_list = 'xSec.dat'
#models = ['HSCPgluinoOnlyNeutral', 'gluino', 'gmsbStau', 'pairStau', 'stopOnlyNeutral', 'stop', 'tauPrimeCharge1e', 'tauPrimeCharge2e']
#models = [ 'gluino', 'gmsbStau', 'pairStau', 'stop', 'DYcharge1e', 'DYcharge2e']
models = []
if(labelSignal=="gluino"):
    models = [ 'gluino' ]
elif(labelSignal=="ppStau"):
    models = [ 'pairStau' ]
elif(labelSignal=="stop"):
    models = [ 'stop' ]
elif(labelSignal=="DYQ1"):
    models = [ 'Charge1e' ]
elif(labelSignal=="DYQ2"):
    models = [ 'Charge2e' ]


data = np.loadtxt(xsec_list, dtype=str)
xsec_hscp = {}
sample_names = []
for i in range(len(data)):
    if ('HSCP' in data[i,0]):
        name = data[i,0][:data[i,0].find('_TuneCP5')]
        print name
        xsec_hscp[name] = float(data[i, 1])
        flag = 0
        for m in models:
            if m in name:flag = 1
        if flag == 0:continue
        sample_names.append(name)

signal_names = {}
for m in models:
    mass = []
    signal_names[m] = []
    for s in sample_names:
        if m+'_' in s:
            signal_names[m].append(s)
            mass.append(int(s[s.find('M-')+2:]))
    mass = np.array(mass)
    inds = mass.argsort()
    signal_names[m] = list(np.array(signal_names[m])[inds])

print 'sample names, signal names',sample_names, signal_names

signal = []
for k,v in signal_names.items(): signal += v
print 'signal',signal

limitTrees =OrderedDict()
dataCards = OrderedDict()
limits = OrderedDict()


#dataCardDir = 'mass_shape_analysis_dir/'
#limitDir = 'mass_shape_analysis_dir_limits/'

if searchRegion=='SR1':
    dataCardDir = 'datacards_SR1_test_UnB_v4_Raph_withGoodSignals/'
    limitDir = 'limitTrees_SR1_test_UnB_v4_Raph_withGoodSignals/'

if searchRegion=='SR2':
    dataCardDir = 'datacards_SR2_test_UnB_v4_Raph_withGoodSignals/'
    limitDir = 'limitTrees_SR2_test_UnB_v4_Raph_withGoodSignals/'

if searchRegion=='SR3':
    dataCardDir = 'datacards_SR3_ReRunGael/'
    limitDir = 'limitTrees_SR3_ReRunGael/'
    #limitDir = 'limitTrees_SR3_ReRunGael_CLS/'

for s in signal:
    print 'signal:', s
    limitTrees[s] = {}
    dataCards[s] = {}
    if 'gluino' in s:
        name = s.replace('HSCPg', 'G')
    elif 'Stau' in s:
        name = s.replace('HSCP', '')
    elif 'stop' in s:
        name = s.replace('HSCPs', 'S')
    elif 'HSCPtauPrimeCharge1e' in s:
        name = s.replace('HSCPtauPrimeCharge1e_M-', 'DYcharge1e_')
    elif 'HSCPtauPrimeCharge2e' in s:
        name = s.replace('HSCPtauPrimeCharge2e_M-', 'DYcharge2e_')
    name = name.replace('_M-', '')
    print 'name:', name
    dataCards[s] = dataCardDir + '{}_2018.txt'.format(name)
    print 'datacard:', dataCards[s]
    limitTrees[s] = limitDir + 'higgsCombine.{}'.format(name) + '_2018.AsymptoticLimits.mH120.root'
    print (limitDir + 'higgsCombine.{}'.format(name) + '_2018.AsymptoticLimits.mH120.root')

for i,m in enumerate(limitTrees.keys()):
    if not os.path.isfile(dataCards[m]):
        continue
    if len(uproot.open(limitTrees[m]).keys()) == 2:
        T = uproot.open(limitTrees[m])['limit']
        limits[m] = np.array(T.array('limit'))

print 'limits',limits

# load theoretical xsec
import json
path = 'xsec/json/'

filenames={}

if(labelSignal=="gluino"):
    filenames = {
        'gluino': 'pp13_gluino_NNLO+NNLL.json',
    }
elif(labelSignal=="ppStau"):
    filenames = {
        'pairStauLR':'pp13_slep_LR_NLO+NLL_PDF4LHC.json',
        #'pairStauLL':'pp13_slep_L_NLO+NLL_PDF4LHC.json',
        #'pairStauRR':'pp13_slep_R_NLO+NLL_PDF4LHC.json',
    }
elif(labelSignal=="stop"):
    filenames = {
        'stop':'pp13_stopsbottom_NNLO+NNLL.json',
    }
elif(labelSignal=="DYQ1"):
    filenames = {
        'DYQ1':'dy1e.json',
    }
elif(labelSignal=="DYQ2"):
    filenames = {
        'DYQ2':'dy2e.json',
    }

print filenames

mass = {}
theoretical_xsec = {}
for f, file in filenames.items():
    data = json.load(open( path + file))
    mass[f] = []
    theoretical_xsec[f] = []
    for k,v in data['data'].items():
        mass[f].append(int(k))
        theoretical_xsec[f].append(float(v['xsec_pb']))
    mass[f] = np.array(mass[f])
    theoretical_xsec[f] = np.array(theoretical_xsec[f])
    inds = mass[f].argsort()
    mass[f] = mass[f][inds]
    theoretical_xsec[f] = theoretical_xsec[f][inds]


# make plots

leg = rt.TLegend(0.55,0.58,0.87,0.88,'')
leg.SetHeader("95% CL Upper Limits")
leg.SetTextSize(0.03)
leg.SetBorderSize(0)
leg.SetEntrySeparation(0.01)

c = rt.TCanvas('c','c', 700, 600)

c.SetLeftMargin(.15)
c.SetBottomMargin(.15)
c.SetTopMargin(0.1)
c.SetRightMargin(0.05)

c.SetFrameLineWidth(1)

rt.gStyle.SetOptFit(1011)

h = {}
h_exp1sig = {}
h_exp2sig = {}
h_obs = {}
h_others = {}
for i, k in enumerate(mass.keys()):
    h[k+'theoretical'] = create_TGraph(mass[k]/1000.,theoretical_xsec[k],  axis_title=['mass [TeV]', 'Cross Section [pb]'])
    h[k+'theoretical'].SetLineColor(4)
    h[k+'theoretical'].SetLineStyle(1)
    h[k+'theoretical'].SetLineWidth(1)
   
    #h[k+'theor_up'] = create_TGraph(mass[k]/1000.,1.1*theoretical_xsec[k],  axis_title=[''])
    #h[k+'theor_down'] = create_TGraph(mass[k]/1000.,0.9*theoretical_xsec[k],  axis_title=[''])
    h[k+'theor_smooth'] = make_smooth_graph(create_TGraph(mass[k]/1000.,0.9*theoretical_xsec[k],  axis_title=['']), create_TGraph(mass[k]/1000.,1.1*theoretical_xsec[k],  axis_title=['']))

    h[k+'theor_smooth'].SetLineColor(4)
    h[k+'theor_smooth'].SetLineStyle(7)
    h[k+'theor_smooth'].SetLineWidth(1)
    h[k+'theor_smooth'].SetMarkerSize(0.5)
    '''
    if(i==0):
        h[k+'theoretical'].SetLineColor(4)
        h[k+'theor_up'].SetLineColor(4)
        h[k+'theor_down'].SetLineColor(4)
        h[k+'theor_smooth'].SetLineColor(4)
    if(i==1):
        h[k+'theoretical'].SetLineColor(6)
        h[k+'theor_up'].SetLineColor(6)
        h[k+'theor_down'].SetLineColor(6)
        h[k+'theor_smooth'].SetLineColor(6)
    if(i==2):
        h[k+'theoretical'].SetLineColor(2)
        h[k+'theor_up'].SetLineColor(2)
        h[k+'theor_down'].SetLineColor(2)
        h[k+'theor_smooth'].SetLineColor(2)
    '''

for i, m in enumerate(signal_names.keys()):
    x = []
    y_obs = []
    y = []
    y_up = []
    y_up2 = []
    y_down = []
    y_down2 = []
    xAxisName = []
    for key in limits.keys():
        print 'key:', key
        if m in key and len(limits[key])>0:
            if ('gluino' in key):
                xAxisName =['m(#tilde{g}) [TeV]','Cross Section [pb]']
            if('Stau' in key):
                xAxisName =['m(#tilde{#tau}) [TeV]','Cross Section [pb]']
            if('stop' in key):
                xAxisName =['m(#tilde{t}) [TeV]','Cross Section [pb]']
            if('HSCPtauPrimeCharge1e' in key):
                xAxisName =["m(#tau'^{1e}) [TeV]",'Cross Section [pb]']
            if('HSCPtauPrimeCharge2e' in key):
                xAxisName =["m(#tau'^{2e}) [TeV]",'Cross Section [pb]']
              

            if (('gluino' in key) or ('Stau' in key) or ('stop' in key) or ('HSCPtauPrimeCharge1e' in key) or ('HSCPtauPrimeCharge2e' in key)):
                print 'xsec key', xsec_hscp[key]
                y.append(limits[key][2]*xsec_hscp[key])
                y_up.append(limits[key][3]*xsec_hscp[key])
                y_up2.append(limits[key][4]*xsec_hscp[key])
                y_down.append(limits[key][1]*xsec_hscp[key])
                y_down2.append(limits[key][0]*xsec_hscp[key])

                y_obs.append(limits[key][5]*xsec_hscp[key])
              
            x.append(float(key[key.find('M-')+2:])/1000.)
            print x

    if len(x) ==0 :continue


    #h_obs[m+'_'+labelSR] = create_TGraph(x,y_obs,  axis_title=['mass [TeV]', '95% CL Limit on #sigma [pb]'])
    h_obs[m+'_'+labelSR] = create_TGraph(x,y_obs,axis_title=xAxisName) 
    h[m+'_'+labelSR] = create_TGraph(x,y,axis_title=xAxisName)

    xtmp = np.array(x,dtype=np.float64)
    yup2_tmp = np.array(y_up2,dtype=np.float64)
    ydown2_tmp = np.array(y_down2,dtype=np.float64)
    yup_tmp = np.array(y_up,dtype=np.float64)
    ydown_tmp = np.array(y_down,dtype=np.float64)

    g_mc2plus = rt.TGraph(len(x), xtmp, yup2_tmp)
    g_mc2plus.GetXaxis().SetTitle(xAxisName[0])
    g_mc2plus.GetYaxis().SetTitle(xAxisName[1])

    g_mc2minus = rt.TGraph(len(x), xtmp, ydown2_tmp)
    g_mc2minus.GetXaxis().SetTitle(xAxisName[0])
    g_mc2minus.GetYaxis().SetTitle(xAxisName[1])


    g_mcplus = rt.TGraph(len(x), xtmp, yup_tmp)
    g_mcplus.GetXaxis().SetTitle(xAxisName[0])
    g_mcplus.GetYaxis().SetTitle(xAxisName[1])
    g_mcminus = rt.TGraph(len(x), xtmp, ydown_tmp)
    g_mcminus.GetXaxis().SetTitle(xAxisName[0])
    g_mcminus.GetYaxis().SetTitle(xAxisName[1])

    '''
    h_exp1sig[m + '_'+labelSR] = make_smooth_graph(g_mcminus, g_mcplus) 
    h_exp1sig[m + '_'+labelSR].SetLineColor(0)
    h_exp2sig[m + '_'+labelSR] = make_smooth_graph(g_mc2minus, g_mc2plus)
    h_exp2sig[m + '_'+labelSR].SetLineColor(0)
    '''
    h_exp1sig[m + '_'+labelSR] = create_TGraph(np.hstack((x, np.flip(x))), np.hstack((y_down, np.flip(y_up))),axis_title=xAxisName)
    h_exp2sig[m + '_'+labelSR] = create_TGraph(np.hstack((x, np.flip(x))), np.hstack((y_down2, np.flip(y_up2))), axis_title=xAxisName)


for i, m in enumerate(h.keys()):
    print m 
    if('theoretical' in m):
        h[m].SetLineColor(4)
        if(labelSignal=="gluino"):
            leg.AddEntry(h[m],"#sigma_{th}^{NNLO+NNLL} (pp #rightarrow #tilde{g}#tilde{g})", "L")
        elif(labelSignal=="stop"):
            leg.AddEntry(h[m],"#sigma_{th}^{NNLO+NNLL} (pp #rightarrow #tilde{t}#tilde{t})", "L")
        elif(m=="pairStauRRtheoretical"):
            leg.AddEntry(h[m],"#sigma_{th}^{NLO+NLL} (pp #rightarrow #tilde{#tau}_{R}#tilde{#tau}_{R})", "L")
            h[m].SetLineColor(6)
        elif(m=="pairStauLLtheoretical"):
            leg.AddEntry(h[m],"#sigma_{th}^{NLO+NLL} (pp #rightarrow #tilde{#tau}_{L}#tilde{#tau}_{L})", "L")
            #leg.AddEntry(h[m],"#sigma_{th}^{NLO+NLL} (pp #rightarrow #tilde{#tau}_{L}#tilde{#tau}_{L})#pm1#sigma", "L")
            h[m].SetLineColor(4)
        elif(m=="pairStauLRtheoretical"):
            leg.AddEntry(h[m],"#sigma_{th}^{NLO+NLL} (pp #rightarrow #tilde{#tau}_{L/R}#tilde{#tau}_{L/R})", "L")
            h[m].SetLineColor(2)
        elif(m=="DYQ1theoretical"):
            leg.AddEntry(h[m],"#sigma_{th}^{NLO+NLL} (pp #rightarrow #tilde{#tau}\'^{1e}#tilde{#tau}\'^{1e})", "L")
            h[m].SetLineColor(2)
        elif(m=="DYQ2theoretical"):
            leg.AddEntry(h[m],"#sigma_{th}^{NLO+NLL} (pp #rightarrow #tilde{#tau}\'^{2e}#tilde{#tau}\'^{2e})", "L")
            h[m].SetLineColor(2)
        
    else:
        if('theor' not in m):
            leg.AddEntry(h[m],"Median expected", "L")
            h[m].SetLineColor(1)
            h[m].SetTitle("median_expected_title")
            h[m].SetName("median_expected")

    h[m].SetLineWidth(3)

    h[m].SetLineStyle(2)
    if('theoretical' in m):
        h[m].SetLineStyle(1)
        h[m].SetLineWidth(1)

    if('smooth' in m):
        h[m].SetLineStyle(2) 
        h[m].SetLineColor(4) 
        h[m].SetLineWidth(1)
 
    h[m].SetLineWidth(3)

    h[m].GetXaxis().SetLabelFont(42)
    h[m].GetXaxis().SetTitleFont(42)
    
    h[m].GetYaxis().SetLabelFont(42)
    h[m].GetYaxis().SetTitleFont(42)
    h[m].GetYaxis().SetLabelSize(10)


    h[m].GetXaxis().SetTitleOffset(0.9)
    h[m].GetXaxis().SetLabelSize(10)
    h[m].GetXaxis().SetTitleSize(0.005)
    h[m].GetYaxis().SetTitleSize(0.005)
    h[m].GetYaxis().SetTitleOffset(1.7)


for i,m in enumerate(h.keys()):
    if 'theoretical' in m or 'theor' in m or 'smooth' in m:
        continue

    h_exp1sig[m].SetFillColor(rt.kGreen+1)
    h_exp1sig[m].SetTitle("1sigma_expected_title")
    h_exp1sig[m].SetName("1sigma_expected")

    h_exp2sig[m].SetFillColor(rt.kOrange)
    h_exp2sig[m].SetTitle("2sigma_expected_title")
    h_exp2sig[m].SetName("2sigma_expected")

    h_exp2sig[m].Draw('AF')
    h_exp1sig[m].Draw('Fsame')
    h_obs[m].SetMarkerStyle(20)
    #h_obs[m].Draw("LP,same")
    h_exp1sig[m].GetXaxis().SetLabelSize(0.02)

    h_exp2sig[m].GetXaxis().SetTitleSize(0.05)
    h_exp2sig[m].GetYaxis().SetTitleSize(0.05)

    h_exp2sig[m].GetXaxis().SetLabelSize(0.05)
    h_exp2sig[m].GetYaxis().SetLabelSize(0.05)

    h_exp2sig[m].GetXaxis().SetLabelFont(42)
    h_exp2sig[m].GetYaxis().SetLabelFont(42)

    h_exp2sig[m].GetXaxis().SetTitleOffset(1.5)
    h_exp2sig[m].GetYaxis().SetTitleOffset(1.5)

    if(labelSignal=="gluino"):
        h_exp1sig[m].GetYaxis().SetRangeUser(5e-5,0.2)
        h_exp2sig[m].GetYaxis().SetRangeUser(5e-5,0.2)
        h_exp2sig[m].GetXaxis().SetRangeUser(0.62,2.78)
    elif(labelSignal=="ppStau"):
        h_exp1sig[m].GetYaxis().SetRangeUser(5e-6,0.02)
        h_exp2sig[m].GetYaxis().SetRangeUser(5e-6,0.02)
        h_exp2sig[m].GetXaxis().SetRangeUser(0.2359,1.1011)
    elif(labelSignal=="stop"):
        h_exp1sig[m].GetYaxis().SetRangeUser(5e-5,0.2)
        h_exp2sig[m].GetYaxis().SetRangeUser(5e-5,0.2)
        h_exp2sig[m].GetXaxis().SetRangeUser(0.18,2.82)

    #leg.AddEntry(h_exp2sig[m], "Expected Limit #pm1#sigma, #pm2#sigma","lep")
    leg.AddEntry(h_exp1sig[m],"68% expected","f")
    leg.AddEntry(h_exp2sig[m],"95% expected","f")
    #leg.AddEntry(h_obs[m],"Observed Limit","LP")


for i,m in enumerate(h.keys()):
    if(labelSignal=="gluino"):
        h[m].GetXaxis().SetLimits(400,2700.0)
        h[m].GetYaxis().SetRangeUser(1e-4,2e-2)
    elif(labelSignal=="ppStau"):
        h[m].GetXaxis().SetRangeUser(100,1125.0)
        h[m].GetYaxis().SetRangeUser(5e-6,2e-2)
    elif(labelSignal=="stop"):
        h[m].GetXaxis().SetLimits(700,1000.0)
        h[m].GetYaxis().SetRangeUser(5e-6,2e-2)
    elif(labelSignal=="DYQ1"):
        h[m].GetXaxis().SetLimits(200,2200.0)
        h[m].GetYaxis().SetRangeUser(5e-7,1e-2)
    elif(labelSignal=="DYQ2"):
        h[m].GetXaxis().SetLimits(200,2200.0)
        h[m].GetYaxis().SetRangeUser(5e-7,1e-2)
   
    if 'smooth' in m:
        continue
    h[m].Draw('Lsame')


c.RedrawAxis()
CMS_lumi.lumiTextSize     = 0.5
CMS_lumi.cmsTextSize      = 0.8

CMS_lumi.extraText = "Internal"
CMS_lumi.writeExtraText=True
'''
CMS_lumi.cmsText     = "CMS"
iPos = 0
CMS_lumi.extraText = ""
CMS_lumi.writeExtraText=True
if( iPos==0 ): CMS_lumi.relPosX = 0.12
CMS_lumi.lumi_13TeV  = "100 fb^{-1}"
'''

CMS_lumi.CMS_lumi(c, 1, 11)

leg.Draw()
c.SetLogy()
#c.SetTicky(1)
#c.SetTickx(1)

c.Draw()

c.SaveAs(ofile_name+".root")
c.SaveAs(ofile_name+".pdf")

if(labelSignal=="gluino" and intersect_bool==True):
    print('gluino', find_intersect(h['gluino_'+labelSR],h['gluinotheoretical']))
    print('gluino1', find_intersect(h_exp1sig['gluino_'+labelSR],h['gluinotheoretical']))
    print('gluino2', find_intersect(h_exp2sig['gluino_'+labelSR],h['gluinotheoretical']))
    print('obs', find_intersect(h_obs['gluino_'+labelSR],h['gluinotheoretical']))
elif(labelSignal=="ppStau" and intersect_bool==True):
    #print('pairStauRR', find_intersect(h['pairStau_'+labelSR],h['pairStauRRtheoretical']))
    #print('1sigma', find_intersect(h_exp1sig['pairStau_'+labelSR],h['pairStauRRtheoretical']))
    #print('2sigma', find_intersect(h_exp2sig['pairStau_'+labelSR],h['pairStauRRtheoretical']))
    #print('obs', find_intersect(h_obs['pairStau_'+labelSR],h['pairStauRRtheoretical']))
    #print('pairStauLL', find_intersect(h['pairStau_'+labelSR],h['pairStauLLtheoretical']))
    #print('1sigma', find_intersect(h_exp1sig['pairStau_'+labelSR],h['pairStauLLtheoretical']))
    #print('2sigma', find_intersect(h_exp2sig['pairStau_'+labelSR],h['pairStauLLtheoretical']))
    #print('obs', find_intersect(h_obs['pairStau_'+labelSR],h['pairStauLLtheoretical']))
    print('pairStauLR', find_intersect(h['pairStau_'+labelSR],h['pairStauLRtheoretical']))
    print('1sigma', find_intersect(h_exp1sig['pairStau_'+labelSR],h['pairStauLRtheoretical']))
    print('2sigma', find_intersect(h_exp2sig['pairStau_'+labelSR],h['pairStauLRtheoretical']))
    print('obs', find_intersect(h_obs['pairStau_'+labelSR],h['pairStauLRtheoretical']))
elif(labelSignal=="stop" and intersect_bool==True):
    print('stop', find_intersect(h['stop_'+labelSR],h['stoptheoretical']))
    print('stop1', find_intersect(h_exp1sig['stop_'+labelSR],h['stoptheoretical']))
    print('stop2', find_intersect(h_exp2sig['stop_'+labelSR],h['stoptheoretical']))
    print('obs', find_intersect(h_obs['stop_'+labelSR],h['stoptheoretical']))
elif(labelSignal=="DYQ1" and intersect_bool==True):
    print('DYQ1', find_intersect(h['Charge1e_'+labelSR],h['DYQ1theoretical']))
    print('1sigma', find_intersect(h_exp1sig['Charge1e_'+labelSR],h['DYQ1theoretical']))
    print('2sigma', find_intersect(h_exp2sig['Charge1e_'+labelSR],h['DYQ1theoretical']))
    print('obs', find_intersect(h_obs['Charge1e_'+labelSR],h['DYQ1theoretical']))
elif(labelSignal=="DYQ2" and intersect_bool==True):
    print('DYQ2', find_intersect(h['Charge2e_'+labelSR],h['DYQ2theoretical']))
    print('1sigma', find_intersect(h_exp1sig['Charge2e_'+labelSR],h['DYQ2theoretical']))
    print('2sigma', find_intersect(h_exp2sig['Charge2e_'+labelSR],h['DYQ2theoretical']))
    print('obs', find_intersect(h_obs['Charge2e_'+labelSR],h['DYQ2theoretical']))
