import ROOT
import tdrstyle, CMS_lumi
import numpy as np


def create_area(yval,var2_range,botErrY):
    graph = ROOT.TGraphAsymmErrors(len(var2_range))
    for idx,val in enumerate(var2_range):
        graph.SetPoint(idx, val, yval)
        graph.SetPointError(idx,0,0,0,botErrY)
    return graph

def create_graph(func, var1_val, var2_range):
    graph = ROOT.TGraph()
    for index,var2_val in enumerate(var2_range):
        result = func(var1_val, var2_val)
        graph.SetPoint(index, var2_val, result)
        print("Ms = {}, mg = {}, lifetime = {}".format(var1_val,var2_val,result))
    return graph


def your_function(var1, var2):
    return (8.0 * ((var1/1000000.0)**4) * ((1*1.0/var2*1.0)**5))


var1_values = [10000,100000, 1000000, 10000000, 100000000, 1000000000]
var1_legends = ["10^{7} GeV","10^{8} GeV","10^{9} GeV","10^{10} GeV","10^{11} GeV","10^{12} GeV"]


var2_range = [0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2,2.1,2.2,2.3,2.4,2.5]
var2_range = np.arange(0.2, 2.51, 0.01)

canvas = ROOT.TCanvas("canvas", "Graph Example", 600, 600)
pad1 = ROOT.TPad("pad1", "Histograms", 0., 0.05, 1, 1)
pad1.SetBottomMargin(0.1)
pad1.SetTopMargin(0.1)
pad1.Draw()
pad1.SetLogy(1)
pad1.cd()


legend = ROOT.TLegend(0.35, 0.74, 0.55, 0.89)
legend.SetBorderSize(0)
legend2 = ROOT.TLegend(0.60, 0.74, 0.80, 0.89)
legend2.SetBorderSize(0)
#legend.SetHeader("Mass squark hypothesis")
graphs = []
colors = [ROOT.kBlack, ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kOrange, ROOT.kPink, ROOT.kCyan,ROOT.kSpring]
for i, var1_val in enumerate(var1_values):
    graph = create_graph(your_function, var1_val, var2_range)
    graph.SetLineColor(colors[i])
    graph.SetLineWidth(3)
    graph.SetLineStyle(i)
    graph.SetMarkerColor(colors[i])
    graph.SetMarkerStyle(20 + i)
    graph.SetMarkerSize(1.5)
    graph.SetTitle("")
    graph.GetXaxis().SetTitle("m_{#tilde{g}} [TeV]")
    graph.GetYaxis().SetTitle("#tau [s]")
    graph.GetYaxis().SetNdivisions(10)
    graph.GetYaxis().SetTitleOffset(1.5)
    
    graph.GetYaxis().SetRangeUser(0.00000000001,1000000000000000000000000)
    graph.GetXaxis().SetRangeUser(0,3000)
    graph.Draw("LA" if i == 0 else "L SAME")
    if i < 3:
        legend.AddEntry(graph, "m_{S} = " + str(var1_legends[i]), "L")
    else:
        legend2.AddEntry(graph, "m_{S} = " + str(var1_legends[i]), "L")
    graphs.append(graph)

'''
area = create_area(0.00000005,var2_range,0.00000000001)
area.SetFillColorAlpha(6,0.5)
area.SetMarkerStyle(20)
area.SetMarkerColor(6)
area.SetMarkerSize(1)
area.SetFillStyle(3004)
area.Draw("same E3")
'''
rectangle = ROOT.TPave(0.2, 0, 0.8, 0.1, 0, "NDC")
rectangle.SetFillColorAlpha(ROOT.kBlue, 0.1)
#rectangle.Draw("same")
legend.Draw()
legend2.Draw()
#canvas.RedrawAxis()

#CMS_lumi.extraText = 'Preliminary'
CMS_lumi.cmsText = 'Private work'
CMS_lumi.cmsTextFont = 52
CMS_lumi.relPosX = 0.055

CMS_lumi.extraText = ''
CMS_lumi.lumiTextSize     = 0.0

CMS_lumi.cmsTextSize      = 0.3
#CMS_lumi.cmsTextSize      = 0.3
CMS_lumi.CMS_lumi(canvas, 1, 11)

canvas.SaveAs("gluino_lifetime.pdf")
canvas.SaveAs("gluino_lifetime.root")
