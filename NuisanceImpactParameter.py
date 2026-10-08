"""
Nuisance parameter impacts (Combine).

For one signal model (gluino, stop or stau) and one eta configuration, the
script follows, for every datacard found in the input directory, the standard
procedure of the Combine documentation:

    1. text2workspace.py                           datacard .txt -> workspace .root
    2. combineTool.py -M Impacts --doInitialFit    initial fit of the signal strength r
    3. combineTool.py -M Impacts --doFits          one fit per nuisance parameter
                                                   (the slow step)
    4. combineTool.py -M Impacts -o <json>         collect the results
    5. plotImpactsPrivate.py                       draw the impact plot (.pdf)

By default the fits are done on an Asimov dataset with signal
(-t -1 --expectSignal 1): expected impacts, without looking at the data. With
--unblind the fits use the data of the datacards, which are the observed data
only if the datacards were generated with CreateDatacards.py --unblind.

Input
    <DATACARDS_BASE>/<signal>/shape_<regionBckg>_<etaLabel>_<optionlabel>/
        <Sample>.txt                (shape, default)
        <Sample>_cutandcount.txt    (--cac)

Output
    <DATACARDS_BASE>/<signal>/NIP_plots/shape_<regionBckg>_<etaLabel>[_cutandcount]_<optionlabel>/
        nuis_labels.json         labels of the nuisance parameters on the plots
        <Sample>_impacts.pdf     copy of the impact plot of each mass point
        <Sample>/                working directory of the mass point: workspace,
                                 fit results, <Sample>_impacts.json and .pdf

DATACARDS_BASE is the Datacards/ directory next to this script. All the
commands of a mass point are run from its working directory.

A step that fails ends the sequence of that mass point; the script goes on
with the next one and exits with status 1 at the end.

regionBckg and the default optionlabel are hardcoded in the CONFIGURATION
section; they must be those used to generate the datacards. This script is not
run by the driver shape_ProduceLimitsForDifferentEtaCategory.py.

Usage:
    python3 NuisanceImpactParameter.py --splitEta                # all mass points, expected
    python3 NuisanceImpactParameter.py --sample Gluino1800_2024  # one mass point
    python3 NuisanceImpactParameter.py --signal stop --splitEta  # another signal
    python3 NuisanceImpactParameter.py --optionLabel v2          # another background-prediction option
    python3 NuisanceImpactParameter.py --splitEta --dryRun       # print the commands only
    python3 NuisanceImpactParameter.py --splitEta --extraOpts "--stepSize 0.005" 2>&1 | tee impacts_split.log
"""

from optparse import OptionParser
import os
import re
import sys
import shutil
import json
import glob
import subprocess

# ---------------------------------------------------------------------------
## COMMAND LINE
# ---------------------------------------------------------------------------
parser = OptionParser()
parser.add_option('--signal', dest='signal', default='gluino',
                  type='choice', choices=['gluino', 'stop', 'stau'],
                  help='Signal model: gluino (default), stop or stau.')
parser.add_option('--cac', action='store_true', dest='cac', default=False,
                  help='Use the cut-and-count datacards instead of the shape ones.')
parser.add_option('--splitEta', action='store_true', dest='splitEta', default=False,
                  help='Must match the flag of the other scripts: full tracker '
                       'Eta2p4 (off) or split Eta1/Eta1_2p4 (on).')
parser.add_option('--onlyEta1', action='store_true', dest='onlyEta1', default=False,
                  help='Must match the generation script: central region |eta|<1 '
                       'only (Eta1).')
parser.add_option('--optionLabel', dest='optionlabel', default='',
                  help='Background-prediction option of the datacards (default: the '
                       'one of the CONFIGURATION section).')
parser.add_option('-m', '--mass', type='string', default='120', dest='mass',
                  help="Mass hypothesis mH passed to Combine. It only sets the mH "
                       "label of the output files (default 120 -> mH120, as for "
                       "the limits).")
parser.add_option('--unblind', action='store_true', default=False, dest='unblind',
                  help='Fit the data of the datacards instead of an Asimov dataset.')
parser.add_option('--expectSignal', type='float', default=1.0, dest='expectSignal',
                  help='Signal strength injected in the Asimov dataset (blinded '
                       'mode): 1.0 = nominal signal, 0.0 = background only.')
parser.add_option('--rMin', type='float', default=-5.0, dest='rMin',
                  help='Lower bound of the signal strength r in the fits.')
parser.add_option('--rMax', type='float', default=5.0, dest='rMax',
                  help='Upper bound of the signal strength r in the fits.')
parser.add_option('--robustFit', type='int', default=1, dest='robustFit',
                  help='Value of --robustFit passed to combineTool.py (default 1).')
parser.add_option('--parallel', type='int', default=4, dest='parallel',
                  help='Number of nuisance fits run in parallel (--doFits step).')
parser.add_option('--sample', type='string', default='', dest='sample',
                  help="Process a single mass point (e.g. Gluino1800_2024). "
                       "Default: all of them.")
parser.add_option('--extraOpts', type='string', default='', dest='extraOpts',
                  help='Extra Combine options passed as they are to the fits '
                       '(e.g. "--cminDefaultMinimizerStrategy 0").')
parser.add_option('--excludeNuis', type='string', default='rgx{prop_bin.*}', dest='excludeNuis',
                  help="Nuisance parameters left out of the impact fits (combineTool.py "
                       "regex). Default: the autoMCStats ones (prop_bin*). Empty = none.")
parser.add_option('--blindPlot', action='store_true', default=False, dest='blindPlot',
                  help='Do not print the fitted r on the impact plot.')
parser.add_option('--dryRun', action='store_true', default=False, dest='dryRun',
                  help='Print the commands without running them; nothing is written.')
(options, args) = parser.parse_args()

if options.splitEta and options.onlyEta1:
    parser.error('--splitEta and --onlyEta1 are mutually exclusive')

signalType    = options.signal
isCutAndCount = options.cac
splitEta      = options.splitEta
onlyEta1      = options.onlyEta1
mass          = options.mass
dryRun        = options.dryRun

# ---------------------------------------------------------------------------
## CONFIGURATION
# ---------------------------------------------------------------------------
# Must match the settings used to generate the datacards. The optionlabel
# below is the default one, replaced by the value of --optionLabel if given.
regionBckg  = '9fp10'
optionlabel = options.optionlabel or 'SigmaPtoverPt_0p5_EoP_0p1_v2'

# Root of the datacards, also used for the outputs: the Datacards/ directory
# next to this script
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
DATACARDS_BASE = os.path.join(BASE_DIR, 'Datacards')

# Plotting command: plotImpactsPrivate.py is a wrapper around the plotImpacts.py
# of Combine that replaces the CMS logo by a "private work" label
WRAPPER = os.path.join(BASE_DIR, 'plotImpactsPrivate.py')
PLOTTER = 'python3 ' + WRAPPER

# Labels of the nuisance parameters on the plots (TLatex syntax):
# Combine nuisance name -> label. A name without entry is shown as it is.
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
    'rateAll'          : 'rate |#eta| < 2.4',
    'rateAll_Eta1'     : 'rate |#eta| < 1',
    'rateAll_Eta1_2p4' : 'rate 1#leq |#eta| < 2.4',
}


# ---------------------------------------------------------------------------
## FUNCTIONS
# ---------------------------------------------------------------------------
def mass_of(sample):
    """Mass point of a sample: the first number of its name (0 if none)."""
    m = re.search(r'(\d+)', sample)
    return int(m.group(1)) if m else 0


def find_samples(idir, cutAndCount):
    """
    Names of the samples that have a datacard in `idir`, sorted by mass.

    A sample <Sample> has a shape datacard <Sample>.txt and/or a cut-and-count
    datacard <Sample>_cutandcount.txt: only the kind selected by `cutAndCount`
    is considered. The yield tables (yields_*.txt) written next to the
    datacards are skipped.
    """
    suffix = '_cutandcount.txt' if cutAndCount else '.txt'
    samples = []
    for path in glob.glob(os.path.join(idir, '*.txt')):
        fname = os.path.basename(path)
        if fname.startswith('yields_'):
            continue
        if fname.endswith('_cutandcount.txt') != cutAndCount:
            continue
        samples.append(fname[:-len(suffix)])
    return sorted(samples, key=lambda s: (mass_of(s), s))


def build_commands(name, idir, odir, labelsJson):
    """
    Commands of the five steps for the mass point `name`.

    Returns (datacard, workdir, name of the plot, list of commands). All the
    commands are meant to be run from `workdir`: the workspace is given by its
    absolute path, the other inputs and outputs are relative to `workdir`.
    """
    cacTag   = '_cutandcount' if isCutAndCount else ''
    datacard = os.path.join(idir, name + cacTag + '.txt')
    workdir  = os.path.join(odir, name)
    ws       = os.path.join(workdir, name + '.root')   # workspace, absolute path
    jsonOut  = name + '_impacts.json'                  # relative to workdir
    plotOut  = name + '_impacts'                       # plotImpacts adds .pdf

    # Options shared by the fits
    toy    = '' if options.unblind else ' -t -1 --expectSignal {}'.format(options.expectSignal)
    rrange = ' --rMin {} --rMax {}'.format(options.rMin, options.rMax)
    extra  = (' ' + options.extraOpts) if options.extraOpts else ''
    common = '-M Impacts -d {ws} -m {m}'.format(ws=ws, m=mass)
    fitOpts = '--robustFit {rf}{toy}{rr}{ex}'.format(
        rf=options.robustFit, toy=toy, rr=rrange, ex=extra)
    excl = ' --exclude "{}"'.format(options.excludeNuis) if options.excludeNuis else ''

    cmds = []

    # 1. workspace
    cmds.append('text2workspace.py {dc} -m {m} -o {ws}'.format(dc=datacard, m=mass, ws=ws))

    # 2. initial fit of the signal strength
    cmds.append('combineTool.py {c} --doInitialFit {f}'.format(c=common, f=fitOpts))

    # 3. fits of the nuisance parameters (without the excluded ones)
    cmds.append('combineTool.py {c} --doFits {f} --parallel {p}{x}'.format(
        c=common, f=fitOpts, p=options.parallel, x=excl))

    # 4. collection of the results in a json file (same exclusion, so that the
    #    fits that were not done are not looked for)
    cmds.append('combineTool.py {c} -o {j}{x}'.format(c=common, j=jsonOut, x=excl))

    # 5. plot
    cmds.append('{plotter} -i {j} -o {o} -t {t} --left-margin 0.45 --label-size 0.028{bl}'.format(
        plotter=PLOTTER, j=jsonOut, o=plotOut, t=labelsJson,
        bl=' --blind' if options.blindPlot else ''))

    return datacard, workdir, plotOut + '.pdf', cmds


def run(cmd, cwd):
    """
    Run a shell command from the directory `cwd`; with --dryRun it is only
    printed. Returns True if the command succeeded.
    """
    print('  cd {} && {}'.format(cwd, cmd), flush=True)
    if dryRun:
        return True
    status = subprocess.run(cmd, shell=True, cwd=cwd).returncode
    if status != 0:
        print('  -> FAILED (status {}): {}'.format(status, cmd))
        return False
    return True


def check_impacts_json(path):
    """
    Report the parameters whose post-fit uncertainty is zero on one side in
    the impacts json file, i.e. whose likelihood scan failed.
    """
    if not os.path.isfile(path):
        print('  WARNING: json file not found: {}'.format(path))
        return
    with open(path) as f:
        data = json.load(f)
    bad = []
    for p in data['params']:
        lo, best, hi = p['fit']
        if (hi - best) == 0.0 or (best - lo) == 0.0:
            bad.append(p['name'])
    if bad:
        print('  WARNING: zero post-fit uncertainty, scan failed: {}'.format(', '.join(bad)))
    else:
        print('  OK: {} parameters, no failed scan.'.format(len(data['params'])))


if __name__ == '__main__':

    # Same eta label logic as in the datacard generation script
    if splitEta:
        etaLabel = 'split_Eta1_Eta1_2p4'
    elif onlyEta1:
        etaLabel = 'Eta1'
    else:
        etaLabel = 'Eta2p4'

    cacTag = '_cutandcount' if isCutAndCount else ''
    idir   = os.path.join(DATACARDS_BASE, signalType, 'shape_{}_{}_{}'.format(regionBckg, etaLabel, optionlabel))
    odir   = os.path.join(DATACARDS_BASE, signalType, 'NIP_plots', 'shape_{}_{}{}_{}'.format(regionBckg, etaLabel, cacTag, optionlabel))

    print("Datacards read from : {}".format(idir))
    print("Impacts written to  : {}".format(odir))
    if isCutAndCount:
        print("NOTE: cut-and-count datacards have no shapes; the impacts can still "
              "be computed (lnN nuisances) but the plot is less informative than "
              "in shape mode.")

    # One mass point per datacard
    if not os.path.isdir(idir):
        sys.exit("Datacard directory not found: {}".format(idir))
    all_samples = find_samples(idir, isCutAndCount)
    if not all_samples:
        sys.exit("No {} datacard found in {}".format("cut-and-count" if isCutAndCount else "shape", idir))
    if options.sample:
        if options.sample not in all_samples:
            sys.exit("Unknown sample: {} (expected: {})".format(options.sample, all_samples))
        samples = [options.sample]
    else:
        samples = all_samples

    # Labels of the nuisance parameters, read by the plotting step
    labelsJson = os.path.join(odir, 'nuis_labels.json')
    if not dryRun:
        os.makedirs(odir, exist_ok=True)
        with open(labelsJson, 'w') as f:
            json.dump(NUIS_LABELS, f, indent=2)

    failed = []
    for name in samples:
        print('\n=== {} ==='.format(name))
        datacard, workdir, pdfName, cmds = build_commands(name, idir, odir, labelsJson)

        if not dryRun:
            os.makedirs(workdir, exist_ok=True)
            # fit results of a previous run
            for old in glob.glob(os.path.join(workdir, 'higgsCombine_*.root')):
                os.remove(old)

        ok = True
        for cmd in cmds:
            ok = run(cmd, workdir)
            if not ok:
                print('  Sequence stopped for {}.'.format(name))
                failed.append(name)
                break

        if ok and not dryRun:
            check_impacts_json(os.path.join(workdir, name + '_impacts.json'))

            # Copy of the plot next to the working directories
            src_pdf = os.path.join(workdir, pdfName)
            if os.path.isfile(src_pdf):
                dst_pdf = os.path.join(odir, pdfName)
                shutil.copy(src_pdf, dst_pdf)
                print('  Plot: {}'.format(dst_pdf))
            else:
                print('  WARNING: expected plot not found: {}'.format(src_pdf))

    if failed:
        sys.exit("\nFailed for {} of {} mass points: {}".format(len(failed), len(samples), ', '.join(failed)))
    print('\nDone.')