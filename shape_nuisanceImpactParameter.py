"""
Derivation des "nuisance parameter impacts" (Combine) a partir des datacards

Suit la procedure standard de la documentation Combine :
    1. text2workspace.py   : datacard .txt -> workspace .root
    2. combineTool -M Impacts --doInitialFit : fit initial du POI (r)
    3. combineTool -M Impacts --doFits       : un fit par nuisance (etape lourde)
    4. combineTool -M Impacts -o impacts.json: collecte des resultats
    5. plotImpacts.py        : trace le plot d'impacts (.pdf)

Par defaut, etude ATTENDUE (Asimov, -t -1 --expectSignal 1), donc aveugle.
Avec --unblind, fit sur les vraies donnees.

Usage typique :
    python impacts.py --splitEta                 # tous les points, attendu
    python impacts.py --sample Gluino1800_2024    # un seul point
    python impacts.py --splitEta --dryRun         # affiche les commandes sans rien lancer
"""

# lancer: py shape_nuisanceImpactParameter.py --splitEta --extraOpts "--stepSize 0.005" 2>&1 | tee impacts_split.log


from optparse import OptionParser
import os
import sys
import shutil
import json
import glob
import re

# Wrapper qui remplace le logo CMS et ajoute le label de masse.
# Chemin absolu : abspath() se resout par rapport au repertoire de lancement.
WRAPPER = '/mnt/safe/ui3_1/cms/gcoulon/CMSSW_15_0_13_patch1/src/HSCPLimit/LimitComputation_MassSpectrum/plotImpactsPrivate.py'
PLOTTER = 'python3 ' + WRAPPER

SPARTICLE = {'Gluino': '#tilde{g}', 'Stop': '#tilde{t}', 'Stau': '#tilde{#tau}'}

def sampleLabel(name):
    """'Gluino2000_2024' -> 'm_{#tilde{g}} = 2000 GeV'"""
    m = re.match(r'([A-Za-z]+?)(\d+)_', name)
    if not m:
        return ''
    return ''


NUIS_LABELS = {
    'PU'             : 'Pile-Up',
    'TriggerSF'      : 'Trigger SF',
    'K'              : 'K_{mass}',
    'C'              : 'C_{mass}',
    'Fpix'           : 'F_{pixel}',
    'Jet'            : 'Jet Energy Scale',
    'lumi'           : 'Luminosity',
    'eta'            : '#eta binning',
    'ih'             : 'I_{h} binning',
    'mom'            : '1/p binning',
    'fitIh'          : 'I_{h} fit',
    'fitMom'         : '1/p fit',
    'corrTemplateIh' : 'I_{h} correlation',
    'corrTemplate1oP' : '1/p correlation',
    'rateAll_Eta1'     : 'rate |#eta| < 1',
    'rateAll_Eta1_2p4' : 'rate 1#leq |#eta| < 2.4',
}

if __name__ == '__main__':

    # -----------------------------------------------------------------------
    # CLI
    # -----------------------------------------------------------------------
    parser = OptionParser()
    parser.add_option('--cac', action='store_true', dest='cac', default=False,
                      help='Cut and count (True) ou Shape (False)')
    parser.add_option('--splitEta', action='store_true', dest='splitEta', default=False,
                      help='Doit correspondre au meme booleen des autres scripts : '
                           'tracker complet Eta2p4 (False) ou split Eta1/Eta1_2p4 (True).')
    parser.add_option('--onlyEta1', action='store_true', dest='onlyEta1', default=False,
                  help='Doit correspondre au script de generation : region centrale '
                       'seule |eta|<1 (Eta1).')
    parser.add_option('-m', '--mass', type='string', default='120', dest='mass',
                      help="Hypothese de masse mH passee a combine (doit matcher le naming, "
                           "defaut 120 -> mH120, comme dans le run des limites).")
    parser.add_option('--unblind', action='store_true', default=False, dest='unblind',
                      help='Fit sur les vraies donnees (sinon Asimov attendu).')
    parser.add_option('--expectSignal', type='float', default=1.0, dest='expectSignal',
                      help='Intensite du signal injecte dans l Asimov (mode aveugle). '
                           '1.0 = signal au taux nominal, 0.0 = background-only.')
    parser.add_option('--rMin', type='float', default=-5.0, dest='rMin',
                      help='Borne basse du POI r pour les fits.')
    parser.add_option('--rMax', type='float', default=5.0, dest='rMax',
                      help='Borne haute du POI r pour les fits.')
    parser.add_option('--robustFit', type='int', default=1, dest='robustFit',
                      help='Valeur de --robustFit passee a combineTool (defaut 1).')
    parser.add_option('--parallel', type='int', default=4, dest='parallel',
                      help='Nombre de fits de nuisances lances en parallele (--doFits).')
    parser.add_option('--sample', type='string', default='', dest='sample',
                      help="Ne traiter qu un seul point de masse (cle, ex: Gluino1800_2024). "
                           "Vide = tous.")
    parser.add_option('--extraOpts', type='string', default='', dest='extraOpts',
                      help='Options combine supplementaires passees telles quelles aux fits '
                           '(ex: "--cminDefaultMinimizerStrategy 0").')
    parser.add_option('--dryRun', action='store_true', default=False, dest='dryRun',
                      help='Affiche les commandes sans les executer.')
    parser.add_option('-d', '--debug', type='int', default=1, dest='debug',
                      help='Niveau de verbosite')
    parser.add_option('--excludeNuis', type='string', default='rgx{prop_bin.*}', dest='excludeNuis',
                    help="Nuisances exclues des fits d'impacts (regex combineTool). "
                       "Defaut: exclut les autoMCStats (prop_bin*). Vide = toutes.")
    parser.add_option('--blindPlot', action='store_true', default=False, dest='blindPlot',
                      help='Ne pas afficher r_hat sur le plot d impacts (libere le coin haut droit).')
    (options, args) = parser.parse_args()

    isCutAndCount = options.cac
    splitEta      = options.splitEta
    onlyEta1      = options.onlyEta1
    mass          = options.mass
    debug         = options.debug
    dryRun        = options.dryRun

    # -----------------------------------------------------------------------
    # Chemins — memes conventions que les autres scripts
    # -----------------------------------------------------------------------
    regionBckg = '9fp10'
    tag = 'v2'

    if splitEta:
        etaLabel = 'split_Eta1_Eta1_2p4'
    else:
        etaLabel = 'Eta2p4'
    if onlyEta1: 
        etaLabel = 'Eta1'

    cacTag  = '_cutandcount' if isCutAndCount else ''
    idir    = 'Datacards/gluino/shape_{}_{}_{}'.format(regionBckg, etaLabel, tag)
    odir    = 'Datacards/gluino/NIP_plots/shape_{}_{}_{}_{}'.format(regionBckg, etaLabel, cacTag, tag)
    os.makedirs(odir, exist_ok=True)

    idir_abs = os.path.abspath(idir)
    odir_abs = os.path.abspath(odir)

    labelsJson = os.path.join(odir_abs, 'nuis_labels.json')
    with open(labelsJson, 'w') as f:
        json.dump(NUIS_LABELS, f, indent=2)

    # Repertoire de lancement : c'est par rapport a LUI que la ligne `shapes`
    # de la datacard (chemin relatif vers le .root) doit etre resolue.
    # text2workspace.py DOIT donc tourner ici ; une fois le workspace construit,
    # les shapes y sont importees et le reste peut tourner depuis le workdir.
    launch_dir = os.getcwd()

    print("Datacards lues depuis : {}".format(idir_abs))
    print("Sorties impacts dans  : {}".format(odir_abs))
    if isCutAndCount:
        print("ATTENTION: methode cut & count -> datacard sans shapes ; "
              "les impacts restent calculables (nuisances lnN), mais le plot est "
              "moins informatif qu en shape.")

    # Memes cles que dans le script de generation
    all_samples = [
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

    if options.sample:
        if options.sample not in all_samples:
            sys.exit("Sample inconnu : {} (attendus : {})".format(options.sample, all_samples))
        samples = [options.sample]
    else:
        samples = all_samples

    # -----------------------------------------------------------------------
    # Construction des commandes pour un point de masse
    # -----------------------------------------------------------------------
    def build_commands(name):
        datacard = os.path.join(idir_abs, name + cacTag + '.txt')
        workdir  = os.path.join(odir_abs, name)
        ws       = os.path.join(workdir, name + '.root')   # workspace, chemin ABSOLU
        jsonOut  = name + '_impacts.json'                  # relatif au workdir
        plotOut  = name + '_impacts'                       # plotImpacts ajoute .pdf

        # Flags communs
        toy    = '' if options.unblind else ' -t -1 --expectSignal {}'.format(options.expectSignal)
        rrange = ' --rMin {} --rMax {}'.format(options.rMin, options.rMax)
        extra  = (' ' + options.extraOpts) if options.extraOpts else ''
        common = '-M Impacts -d {ws} -m {m}'.format(ws=ws, m=mass)
        fitOpts = '--robustFit {rf}{toy}{rr}{ex}'.format(
            rf=options.robustFit, toy=toy, rr=rrange, ex=extra)

        # Chaque etape = (commande, repertoire d'execution)
        cmds = []
        
        # 1. workspace : DOIT tourner depuis launch_dir (resolution du chemin
        #    relatif `shapes` de la datacard). Sortie en chemin absolu vers le workdir.
        cmds.append(('text2workspace.py {dc} -m {m} -o {ws}'.format(dc=datacard, m=mass, ws=ws),
                     launch_dir))
        
        # 2-5. tournent depuis le workdir (workspace autonome, shapes deja importees).
        # 2. fit initial du POI
        cmds.append(('combineTool.py {c} --doInitialFit {f}'.format(c=common, f=fitOpts),
                     workdir))
        
        excl = ' --exclude "{}"'.format(options.excludeNuis) if options.excludeNuis else ''

        # 3. fits des nuisances (on saute les autoMCStats)
        cmds.append(('combineTool.py {c} --doFits {f} --parallel {p}{x}'.format(
            c=common, f=fitOpts, p=options.parallel, x=excl), workdir))
        
        # 4. collecte JSON (même exclusion pour ne pas chercher de fits absents)
        cmds.append(('combineTool.py {c} -o {j}{x}'.format(c=common, j=jsonOut, x=excl), workdir))

        # 5. plot
        cmds.append(('{plotter} -i {j} -o {o} -t {t} --left-margin 0.45 --label-size 0.028 '
                     '--extra-label "{lab}"{bl}'.format(
                         plotter=PLOTTER, j=jsonOut, o=plotOut, t=labelsJson,
                         lab=sampleLabel(name),
                         bl=' --blind' if options.blindPlot else ''),
                     workdir))

        return datacard, workdir, plotOut + '.pdf', cmds

    # -----------------------------------------------------------------------
    # Boucle
    # -----------------------------------------------------------------------
    def run(cmd, cwd):
        full = 'cd {} && {}'.format(cwd, cmd)
        if debug > 0 or dryRun:
            print('  ' + full)
        if not dryRun:
            rc = os.system(full)
            if rc != 0:
                print('  -> ECHEC (code {}) : {}'.format(rc, cmd))
                return False
        return True
    
    def check_impacts_json(path):
        if not os.path.isfile(path):
            print('  WARNING: json introuvable : {}'.format(path))
            return
        with open(path) as f:
            data = json.load(f)
        bad = []
        for p in data['params']:
            lo, best, hi = p['fit']
            if (hi - best) == 0.0 or (best - lo) == 0.0:
                bad.append(p['name'])
        if bad:
            print('  ATTENTION: incertitude post-fit nulle, scan echoue : {}'.format(', '.join(bad)))
        else:
            print('  OK: {} parametres, aucun scan echoue.'.format(len(data['params'])))

    for name in samples:
        print('\n=== {} ==='.format(name))
        datacard, workdir, pdfName, cmds = build_commands(name)

        if not os.path.isfile(datacard) and not dryRun:
            print('WARNING: datacard manquante, on saute : {}'.format(datacard))
            continue

        os.makedirs(workdir, exist_ok=True)

        if not dryRun:
            for old in glob.glob(os.path.join(workdir, 'higgsCombine_*.root')):
                os.remove(old)

        ok = True
        for cmd, cwd in cmds:
            ok = run(cmd, cwd)
            if not ok:
                print('  Arret de la sequence pour {}.'.format(name))
                break

        if ok and not dryRun:
            check_impacts_json(os.path.join(workdir, name + '_impacts.json'))

            src_pdf = os.path.join(workdir, pdfName)
            if os.path.isfile(src_pdf):
                dst_pdf = os.path.join(odir_abs, pdfName)
                shutil.copy(src_pdf, dst_pdf)
                print('  Plot : {}'.format(dst_pdf))
            else:
                print('  WARNING: plot attendu introuvable : {}'.format(src_pdf))

    print('\nTermine.')