from optparse import OptionParser
import subprocess
import array
from  array import array

import ROOT
from ROOT import *

import header
from header import WaitForJobs, make_smooth_graph, Inter
import tdrstyle, CMS_lumi


def GraphTheor(name,color,signal_mass,theory_xsecs):
    graphWP = ROOT.TGraph()
    graphWP.SetTitle(name)
    graphWP.SetMarkerStyle(23)
    graphWP.SetMarkerColor(color)
    graphWP.SetMarkerSize(0.5)
    graphWP.GetYaxis().SetRangeUser(5e-5, 0.2)
    graphWP.GetXaxis().SetRangeUser(0.2, 3.0)

    for index,mass in enumerate(signal_mass):
        xsec = theory_xsecs[index]
        graphWP.SetPoint(index,    mass,   xsec    )
    
    graphWP.SetLineWidth(3)
    graphWP.SetLineColor(color)
    return graphWP    

def GraphTheorUp(name,color,signal_mass,theory_xsecs):
    graphWP = ROOT.TGraph()
    graphWP.SetTitle(name+'up')
    graphWP.SetMarkerStyle(23)
    graphWP.SetMarkerColor(color)
    graphWP.SetMarkerSize(0.5)

    graphWP.GetYaxis().SetRangeUser(5e-5, 0.2)
    graphWP.GetXaxis().SetRangeUser(0.2, 3.0)


    for index,mass in enumerate(signal_mass):
        xsec = 1.1 * theory_xsecs[index]
        graphWP.SetPoint(index,    mass,   xsec    )
    
    graphWP.SetLineWidth(2)
    graphWP.SetLineColor(color)
    graphWP.SetLineStyle(2)
    return graphWP    

def GraphTheorDown(name,color,signal_mass,theory_xsecs):
    graphWP = ROOT.TGraph()
    graphWP.SetTitle(name+'down')
    graphWP.SetMarkerStyle(23)
    graphWP.SetMarkerColor(color)
    graphWP.SetMarkerSize(0.5)

    graphWP.GetYaxis().SetRangeUser(5e-5, 0.2)
    graphWP.GetXaxis().SetRangeUser(0.2, 3.0)


    for index,mass in enumerate(signal_mass):
        xsec = 0.9 * theory_xsecs[index]
        graphWP.SetPoint(index,    mass,   xsec    )
    
    graphWP.SetLineWidth(2)
    graphWP.SetLineColor(color)
    graphWP.SetLineStyle(2)
    return graphWP    

gStyle.SetOptStat(0)
gROOT.SetBatch(kTRUE)

parser = OptionParser()

# parser.add_option('-t', '--tag', metavar='FILE', type='string', action='store',
#                 default   =   'dataBsOff',
#                 dest      =   'tag',
#                 help      =   'Tag ran over')
parser.add_option('-s', '--signals', metavar='FILE', type='string', action='store',
                default   =   'bstar_signalsLH.txt',
                dest      =   'signals',
                help      =   'Text file containing the signal names and their corresponding cross sections')

(options, args) = parser.parse_args()

# Open signal file
signal_file = open(options.signals,'r')

names = ["#tilde{g}#tilde{g}","#tilde{t}#tilde{t}","#tilde{#tau}#tilde{#tau}","#tau'^{1e}#tau'^{1e}","#tau'^{2e}#tau'^{2e}"]



signal_massFake = signal_file.readline().split(',')
signal_massFake = [float(m.strip())/1000 for m in signal_massFake]
theory_xsecsFake = signal_file.readline().split(',')
theory_xsecsFake = [float(x.strip()) for x in theory_xsecsFake]


signal_massGluino = signal_file.readline().split(',')
signal_massGluino = [float(m.strip())/1000 for m in signal_massGluino]
theory_xsecsGluino = signal_file.readline().split(',')
theory_xsecsGluino = [float(x.strip()) for x in theory_xsecsGluino]


signal_massStop = signal_file.readline().split(',')
signal_massStop = [float(m.strip())/1000 for m in signal_massStop]
theory_xsecsStop = signal_file.readline().split(',')
theory_xsecsStop = [float(x.strip()) for x in theory_xsecsStop]

signal_massStau = signal_file.readline().split(',')
signal_massStau = [float(m.strip())/1000 for m in signal_massStau]
theory_xsecsStau = signal_file.readline().split(',')
theory_xsecsStau = [float(x.strip()) for x in theory_xsecsStau]

signal_massDy1e = signal_file.readline().split(',')
signal_massDy1e = [float(m.strip())/1000 for m in signal_massDy1e]
theory_xsecsDy1e = signal_file.readline().split(',')
theory_xsecsDy1e = [float(x.strip()) for x in theory_xsecsDy1e]

signal_massDy2e = signal_file.readline().split(',')
signal_massDy2e = [float(m.strip())/1000 for m in signal_massDy2e]
theory_xsecsDy2e = signal_file.readline().split(',')
theory_xsecsDy2e = [float(x.strip()) for x in theory_xsecsDy2e]

# Initialize arrays to eventually store the points on the TGraph
x_mass = array('d')

tdrstyle.setTDRStyle()
# Make Canvas and TGraphs (mostly stolen from other code that formats well)
climits = TCanvas("climits", "climits",700, 600)
climits.SetLogy(True)
climits.SetLeftMargin(.15)
climits.SetBottomMargin(.15)
climits.SetTopMargin(0.1)
climits.SetRightMargin(0.05)
climits.SetFrameLineWidth(1)

gStyle.SetTextFont(42)


# Theory line

graphFake = GraphTheor("fake",46,signal_massFake,theory_xsecsFake)
graphGlu = GraphTheor("gluino",46,signal_massGluino,theory_xsecsGluino)
graphStop = GraphTheor("stop",38,signal_massStop,theory_xsecsStop)
graphStau = GraphTheor("stau",30,signal_massStau,theory_xsecsStau)
graphDY1e = GraphTheor("drellyan1e",28,signal_massDy1e,theory_xsecsDy1e)
graphDY2e = GraphTheor("drellyan2e",41,signal_massDy2e,theory_xsecsDy2e)


graphFakeUp = GraphTheorUp("fake",46,signal_massFake,theory_xsecsFake)
graphGluUp = GraphTheorUp("gluino",46,signal_massGluino,theory_xsecsGluino)
graphStopUp = GraphTheorUp("stop",38,signal_massStop,theory_xsecsStop)
graphStauUp = GraphTheorUp("stau",30,signal_massStau,theory_xsecsStau)
graphDY1eUp = GraphTheorUp("drellyan1e",28,signal_massDy1e,theory_xsecsDy1e)
graphDY2eUp = GraphTheorUp("drellyan2e",41,signal_massDy2e,theory_xsecsDy2e)


graphFakeDown = GraphTheorDown("fake",46,signal_massFake,theory_xsecsFake)
graphGluDown = GraphTheorDown("gluino",46,signal_massGluino,theory_xsecsGluino)
graphStopDown = GraphTheorDown("stop",38,signal_massStop,theory_xsecsStop)
graphStauDown = GraphTheorDown("stau",30,signal_massStau,theory_xsecsStau)
graphDY1eDown = GraphTheorDown("drellyan1e",28,signal_massDy1e,theory_xsecsDy1e)
graphDY2eDown = GraphTheorDown("drellyan2e",41,signal_massDy2e,theory_xsecsDy2e)

WPuncGlu = make_smooth_graph(graphGluDown, graphGluUp)
WPuncStop = make_smooth_graph(graphStopDown, graphStopUp)
WPuncStau = make_smooth_graph(graphStauDown, graphStauUp)
WPuncDY1e = make_smooth_graph(graphDY1eDown, graphDY1eUp)
WPuncDY2e = make_smooth_graph(graphDY2eDown, graphDY2eUp)

WPuncGlu.SetFillColor(4)
WPuncGlu.SetFillStyle(3004)
WPuncGlu.SetLineColor(0)

graphFake.GetXaxis().SetRangeUser(0.3,3.)
graphGlu.GetXaxis().SetRangeUser(0.3,3.)
graphStop.GetXaxis().SetRangeUser(0.3,3.)
graphStau.GetXaxis().SetRangeUser(0.3,3.)
graphDY1e.GetXaxis().SetRangeUser(0.3,3.)
graphDY2e.GetXaxis().SetRangeUser(0.3,3.)

minY = 0.00001
maxY = 0.1
graphFake.GetYaxis().SetRangeUser(minY,maxY)
graphGlu.GetYaxis().SetRangeUser(minY,maxY)
graphStop.GetYaxis().SetRangeUser(minY,maxY)
graphStau.GetYaxis().SetRangeUser(minY,maxY)
graphDY1e.GetYaxis().SetRangeUser(minY,maxY)
graphDY2e.GetYaxis().SetRangeUser(minY,maxY)


graphFake.GetYaxis().SetTitle("Cross section [pb]")
graphFake.GetXaxis().SetTitle("Mass [TeV]")
graphFake.SetMarkerSize(0)
graphFake.SetMarkerStyle(0)
graphFake.SetLineWidth(0)
graphFake.GetXaxis().SetTitleSize(0.04)
graphFake.GetYaxis().SetTitleSize(0.04)

graphFake.GetYaxis().SetTitleOffset(1.7)
graphFake.GetXaxis().SetTitleOffset(1.5)

graphGlu.GetYaxis().SetTitle("Cross section [pb]")
graphGlu.GetXaxis().SetTitle("Mass [TeV]")

graphGlu.GetXaxis().SetTitleSize(0.04)
graphGlu.GetYaxis().SetTitleSize(0.04)

graphGlu.GetYaxis().SetTitleOffset(1.5)
graphGlu.GetXaxis().SetTitleOffset(1.5)

graphFake.Draw("Al")
graphStau.Draw("same l")
graphGlu.Draw("same l")
graphStop.Draw("same l")
graphDY1e.Draw("same l")
graphDY2e.Draw("same l")

graphGluUp.Draw("same l")
graphStopUp.Draw("same l")
graphStauUp.Draw("same l")
graphDY1eUp.Draw("same l")
graphDY2eUp.Draw("same l")

graphGluDown.Draw("same l")
graphStopDown.Draw("same l")
graphStauDown.Draw("same l")
graphDY1eDown.Draw("same l")
graphDY2eDown.Draw("same l")


gStyle.SetLegendFont(62)
legend = TLegend(0.65, 0.6, 0.85, 0.85, '')
legend.SetTextSize(0.04)
legend2 = TLegend(0.72, 0.7, 0.92, 0.85, '')
#legend.SetHeader("95% CL U	pper Limits")
legend.AddEntry(graphGlu,names[0],"l")
legend.AddEntry(graphStop,names[1],"l")
legend.AddEntry(graphStau,names[2],"l")
legend.AddEntry(graphDY1e,names[3],"l")
legend.AddEntry(graphDY2e,names[4],"l")
#legend.AddEntry(graphWP, "#sigma^{"+options.xsorder+"}_{th}("+options.process+")#pm1#sigma", "l")   # NOT GENERIC

legend.SetBorderSize(0)
legend.SetFillStyle(0)
legend.SetLineColor(0)

legend2.SetBorderSize(0)
legend2.SetFillStyle(0)
legend2.SetLineColor(0)

legend.Draw("same")
#legend2.Draw("same")

# legend lines for theory
'''
tmpyposition = 0.66
tmpline.SetLineColor(4)
tmpline.SetLineStyle(2)
tmpline.SetLineWidth(2)
tmpline.DrawLineNDC(0.517,tmpyposition,0.588,tmpyposition)

tmpyposition = 0.64
tmpline.SetLineColor(4)
tmpline.SetLineStyle(2)
tmpline.SetLineWidth(2)
tmpline.DrawLineNDC(0.517,tmpyposition,0.588,tmpyposition)

'''
# TPT.Draw()
climits.RedrawAxis()

#CMS_lumi.extraText = 'Preliminary'
CMS_lumi.writeExtraText = False
CMS_lumi.cmsText = 'Private work'
CMS_lumi.cmsTextFont = 52

#CMS_lumi.extraText = 'Private work'
CMS_lumi.lumi_13TeV = 'NLO+NLL - NNLO + NNLL'
CMS_lumi.lumiTextSize     = 0.25

CMS_lumi.cmsTextSize      = 0.32
#CMS_lumi.cmsTextSize      = 0.3
CMS_lumi.CMS_lumi(climits, 1, 11)


climits.SaveAs("theory/all_xsec.pdf")
