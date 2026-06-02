import ROOT
import subprocess
import os
import sys
sys.argv.append(' -b- ')


 
hyp_sigGlu = ["Gluino100","Gluino200","Gluino400","Gluino500","Gluino800","Gluino1000","Gluino1400","Gluino1600","Gluino1800","Gluino2000","Gluino2200","Gluino2400", "Gluino2600"]

hyp_sigStop = ["Stop100","Stop400","Stop500","Stop800","Stop1000","Stop1200","Stop1400","Stop1600","Stop1800","Stop2000","Stop2200","Stop2400","Stop2600"]

#hyp_sigPpstau = ["pairStau200","pairStau247","pairStau308","pairStau432","pairStau557","pairStau651","pairStau745","pairStau871","pairStau1029","pairStau1218","pairStau1409","pairStau1599"]
hyp_sigPpstau = ["pairStau308"]

hyp_sigGmsbStau = ["gmsbStau200","gmsbStau247",'gmsbStau308','gmsbStau432','gmsbStau557','gmsbStau651','gmsbStau745','gmsbStau871','gmsbStau1029','gmsbStau1218','gmsbStau1409','gmsbStau1599']

#hyp_sigDY1e = ['DYcharge1e_100','DYcharge1e_200','DYcharge1e_400','DYcharge1e_500','DYcharge1e_800','DYcharge1e_1000','DYcharge1e_1400','DYcharge1e_1800','DYcharge1e_2200','DYcharge1e_2600']
hyp_sigDY1e = ['DYcharge1e_400']

#hyp_sigDY2e = ['DYcharge2e_100','DYcharge2e_200','DYcharge2e_400','DYcharge2e_500','DYcharge2e_800','DYcharge2e_1000','DYcharge2e_1400','DYcharge2e_1800','DYcharge2e_2200','DYcharge2e_2600']
hyp_sigDY2e = ['DYcharge2e_100','DYcharge2e_1000']


hyp_tauPrime2e_200_Zprime = ['tauPrime2e-200-ZPrime-3000','tauPrime2e-200-ZPrime-4000','tauPrime2e-200-ZPrime-5000','tauPrime2e-200-ZPrime-6000','tauPrime2e-200-ZPrime-7000']
hyp_tauPrime2e_200_ZprimeSSM = ['tauPrime2e-200-ZPrimeSSM-3000','tauPrime2e-200-ZPrimeSSM-4000','tauPrime2e-200-ZPrimeSSM-5000','tauPrime2e-200-ZPrimeSSM-6000','tauPrime2e-200-ZPrimeSSM-7000']

hyp_tauPrime2e_400_Zprime = ['tauPrime2e-400-ZPrime-3000','tauPrime2e-400-ZPrime-4000','tauPrime2e-400-ZPrime-5000','tauPrime2e-400-ZPrime-6000','tauPrime2e-400-ZPrime-7000']
hyp_tauPrime2e_400_ZprimeSSM = ['tauPrime2e-400-ZPrimeSSM-3000','tauPrime2e-400-ZPrimeSSM-4000','tauPrime2e-400-ZPrimeSSM-5000','tauPrime2e-400-ZPrimeSSM-6000','tauPrime2e-400-ZPrimeSSM-7000']

hyp_tauPrime2e_600_Zprime = ['tauPrime2e-600-ZPrime-3000','tauPrime2e-600-ZPrime-4000','tauPrime2e-600-ZPrime-5000','tauPrime2e-600-ZPrime-6000','tauPrime2e-600-ZPrime-7000']
hyp_tauPrime2e_600_ZprimeSSM = ['tauPrime2e-600-ZPrimeSSM-3000','tauPrime2e-600-ZPrimeSSM-4000','tauPrime2e-600-ZPrimeSSM-5000','tauPrime2e-600-ZPrimeSSM-6000','tauPrime2e-600-ZPrimeSSM-7000']

hyp_tauPrime2e_800_Zprime = ['tauPrime2e-800-ZPrime-3000','tauPrime2e-800-ZPrime-4000','tauPrime2e-800-ZPrime-5000','tauPrime2e-800-ZPrime-6000','tauPrime2e-800-ZPrime-7000']
hyp_tauPrime2e_800_ZprimeSSM = ['tauPrime2e-800-ZPrimeSSM-3000','tauPrime2e-800-ZPrimeSSM-4000','tauPrime2e-800-ZPrimeSSM-5000','tauPrime2e-800-ZPrimeSSM-6000','tauPrime2e-800-ZPrimeSSM-7000']

hyp_tauPrime2e_1000_Zprime = ['tauPrime2e-1000-ZPrime-3000','tauPrime2e-1000-ZPrime-4000','tauPrime2e-1000-ZPrime-5000','tauPrime2e-1000-ZPrime-6000','tauPrime2e-1000-ZPrime-7000']
hyp_tauPrime2e_1000_ZprimeSSM = ['tauPrime2e-1000-ZPrimeSSM-3000','tauPrime2e-1000-ZPrimeSSM-4000','tauPrime2e-1000-ZPrimeSSM-5000','tauPrime2e-1000-ZPrimeSSM-6000','tauPrime2e-1000-ZPrimeSSM-7000']

hyp_tauPrime2e_1200_Zprime = ['tauPrime2e-1200-ZPrime-3000','tauPrime2e-1200-ZPrime-4000','tauPrime2e-1200-ZPrime-5000','tauPrime2e-1200-ZPrime-6000','tauPrime2e-1200-ZPrime-7000']
hyp_tauPrime2e_1200_ZprimeSSM = ['tauPrime2e-1200-ZPrimeSSM-3000','tauPrime2e-1200-ZPrimeSSM-4000','tauPrime2e-1200-ZPrimeSSM-5000','tauPrime2e-1200-ZPrimeSSM-6000','tauPrime2e-1200-ZPrimeSSM-7000']

hyp_tauPrime2e_1400_Zprime = ['tauPrime2e-1400-ZPrime-3000','tauPrime2e-1400-ZPrime-4000','tauPrime2e-1400-ZPrime-5000','tauPrime2e-1400-ZPrime-6000','tauPrime2e-1400-ZPrime-7000']
hyp_tauPrime2e_1400_ZprimeSSM = ['tauPrime2e-1400-ZPrimeSSM-3000','tauPrime2e-1400-ZPrimeSSM-4000','tauPrime2e-1400-ZPrimeSSM-5000','tauPrime2e-1400-ZPrimeSSM-6000','tauPrime2e-1400-ZPrimeSSM-7000']



def mergeCombWorkspace(signals, directory, outputdir):
    chains = {}
    ext = ''

    for mass_point in signals:
        chains[mass_point] = ROOT.TChain("limit")
        root_files = [] 

        root_files.append("{}/higgsCombine.{}_2018{}.HybridNew.mH120.quant0.025.root".format(directory,mass_point,ext)) 
        root_files.append("{}/higgsCombine.{}_2018{}.HybridNew.mH120.quant0.160.root".format(directory,mass_point,ext))
        root_files.append("{}/higgsCombine.{}_2018{}.HybridNew.mH120.quant0.500.root".format(directory,mass_point,ext))
        root_files.append("{}/higgsCombine.{}_2018{}.HybridNew.mH120.quant0.840.root".format(directory,mass_point,ext))
        root_files.append("{}/higgsCombine.{}_2018{}.HybridNew.mH120.quant0.975.root".format(directory,mass_point,ext))
        root_files.append("{}/higgsCombine.{}_2018{}.HybridNew.mH120.root".format(directory,mass_point,ext))

        for root_file in root_files:
            chains[mass_point].Add(root_file)


        output_file = "{}/higgsCombine.{}_2018{}.HybridNew.all.mH120.root".format(outputdir,mass_point,ext)
        chains[mass_point].Merge(output_file)

        print("Merged :         {}        in         {}".format(mass_point, output_file))



# ---------------------------------------------------------------

directory = "limitTrees_SR3_Test_SystK1C1_codeChanged_CLS"
outputdir = "limitTrees_SR3_Test_SystK1C1_codeChanged_CLS_merged"
os.system('mkdir -p ' + outputdir)


mergeCombWorkspace(hyp_sigPpstau, directory, outputdir)

'''
mergeCombWorkspace(hyp_sigGlu, directory, outputdir)
mergeCombWorkspace(hyp_sigStop, directory, outputdir)
mergeCombWorkspace(hyp_sigPpstau, directory, outputdir)
mergeCombWorkspace(hyp_sigGmsbStau, directory, outputdir)
mergeCombWorkspace(hyp_sigDY1e, directory, outputdir)
mergeCombWorkspace(hyp_sigDY2e, directory, outputdir)
'''

'''
mergeCombWorkspace(hyp_tauPrime2e_200_Zprime)
mergeCombWorkspace(hyp_tauPrime2e_200_ZprimeSSM)
mergeCombWorkspace(hyp_tauPrime2e_400_Zprime)
mergeCombWorkspace(hyp_tauPrime2e_400_ZprimeSSM)
mergeCombWorkspace(hyp_tauPrime2e_600_Zprime)
mergeCombWorkspace(hyp_tauPrime2e_600_ZprimeSSM)
mergeCombWorkspace(hyp_tauPrime2e_800_Zprime)
mergeCombWorkspace(hyp_tauPrime2e_800_ZprimeSSM)
mergeCombWorkspace(hyp_tauPrime2e_1000_Zprime)
mergeCombWorkspace(hyp_tauPrime2e_1000_ZprimeSSM)
mergeCombWorkspace(hyp_tauPrime2e_1200_Zprime)
mergeCombWorkspace(hyp_tauPrime2e_1200_ZprimeSSM)
mergeCombWorkspace(hyp_tauPrime2e_1400_Zprime)
mergeCombWorkspace(hyp_tauPrime2e_1400_ZprimeSSM)
'''
