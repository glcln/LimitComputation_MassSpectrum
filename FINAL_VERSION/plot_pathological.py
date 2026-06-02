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

gStyle.SetOptStat(0)
gROOT.SetBatch(kTRUE)

parser = OptionParser()



# Initialize arrays to eventually store the points on the TGraph

tdrstyle.setTDRStyle()
markerColor = [9,8,1,46,40,2]
markerStyle = [20,23,22,21,49,39]
entryLeg = ["Observed","-2#sigma","-1#sigma","Median expected","+1#sigma","+2#sigma"]
iDir = '/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/tst_hybrid_v3/'
names = ["Stop1000","Stop1200","Stop1400","Stop1600","Stop1800","Stop2000","Stop2200","Stop2400","Stop2600"]
ext = ["higgsCombine."+names[i]+"_2018.HybridNew.all.mH120.root" for i in range(len(names))]

massPoints = [1.,1.2,1.4,1.6,1.8,2.,2.2,2.4,2.6]
quantiles = [-1,0.025, 0.16, 0.5, 0.84, 0.975]

def is_sorted(lst):
    return all(lst[i] <= lst[i + 1] for i in range(len(lst) - 1))

def get_values_from_file(file_path):
    this_output = TFile.Open(file_path)
    
    if not this_output: 
        print("No root file opened")
        exit()

    this_tree = this_output.Get('limit')

    quantiles = []
    limits = []
    limits_err = []
    for ievent in range(int(this_tree.GetEntries())):
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

    return sorted_limits_err,sorted_limits


def get_values_given_quantile(file_paths,quantile):
    this_output = TFile.Open(file_path)
    
    if not this_output: 
        print("No root file opened")
        exit()

    this_tree = this_output.Get('limit')

    quantiles = []
    limits = []
    limits_err = []
    for ievent in range(int(this_tree.GetEntries())):
        this_tree.GetEntry(ievent)
        if(round(this_tree.quantileExpected,3) == quantile):
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

    return sorted_limits_err,sorted_limits


def plot_graphs(data_list):
    canvas = ROOT.TCanvas("canvas", "Graphs", 500, 500)
    canvas.cd()
    a = ROOT.TH1D("a","a",100,massPoints[0]-0.1,massPoints[-1]+0.1)
    gStyle.SetLegendFont(62)
    legend = ROOT.TLegend(0.15, 0.78, 0.45, 0.88)
    legend.SetFillStyle(0)
    a.SetMarkerSize(0)
    a.SetMarkerStyle(1)
    a.SetTitle("")
    a.GetYaxis().SetTitleOffset(1.5)
    a.GetYaxis().SetTitleSize(0.035)
    a.GetYaxis().SetLabelSize(0.025)
    a.GetXaxis().SetLabelSize(0.025)
    a.GetXaxis().SetTitle("Mass [TeV]")
    a.SetStats(False)
    a.GetXaxis().SetRangeUser(0.8,2.8)
    a.GetYaxis().SetRangeUser(0.00001,0.02)

    a.Draw("") 
    graphs = {}
    count = 0
    for quantile, data in data_list.items():
        graph = ROOT.TGraph()
        graph.SetTitle("")
        graph.SetMarkerStyle(20)
        graph.SetMarkerSize(0.7)
        graph.SetMarkerColor(markerColor[count])
        legend.AddEntry(graph,entryLeg[count],"p")
        for i, (mass_point, ratio) in enumerate(data):
            print("mass point = {}, ratio = {}".format(mass_point,ratio[count]))
            graph.SetPoint(i, mass_point, ratio[count])

        graph.Draw("same P")

        count+=1

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(1)
    latex.SetTextFont(52)
    latex.SetTextAlign(11)
    latex.SetTextSize(0.03)
    latex.DrawLatex(0.18, 0.938, "Private work      -    ")
    
    latex2 = ROOT.TLatex()
    latex2.SetNDC()
    latex2.SetTextAngle(0)
    latex2.SetTextColor(46)
    latex2.SetTextFont(52)
    latex2.SetTextAlign(11)
    latex2.SetTextSize(0.03)
    latex2.DrawLatex(0.42, 0.938, "Gluino")

    canvas.RedrawAxis() 
    canvas.SaveAs("testErrors.pdf")

def plot_graphs2(data_list):
    canvas = ROOT.TCanvas("canvas", "Graphs", 500, 500)
    canvas.cd()
    a = ROOT.TH1D("a","a",100,massPoints[0]-0.1,massPoints[-1]+0.1)
    gStyle.SetLegendFont(62)
    legend = ROOT.TLegend(0.18, 0.72, 0.54, 0.94)
    legend.SetFillStyle(0)
    a.SetMarkerSize(0)
    a.SetMarkerStyle(1)
    a.SetTitle("")
    a.GetYaxis().SetTitleOffset(1.5)
    a.GetYaxis().SetTitleSize(0.035)
    a.GetYaxis().SetLabelSize(0.035)
    a.GetXaxis().SetLabelSize(0.025)
    a.GetXaxis().SetTitleSize(0.04)
    a.GetXaxis().SetTitle("Mass [TeV]")
    a.GetYaxis().SetTitle("Cross-section relative error (%)")
    a.SetStats(False)
    a.GetXaxis().SetRangeUser(0.8,2.8)

    #a.GetYaxis().SetRangeUser(0.,4)
    a.GetYaxis().SetRangeUser(0.,2)

    a.Draw("") 





    '''
    ratiosObs = [0.0219,10,0.01280,0.0165,0.01835,0.01901,0.0132,0.0205,0.0182]
    ratiosm2sig = [0.0112,10,0.0172,0.0145,0.0181,0.0221,0.0120,0.0173,0.0191]
    ratiosm1sig = [0.0204,10,0.0209,0.00652,0.0226,0.00702,0.0157,0.01076,0.01691]
    ratiosExp = [0.0137,10,0.0186,0.0118,0.0145,0.0155,0.0134,0.0090,0.0125]
    ratiosp1sig = [0.0108,10,0.0110,0.0103,0.00943,0.0089,0.0109,0.00974,0.00957]
    ratiosp2sig = [0.0042,10,0.0182,0.0135,0.0118,0.0139,0.0124,0.01426,0.0107]
    '''


    #20k TOYS
    ratiosObs = [0.0105,10,0.0103,0.0120,0.01098,0.00820,0.00890,0.0121,0.0112]
    ratiosm2sig = [0.0067,10,0.01041,0.00983,0.01129,0.01213,0.0103,0.00694,0.0097]
    ratiosm1sig = [0.0099,10,0.00606,0.00524,0.00943,0.0102,0.00758,0.00659,0.010]
    ratiosExp = [0.00663,10,0.00665,0.004706,0.0089,0.00398,0.00726,0.00641,0.0061]
    ratiosp1sig = [0.00325,10,0.004397,0.004877,0.00399,0.003632,0.00369,0.003743,0.00272]
    ratiosp2sig = [0.00248,10,0.0040107,0.00244,0.00483,0.00345,0.00347,0.00356,0.004831]



    averages = [(sum(x) / len(x)) for x in zip(ratiosObs, ratiosm2sig, ratiosm1sig, ratiosExp, ratiosp1sig, ratiosp2sig)]
    #averages.pop(1)    



    ratiosAll = [ratiosObs,ratiosm2sig,ratiosm1sig,ratiosExp,ratiosp1sig,ratiosp2sig]


    graphobs = ROOT.TGraph()
    graphm2sig = ROOT.TGraph()
    graphm1sig = ROOT.TGraph()
    graphexp = ROOT.TGraph()
    graphp1sig = ROOT.TGraph()
    graphp2sig = ROOT.TGraph()
    graphAverage = ROOT.TGraph()
    graphAverage.SetLineColor(1)
    graphAverage.SetLineStyle(2)
    graphAverage.SetLineWidth(2)
    graphAll = [graphobs,graphm2sig,graphm1sig,graphexp,graphp1sig,graphp2sig]

    for i in range(len(averages)):
        if i == 0:
            graphAverage.SetPoint(i,massPoints[i],averages[i]*100)
        if i ==1:
            continue
        if i > 1:
            graphAverage.SetPoint(i-1,massPoints[i],averages[i]*100)
            

    for j in range(len(ratiosAll)):
        for i in range(len(ratiosAll[j])):
            graphAll[j].SetPoint(i,massPoints[i],ratiosAll[j][i]*100)
        

    for i in range(len(graphAll)): 
        #graphAll[i].SetMarkerStyle(20)
        graphAll[i].SetMarkerSize(0.7)
        graphAll[i].SetMarkerColor(markerColor[i]) 
        graphAll[i].SetMarkerStyle(markerStyle[i]) 
        graphAll[i].SetTitle("")
        legend.AddEntry(graphAll[i],entryLeg[i],"p")
        graphAll[i].Draw("same P")

    #legend.AddEntry(graphAverage,"Average relative error","l")
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(1)
    latex.SetTextFont(52)
    latex.SetTextAlign(11)
    latex.SetTextSize(0.03)
    latex.DrawLatex(0.16, 0.959, "Private work      -    ")
    
    latex2 = ROOT.TLatex()
    latex2.SetNDC()
    latex2.SetTextAngle(0)
    latex2.SetTextColor(46)
    latex2.SetTextFont(52)
    latex2.SetTextAlign(11)
    latex2.SetTextSize(0.03)
    latex2.DrawLatex(0.41, 0.959, "Gluino")
    legend.SetBorderSize(1)
    legend.Draw("same")
    #graphAverage.Draw("same l")
    canvas.RedrawAxis() 
    canvas.SaveAs("testErrors_20k.pdf")
#iDir = '/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/limitTrees_tamas/tst_hybrid_tamas/'

quantile_lists = {quantile: [] for quantile in quantiles}


for root_file,mass_point in zip(ext,massPoints):
    limit_errors, limits = get_values_from_file(iDir+root_file)
    for i, quantile in enumerate(quantiles):
        ratios = [error / limit for error, limit in zip(limit_errors, limits)]
        quantile_lists[quantile].append((mass_point, ratios))


for quantile, data_list in quantile_lists.items():
    print("Quantile: {}".format(quantile))
    for mass_point, ratios in data_list:
        print("Mass Point: {}, Ratios: {}".format(mass_point,ratios))

#plot_graphs(quantile_lists)
plot_graphs2(quantile_lists)
