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

    result_graph.GetXaxis().SetRangeUser(100,1100)
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

    #ratio_hist = divide_tgraphs(object1,object2)
    
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
    object1.Draw("AL")
    object2.Draw("same l")

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
    
    latex.DrawLatex(0.21, 0.91, "Private work      -    ")
    
    latex2 = ROOT.TLatex()
    latex2.SetNDC()
    latex2.SetTextAngle(0)
    latex2.SetTextColor(46)
    latex2.SetTextFont(52)
    latex2.SetTextAlign(11)
    latex2.SetTextSize(0.03)
    
    latex2.DrawLatex(0.46, 0.91, nameSig)
    
    latex3 = ROOT.TLatex()
    latex3.SetNDC()
    latex3.SetTextAngle(0)
    latex3.SetTextColor(1)
    latex3.SetTextFont(42)
    latex3.SetTextAlign(11)
    latex3.SetTextSize(0.025)
    
    latex3.DrawLatex(0.72, 0.91, "101 fb^{-1} (13 TeV)")
    nameRoot = "ratios_cls_asymp/both_median_expected_hybrid_and_asymptotic_{}.root".format(nameLeg)
    #canvas_ratio.SaveAs(nameRoot)
    namePng = nameRoot.replace('.root','.pdf')
    canvas_ratio.SaveAs(namePng)


def get_ratio(name_rootFiles,nameSig,nameLeg):
    strFile1 = "/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/FINAL_VERSION/hybrid/{}".format(name_rootFiles)
    file1 = ROOT.TFile(strFile1,"READ")
    
    
    strFile2 = "/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/FINAL_VERSION/asymptotic/{}".format(name_rootFiles)
    
    file2 = ROOT.TFile(strFile2,"READ")
    
    
    canvas1 = file1.Get("climits")
    canvas2 = file2.Get("climits")
    
    # List all objects on the first canvas
    print("Objects on the first canvas:")
    
    
    for obj in canvas1.GetListOfPrimitives():
        print(obj.GetName())
        print(obj.GetTitle())
        print(type(obj))
        
    
    print("\nObjects on the second canvas:")
    for obj in canvas2.GetListOfPrimitives():
        print(obj.GetName())
        print(obj.GetTitle())
        print(type(obj))
    
    object_name = "median_expected" 
    
    
    object1 = canvas1.GetPrimitive(object_name)
    object2 = canvas2.GetPrimitive(object_name)
    
    x_axis = object1.GetXaxis()
    min_x = x_axis.GetXmin()
    max_x = x_axis.GetXmax()
    print("min x = {}, max x = {}".format(min_x,max_x))
    
    canvas_ratio = ROOT.TCanvas("c_ratio", "Ratio Canvas", 500, 500)
    
    
    ratio_hist = divide_tgraphs(object1,object2)
    ratio_hist.SetMarkerStyle(49)
    ratio_hist.SetMarkerColor(46)
    ratio_hist.SetMarkerSize(1.5)
    
    gStyle.SetLegendFont(62)
    
    
    legend = ROOT.TLegend(0.15, 0.78, 0.45, 0.88)
    legend.SetFillStyle(0)
    #legend.SetBorderSize(0)
    #legend.SetLineColor(0)
    
    #legend.SetHeader(nameSig)
    legend.AddEntry(ratio_hist, "Full CLs / Asymptotic", "p") 
    ratio_hist.Draw("AP")
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
    
    latex.DrawLatex(0.11, 0.91, "Private work      -    ")
    
    latex2 = ROOT.TLatex()
    latex2.SetNDC()
    latex2.SetTextAngle(0)
    latex2.SetTextColor(46)
    latex2.SetTextFont(52)
    latex2.SetTextAlign(11)
    latex2.SetTextSize(0.03)
    
    latex2.DrawLatex(0.36, 0.91, nameSig)
    
    latex3 = ROOT.TLatex()
    latex3.SetNDC()
    latex3.SetTextAngle(0)
    latex3.SetTextColor(1)
    latex3.SetTextFont(42)
    latex3.SetTextAlign(11)
    latex3.SetTextSize(0.025)
    
    latex3.DrawLatex(0.72, 0.91, "101 fb^{-1} (13 TeV)")
    nameRoot = "ratios_cls_asymp/ratio_median_expected_hybrid_over_asymptotic_{}.root".format(nameLeg)
    #canvas_ratio.SaveAs(nameRoot)
    namePng = nameRoot.replace('.root','.pdf')
    canvas_ratio.SaveAs(namePng)

def main():
    #name_rootFiles = ["limits_combine_101fb_signals_tauPrime1e_tPrime.root","limits_combine_101fb_signals_tauPrime2e_tPrime.root","limits_combine_101fb_signals_gluino_v1_gluino.root","limits_combine_101fb_signals_stop_stop.root","limits_combine_101fb_signals_ppStau_tau.root","limits_combine_101fb_signals_ppStauGMSB_tau.root","limits_combine_101fb_signals_Zprime-M600_ssm_ZPrime_NoTheo_HybridNew.root"]
    name_rootFiles = ["limits_combine_101fb_signals_Zprime-M600_ssm_ZPrime_NoTheo_HybridNew.root"]

    nameSig = ["#tau'^{1e}","#tau'^{2e}","Gluino","Stop","Pair-produced Stau","GMSB Stau","Z'"]
    nameLeg = ["tauprime_1e","tauprime_2e","Gluino","Stop","pairStau","gmsbStau","Zprime"]
    #nameSig = ["Z'"]
    #nameLeg = ["Zprime"]   
    for i in range(len(name_rootFiles)):
        print("Generating ratio for {}".format(name_rootFiles[i]))
        get_ratio(name_rootFiles[i],nameSig[i],nameLeg[i])
        plot_both(name_rootFiles[i],nameSig[i],nameLeg[i])
    

if __name__=="__main__":
    main()
