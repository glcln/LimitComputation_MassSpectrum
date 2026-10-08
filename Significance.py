"""
Expected significance as a function of the signal mass.

For one signal model (gluino, stop or stau) and one eta configuration, the
script runs `combine -M Significance` on every datacard found in the input
directory, on an Asimov dataset with the signal injected at r = 1
(-t -1 --expectSignal=1), and draws the resulting expected significance versus
the mass.

Input
    <DATACARDS_BASE>/<signal>/shape_<regionBckg>_<etaLabel>_<optionlabel>/
        <Sample>.txt                (shape, default)
        <Sample>_cutandcount.txt    (--cac)

Output
    <LIMITS_BASE>/<signal>/shape_<regionBckg>_<etaLabel>[_cutandcount]_<optionlabel>/
        higgsCombine.<Sample>.Significance.mH120.root
        pdf/summary_significance_<signal>_<etaLabel>.pdf
        Cfile/summary_significance_<signal>.C
        rootfile/summary_significance_<signal>.root

DATACARDS_BASE and LIMITS_BASE are the Datacards/ and Limits/ directories next
to this script. Combine is run from the output directory, so its result trees
are written there directly.

With --plotOnly Combine is not run: the plot is redrawn from the result trees
found in the output directory.

regionBckg and the default optionlabel are hardcoded in the CONFIGURATION
section; they must be those used to generate the datacards. This script is not
run by the driver ProduceLimitsForDifferentEtaCategory.py.

Usage:
    python3 Significance.py                    # gluino, full tracker, shape
    python3 Significance.py --splitEta         # two eta categories
    python3 Significance.py --onlyEta1         # central region only
    python3 Significance.py --cac              # cut-and-count
    python3 Significance.py --signal stop      # another signal
    python3 Significance.py --optionLabel v2   # another background-prediction option
    python3 Significance.py --plotOnly         # redraw without running Combine
"""

from optparse import OptionParser
import glob
import os
import re
import subprocess
import sys

import ROOT as rt
from ROOT import TCanvas, TLatex, TGraph

rt.gROOT.SetBatch(True)

import tdrstyle
tdrstyle.setTDRStyle()

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
                  help='Two eta categories, Eta1 and Eta1_2p4, instead of the full '
                       'tracker Eta2p4.')
parser.add_option('--onlyEta1', action='store_true', dest='onlyEta1', default=False,
                  help='Central region |eta|<1 only (Eta1).')
parser.add_option('--optionLabel', dest='optionlabel', default='',
                  help='Background-prediction option of the datacards (default: the '
                       'one of the CONFIGURATION section).')
parser.add_option('--plotOnly', action='store_true', dest='plotOnly', default=False,
                  help='Do not run Combine: read the existing result trees and redraw.')
(options, args) = parser.parse_args()

if options.splitEta and options.onlyEta1:
    parser.error('--splitEta and --onlyEta1 are mutually exclusive')

signalType    = options.signal
isCutAndCount = options.cac
splitEta      = options.splitEta
onlyEta1      = options.onlyEta1
plotOnly      = options.plotOnly

# ---------------------------------------------------------------------------
## CONFIGURATION
# ---------------------------------------------------------------------------
# Must match the settings used to generate the datacards. The optionlabel
# below is the default one, replaced by the value of --optionLabel if given.
regionBckg  = '9fp10'
optionlabel = options.optionlabel or 'SigmaPtoverPt_0p5_EoP_0p1_v2'

# Roots of the input (datacards) and output (Combine results, plots) trees:
# the Datacards/ and Limits/ directories next to this script
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
DATACARDS_BASE = os.path.join(BASE_DIR, 'Datacards')
LIMITS_BASE    = os.path.join(BASE_DIR, 'Limits')

# Per-signal plot settings: x-axis range [GeV]
SIGNAL_PLOT_CONFIG = {
    'gluino': {'xrange': (1000, 2700)},
    'stop'  : {'xrange': (600, 2700)},
    'stau'  : {'xrange': (200, 1700)},
}

# Eta label drawn on the plot: etaLabel -> (x position in NDC, TLatex text)
ETA_DISPLAY = {
    'Eta2p4'              : (0.8, "#bf{|#eta|<2.4}"),
    'Eta1'                : (0.8, "#bf{|#eta|<1}"),
    'split_Eta1_Eta1_2p4' : (0.6, "#bf{|#eta|<1 & 1#leq|#eta|<2.4}"),
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


def find_results(odir):
    """Names of the samples that have a Significance result tree in `odir`, sorted by mass."""
    prefix, suffix = 'higgsCombine.', '.Significance.mH120.root'
    samples = [os.path.basename(p)[len(prefix):-len(suffix)]
               for p in glob.glob(os.path.join(odir, prefix + '*' + suffix))]
    return sorted(samples, key=lambda s: (mass_of(s), s))


def setColorAndMarker(gr, color, marker):
    """Set the line colour, marker colour and marker style of a graph."""
    gr.SetMarkerColor(color)
    gr.SetLineColor(color)
    gr.SetMarkerStyle(marker)
    gr.SetMarkerSize(2)
    return gr


def parse_significance(root_path):
    """
    Significance stored by Combine in the first entry of the `limit` tree of
    `root_path`, or None if the file or the tree is missing or empty.
    """
    if not os.path.isfile(root_path):
        return None
    f = rt.TFile.Open(root_path)
    if not f or f.IsZombie():
        return None
    t = f.Get('limit')
    if not t or t.GetEntries() == 0:
        f.Close()
        return None
    t.GetEntry(0)
    z = t.limit
    f.Close()
    return z


if __name__ == '__main__':

    # Same eta label logic as in the datacard generation script
    if splitEta:
        etaLabel = 'split_Eta1_Eta1_2p4'
    elif onlyEta1:
        etaLabel = 'Eta1'
    else:
        etaLabel = 'Eta2p4'

    endname = "_cutandcount" if isCutAndCount else ""

    idir = os.path.join(DATACARDS_BASE, signalType, 'shape_{}_{}_{}'.format(regionBckg, etaLabel, optionlabel))
    oDir = os.path.join(LIMITS_BASE, signalType, 'shape_{}_{}{}_{}'.format(regionBckg, etaLabel, endname, optionlabel)) + os.sep

    # One mass point per datacard, or per existing result tree with --plotOnly
    if plotOnly:
        samples = find_results(oDir)
        if not samples:
            sys.exit("No Significance result found in {}".format(oDir))
    else:
        if not os.path.isdir(idir):
            sys.exit("Datacard directory not found: {}".format(idir))
        samples = find_samples(idir, isCutAndCount)
        if not samples:
            sys.exit("No {} datacard found in {}".format("cut-and-count" if isCutAndCount else "shape", idir))
        os.makedirs(oDir, exist_ok=True)

    # --- Expected significance of each mass point ---
    results = []  # (mass, Z)
    for sample in samples:
        out_root = "{}higgsCombine.{}.Significance.mH120.root".format(oDir, sample)

        if not plotOnly:
            dc = os.path.join(idir, sample + endname + '.txt')
            # Asimov dataset (-t -1) with the signal injected at r = 1
            run_sig = (
                "combine -M Significance"
                " -n .{name}"
                " {dc}"
                " -t -1 --expectSignal=1"
            ).format(name=sample, dc=dc)
            print("Running: {}".format(run_sig), flush=True)
            # Combine writes its output in its working directory: run it from oDir
            status = subprocess.run(run_sig, shell=True, cwd=oDir).returncode
            if status != 0:
                # do not read a result tree left by a previous run
                print("WARNING: combine exited with status {} for {}: mass point skipped".format(status, sample))
                continue

        z = parse_significance(out_root)
        if z is None:
            print("WARNING: no significance for {}".format(sample))
            continue
        results.append((mass_of(sample), z))

    results.sort()
    if not results:
        sys.exit("No significance could be read.")

    gr = TGraph(len(results))
    gr.SetTitle("")   # no title box, whatever the default of the ROOT version
    for i, (m, z) in enumerate(results):
        gr.SetPoint(i, float(m), float(z))
        print("mass {:>5} GeV -> Z = {:.3f}".format(m, z))

    zmax = max(z for _, z in results)
    # Lower edge of the (logarithmic) y axis: 1, or below the smallest positive
    # significance when it is under 1
    zmin_pos = min([z for _, z in results if z > 0] or [1.0])
    ymin = 1 if zmin_pos > 1 else 0.5 * zmin_pos

    # --- Plot ---
    c2 = TCanvas("c2", "c2", 800, 600)
    c2.SetBottomMargin(0.12)
    c2.SetLeftMargin(0.1)
    c2.SetGrid()
    c2.SetTicky(1)
    c2.SetTickx(1)

    gr.GetXaxis().SetTitle("Mass [GeV]")
    gr.GetYaxis().SetTitle("Expected significance")
    gr.GetXaxis().SetNdivisions(510)
    gr.GetXaxis().SetLabelFont(43)   # font 43: label size given in pixels
    gr.GetXaxis().SetLabelSize(24)
    gr.GetXaxis().SetTitleSize(0.05)
    gr.GetYaxis().SetLabelFont(43)
    gr.GetYaxis().SetLabelSize(24)
    gr.GetYaxis().SetTitleSize(0.05)
    gr.GetYaxis().SetTitleOffset(1.0)
    gr.GetXaxis().SetTitleOffset(1.0)
    gr.GetXaxis().SetRangeUser(*SIGNAL_PLOT_CONFIG[signalType]['xrange'])
    gr.SetMinimum(ymin)
    gr.SetMaximum(zmax * 1.4)
    c2.SetLogy()

    setColorAndMarker(gr, rt.kRed, 34)

    # CMS label, luminosity and eta region
    latex = TLatex(0.1, 0.96, "#scale[1.3]{#it{Private work (CMS data)}}")
    latex.SetNDC()
    latex.SetTextFont(42)
    latex.SetTextSize(0.04)

    latex2 = TLatex(0.73, 0.96, "109 fb^{-1} (13.6 TeV)")
    latex2.SetNDC()
    latex2.SetTextFont(42)
    latex2.SetTextSize(0.04)

    eta_x, eta_text = ETA_DISPLAY[etaLabel]
    latex3 = TLatex(eta_x, 0.88, eta_text)
    latex3.SetNDC()
    latex3.SetTextFont(42)
    latex3.SetTextSize(0.07)

    gr.Draw("APL")
    latex.Draw()
    latex2.Draw()
    latex3.Draw()

    for sub in ('pdf', 'Cfile', 'rootfile'):
        os.makedirs(oDir + sub, exist_ok=True)

    outTitle = "significance_" + signalType
    c2.SaveAs(oDir + "pdf/summary_" + outTitle + "_" + etaLabel + ".pdf")
    c2.SaveAs(oDir + "Cfile/summary_" + outTitle + ".C")
    c2.SaveAs(oDir + "rootfile/summary_" + outTitle + ".root")
    print("Saved: {}pdf/summary_{}_{}.pdf".format(oDir, outTitle, etaLabel))