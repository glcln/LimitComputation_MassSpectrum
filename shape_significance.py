from optparse import OptionParser
import os
import re

import ROOT as rt
from ROOT import TCanvas, TLatex, TLegend, TGraph

rt.gROOT.SetBatch(True)

import tdrstyle
tdrstyle.setTDRStyle()

# Lancer la commande:

# FullTracker : py shape_drawSignificance.py
# Split Eta1/Eta1_2p4 : py shape_drawSignificance.py --splitEta
# Region centrale seule : py shape_drawSignificance.py --onlyEta1
# Cut and count : py shape_drawSignificance.py --cac
# Sauter le calcul Combine et juste retracer : py shape_drawSignificance.py --plotOnly

# Significance EXPECTED (Asimov, signal injecte mu=1) en fonction de la masse
# du gluino, tracee facon Run2 avec le fancing de plotSummary.


def setColorAndMarker(gr, color, marker, size=1):
    gr.SetMarkerColor(color)
    gr.SetLineColor(color)
    gr.SetMarkerStyle(marker)
    gr.SetMarkerSize(2)
    return gr


def parse_significance(root_path):
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

    parser = OptionParser()
    parser.add_option('-d', '--debug', type='int', default=1, dest='debug')
    parser.add_option('--cac', action='store_true', dest='cac', default=False,
                      help='Cut and count method (True) ou Shape (False)')
    parser.add_option('--splitEta', action='store_true', dest='splitEta', default=False)
    parser.add_option('--onlyEta1', action='store_true', dest='onlyEta1', default=False)
    parser.add_option('--plotOnly', action='store_true', dest='plotOnly', default=False,
                      help='Ne relance pas Combine, lit les .root existants et retrace')

    (options, args) = parser.parse_args()
    debug         = options.debug
    isCutAndCount = options.cac
    splitEta      = options.splitEta
    onlyEta1      = options.onlyEta1
    plotOnly      = options.plotOnly

    # Doit correspondre aux parametres du script de generation des datacards
    regionBckg  = '9fp10'
    optionlabel = 'v2'
    etalabeldir = 'Eta1_2p4'

    if splitEta:
        etaLabel = 'split_Eta1_' + etalabeldir
    elif onlyEta1:
        etaLabel = 'Eta1'
    else:
        etaLabel = 'Eta2p4'

    # etaname pour le label TLatex (region physique tracee)
    etaname = etaLabel

    idir = 'Datacards/gluino/shape_{}_{}_{}'.format(regionBckg, etaLabel, optionlabel)
    oDir = 'Limits/gluino/shape_{}_{}'.format(regionBckg, etaLabel) \
           + ("_cutandcount" if isCutAndCount else "") + '_' + optionlabel + '/'
    os.makedirs(oDir, exist_ok=True)

    endname = "_cutandcount" if isCutAndCount else ""

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

    def mass_of(sample):
        return int(re.search(r'Gluino(\d+)_', sample).group(1))

    # --- Calcul de la significance expected par mass point ---
    results = []  # (mass, Z)
    for sample in samples:
        out_root = "{}higgsCombine.{}.Significance.mH120.root".format(oDir, sample)

        if not plotOnly:
            dc = '{}/{}{}.txt'.format(idir, sample, endname)
            if not os.path.isfile(dc):
                print("WARNING datacard manquante: {}".format(dc))
                continue
            run_sig = (
                "combine -M Significance"
                " -n .{name}"
                " {dc}"
                " -t -1 --expectSignal=1"
            ).format(name=sample, dc=dc)
            if debug > 0:
                print("Running: {}".format(run_sig))
            os.system(run_sig)
            os.system("mv higgsCombine.{}.Significance.mH120.root {} 2>/dev/null".format(sample, oDir))

        z = parse_significance(out_root)
        if z is None:
            print("WARNING pas de significance pour {}".format(sample))
            continue
        results.append((mass_of(sample), z))

    results.sort()
    if not results:
        raise RuntimeError("Aucune significance recuperee.")

    gr = TGraph(len(results))
    for i, (m, z) in enumerate(results):
        gr.SetPoint(i, float(m), float(z))
        print("mass {:>5} GeV -> Z = {:.3f}".format(m, z))

    zmax = max(z for _, z in results)

    # --- Trace facon plotSummary ---
    c2 = TCanvas("c2", "c2", 800, 600)
    c2.SetBottomMargin(0.12)
    c2.SetLeftMargin(0.1)
    c2.SetGrid()
    c2.SetTicky(1)
    c2.SetTickx(1)

    gr.GetXaxis().SetTitle("Mass [GeV]")
    gr.GetYaxis().SetTitle("Expected significance")
    gr.GetXaxis().SetNdivisions(510)
    gr.GetXaxis().SetLabelFont(43)   # taille en pixels
    gr.GetXaxis().SetLabelSize(24)
    gr.GetXaxis().SetTitleSize(0.05)
    gr.GetYaxis().SetLabelFont(43)
    gr.GetYaxis().SetLabelSize(24)
    gr.GetYaxis().SetTitleSize(0.05)
    gr.GetYaxis().SetTitleOffset(1.0)
    gr.GetXaxis().SetTitleOffset(1.0)
    gr.GetXaxis().SetRangeUser(1000, 2700)
    gr.SetMinimum(1)
    gr.SetMaximum(zmax * 1.4)
    c2.SetLogy()

    setColorAndMarker(gr, rt.kRed, 34)

    # CMS + lumi + region eta
    latex = TLatex(0.1, 0.96, "#scale[1.3]{#it{Private work (CMS data)}}")
    latex.SetNDC()
    latex.SetTextFont(42)
    latex.SetTextSize(0.04)

    latex2 = TLatex(0.73, 0.96, "109 fb^{-1} (13.6 TeV)")
    latex2.SetNDC()
    latex2.SetTextFont(42)
    latex2.SetTextSize(0.04)

    latex3 = TLatex(0.8, 0.88, "#bf{|#eta|<1}")
    if (etaname == 'split_Eta1_Eta1_2p4'):
        latex3 = TLatex(0.6, 0.88, "#bf{|#eta|<1 & 1#leq|#eta|<2.4}")
    if (etaname == 'Eta2p4'):
        latex3 = TLatex(0.8, 0.88, "#bf{|#eta|<2.4}")
    latex3.SetNDC()
    latex3.SetTextFont(42)
    latex3.SetTextSize(0.07)


    gr.Draw("APL")
    latex.Draw()
    latex2.Draw()
    latex3.Draw()

    os.system('mkdir -p ' + oDir + 'pdf ' + oDir + 'Cfile ' + oDir + 'rootfile')

    outTitle = "significance_gluino"
    c2.SaveAs(oDir + "pdf/summary_" + outTitle + "_" + etaname + ".pdf")
    c2.SaveAs(oDir + "Cfile/summary_" + outTitle + ".root")
    c2.SaveAs(oDir + "rootfile/summary_" + outTitle + ".C")
    print("Saved: {}pdf/summary_{}_{}.pdf".format(oDir, outTitle, etaname))