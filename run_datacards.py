from optparse import OptionParser
import numpy as np
import os
import sys

from threading import Thread
from combine_parameters import toy_number,nice_priority,upperFactor


def readNorm(f_cscCard):
    f = open(f_cscCard,"r")
    norm = float(f.readline().split()[3])
    return norm

def insert(originalfile,string):
    with open(originalfile,'r') as f:
        with open('newfile.txt','w') as f2:
            f2.write(string)
            f2.write(f.read())
    os.rename('newfile.txt',originalfile)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-l', '--limits',type='string', action='store',
                    default   =   'Asymptotic',
                    dest      =   'limits',
                    help      =   'string to chose the type of limit computation, asymptotic or full CLS')
    parser.add_option('-s', '--significance', action='store_true',
                    default   =   False,
                    dest      =   'sig',
                    help      =   'Perform significance computation if bool is true')

    parser.add_option('-d', '--debug', type='int',
                    default       =       1,
                    dest          =       'debug',
                    help          =       'Debug level')

    (options, args) = parser.parse_args()
    debug = options.debug
    



    input_dir='datacards_SR3_ReRunGael'
    tree_dir='limitTrees_SR3_ReRunGael'  # = output directory here
    if(options.limits == "CLS"):
        tree_dir = tree_dir+"_CLS"
	
    os.system("mkdir -p {0}/".format(input_dir))
    os.system("mkdir -p {0}/".format(tree_dir))

    samples = [
        'Gluino100_2018',
        'Gluino200_2018',
        'Gluino400_2018',
        'Gluino500_2018',
        'Gluino800_2018',
        'Gluino1000_2018',
        'Gluino1400_2018',
        'Gluino1600_2018',
	    'Gluino1800_2018',
        'Gluino2000_2018',
        'Gluino2200_2018',
        'Gluino2400_2018',
        'Gluino2600_2018',

        'Stop100_2018',
        'Stop400_2018',
        'Stop500_2018',
        'Stop800_2018',
        'Stop1000_2018',
        'Stop1200_2018',
        'Stop1400_2018',
        'Stop1600_2018',
	    'Stop1800_2018',
        'Stop2000_2018',
        'Stop2200_2018',
        'Stop2400_2018',
        'Stop2600_2018',

        'pairStau200_2018',
        'pairStau247_2018',
        'pairStau308_2018',
        'pairStau432_2018',
        'pairStau557_2018',
        'pairStau651_2018',
        'pairStau745_2018',
        'pairStau871_2018',
        'pairStau1029_2018',
        'pairStau1218_2018',
        'pairStau1409_2018',
        'pairStau1599_2018',

        'gmsbStau200_2018',
        'gmsbStau247_2018',
        'gmsbStau308_2018',
        'gmsbStau432_2018',
        'gmsbStau557_2018',
        'gmsbStau651_2018',
        'gmsbStau745_2018',
        'gmsbStau871_2018',
        'gmsbStau1029_2018',
        'gmsbStau1218_2018',
        'gmsbStau1409_2018',
        'gmsbStau1599_2018',

        'DYcharge1e_100_2018',
        'DYcharge1e_200_2018',
        'DYcharge1e_400_2018',
        'DYcharge1e_500_2018',
        'DYcharge1e_800_2018',
        'DYcharge1e_1000_2018',
        'DYcharge1e_1400_2018',
        'DYcharge1e_1800_2018',
        'DYcharge1e_2200_2018',
        'DYcharge1e_2600_2018',

        'DYcharge2e_100_2018',
        'DYcharge2e_200_2018',
        'DYcharge2e_400_2018',
        'DYcharge2e_500_2018',
        'DYcharge2e_800_2018',
        'DYcharge2e_1000_2018',
        'DYcharge2e_1400_2018',
        'DYcharge2e_1800_2018',
        'DYcharge2e_2200_2018',
        'DYcharge2e_2600_2018',

        'tauPrime2e-200-ZPrime-3000_2018',
        'tauPrime2e-200-ZPrime-4000_2018',
        'tauPrime2e-200-ZPrime-5000_2018',
        'tauPrime2e-200-ZPrime-6000_2018',
        'tauPrime2e-200-ZPrime-7000_2018',
        'tauPrime2e-200-ZPrimeSSM-3000_2018',
        'tauPrime2e-200-ZPrimeSSM-4000_2018',
        'tauPrime2e-200-ZPrimeSSM-5000_2018',
        'tauPrime2e-200-ZPrimeSSM-6000_2018',
        'tauPrime2e-200-ZPrimeSSM-7000_2018',

        'tauPrime2e-400-ZPrime-3000_2018',
        'tauPrime2e-400-ZPrime-4000_2018',
        'tauPrime2e-400-ZPrime-5000_2018',
        'tauPrime2e-400-ZPrime-6000_2018',
        'tauPrime2e-400-ZPrime-7000_2018',
        'tauPrime2e-400-ZPrimeSSM-3000_2018',
        'tauPrime2e-400-ZPrimeSSM-4000_2018',
        'tauPrime2e-400-ZPrimeSSM-5000_2018',
        'tauPrime2e-400-ZPrimeSSM-6000_2018',
        'tauPrime2e-400-ZPrimeSSM-7000_2018',

        'tauPrime2e-600-ZPrime-3000_2018',
        'tauPrime2e-600-ZPrime-4000_2018',
        'tauPrime2e-600-ZPrime-5000_2018',
        'tauPrime2e-600-ZPrime-6000_2018',
        'tauPrime2e-600-ZPrime-7000_2018',
        'tauPrime2e-600-ZPrimeSSM-3000_2018',
        'tauPrime2e-600-ZPrimeSSM-4000_2018',
        'tauPrime2e-600-ZPrimeSSM-5000_2018',
        'tauPrime2e-600-ZPrimeSSM-6000_2018',
        'tauPrime2e-600-ZPrimeSSM-7000_2018',

        'tauPrime2e-800-ZPrime-4000_2018',
        'tauPrime2e-800-ZPrime-5000_2018',
        'tauPrime2e-800-ZPrime-6000_2018',
        'tauPrime2e-800-ZPrime-7000_2018',
        'tauPrime2e-800-ZPrimeSSM-4000_2018',
        'tauPrime2e-800-ZPrimeSSM-5000_2018',
        'tauPrime2e-800-ZPrimeSSM-6000_2018',
        'tauPrime2e-800-ZPrimeSSM-7000_2018',

        'tauPrime2e-1000-ZPrime-3000_2018',
        'tauPrime2e-1000-ZPrime-4000_2018',
        'tauPrime2e-1000-ZPrime-5000_2018',
        'tauPrime2e-1000-ZPrime-6000_2018',
        'tauPrime2e-1000-ZPrime-7000_2018',
        'tauPrime2e-1000-ZPrimeSSM-3000_2018',
        'tauPrime2e-1000-ZPrimeSSM-4000_2018',
        'tauPrime2e-1000-ZPrimeSSM-5000_2018',
        'tauPrime2e-1000-ZPrimeSSM-6000_2018',
        'tauPrime2e-1000-ZPrimeSSM-7000_2018',

        'tauPrime2e-1200-ZPrime-3000_2018',
        'tauPrime2e-1200-ZPrime-4000_2018',
        'tauPrime2e-1200-ZPrime-5000_2018',
        'tauPrime2e-1200-ZPrime-6000_2018',
        'tauPrime2e-1200-ZPrime-7000_2018',
        'tauPrime2e-1200-ZPrimeSSM-3000_2018',
        'tauPrime2e-1200-ZPrimeSSM-4000_2018',
        'tauPrime2e-1200-ZPrimeSSM-5000_2018',
        'tauPrime2e-1200-ZPrimeSSM-6000_2018',
        'tauPrime2e-1200-ZPrimeSSM-7000_2018',

        'tauPrime2e-1400-ZPrime-3000_2018',
        'tauPrime2e-1400-ZPrime-4000_2018',
        'tauPrime2e-1400-ZPrime-5000_2018',
        'tauPrime2e-1400-ZPrime-6000_2018',
        'tauPrime2e-1400-ZPrime-7000_2018',
        'tauPrime2e-1400-ZPrimeSSM-3000_2018',
        'tauPrime2e-1400-ZPrimeSSM-4000_2018',
        'tauPrime2e-1400-ZPrimeSSM-5000_2018',
        'tauPrime2e-1400-ZPrimeSSM-6000_2018',
        'tauPrime2e-1400-ZPrimeSSM-7000_2018',
    ]

    samples = [
        'Gluino100_2018',
        'Gluino200_2018',
        'Gluino400_2018',
        'Gluino500_2018',
        'Gluino800_2018',
        'Gluino1000_2018',
        'Gluino1400_2018',
        'Gluino1600_2018',
	    'Gluino1800_2018',
        'Gluino2000_2018',
        'Gluino2200_2018',
        'Gluino2400_2018',
        'Gluino2600_2018',

        'Stop100_2018',
        'Stop400_2018',
        'Stop500_2018',
        'Stop800_2018',
        'Stop1000_2018',
        'Stop1200_2018',
        'Stop1400_2018',
        'Stop1600_2018',
	    'Stop1800_2018',
        'Stop2000_2018',
        'Stop2200_2018',
        'Stop2400_2018',
        'Stop2600_2018',

        'pairStau200_2018',
        'pairStau247_2018',
        'pairStau308_2018',
        'pairStau432_2018',
        'pairStau557_2018',
        'pairStau651_2018',
        'pairStau745_2018',
        'pairStau871_2018',
        'pairStau1029_2018',
        'pairStau1218_2018',
        'pairStau1409_2018',
        'pairStau1599_2018',

        'gmsbStau200_2018',
        'gmsbStau247_2018',
        'gmsbStau308_2018',
        'gmsbStau432_2018',
        'gmsbStau557_2018',
        'gmsbStau651_2018',
        'gmsbStau745_2018',
        'gmsbStau871_2018',
        'gmsbStau1029_2018',
        'gmsbStau1218_2018',
        'gmsbStau1409_2018',
        'gmsbStau1599_2018',

        'DYcharge1e_100_2018',
        'DYcharge1e_200_2018',
        'DYcharge1e_400_2018',
        'DYcharge1e_500_2018',
        'DYcharge1e_800_2018',
        'DYcharge1e_1000_2018',
        'DYcharge1e_1400_2018',
        'DYcharge1e_1800_2018',
        'DYcharge1e_2200_2018',
        'DYcharge1e_2600_2018',

        'DYcharge2e_100_2018',
        'DYcharge2e_200_2018',
        'DYcharge2e_400_2018',
        'DYcharge2e_500_2018',
        'DYcharge2e_800_2018',
        'DYcharge2e_1000_2018',
        'DYcharge2e_1400_2018',
        'DYcharge2e_1800_2018',
        'DYcharge2e_2200_2018',
        'DYcharge2e_2600_2018'
    ]
    
   
    
    

    def task(sample):
        name=sample
        name2="datacard_"+sample
        name2=sample
        print name

        if(options.limits == "CLS"):
            expMedian = "0.5"
            expp1sig = "0.84"
            expp2sig = "0.975"
            expm1sig = "0.16"
            expm2sig = "0.025"
    
            nameMedian = name+"_"+expMedian.replace(".","p")
            namep1sig = name+"_"+expp1sig.replace(".","p")
            namep2sig = name+"_"+expp2sig.replace(".","p")
            namem1sig = name+"_"+expm1sig.replace(".","p")
            namem2sig = name+"_"+expm2sig.replace(".","p")
        
            run_combine_median = "nice -n {} combine -H AsymptoticLimits -M HybridNew  -n .{} -d {}/{}.txt --expectedFromGrid={} --saveWorkspace --LHCmode LHC-limits -v 1 --rRelAcc 0.000005 --rAbsAcc 0.000005 --adaptiveToys 1 -T {} &".format(nice_priority,name, input_dir, name2,expMedian,toy_number)
            print run_combine_median
            os.system(run_combine_median)
            os.system("mv higgsCombine.{0}.HybridNew.mH120.quant0.500.root {1}/".format(name, tree_dir))
   
            run_combine_observed = "nice -n {} combine -H AsymptoticLimits -M HybridNew  -n .{} -d {}/{}.txt --saveWorkspace --LHCmode LHC-limits -v 1 --rRelAcc 0.000005 --rAbsAcc 0.000005 &".format(nice_priority,name, input_dir, name2)
            os.system(run_combine_observed)
            os.system("mv higgsCombine.{0}.HybridNew.mH120.root {1}/higgsCombine.{2}.HybridNew.mH120.obs.root".format(name,tree_dir,name))

 
            run_combine_p1sig = "nice -n {} combine -H AsymptoticLimits -M HybridNew  -n .{} -d {}/{}.txt --expectedFromGrid={} --saveWorkspace --LHCmode LHC-limits -v 1 --rRelAcc 0.000005 --rAbsAcc 0.000005 --adaptiveToys 1 -T {} &".format(nice_priority,name, input_dir, name2,expp1sig,toy_number)
            print run_combine_p1sig
            os.system(run_combine_p1sig)
            os.system("mv higgsCombine.{0}.HybridNew.mH120.quant0.840.root {1}/".format(name, tree_dir))
     
            run_combine_p2sig = "nice -n {} combine -H AsymptoticLimits -M HybridNew  -n .{} -d {}/{}.txt --expectedFromGrid={} --saveWorkspace --LHCmode LHC-limits -v 1 --rRelAcc 0.000005 --rAbsAcc 0.000005 --adaptiveToys 1 -T {} &".format(nice_priority,name, input_dir, name2,expp2sig,toy_number)
            print run_combine_p2sig
            os.system(run_combine_p2sig)
            os.system("mv higgsCombine.{0}.HybridNew.mH120.quant0.975.root {1}/".format(name, tree_dir))
    
    
            run_combine_m1sig = "nice -n {} combine -H AsymptoticLimits -M HybridNew  -n .{} -d {}/{}.txt --expectedFromGrid={} --saveWorkspace --LHCmode LHC-limits -v 1 --rRelAcc 0.000005 --rAbsAcc 0.000005 --adaptiveToys 1 -T {} &".format(nice_priority,name, input_dir, name2,expm1sig,toy_number)
            print run_combine_m1sig
            os.system(run_combine_m1sig)
            os.system("mv higgsCombine.{0}.HybridNew.mH120.quant0.160.root {1}/".format(name, tree_dir))
            
            run_combine_m2sig = "nice -n {} combine -H AsymptoticLimits -M HybridNew  -n .{} -d {}/{}.txt --expectedFromGrid={} --saveWorkspace --LHCmode LHC-limits -v 1 --rRelAcc 0.000005 --rAbsAcc 0.000005 --adaptiveToys 1 -T {} &".format(nice_priority,name, input_dir, name2,expm2sig,toy_number)
            print run_combine_m2sig
            os.system(run_combine_m2sig)
            os.system("mv higgsCombine.{0}.HybridNew.mH120.quant0.025.root {1}/".format(name, tree_dir))

        if(options.limits == "Asymptotic"):
            run_combine = "combine -M AsymptoticLimits -n .{} -d {}/{}.txt --rRelAcc 0.000005 --rAbsAcc 0.000005 --rMin -1000.0 --rMax 1000.0".format(name, input_dir, name2)
            if(debug>0):
                print("Running command {}".format(run_combine))
            os.system(run_combine)
            os.system("mv higgsCombine.{0}.AsymptoticLimits.mH120.root {1}/".format(name, tree_dir))


        if(options.sig):
            run_combine = "combine -M Significance -n .{} {}/{}.txt -t -1 --expectSignal=1" .format(name, input_dir, name2)
            #run_combine = "combine -M Significance -n .{} {}/{}.txt" .format(name, input_dir, name2)
            print run_combine
            os.system(run_combine)
            os.system("mv higgsCombine.{0}.Significance.mH120.root {1}/".format(name, tree_dir))
    
    for sample in samples:
        ### For parallel running, use both following lines
        #t = Thread(target=task, args=(sample,))
        #t.start()
        
        ### use this line to run signal one after the other
        task(sample)
