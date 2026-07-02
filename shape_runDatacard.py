from optparse import OptionParser
import os
import sys

# Lancer la commande:

# FullTracker + shape + asymptotique: py shape_runDatacard.py
# Séparation Eta1/Eta1_2p4 + shape + asymptotique: py shape_runDatacard.py --splitEta

# Cut and count: py shape_runDatacard.py --cac (--splitEta)

# Idem mais en CLS: py shape_runDatacard.py -l CLS (--splitEta)

# Calculer la significance: py shape_runDatacard.py (--splitEta) -s



if __name__ == '__main__':

    # SETUP
    parser = OptionParser()
    parser.add_option('-l', '--limits', type='string', action='store',
                    default='Asymptotic', dest='limits',
                    help='Asymptotic or CLS')
    parser.add_option('-s', '--significance', action='store_true',
                    default=False, dest='sig',
                    help='Perform significance computation')
    parser.add_option('-d', '--debug', type='int',
                    default=1, dest='debug',
                    help='Debug level')
    parser.add_option('--cac', action='store_true', dest='cac', default=False,
                  help='Chose if cut and count method (True) or Shape (False)')
    parser.add_option('--splitEta', action='store_true', dest='splitEta', default=False,
                  help='Doit correspondre au meme booleen du script de generation : '
                       'tracker complet Eta2p4 (False) ou split Eta1/Eta1_2p4 (True).')
    parser.add_option('--onlyEta1', action='store_true', dest='onlyEta1', default=False,
                  help='Doit correspondre au script de generation : region centrale '
                       'seule |eta|<1 (Eta1).')

    (options, args) = parser.parse_args()
    debug = options.debug
    isCutAndCount = options.cac
    splitEta      = options.splitEta
    onlyEta1 = options.onlyEta1

    if (isCutAndCount): 
        print("Running cut and count limits")
    else :
        print("Running shape limits")

    # Doit correspondre aux parametres du script de generation des datacards
    regionBckg = '9fp10'
    optionlabel = ''#'etaAbs_etaRebinPerso_1oPRebinBig_Oldfit_EtaCategory'
    

    # Meme logique d'etiquette que dans le script de generation
    if splitEta:
        etaLabel = 'split_Eta1_Eta1_2p4'
    elif onlyEta1:
        etaLabel = 'Eta1'
    else:
        etaLabel = 'Eta2p4'

    idir = 'MyNewDataCards/datacards_shape_{}_{}_{}'.format(regionBckg, etaLabel, optionlabel)
    odir = 'MyNewDataCards/limit_shape_{}_{}'.format(regionBckg, etaLabel) + ("_cutandcount" if isCutAndCount else "") + '_' + optionlabel
    if options.limits == "CLS":
        odir += "_CLS"

    os.makedirs(idir, exist_ok=True)
    os.makedirs(odir, exist_ok=True)

    # Doit correspondre aux cles de fpath{} dans le script de generation
    samples = [
        'Gluino1100_2024',
        'Gluino1200_2024',
        'Gluino1300_2024',
        'Gluino1400_2024',
        'Gluino1600_2024',
        'Gluino1800_2024',
        'Gluino2000_2024',
        'Gluino2200_2024',
        'Gluino2400_2024',
        'Gluino2600_2024',
    ]

    def task(sample):
        name = sample
        if debug > 0:
            print("Processing: {}".format(name))

        if options.limits == "Asymptotic":
            run_combine = (
                "combine -M AsymptoticLimits"
                " -n .{name}"
                " -d {idir}/{name}" + ("_cutandcount" if isCutAndCount else "") + ".txt"
                " --rRelAcc 0.000005 --rAbsAcc 0.000005"
                " --rMin -1000.0 --rMax 1000.0"
            ).format(name=name, idir=idir, debug=debug)

            if debug > 0:
                print("Running: {}".format(run_combine))
            os.system(run_combine)
            os.system("mv higgsCombine.{0}.AsymptoticLimits.mH120.root {1}/".format(name, odir))

        elif options.limits == "CLS":
            from combine_parameters import toy_number, nice_priority
            import time
            absAcc = 0.0005
            quantiles = {
                "0p5":   "0.5",
                "0p84":  "0.84",
                "0p975": "0.975",
                "0p16":  "0.16",
                "0p025": "0.025",
            }
            base_cmd = (
                "nice -n {nice} combine -H AsymptoticLimits -M HybridNew"
                " -n .{name}"
                " -d {idir}/{name}" + ("_cutandcount" if isCutAndCount else "") + ".txt"
                " --saveWorkspace --LHCmode LHC-limits"
                " --rAbsAcc {acc}"
                " -v 1"
            )
            cmd_obs = base_cmd.format(nice=nice_priority, name=name, idir=idir, acc=0.00005) + " &"
            os.system(cmd_obs)

            for label, q in quantiles.items():
                cmd = (base_cmd + " --expectedFromGrid={q} --adaptiveToys 1 -T {T} &").format(
                    nice=nice_priority, name=name, idir=idir, acc=absAcc, q=q, T=toy_number)
                print(cmd)
                os.system(cmd)
            time.sleep(7200)

        if options.sig:
            run_sig = (
                "combine -M Significance"
                " -n .{name}"
                " {idir}/{name}" + ("_cutandcount" if isCutAndCount else "") + ".txt"
                " -t -1 --expectSignal=1"
            ).format(name=name, idir=idir)
            print(run_sig)
            os.system(run_sig)
            os.system("mv higgsCombine.{0}.Significance.mH120.root {1}/".format(name, odir))

    for sample in samples:
        task(sample)