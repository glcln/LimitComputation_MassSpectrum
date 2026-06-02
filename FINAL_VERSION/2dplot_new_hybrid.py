import ROOT
import sys


#######################
#######################
#######################
#######################
#######################
#######################
#  To add:
#  Change color scale to be excluded XS
#  Show contour at XS excluded XS from ATLAS
#  Show contour at XS expected from ATLAS


outputFile = ROOT.TFile("output_BR100pct.root")
#outputFile = ROOT.TFile("output_BR10pct.root")
#outputFile1 = ROOT.TFile("output_BR1pct.root")

canvas = ROOT.TCanvas("FinalCurves","FinalCurves")

tauPrimeMass = (200, 400, 600, 800, 1000, 1200, 1400)
ZPrimeMass = (3000, 4000, 5000, 6000, 7000)

#setup
dummy = ROOT.TH2D("dummy",";m_{#tau'^{#scale[0.5]{ }2e}} [GeV];m_{Z'} [GeV];thing",10,200,1400,10,3000,7000)
dummy.GetZaxis().SetTitle("Observed cross section limit [pb]")
dummy.Draw("axis")
#outputFile.Get("expectedUpperLimit_gr").Draw("colz same")
outputFile.Get("upperLimit_gr").Draw("colz same")
dummy.SetMinimum(1e-5)
dummy.SetMaximum(3.5e-2)
ROOT.gPad.SetLogz()
ROOT.gPad.SetRightMargin(0.15)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)
#ROOT.gStyle.SetPalette(ROOT.kRainBow)


graphOrig = ROOT.TGraph()
for x in tauPrimeMass :
  for y in ZPrimeMass :
    graphOrig.SetPoint(graphOrig.GetN(), x, y)

phenoContour = ROOT.TGraph("phenoContour.csv", "%lg,%lg")
graphOrig.SetMarkerColor(1)
graphOrig.SetMarkerStyle(ROOT.kCircle)
graphOrig.SetMarkerSize(0.75)
graphOrig.Draw("PSAME")
phenoContour.Draw("SAME LF")
#phenoContour.SetFillColorAlpha(ROOT.kBlue-2,0.2)
phenoContour.SetFillColorAlpha(ROOT.kBlue,0.99)
phenoContour.SetFillStyle(3005)
phenoContour.SetLineColor(ROOT.kBlack)
phenoContour.SetLineWidth(2)

'''
if outputFile.Get("Band_1s_0"):
    for iGraph in range(  3  ):
        try:
            outputFile.Get("Band_1s_%d"%iGraph).Draw("L")
        except:
            pass

for iGraph in range(3):
    try:
        outputFile.Get("Exp_%d"%iGraph).Draw("L")
        # outputFile10.Get("Exp_%d"%iGraph).Draw("L")
        # outputFile1.Get("Exp_%d"%iGraph).Draw("L")
    except:
        pass


for iGraph in range(3):
    try:
        outputFile.Get("Obs_%d"%iGraph).Draw("L")
    except:
        pass
'''
marker = ROOT.TGraph()
marker.SetPoint(0,650,5200)
marker.SetMarkerStyle(29)
marker.SetMarkerSize(2)
marker.SetMarkerColor(ROOT.kBlack)
marker.Draw("P")

latex = ROOT.TLatex()
latex.SetTextFont(63)
latex.SetTextSize(14)
latex.DrawLatex(650,5200,"    Best fit from\n [2205.04473]")

tex2 = ROOT.TLatex(0.12,0.94,"CMS");
#tex2 = ROOT.TLatex(0.20,0.94,"CMS");#if there is 10^x
tex2.SetNDC();
tex2.SetTextFont(61);
tex2.SetTextSize(0.0675);
tex2.SetLineWidth(2);

#tex3 = ROOT.TLatex(0.27,0.94,"Simulation"); # for square plots
#tex3 = ROOT.TLatex(0.28,0.94,"Work in Progress 2018"); #if there is 10^x
tex3 = ROOT.TLatex(0.65,0.94,"101 fb^{-1} (13 TeV)");
tex3.SetNDC();
tex3.SetTextFont(52);
tex3.SetTextSize(0.0485);
tex3.SetLineWidth(2);


tex2.Draw("SAME")
tex3.Draw("SAME")
ROOT.gPad.RedrawAxis()
canvas.SaveAs("ZPrimeTPrime_2DLimit_hybrid_newSys.pdf")
canvas.SaveAs("ZPrimeTPrime_2DLimit_hybrid_newSys.C")
canvas.SaveAs("ZPrimeTPrime_2DLimit_hybrid_newSys.root")

