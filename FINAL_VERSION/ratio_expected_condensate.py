import ROOT
import ctypes

from ROOT import *

def divide_tgraphs(graph1,graph2):
    print("Graph 1 has {} points".format(graph1.GetN()))
    print("Graph 2 has {} points".format(graph2.GetN()))
    
    if graph1.GetN() != graph2.GetN():
        print("Error: Input graphs must have the same number of points.")
        return None
    result_graph = ROOT.TGraphErrors(graph1.GetN())
    ratio_vals = []
    for i in range(graph1.GetN()):
        
        x1 = ctypes.c_double(0)
        y1 = ctypes.c_double(0)

        x2 = ctypes.c_double(0)
        y2 = ctypes.c_double(0)

        ratio = ctypes.c_double(0) 
        err_ratio = ctypes.c_double(0) 
      
        graph1.GetPoint(i, x1, y1)
        ex1 = graph1.GetErrorX(i)
        ey1 = graph1.GetErrorY(i)

        graph2.GetPoint(i, x2, y2)
        ex2 = graph2.GetErrorX(i)
        ey2 = graph2.GetErrorY(i)

        print("Graph 1 : [x1,y1] = [{}-{}] \t Graph 2 : [x2,y2] = [{},{}]".format(x1,y1,x2,y2))
        print("\n")
        if y2 != 0:
            ratio = y1.value / y2.value
            error_ratio = ratio * ((ey1 / y1.value)**2 + (ey2 / y2.value)**2)**0.5
        else:
            ratio = 0
            error_ratio = 0

        result_graph.SetPoint(i, x1, ratio)
        ratio_vals.append(ratio)
        result_graph.SetPointError(i, 0, 0)

    result_graph.GetXaxis().SetRangeUser(0.2,2800)
    min_ratio = min(ratio_vals)
    max_ratio = max(ratio_vals)
    result_graph.GetYaxis().SetRangeUser(min_ratio*0.95,max_ratio*1.05)
    #result_graph.GetYaxis().SetRangeUser(0.9,1.1)
    result_graph.SetTitle("")
    result_graph.GetYaxis().SetTitle("Cross-section ratios")
    result_graph.GetYaxis().SetTitleOffset(1.5)
    result_graph.GetYaxis().SetTitleSize(0.035)
    result_graph.GetYaxis().SetLabelSize(0.025) 
    result_graph.GetXaxis().SetLabelSize(0.025) 
    result_graph.GetXaxis().SetTitle("Mass [TeV]")
    return result_graph


def find_max_value(graph):
    min_y = max(graph.GetY()[i] for i in range(graph.GetN()))
    return min_y

def find_max_between_two_graphs(graph1, graph2):
    max_y_graph1 = find_max_value(graph1)
    max_y_graph2 = find_max_value(graph2)
    return max(max_y_graph1, max_y_graph2)


def find_min_value(graph):
    min_y = min(graph.GetY()[i] for i in range(graph.GetN()))
    return min_y

def find_min_between_two_graphs(graph1, graph2):
    min_y_graph1 = find_min_value(graph1)
    min_y_graph2 = find_min_value(graph2)
    return min(min_y_graph1, min_y_graph2)


def plot_both(name_rootFiles,nameSig,nameLeg):
    strFile1 = "/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/FINAL_VERSION/hybrid/{}".format(name_rootFiles)
    file1 = ROOT.TFile(strFile1,"READ")
    
    strFile2 = "/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/FINAL_VERSION/asymptotic/{}".format(name_rootFiles)
    
    file2 = ROOT.TFile(strFile2,"READ")
    
    
    canvas1 = file1.Get("climits")
    canvas2 = file2.Get("climits")

    object_name = "median_expected" 

    object1 = canvas1.GetPrimitive(object_name)
    object2 = canvas2.GetPrimitive(object_name)
    object1.SetTitle("") 
    object2.SetTitle("") 
    x_axis = object1.GetXaxis()
    min_x = x_axis.GetXmin()
    max_x = x_axis.GetXmax()
    print("min x = {}, max x = {}".format(min_x,max_x))
    
    canvas_ratio = ROOT.TCanvas("c_ratio", "Ratio Canvas", 500, 500)
    
    object1.SetLineColor(46)
    object2.SetLineColor(1)
    max_val = find_max_between_two_graphs(object1, object2)
    min_val = find_min_between_two_graphs(object1, object2)
    gStyle.SetLegendFont(62)
        
    legend = ROOT.TLegend(0.35, 0.78, 0.65, 0.88)
    legend.SetFillStyle(0)

    legend.AddEntry(object1, "Full CLs", "l") 
    legend.AddEntry(object2, "Asymptotic CLs", "l") 
    object1.GetYaxis().SetRangeUser(min_val*0.9,max_val*1.1)
    object1.GetYaxis().SetLabelSize(0.03)
    object2.GetYaxis().SetLabelSize(0.03)
    object1.SetTitle("")
    object1.GetYaxis().SetTitle("Median expected cross-section [pb]")
    object1.GetYaxis().SetTitleOffset(1.4)
    object1.GetYaxis().SetTitleSize(0.035)
    object1.GetXaxis().SetTitleSize(0.035)
    object1.GetYaxis().SetLabelSize(0.025)
    object1.GetXaxis().SetLabelSize(0.025) 

    if "Stau" in nameSig:
        object1.GetYaxis().SetLabelSize(0.018) 
        object1.GetYaxis().SetRangeUser(0.00005,0.0015)
    else:
        object1.GetYaxis().SetLabelSize(0.025) 

    object1.GetXaxis().SetTitle("Mass [TeV]")
    #object1.GetYaxis().SetExponentOffset(-0.05, 0)
    object1.Draw("AL")
    object2.Draw("same l")
    #legend.SetHeader("Signal : " + nameSig)
    legend.Draw("SAME")
    
    LineOne=TLine(min_x,1.,max_x,1.)
    LineOne.SetLineColor(1)
    LineOne.SetLineStyle(4)
    LineOne.SetLineWidth(2)
    LineOne.Draw("same")
    
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(1)
    latex.SetTextFont(52)
    latex.SetTextAlign(11)
    latex.SetTextSize(0.03)
    
    latex.DrawLatex(0.155, 0.906, "Private work      -    ")
    
    latex2 = ROOT.TLatex()
    latex2.SetNDC()
    latex2.SetTextAngle(0)
    latex2.SetTextColor(46)
    latex2.SetTextFont(52)
    latex2.SetTextAlign(11)
    latex2.SetTextSize(0.03)
    
    latex2.DrawLatex(0.42, 0.906, nameSig)
    
    latex3 = ROOT.TLatex()
    latex3.SetNDC()
    latex3.SetTextAngle(0)
    latex3.SetTextColor(1)
    latex3.SetTextFont(42)
    latex3.SetTextAlign(11)
    latex3.SetTextSize(0.028)
    
    latex3.DrawLatex(0.72, 0.906, "101 fb^{-1} (13 TeV)")
    nameRoot = "ratios_cls_asymp/both_median_expected_hybrid_and_asymptotic_{}.root".format(nameLeg)
    canvas_ratio.SaveAs(nameRoot)
    namePng = nameRoot.replace('.root','.pdf')
    canvas_ratio.SaveAs(namePng)


def get_ratio(name_rootFiles,nameSig,nameLeg,color):
    strFile1 = "/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/FINAL_VERSION/hybrid/{}".format(name_rootFiles)
    file1 = ROOT.TFile(strFile1,"READ")
    strFile2 = "/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/FINAL_VERSION/asymptotic/{}".format(name_rootFiles)
    
    file2 = ROOT.TFile(strFile2,"READ")
    
    
    canvas1 = file1.Get("climits")
    canvas2 = file2.Get("climits")
    object_name = "median_expected" 
    
    
    object1 = canvas1.GetPrimitive(object_name)
    object2 = canvas2.GetPrimitive(object_name)
    
    x_axis = object1.GetXaxis()
    min_x = x_axis.GetXmin()
    max_x = x_axis.GetXmax()
    ratio_hist = divide_tgraphs(object1,object2)
    ratio_hist.SetMarkerStyle(49)
    ratio_hist.SetMarkerColor(color)
    ratio_hist.SetMarkerSize(1.5)
    return ratio_hist

def plot_ratios(ratios):
    canvas_ratio = ROOT.TCanvas("c_ratio", "Ratio Canvas", 500, 500) 
    gStyle.SetLegendFont(62)
    legend = ROOT.TLegend(0.15, 0.78, 0.45, 0.88)
    legend.SetFillStyle(0)
    legend.SetHeader("Full CLs / Asymptotic")
    legend.AddEntry(ratios[0], "#tilde{g}", "p") 
    legend.AddEntry(ratios[1], "pair-produced #tilde{#tau}", "p") 
    a = ROOT.TH1D("a","a",2600,0.2,2.8)
    a.SetMarkerStyle(1)
    a.SetMarkerSize(0)
    a.GetYaxis().SetRangeUser(0.9,1.5)    
    a.SetTitle("")
    a.GetYaxis().SetTitle("Cross-section ratios")
    a.GetYaxis().SetTitleOffset(1.5)
    a.GetYaxis().SetTitleSize(0.035)
    a.GetYaxis().SetLabelSize(0.025) 
    a.GetXaxis().SetLabelSize(0.025) 
    a.GetXaxis().SetTitle("Mass [TeV]")
    a.SetStats(False)

    ratios[0].GetXaxis().SetRangeUser(0.2,2.8)
    ratios[1].GetXaxis().SetRangeUser(0.2,2.8)
    a.Draw("")

    ratios[0].Draw("same P")
    ratios[1].Draw("same P")
    legend.Draw("SAME")
    
    LineOne=TLine(0.2,1.,2.8,1.)
    LineOne.SetLineColor(1)
    LineOne.SetLineStyle(4)
    LineOne.SetLineWidth(2)
    LineOne.Draw("same")
    
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(1)
    latex.SetTextFont(52)
    latex.SetTextAlign(11)
    latex.SetTextSize(0.03)
    
    latex.DrawLatex(0.105, 0.906, "Private work")
    
    latex2 = ROOT.TLatex()
    latex2.SetNDC()
    latex2.SetTextAngle(0)
    latex2.SetTextColor(46)
    latex2.SetTextFont(52)
    latex2.SetTextAlign(11)
    latex2.SetTextSize(0.03)
    
    #latex2.DrawLatex(0.36, 0.91, nameSig)
    
    latex3 = ROOT.TLatex()
    latex3.SetNDC()
    latex3.SetTextAngle(0)
    latex3.SetTextColor(1)
    latex3.SetTextFont(42)
    latex3.SetTextAlign(11)
    latex3.SetTextSize(0.028)
    
    latex3.DrawLatex(0.72, 0.906, "101 fb^{-1} (13 TeV)")
    nameRoot = "ratios_cls_asymp/ratio_median_expected_hybrid_over_asymptotic_gluinoAndStau.root"
    canvas_ratio.SaveAs(nameRoot)
    namePng = nameRoot.replace('.root','.pdf')
    canvas_ratio.SaveAs(namePng)


def main():
    name_rootFiles = ["limits_combine_101fb_signals_gluino_v1_gluino.root","limits_combine_101fb_signals_ppStau_tau.root"]
    nameSig = ["Gluino","Pair-produced Stau"]
    nameLeg = ["Gluino","pairStau"]
    colors = [46,30] 
    ratios = []   
    for i in range(len(name_rootFiles)):
        print("Generating ratio for {}".format(name_rootFiles[i]))
        a = get_ratio(name_rootFiles[i],nameSig[i],nameLeg[i],colors[i])
        ratios.append(a)

        plot_both(name_rootFiles[i],nameSig[i],nameLeg[i])
    
    plot_ratios(ratios)

if __name__=="__main__":
    main()
