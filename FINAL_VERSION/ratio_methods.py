import ROOT
import ctypes

from ROOT import *

def divide_tgraphs(graph1,graph2):
    print("Graph 1 has {} points".format(graph1.GetN()))
    for i in range(graph1.GetN()):
        x1 = ctypes.c_double(0)
        y1 = ctypes.c_double(0)
        graph1.GetPoint(i, x1, y1)
        print("Point {} x = {} , y = {}".format(i,x1,y1)) 
    print("Graph 2 has {} points".format(graph2.GetN()))
    for i in range(graph2.GetN()):
        x1 = ctypes.c_double(0)
        y1 = ctypes.c_double(0)
        graph2.GetPoint(i, x1, y1)
        print("Point {} x = {} , y = {}".format(i,x1,y1)) 

    
    result_graph = ROOT.TGraphErrors(graph1.GetN())
    ratio_vals = []
    counter = 0
    for i in range(graph1.GetN()):
        x1 = graph1.GetX()[i]
        y1 = graph1.GetY()[i]
        found_x2 = False
        
        for j in range(graph2.GetN()):
            x2 = graph2.GetX()[j]
            if x1 == x2:
                y2 = graph2.GetY()[j]
                print("Matching X = {}, y1 = {} and y2 = {}, ratio -> {}".format(x1,y1,y2,y1/y2))
                ratio = y1 / y2
                result_graph.SetPoint(counter, x1, ratio)
                counter+=1
                ratio_vals.append(ratio)
                found_x2 = True
                break
        if not found_x2:
            print("Didnt find matching X = {} value".format(x1))
 

    result_graph.GetXaxis().SetRangeUser(100,1100)
    min_ratio = min(ratio_vals)
    max_ratio = max(ratio_vals)
    result_graph.GetYaxis().SetRangeUser(min_ratio*0.8,max_ratio*1.2)
    #result_graph.GetYaxis().SetRangeUser(0.9,1.1)
    result_graph.SetTitle("")
    result_graph.GetYaxis().SetTitle("Cross-section ratios")
    result_graph.GetYaxis().SetTitleOffset(1.5)
    result_graph.GetYaxis().SetTitleSize(0.035)
    result_graph.GetYaxis().SetLabelSize(0.025) 
    result_graph.GetXaxis().SetLabelSize(0.025) 
    result_graph.GetXaxis().SetTitle("Mass [TeV]")
    return result_graph



def get_ratio(name_rootFiles,name_rootFilesIon,nameSig,nameLeg):
    strFile1 = "/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/FINAL_VERSION/hybrid/{}".format(name_rootFiles)
    file1 = ROOT.TFile(strFile1,"READ")
    strFile2 = "/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/FINAL_VERSION/hybrid_ionization/{}".format(name_rootFilesIon)
    '''
    firstPart = "_".join(strFile2.split("_")[:-1])

    lastPart = strFile2.split("_")[-1]
    ionMeth = firstPart + "_ionization_" + lastPart
    print(ionMeth) 
    strFile2 = ionMeth 
    '''
    '''
    if 'ppStauGMSB' in strFile1:
        strFile2 = '/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/FINAL_VERSION/hybrid_ionization/limits_combine_101fb_signals_gmsbStau_ionization_tau.root'

    if 'Zprime' in strFile1:
        strFile2 = '/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/FINAL_VERSION/hybrid_ionization/limits_combine_101fb_signals_Zprime-M600_ssm_ionization_ZPrime.root'
    '''
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
    
    
    legend = ROOT.TLegend(0.15, 0.78, 0.55, 0.88)
    legend.SetFillStyle(0)
    #legend.SetBorderSize(0)
    #legend.SetLineColor(0)
    
    #legend.SetHeader(nameSig)
    legend.AddEntry(ratio_hist, "Mass method / Ionization method", "p") 
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
    nameRoot = "ratios_methods/ratio_median_expected_mass_over_ionization_{}.root".format(nameLeg)
    #canvas_ratio.SaveAs(nameRoot)
    namePng = nameRoot.replace('.root','.pdf')
    canvas_ratio.SaveAs(namePng)

def main():
    name_rootFiles = ["limits_combine_101fb_signals_tauPrime1e_tPrime.root","limits_combine_101fb_signals_tauPrime2e_tPrime.root","limits_combine_101fb_signals_gluino_v1_gluino.root","limits_combine_101fb_signals_stop_stop.root","limits_combine_101fb_signals_ppStau_tau.root","limits_combine_101fb_signals_ppStauGMSB_tau.root","limits_combine_101fb_signals_Zprime-M600_ssm_ZPrime.root"]
 
    name_rootFiles_ion = ["limits_combine_101fb_signals_tauPrime1e_ionization_tPrime.root","limits_combine_101fb_signals_tauPrime2e_ionization_tPrime.root","limits_combine_101fb_signals_gluino_v1_ionization_gluino.root","limits_combine_101fb_signals_stop_ionization_stop.root","limits_combine_101fb_signals_ppStau_ionization_tau.root","limits_combine_101fb_signals_gmsbStau_ionization_tau.root","limits_combine_101fb_signals_Zprime-M600_ssm_ionization_ZPrime.root"]


    #name_rootFiles = ["limits_combine_101fb_signals_tauPrime1e_tPrime.root","limits_combine_101fb_signals_gluino_v1_gluino.root","limits_combine_101fb_signals_stop_stop.root","limits_combine_101fb_signals_ppStau_tau.root","limits_combine_101fb_signals_ppStauGMSB_tau.root","limits_combine_101fb_signals_Zprime-M600_ssm_ZPrime.root"]

    #name_rootFiles_ion = ["limits_combine_101fb_signals_tauPrime1e_ionization_tPrime.root","limits_combine_101fb_signals_gluino_v1_ionization_gluino.root","limits_combine_101fb_signals_stop_ionization_stop.root","limits_combine_101fb_signals_ppStau_ionization_tau.root","limits_combine_101fb_signals_gmsbStau_ionization_tau.root","limits_combine_101fb_signals_Zprime-M600_ssm_ionization_ZPrime.root"]

    nameSig = ["#tau'^{1e}","#tau'^{2e}","Gluino","Stop","Pair-produced Stau","GMSB Stau","Z'"]
    nameLeg = ["tauprime_1e","tauprime_2e","Gluino","Stop","pairStau","gmsbStau","Zprime"]
    #nameSig = ["#tau'^{1e}","Gluino","Stop","Pair-produced Stau","GMSB Stau","Z'"]
    #nameLeg = ["tauprime_1e","Gluino","Stop","pairStau","gmsbStau","Zprime"]

    for i in range(len(name_rootFiles)):
        print("Generating ratio for {}".format(name_rootFiles[i]))
        get_ratio(name_rootFiles[i],name_rootFiles_ion[i],nameSig[i],nameLeg[i])
    

if __name__=="__main__":
    main()
