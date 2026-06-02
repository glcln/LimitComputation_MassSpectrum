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
#outputFile10 = ROOT.TFile("output_BR10pct.root")
#outputFile1 = ROOT.TFile("output_BR1pct.root")

canvas = ROOT.TCanvas("FinalCurves","FinalCurves")


#setup
dummy = ROOT.TH2D("dummy",";m(#tau'^{2e}) [GeV];m(Z') [GeV];thing",10,200,1400,10,3000,7000)
dummy.Draw("axis")
#outputFile.Get("expectedUpperLimit_gr").Draw("colz same")
outputFile.Get("upperLimit_gr").Draw("colz same")
dummy.SetMinimum(7e-6)
dummy.SetMaximum(3.5e-2)
ROOT.gPad.SetLogz()
ROOT.gPad.SetRightMargin(0.15)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)
#ROOT.gStyle.SetPalette(ROOT.kRainBow)



phenoContour = ROOT.TGraph("phenoContour.csv", "%lg,%lg")
phenoContour.Draw("same LF")
#phenoContour.SetFillColorAlpha(ROOT.kBlue-2,0.2)
phenoContour.SetFillColorAlpha(ROOT.kBlue,0.99)
phenoContour.SetFillStyle(3005)
phenoContour.SetLineColor(ROOT.kBlue)
phenoContour.SetLineWidth(2)

if outputFile.Get("Band_1s_0"):
    for iGraph in range(  3  ):
        try:
            outputFile.Get("Band_1s_%d"%iGraph).Draw("same L")
        except:
            pass
'''
for iGraph in range(3):
    try:
        outputFile.Get("Exp_%d"%iGraph).Draw("L")
        # outputFile10.Get("Exp_%d"%iGraph).Draw("L")
        # outputFile1.Get("Exp_%d"%iGraph).Draw("L")
    except:
        pass

'''
for iGraph in range(3):
    try:
        outputFile.Get("Obs_%d"%iGraph).Draw("same L")
    except:
        pass

marker = ROOT.TGraph()
marker.SetPoint(0,650,5200)
marker.SetMarkerStyle(29)
marker.SetMarkerSize(2)
marker.SetMarkerColor(ROOT.kBlack)
marker.Draw("same P")

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
tex3 = ROOT.TLatex(0.65,0.94,"100 fb^{-1} (13 TeV)");
tex3.SetNDC();
tex3.SetTextFont(52);
tex3.SetTextSize(0.0485);
tex3.SetLineWidth(2);


tex2.Draw("SAME")
tex3.Draw("SAME")
ROOT.gPad.RedrawAxis()
canvas.SaveAs("ZPrimeTPrime_2DLimit.pdf")
canvas.SaveAs("ZPrimeTPrime_2DLimit.root")


