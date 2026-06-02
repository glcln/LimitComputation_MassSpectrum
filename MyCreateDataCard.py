import ROOT as rt
import csv
import re
import sys
import collections
import os

from collections import OrderedDict
import numpy as np
import array

rt.gROOT.SetBatch(True)


def integralHisto(h,xmin,xmax):
    return h.Integral(h.FindBin(xmin),h.FindBin(xmax))

def MakeDatacard(outDataCardsDir,  modelName, signal2018, bkg2018, sig_2018_unc, sig_unc_correlated, bkg_2018_unc, bkg_unc_correlated):

    text_file = open(outDataCardsDir+modelName+".txt", "w")

    text_file.write('imax {0} \n'.format(1))
    text_file.write('jmax {0} \n'.format(1))
    text_file.write('kmax * \n')
    text_file.write('shapes * * FAKE \n')
    text_file.write('--------------- \n')
    text_file.write('--------------- \n')
    text_file.write('bin \t Ch2018 \n')
    text_file.write('observation \t {} \n'.format(0.0))
    text_file.write('------------------------------ \n')
    text_file.write('bin \t Ch2018 \t Ch2018 \n')
    text_file.write('process \t signal \t bkg \n')
    text_file.write('process\t 0 \t 1 \t \n')
    text_file.write('rate \t {} \t {} \n'.format(signal2018, bkg2018))
    text_file.write('------------------------------ \n')

    #### uncertainties ####
    for k,v in sig_2018_unc.items():
        if len(v)==2:
            text_file.write('{} \t lnN \t {}/{} \t - \n'.format(k, v[0],v[1]))
        else:text_file.write('{} \t lnN \t {} \t - \n'.format(k, v[0]))

    for k,v in sig_unc_correlated.items():
        if len(v)==4:
            text_file.write('{} \t lnN \t {}/{} \t - \n'.format(k, v[0],v[1]))
        else:text_file.write('{} \t lnN \t {} \t - \n'.format(k, v[0]))

    text_file.write('sig_lumi \t lnN \t 1.025 \t - \n')

    for k,v in bkg_2018_unc.items():
        if len(v)==2:
            vPrime=max(abs(1-v[0]),abs(1-v[1]))+1
            text_file.write('{} \t lnN \t -  \t {} \n'.format(k, vPrime))
        else:text_file.write('{} \t lnN \t -  \t {} \n'.format(k, v[0]))
    
    for k,v in bkg_unc_correlated.items():
        if len(v)==2:
            vPrime=max(abs(1-v[0]),abs(1-v[1]))+1
            text_file.write('{} \t lnN \t - \t {} \n'.format(k, vPrime))
        else:text_file.write('{} \t lnN \t - \t {} \n'.format(k, v[0]))

    text_file.close()



if __name__ == '__main__':

    # SETUP
    fpath = OrderedDict()
    fpathPred = OrderedDict()
    massPlotsSignal = OrderedDict()
    mass_plot = OrderedDict()

    idirData = '/opt/sbg/cms/safe1/cms/gcoulon/CMSSW_10_6_30/src/HSCPTreeAnalyzer/output/Gstrip_2p28/'
    versionData = '2p28'
    idirROOT='HSCParticleAnalyzer/BaseName/'
    searchRegion = 'SR3'
    regionBckg = '9fp10'
    regionBckg = '999ias100'
    eta = 'Eta1'
 
    outDataCardsDir = "MyDataCards/datacards_" + regionBckg + "_" + eta + "/"
    os.system("mkdir -p {0}".format(outDataCardsDir))


    # SIGNAL PART
    name = {
        'Gluino2000_2018': '$\\tilde{g}$ (M=2000 GeV)',
    }

    target={
       'Gluino2000_2018': 2000,
    }

    fpath['Gluino2000_2018'] = "/opt/sbg/cms/safe1/cms/gcoulon/CMSSW_10_6_30/src/HSCPTreeAnalyzer/output/Gluino2000_massCut_0_pT70_V5p10_Gstrip_Fpix_Scaled.root"
    
    

    # GET SYSTEMATIC UNCERTAINTIES
    massPlotsSignal['Nominal'] = 'mass_p_regionD_' + regionBckg + '_SingleMu_Eta1'
    '''
    massPlotsSignal['PU_up'] = idirROOT+'PostS_'+searchRegion+'_Mass_Pileup_up'
    massPlotsSignal['PU_down'] = idirROOT+'PostS_'+searchRegion+'_Mass_Pileup_down'
    massPlotsSignal['Fpix_up'] = idirROOT+'PostS_'+searchRegion+'_Mass_ProbQNoL1_up'
    massPlotsSignal['Fpix_down'] = idirROOT+'PostS_'+searchRegion+'_Mass_ProbQNoL1_down'
    massPlotsSignal['Pt_up'] = idirROOT+'PostS_'+searchRegion+'_Mass_Pt_up'
    massPlotsSignal['Pt_down'] = idirROOT+'PostS_'+searchRegion+'_Mass_Pt_down'
    massPlotsSignal['Trigger_up'] = idirROOT+'PostS_'+searchRegion+'_Mass_Trigger_up'
    massPlotsSignal['Trigger_down'] = idirROOT+'PostS_'+searchRegion+'_Mass_Trigger_down'
    massPlotsSignal['K_up'] = idirROOT+'PostS_'+searchRegion+'_Mass_K_up1'
    massPlotsSignal['K_down'] = idirROOT+'PostS_'+searchRegion+'_Mass_K_down1'
    massPlotsSignal['C_up'] = idirROOT+'PostS_'+searchRegion+'_Mass_C_up1'
    massPlotsSignal['C_down'] = idirROOT+'PostS_'+searchRegion+'_Mass_C_down1'
    '''


    # Here: obs=pred, because of blinding
    fpathPred['obs_2018'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta4_rebinIh4_rebinP2_rebinMass1_EtaReweighting.root')
    fpathPred['pred_2018_nominal'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta4_rebinIh4_rebinP2_rebinMass1_EtaReweighting.root')
    fpathPred['pred_2018_etaup'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta2_rebinIh4_rebinP2_rebinMass1_EtaReweighting.root')
    fpathPred['pred_2018_etadown'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta8_rebinIh4_rebinP2_rebinMass1_EtaReweighting.root')
    fpathPred['pred_2018_ihup'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta4_rebinIh2_rebinP2_rebinMass1_EtaReweighting.root')
    fpathPred['pred_2018_ihdown'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta4_rebinIh8_rebinP2_rebinMass1_EtaReweighting.root')
    fpathPred['pred_2018_momup'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta4_rebinIh4_rebinP1_rebinMass1_EtaReweighting.root')
    fpathPred['pred_2018_momdown'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta4_rebinIh4_rebinP4_rebinMass1_EtaReweighting.root')
    fpathPred['pred_2018_corrih'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta4_rebinIh4_rebinP2_rebinMass1_corrTemplateIh_EtaReweighting.root')
    fpathPred['pred_2018_fitihup'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta4_rebinIh4_rebinP2_rebinMass1_fitIhUp_EtaReweighting.root')
    fpathPred['pred_2018_fitihdown'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta4_rebinIh4_rebinP2_rebinMass1_fitIhDown_EtaReweighting.root')
    fpathPred['pred_2018_fitmomup'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta4_rebinIh4_rebinP2_rebinMass1_fitPUp_EtaReweighting.root')
    fpathPred['pred_2018_fitmomdown'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta4_rebinIh4_rebinP2_rebinMass1_fitPDown_EtaReweighting.root')
    #fpathPred['pred_2018_nofit'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta4_rebinIh4_rebinP2_rebinMass1_NoFit_EtaReweighting.root')
    fpathPred['pred_2018_corrP'] = rt.TFile(idirData + 'Mu2018_massCut_0_pT70_V' + versionData + '_Gstrip_Fpix_' + eta + '_cutIndex3_rebinEta4_rebinIh4_rebinP2_rebinMass1_corrTemplateP_EtaReweighting.root')
    

    mass_plot['obs_2018'] = fpathPred['obs_2018'].Get("mass_obs_"+regionBckg)
    mass_plot['pred_2018_nominal'] = fpathPred['pred_2018_nominal'].Get("mass_predBC_"+regionBckg)
    mass_plot['pred_2018_etaup'] = fpathPred['pred_2018_etaup'].Get("mass_predBC_"+regionBckg)
    mass_plot['pred_2018_etadown'] = fpathPred['pred_2018_etadown'].Get("mass_predBC_"+regionBckg)
    mass_plot['pred_2018_ihup'] = fpathPred['pred_2018_ihup'].Get("mass_predBC_"+regionBckg)
    mass_plot['pred_2018_ihdown'] = fpathPred['pred_2018_ihdown'].Get("mass_predBC_"+regionBckg)
    mass_plot['pred_2018_momup'] = fpathPred['pred_2018_momup'].Get("mass_predBC_"+regionBckg)
    mass_plot['pred_2018_momdown'] = fpathPred['pred_2018_momdown'].Get("mass_predBC_"+regionBckg)
    mass_plot['pred_2018_corrih'] = fpathPred['pred_2018_corrih'].Get("mass_predBC_"+regionBckg)
    mass_plot['pred_2018_fitihup'] = fpathPred['pred_2018_fitihup'].Get("mass_predBC_"+regionBckg)
    mass_plot['pred_2018_fitihdown'] = fpathPred['pred_2018_fitihdown'].Get("mass_predBC_"+regionBckg)
    mass_plot['pred_2018_fitmomup'] = fpathPred['pred_2018_fitmomup'].Get("mass_predBC_"+regionBckg)
    mass_plot['pred_2018_fitmomdown'] = fpathPred['pred_2018_fitmomdown'].Get("mass_predBC_"+regionBckg)
    #mass_plot['pred_2018_nofit'] = fpathPred['pred_2018_nofit'].Get("mass_predBC_"+regionBckg)
    mass_plot['pred_2018_corrP'] = fpathPred['pred_2018_corrP'].Get("mass_predBC_"+regionBckg)

    '''   GLUINO m=2000 with Gstrip regions (SR3)
    sig2018_Fpix 	 lnN 	 - 	 - 	 1.0/1.0 	 - 
    sig2018_Gstrip 	 lnN 	 - 	 - 	 0.999210911488/1.00146980555 	 - 
    sig2018_K 	 lnN 	 - 	 - 	 1.00596861116/0.994488631975 	 - 
    sig2018_C 	 lnN 	 - 	 - 	 1.00205568712/1.00001778301 	 - 
    sig2018_Pt 	 lnN 	 - 	 - 	 1.0/1.0 	 - 
    sig_pu 	 lnN 	 0.995238732124/1.00312547152 	 - 	 0.995238732124/1.00312547152 	 - 
    sig_Trigger 	 lnN 	 0.783906987462/1.21239904595 	 - 	 0.783906987462/1.21239904595 	 - 
    sig_lumi 	 lnN 	 1.023 	 - 	 1.025 	 - 
    '''

    signal_pu_up = 1.05
    signal_pu_down = 0.95
    signal_Fpix_up = 1.05
    signal_Fpix_down = 0.95
    signal_Pt_up = 1.01
    signal_Pt_down = 0.99
    signal_Trigger_up = 1.20
    signal_Trigger_down = 0.80
    signal_K_up = 1.01
    signal_K_down = 0.99
    signal_C_up = 1.01
    signal_C_down = 0.99


    for signal in fpath.keys():
        
        ifile = rt.TFile(fpath[signal])
        nominalSignal_TH2 = ifile.Get(massPlotsSignal['Nominal'])
        nominalSignal = nominalSignal_TH2.ProjectionY("nominalSignal", 1, nominalSignal_TH2.GetNbinsX())
        
        mean = nominalSignal.GetMean()
        stddev = nominalSignal.GetStdDev()

        xmin = mean - stddev
        xmax = mean + 2*stddev
        print("Signal: " + signal + " ; mass range: ", xmin, xmax)

        if (xmin < 300): xmin = 300

        # Calculate the yields in the signal region
        bkg_2018_nominal = integralHisto(mass_plot['pred_2018_nominal'],xmin,xmax)
        bkg_2018_etaBinning_up = integralHisto(mass_plot['pred_2018_etaup'],xmin,xmax)
        bkg_2018_etaBinning_down = integralHisto(mass_plot['pred_2018_etadown'],xmin,xmax)
        bkg_2018_ihBinning_up = integralHisto(mass_plot['pred_2018_ihup'],xmin,xmax)
        bkg_2018_ihBinning_down = integralHisto(mass_plot['pred_2018_ihdown'],xmin,xmax)
        bkg_2018_momBinning_up = integralHisto(mass_plot['pred_2018_momup'],xmin,xmax)
        bkg_2018_momBinning_down = integralHisto(mass_plot['pred_2018_momdown'],xmin,xmax)
        bkg_2018_corrTemplateIh_up = integralHisto(mass_plot['pred_2018_corrih'],xmin,xmax)
        bkg_2018_corrTemplateIh_down = integralHisto(mass_plot['pred_2018_corrih'],xmin,xmax)
        bkg_2018_fitIh_up = integralHisto(mass_plot['pred_2018_fitihup'],xmin,xmax)
        bkg_2018_fitIh_down = integralHisto(mass_plot['pred_2018_fitihdown'],xmin,xmax)
        bkg_2018_fitMom_up = integralHisto(mass_plot['pred_2018_fitmomup'],xmin,xmax)
        bkg_2018_fitMom_down = integralHisto(mass_plot['pred_2018_fitmomdown'],xmin,xmax)
        #bkg_2018_nofit = integralHisto(mass_plot['pred_2018_nofit'],xmin,xmax)
        bkg_2018_corrTemplateP_up = integralHisto(mass_plot['pred_2018_corrP'],xmin,xmax)
        bkg_2018_corrTemplateP_down = integralHisto(mass_plot['pred_2018_corrP'],xmin,xmax)
        
        signal_yield = integralHisto(nominalSignal,xmin,xmax)
        '''
        signal_pu_up = integralHisto(ifile.Get(massPlotsSignal['PU_up']),xmin,xmax)
        signal_pu_down = integralHisto(ifile.Get(massPlotsSignal['PU_down']),xmin,xmax)
        signal_Fpix_up = integralHisto(ifile.Get(massPlotsSignal['Fpix_up']),xmin,xmax)
        signal_Fpix_down = integralHisto(ifile.Get(massPlotsSignal['Fpix_down']),xmin,xmax)
        signal_Pt_up = integralHisto(ifile.Get(massPlotsSignal['Pt_up']),xmin,xmax)
        signal_Pt_down = integralHisto(ifile.Get(massPlotsSignal['Pt_down']),xmin,xmax)
        signal_Trigger_up = integralHisto(ifile.Get(massPlotsSignal['Trigger_up']),xmin,xmax)
        signal_Trigger_down = integralHisto(ifile.Get(massPlotsSignal['Trigger_down']),xmin,xmax)
        signal_K_up = integralHisto(ifile.Get(massPlotsSignal['K_up']),xmin,xmax)
        signal_K_down = integralHisto(ifile.Get(massPlotsSignal['K_down']),xmin,xmax)
        signal_C_up = integralHisto(ifile.Get(massPlotsSignal['C_up']),xmin,xmax)
        signal_C_down = integralHisto(ifile.Get(massPlotsSignal['C_down']),xmin,xmax)
        '''

        # Normalize the uncertainties to the nominal yield
        if(bkg_2018_nominal!=0):
            bkg_2018_etaBinning_up /= bkg_2018_nominal
            bkg_2018_etaBinning_down /= bkg_2018_nominal
            bkg_2018_ihBinning_up /= bkg_2018_nominal
            bkg_2018_ihBinning_down /= bkg_2018_nominal
            bkg_2018_momBinning_up /= bkg_2018_nominal
            bkg_2018_momBinning_down /= bkg_2018_nominal
            bkg_2018_corrTemplateIh_up /= bkg_2018_nominal
            bkg_2018_corrTemplateIh_down /= bkg_2018_nominal
            bkg_2018_fitIh_up /= bkg_2018_nominal
            bkg_2018_fitIh_down /= bkg_2018_nominal
            bkg_2018_fitMom_up /= bkg_2018_nominal
            bkg_2018_fitMom_down /= bkg_2018_nominal
            #bkg_2018_nofit /= bkg_2018_nominal
            bkg_2018_corrTemplateP_up /= bkg_2018_nominal
            bkg_2018_corrTemplateP_down /= bkg_2018_nominal

        '''
        if(signal_yield != 0):
            signal_pu_up /= signal_yield
            signal_pu_down /= signal_yield
            signal_Fpix_up /= signal_yield
            signal_Fpix_down /= signal_yield
            signal_Pt_up /= signal_yield
            signal_Pt_down /= signal_yield
            signal_Trigger_up /= signal_yield
            signal_Trigger_down /= signal_yield
            signal_K_up /= signal_yield
            signal_K_down /= signal_yield
            signal_C_up /= signal_yield
            signal_C_down /= signal_yield
        '''

        # Save in dictionaries for the datacard
        sig_2018_unc = {
            'sig2018_Fpix': [signal_Fpix_down, signal_Fpix_up],
            'sig2018_Pt': [signal_Pt_down, signal_Pt_up],
            'sig2018_K': [signal_K_down, signal_K_up],
            'sig2018_C': [signal_C_down, signal_C_up],
        }

        sig_unc_correlated = {
            'sig_pu' : [signal_pu_down, signal_pu_up],
            'sig_Trigger' : [signal_Trigger_down, signal_Trigger_up],
        }
            
        bkg_2018_unc = {
            'bkg2018_fitIh': [bkg_2018_fitIh_down, bkg_2018_fitIh_up],
            'bkg2018_fitMom': [bkg_2018_fitMom_down, bkg_2018_fitMom_up],
            #'bkg2018_nofit': [bkg_2018_nofit],
        }

        bkg_unc_correlated = {
            'bkg_etaBinning' : [bkg_2018_etaBinning_down, bkg_2018_etaBinning_up],
            'bkg_ihBinning' : [bkg_2018_ihBinning_down, bkg_2018_ihBinning_up],
            'bkg_momentumBinning' : [bkg_2018_momBinning_down, bkg_2018_momBinning_up],
            'bkg_correctionTemplateIh' : [bkg_2018_corrTemplateIh_down, bkg_2018_corrTemplateIh_up],
            'bkg_correctionTemplateP' : [bkg_2018_corrTemplateP_down, bkg_2018_corrTemplateP_up],
        }

        # Make the datacard
        #intLumi = 41.5 #2017
        intLumi = 59.9 #2018
        #intLumi = 101. # 2017 + 2018
        MakeDatacard(outDataCardsDir, signal, signal_yield*intLumi/101, bkg_2018_nominal, sig_2018_unc,  sig_unc_correlated, bkg_2018_unc, bkg_unc_correlated)

        # Save in a .root file the nominalSignal histo:
        fout = rt.TFile(outDataCardsDir + signal + ".root", "RECREATE")
        fout.cd()
        nominalSignal.SetName("nominalSignal")
        nominalSignal.Write()
        fout.Close()
        
