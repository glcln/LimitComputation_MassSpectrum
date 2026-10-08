"""
Correlation matrix of the nuisance parameters, for the shape datacards.

For one signal model (gluino, stop or stau) and one eta configuration, and for
every shape datacard found in the input directory:
    1. text2workspace.py : datacard .txt -> workspace .root
    2. combine -M FitDiagnostics --saveWithUncertainties : writes the fit
       results fit_s and fit_b, with their covariance matrix, in
       fitDiagnostics_<Sample>.root
    3. the correlation matrix of the chosen fit result is read
       (RooFitResult::correlationHist), reduced to the parameters to show,
       and drawn

By default the signal+background fit (fit_s) of an Asimov dataset with signal
(-t -1 --expectSignal 1) is used. --bkgOnly selects the background-only fit
(fit_b, --expectSignal 0); --unblind fits the data of the datacards, which are
the observed data only if the datacards were generated with
CreateDatacards.py --unblind.

Input and output directory
    <DATACARDS_BASE>/<signal>/shape_<regionBckg>_<etaLabel>_<optionlabel>/
        <Sample>.txt                  input datacard
        <Sample>_ws.root              workspace
        fitDiagnostics_<Sample>.root  fit results
        correlation_<Sample>.pdf      plot
    plus the other files Combine writes in its working directory.

DATACARDS_BASE is the Datacards/ directory next to this script. Combine and
text2workspace.py must be in the PATH (CMSSW + Combine environment).

A mass point whose commands fail is skipped; the script goes on with the next
one and exits with status 1 at the end.

regionBckg and the default optionlabel are hardcoded in the CONFIGURATION
section; they must be those used to generate the datacards. This script is not
run by the driver shape_ProduceLimitsForDifferentEtaCategory.py.

Usage:
    python3 CorrelationMatrix.py                        # gluino, full tracker
    python3 CorrelationMatrix.py --splitEta             # two eta categories
    python3 CorrelationMatrix.py --splitEta --dropRate  # without the rateAll parameters
    python3 CorrelationMatrix.py --bkgOnly              # background-only fit
    python3 CorrelationMatrix.py --signal stau          # another signal
    python3 CorrelationMatrix.py --optionLabel v2       # another background-prediction option
    python3 CorrelationMatrix.py --dryRun               # print the commands only
"""

from optparse import OptionParser
import glob
import os
import re
import subprocess
import sys
import ROOT as rt

rt.gROOT.SetBatch(True)

# ---------------------------------------------------------------------------
## COMMAND LINE
# ---------------------------------------------------------------------------
parser = OptionParser()
parser.add_option('--signal', dest='signal', default='gluino',
                  type='choice', choices=['gluino', 'stop', 'stau'],
                  help='Signal model: gluino (default), stop or stau.')
parser.add_option('--splitEta', action='store_true', dest='splitEta', default=False,
                  help='Two eta categories (Eta1 + Eta1_2p4).')
parser.add_option('--onlyEta1', action='store_true', dest='onlyEta1', default=False,
                  help='Central region only (Eta1).')
parser.add_option('--optionLabel', dest='optionlabel', default='',
                  help='Background-prediction option of the datacards (default: the '
                       'one of the CONFIGURATION section).')
parser.add_option('--unblind', action='store_true', dest='unblind', default=False,
                  help='Fit the data of the datacards instead of an Asimov dataset (-t -1).')
parser.add_option('--bkgOnly', action='store_true', dest='bkgOnly', default=False,
                  help='Background-only model (fit_b). Default: signal+background '
                       '(fit_s, --expectSignal 1).')
parser.add_option('--dryRun', action='store_true', dest='dryRun', default=False,
                  help='Print the commands without running them.')
parser.add_option('--keepPropBin', action='store_true', dest='keepPropBin', default=False,
                  help='Keep the autoMCStats parameters (prop_bin*) in the plot.')
parser.add_option('--dropRate', action='store_true', dest='dropRate', default=False,
                  help='Also leave the rateParam parameters (rateAll*) out of the plot.')
parser.add_option('--noFreeze', action='store_true', dest='noFreeze', default=False,
                  help='Do not freeze the disabled nuisances: they stay in the fit '
                       'and are only left out of the plot.')
(options, args) = parser.parse_args()

if options.splitEta and options.onlyEta1:
    parser.error('--splitEta and --onlyEta1 are mutually exclusive')

signalType  = options.signal
splitEta    = options.splitEta
onlyEta1    = options.onlyEta1
unblind     = options.unblind
bkgOnly     = options.bkgOnly
dryRun      = options.dryRun
keepPropBin = options.keepPropBin
dropRate    = options.dropRate
noFreeze    = options.noFreeze

# ---------------------------------------------------------------------------
## CONFIGURATION
# ---------------------------------------------------------------------------
# Must match the settings used to generate the datacards. The optionlabel
# below is the default one, replaced by the value of --optionLabel if given.
regionBckg  = '9fp10'
optionlabel = options.optionlabel or 'SigmaPtoverPt_0p5_EoP_0p1_v2'

# Root of the datacards, also used for the outputs: the Datacards/ directory
# next to this script
DATACARDS_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Datacards')

# Particle symbol of each signal in the mass label of the plot (TLatex)
SPARTICLE = {'gluino': '#tilde{g}', 'stop': '#tilde{t}', 'stau': '#tilde{#tau}'}

# Labels of the parameters on the axes: Combine name -> label.
# ROOT does not use the LaTeX syntax ($...$, \textrm{}) but TLatex:
# subscript -> _{...}, superscript -> ^{...}, Greek letters -> #eta, #mu, ...
NUIS_LABELS = {
    'PU'             : 'Pile-Up',
    'TriggerSF'      : 'Trigger SF',
    'K'              : 'K_{mass}',
    'C'              : 'C_{mass}',
    'Fpix'           : 'F_{pixel}',
    'Jet'            : 'Jet energy scale',
    'lumi'           : 'Luminosity',
    'eta'            : '#eta binning',
    'ih'             : 'I_{h} binning',
    'mom'            : '1/p binning',
    'fitIh'          : 'I_{h} fit',
    'fitMom'         : '1/p fit',
    'corrTemplateIh' : 'I_{h} correlation',
    'corrTemplate1oP': '1/p correlation',
    'r'              : 'Signal strength r',   # parameter of interest
}

# Reference list: all the systematics the datacards can hold (must match
# CreateDatacards.py). The parameter of interest 'r', the rateAll and the
# prop_bin* parameters are not part of it, they are handled separately.
NUIS_ALL = [
    'PU', 'TriggerSF', 'K', 'C', 'Fpix', 'Jet', 'lumi',
    'eta', 'ih', 'mom', 'fitIh', 'fitMom',
    'corrTemplateIh', 'corrTemplate1oP',
]

# Disabled nuisances. Commenting out an entry of NUIS_LABELS is enough to
# disable a nuisance: it is then frozen to its nominal value in the fit
# (--freezeParameters), which is equivalent to removing its line from the
# datacard, and left out of the plot.
FROZEN_NUIS = [n for n in NUIS_ALL if n not in NUIS_LABELS]

# Name prefixes of the parameters left out of the plot. This only filters what
# is shown: these parameters stay in the fit.
DROP_PREFIXES = []
if not keepPropBin:
    DROP_PREFIXES.append("prop_bin")
if dropRate:
    DROP_PREFIXES.append("rateAll")

# Same eta label logic as in the datacard generation script
if splitEta:
    etaLabel = 'split_Eta1_Eta1_2p4'
elif onlyEta1:
    etaLabel = 'Eta1'
else:
    etaLabel = 'Eta2p4'

# The outputs are written next to the datacards
inCardsDir = os.path.join(DATACARDS_BASE, signalType, 'shape_{}_{}_{}'.format(regionBckg, etaLabel, optionlabel)) + os.sep
outDir     = inCardsDir


# ---------------------------------------------------------------------------
## FUNCTIONS
# ---------------------------------------------------------------------------
def mass_of(sample):
    """Mass point of a sample: the first number of its name (0 if none)."""
    m = re.search(r'(\d+)', sample)
    return int(m.group(1)) if m else 0


def find_samples(idir):
    """
    Names of the samples that have a shape datacard <Sample>.txt in `idir`,
    sorted by mass. The cut-and-count datacards (<Sample>_cutandcount.txt) and
    the yield tables (yields_*.txt) written next to them are skipped.
    """
    samples = []
    for path in glob.glob(os.path.join(idir, '*.txt')):
        fname = os.path.basename(path)
        if fname.startswith('yields_') or fname.endswith('_cutandcount.txt'):
            continue
        samples.append(fname[:-len('.txt')])
    return sorted(samples, key=lambda s: (mass_of(s), s))


def pretty_label(raw):
    """
    Translate a Combine parameter name into its TLatex label.
    A name of the form <base>_<suffix>, with <base> in NUIS_LABELS, is shown
    as '<label of base> (<suffix>)', e.g. 'K_Eta1' -> 'K_{mass} (Eta1)'.
    A name without any match is returned unchanged.
    """
    if raw in NUIS_LABELS:
        return NUIS_LABELS[raw]

    # per-category variants: <base>_<eta> (e.g. K_Eta1, C_Eta1_2p4)
    for base, lab in NUIS_LABELS.items():
        if raw.startswith(base + '_'):
            suffix = raw[len(base) + 1:]          # e.g. 'Eta1', 'Eta1_2p4'
            return '{} ({})'.format(lab, suffix)

    return raw


def is_dropped(raw):
    """True if the parameter must be left out of the plot."""
    if any(raw.startswith(p) for p in DROP_PREFIXES):
        return True
    # disabled nuisances: exact name or per-category variant <name>_<eta>
    for n in FROZEN_NUIS:
        if raw == n or raw.startswith(n + '_'):
            return True
    return False

def run(cmd, cwd=None):
    """
    Run a shell command from `cwd`; with --dryRun it is only printed.
    Raises CalledProcessError if the command fails.
    """
    print(">>> " + cmd + ("   [cwd={}]".format(cwd) if cwd else ""), flush=True)
    if dryRun:
        return
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)


def make_workspace(cardName, mass):
    """Build the workspace of a datacard with text2workspace.py; returns its path."""
    cardTxt = inCardsDir + cardName + ".txt"
    wsAbs   = outDir + cardName + "_ws.root"
    run("text2workspace.py {} -m {} -o {}".format(cardTxt, mass, wsAbs),
        cwd=outDir)
    return wsAbs


def run_fitdiagnostics(wsAbs, cardName, mass):
    """
    Run FitDiagnostics with --saveWithUncertainties; returns the path of the
    fitDiagnostics file.
    Two independent choices:
      - model: signal+background (default, fit_s, --expectSignal 1) or
               background-only (--bkgOnly, fit_b, --expectSignal 0)
      - data : Asimov dataset (-t -1, default) or the data of the datacard
               (--unblind)
    """
    tag = "_{}".format(cardName)

    expect = "--expectSignal 0" if bkgOnly else "--expectSignal 1"
    asimov = "" if unblind else "-t -1 "

    # Freeze the disabled nuisances. rgx{} is used rather than the bare names:
    # it also covers per-category variants (<name>_Eta1, <name>_Eta1_2p4) and,
    # if the name is not in the datacard, the regex matches nothing instead of
    # making Combine fail.
    freeze = ""
    if FROZEN_NUIS and not noFreeze:
        rgx = ",".join("rgx{{^{}(_.*)?$}}".format(n) for n in FROZEN_NUIS)
        freeze = "--freezeParameters '{}' ".format(rgx)

    cmd = ("combine -M FitDiagnostics {ws} -m {m} "
           "--saveWithUncertainties --robustFit 1 "
           "{freeze}{asimov}{expect} -n {tag}").format(
               ws=wsAbs, m=mass, freeze=freeze, asimov=asimov,
               expect=expect, tag=tag)
    run(cmd, cwd=outDir)

    return outDir + "fitDiagnostics{}.root".format(tag)


def extract_correlation(fdFile):
    """
    Read the RooFitResult (fit_s, or fit_b with --bkgOnly) of the
    fitDiagnostics file and return its correlation matrix as a TH2D reduced
    to the parameters to show (see is_dropped), with the axis labels
    translated by pretty_label().
    Raises IOError if the file cannot be opened and KeyError if the fit
    result is missing.
    """
    fitName = "fit_b" if bkgOnly else "fit_s"
    f = rt.TFile.Open(fdFile, "READ")
    if not f or f.IsZombie():
        raise IOError("Cannot open {}".format(fdFile))
    fit = f.Get(fitName)
    if not fit:
        f.Close()
        raise KeyError("{} not found in {}".format(fitName, fdFile))

    corrFull = fit.correlationHist()   # TH2D, symmetric, labels = parameter names
    corrFull.SetDirectory(0)
    f.Close()

    # --- bins to keep (prop_bin / rateAll / disabled nuisances filtered out) ---
    n = corrFull.GetNbinsX()
    keep = []   # 1-based bin indices
    for i in range(1, n + 1):
        lab = corrFull.GetXaxis().GetBinLabel(i)
        if is_dropped(lab):
            continue
        keep.append(i)

    m = len(keep)
    corr = rt.TH2D("corr_reduced", "", m, 0, m, m, 0, m)
    corr.SetDirectory(0)
    # correlationHist() orders the Y axis as the MIRROR of the X axis: the Y
    # bin 'jy' of corrFull is the parameter of X index (n+1-jy). The same
    # convention is kept here, so that the diagonal is 1 and the X and Y labels
    # line up (X increasing along the bottom, Y decreasing along the left).
    for a, ia in enumerate(keep):           # a: new 0-based X index
        rawX  = corrFull.GetXaxis().GetBinLabel(ia)
        labX  = pretty_label(rawX)
        corr.GetXaxis().SetBinLabel(a + 1, labX)
        # Y label in reverse order
        corr.GetYaxis().SetBinLabel(m - a, labX)
        for b, ib in enumerate(keep):       # b: new 0-based index of the other parameter
            # source Y bin of the parameter ib: mirror on the original Y axis
            iy_src = n + 1 - ib
            val = corrFull.GetBinContent(ia, iy_src)
            # destination Y bin, mirrored as well
            corr.SetBinContent(a + 1, m - b, val)
    return corr


def draw_correlation(corr, cardName, mass):
    """Draw the matrix (COLZ TEXT, viridis palette) and save it as a pdf."""
    n = corr.GetNbinsX()
    c = rt.TCanvas("c_" + cardName, "", 1200, 800)
    c.SetLeftMargin(0.15)
    c.SetRightMargin(0.11)
    c.SetBottomMargin(0.20)
    c.SetTopMargin(0.08)

    latex1 = rt.TLatex(0.15, 0.94, "#scale[1.2]{#it{Private Work (CMS data)}}")
    latex1.SetNDC()
    latex1.SetTextFont(42)
    latex1.SetTextSize(0.04)

    latex2 = rt.TLatex(0.70, 0.94, "#scale[1.2]{#bf{m_{" + SPARTICLE[signalType] + "}=" + str(mass) + " GeV}}")
    latex2.SetNDC()
    latex2.SetTextFont(42)
    latex2.SetTextSize(0.04)

    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetPalette(rt.kViridis)
    rt.gStyle.SetPaintTextFormat("1.3g")

    corr.SetMinimum(-1.0)
    corr.SetMaximum(1.0)
    corr.GetXaxis().SetLabelSize(0.035)
    corr.GetYaxis().SetLabelSize(0.035)
    corr.GetXaxis().LabelsOption("v")   # vertical labels along the bottom
    corr.SetMarkerSize(0.9 if n > 12 else 1.2)
    corr.Draw("COLZ TEXT")

    latex1.Draw("same")
    latex2.Draw("same")

    outPdf = outDir + "correlation_{}.pdf".format(cardName)
    if not dryRun:
        c.SaveAs(outPdf)


# ---------------------------------------------------------------------------
## MAIN
# ---------------------------------------------------------------------------
if __name__ == '__main__':

    print("Signal          : {}".format(signalType))
    print("Eta region      : {}".format(etaLabel))
    print("Model           : {}".format("background-only (fit_b)" if bkgOnly
                                        else "signal+background (fit_s)"))
    print("Data            : {}".format("data of the datacards (unblind)" if unblind
                                        else "Asimov (-t -1)"))
    print("Left out        : {}".format(", ".join(DROP_PREFIXES) if DROP_PREFIXES
                                        else "none"))
    print("Cards dir       : {}".format(inCardsDir))
    print("Out dir         : {}".format(outDir))

    print("Frozen          : {}".format(", ".join(FROZEN_NUIS) if FROZEN_NUIS
                                        else "none"))
    if FROZEN_NUIS and noFreeze:
        print("                  (--noFreeze: only left out of the plot)")
    print("-" * 60)

    # One matrix per shape datacard, i.e. per mass point: the signal nuisances
    # (K, C, Fpix, ...) depend on the signal
    if not os.path.isdir(inCardsDir):
        sys.exit("Datacard directory not found: {}".format(inCardsDir))
    samples = find_samples(inCardsDir)
    if not samples:
        sys.exit("No shape datacard found in {}".format(inCardsDir))

    failed = []
    for cardName in samples:
        mass = mass_of(cardName)

        print("\n=== {} (m = {} GeV) ===".format(cardName, mass))
        try:
            wsAbs  = make_workspace(cardName, mass)
            fdFile = run_fitdiagnostics(wsAbs, cardName, mass)

            if dryRun:
                continue

            corr = extract_correlation(fdFile)
            draw_correlation(corr, cardName, mass)
        except (subprocess.CalledProcessError, IOError, KeyError) as e:
            print("ERROR for {}: {} -> next".format(cardName, e))
            failed.append(cardName)

    if failed:
        sys.exit("\nFailed for {} mass point(s): {}".format(len(failed), ', '.join(failed)))
    print("\nDone.")