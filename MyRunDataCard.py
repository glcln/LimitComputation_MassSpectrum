from optparse import OptionParser
import numpy as np
import os
import sys
import time

from threading import Thread
from combine_parameters import toy_number,nice_priority,upperFactor
import subprocess

if __name__ == '__main__':


    # SETUP
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
    
    print("Computing significances ? {}".format(options.sig))


    eta = "EtaMix"
    idir = 'MyDataCards/datacards_8fp10_' + eta
    odir = 'MyDataCards/limit_8fp10_' + eta  # = output directory here
    if(options.limits == "CLS"):
        odir += "_CLS"
	
    os.system("mkdir -p {0}/".format(idir))
    os.system("mkdir -p {0}/".format(odir))



    #SAMPLES
    samples = [
        'Gluino2000_2018',
        #'Gluino2000_2018_Original',
    ]


    # MAIN
    def task(sample):
        name = sample
        print name
        
        if(options.limits == "CLS"):
            expMedian = "0.5"
            expp1sig = "0.84"
            expp2sig = "0.975"
            expm1sig = "0.16"
            expm2sig = "0.025"
    
            nameMedian = name + "_"+expMedian.replace(".","p")
            namep1sig = name + "_"+expp1sig.replace(".","p")
            namep2sig = name + "_"+expp2sig.replace(".","p")
            namem1sig = name + "_"+expm1sig.replace(".","p")
            namem2sig = name + "_"+expm2sig.replace(".","p")
            absAcc = 0.0005

            ext = "_frozenUpGiSis"

            run_combine_observed = "nice -n {} combine -H AsymptoticLimits -M HybridNew  -n .{} -d {}/{}.txt --saveWorkspace --LHCmode LHC-limits -v 1 --rAbsAcc 0.00005 &".format(nice_priority, name, idir, name)
 
            run_combine_median = "nice -n {} combine -H AsymptoticLimits -M HybridNew  -n .{} -d {}/{}.txt --expectedFromGrid={} --saveWorkspace --LHCmode LHC-limits -v 1 --rAbsAcc {} --adaptiveToys 1 -T {} &".format(nice_priority, name, idir, name, expMedian, absAcc, toy_number)   
            
            run_combine_p1sig = "nice -n {} combine -H AsymptoticLimits -M HybridNew  -n .{} -d {}/{}.txt --expectedFromGrid={} --saveWorkspace --LHCmode LHC-limits -v 1 --rAbsAcc {} --adaptiveToys 1 -T {} &".format(nice_priority, name, idir, name, expp1sig, absAcc, toy_number)
     
            run_combine_p2sig = "nice -n {} combine -H AsymptoticLimits -M HybridNew  -n .{} -d {}/{}.txt --expectedFromGrid={} --saveWorkspace --LHCmode LHC-limits -v 1 --rAbsAcc {} --adaptiveToys 1 -T {} &".format(nice_priority, name, idir, name, expp2sig, absAcc, toy_number)
        
            run_combine_m1sig = "nice -n {} combine -H AsymptoticLimits -M HybridNew  -n .{} -d {}/{}.txt --expectedFromGrid={} --saveWorkspace --LHCmode LHC-limits -v 1 --rAbsAcc {} --adaptiveToys 1 -T {} &".format(nice_priority, name, idir, name, expm1sig, absAcc, toy_number)
            
            run_combine_m2sig = "nice -n {} combine -H AsymptoticLimits -M HybridNew  -n .{} -d {}/{}.txt --expectedFromGrid={} --saveWorkspace --LHCmode LHC-limits -v 1 --rAbsAcc {} --adaptiveToys 1 -T {} &".format(nice_priority, name, idir, name, expm2sig, absAcc, toy_number)


            commands_combine = [run_combine_m2sig,run_combine_observed,run_combine_p1sig]
            for command in commands_combine:
                print(command)
                os.system(command)
            time.sleep(7200)

            commands_combine2 = [run_combine_p2sig,run_combine_m1sig,run_combine_median]
            for command in commands_combine2:
                print(command)
                os.system(command)

            time.sleep(7200)


        if(options.limits == "Asymptotic"):
            run_combine = "combine -M AsymptoticLimits -n .{} -d {}/{}.txt --rRelAcc 0.000005 --rAbsAcc 0.000005 --rMin -1000.0 --rMax 1000.0".format(name, idir, name)
            if(debug>0):
                print("Running command {}".format(run_combine))
            os.system(run_combine)
            os.system("mv higgsCombine.{0}.AsymptoticLimits.mH120.root {1}/".format(name, odir))


        if(options.sig):
            run_combine = "combine -M Significance -n .{} {}/{}.txt -t -1 --expectSignal=1" .format(name, idir, name)
            print run_combine
            os.system(run_combine)
            os.system("mv higgsCombine.{0}.Significance.mH120.root {1}/".format(name, odir))



    for sample in samples:
        task(sample)
