"""
Matrice de correlation entre nuisances (facon Run2), a partir des datacards
produites par MakeDatacard_Shape.py.

Chaine :
    1. text2workspace.py   : datacard .txt -> workspace .root
    2. combine -M FitDiagnostics --saveWithUncertainties : ecrit fit_b/fit_s
       (avec matrice de covariance/correlation) dans fitDiagnostics*.root
    3. extraction du RooFitResult -> correlationHist() (TH2)
    4. filtrage des prop_bin* (autoMCStats) + trace facon Run2

Par defaut : modele signal+background (fit_s, --expectSignal 1) en Asimov (-t -1),
comme la note d'analyse. --bkgOnly pour fit_b, --unblind pour vraies donnees.

Prerequis : environnement CMSSW + Combine (text2workspace.py, combine dans le PATH).
A LANCER depuis la racine du projet (LimitComputation_MassSpectrum/), la ou
existe MyNewDataCards/, pour que les chemins relatifs 'shapes' resolvent.
"""

from optparse import OptionParser
import os
import subprocess
import array
import ROOT as rt

rt.gROOT.SetBatch(True)

# ---------------------------------------------------------------------------
## LABELS : nom de nuisance Combine -> label TLatex affiche sur les axes
# ---------------------------------------------------------------------------
# ROOT n'utilise PAS la syntaxe LaTeX ($...$, \textrm{}) mais TLatex :
#   indice -> _{...}, exposant -> ^{...}, lettres grecques -> #eta, #mu, ...
# Ci-dessous la traduction du LaTeX demande vers TLatex.
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
    'r'              : 'Signal strength r',   # POI (signal strength)
}

# ---------------------------------------------------------------------------
## NUISANCES ACTIVES
# ---------------------------------------------------------------------------
# Liste de reference : toutes les systematiques que les datacards peuvent
# contenir (doit matcher MakeDatacard_Shape.py). Le POI 'r', les rateAll et
# les prop_bin* n'en font PAS partie, ils sont geres separement.
NUIS_ALL = [
    'PU', 'TriggerSF', 'K', 'C', 'Fpix', 'Jet', 'lumi',
    'eta', 'ih', 'mom', 'fitIh', 'fitMom',
    'corrTemplateIh', 'corrTemplate1oP',
]

# Commenter une entree de NUIS_LABELS suffit a desactiver la nuisance :
# elle est alors gelee a sa valeur nominale dans le fit (--freezeParameters),
# ce qui equivaut a retirer sa ligne de la datacard.
FROZEN_NUIS = [n for n in NUIS_ALL if n not in NUIS_LABELS]


def pretty_label(raw):
    """
    Traduit un nom de nuisance Combine en label TLatex.
    Gere les suffixes de decorrelation par categorie eta, p.ex.
    'K_Eta1' -> 'K_{mass} (Eta1)', 'rateAll_Eta1_2p4' -> ... (si affiche).
    Si aucune correspondance : renvoie le nom brut inchange.
    """
    if raw in NUIS_LABELS:
        return NUIS_LABELS[raw]

    # nuisances decorrelees : <base>_<eta> (ex: K_Eta1, C_Eta1_2p4)
    for base, lab in NUIS_LABELS.items():
        if raw.startswith(base + '_'):
            suffix = raw[len(base) + 1:]          # ex: 'Eta1', 'Eta1_2p4'
            return '{} ({})'.format(lab, suffix)

    return raw


# ---------------------------------------------------------------------------
## SETUP (hardcode, comme les autres scripts d'analyse)
# ---------------------------------------------------------------------------
parser = OptionParser()
parser.add_option('--splitEta', action='store_true', dest='splitEta', default=False,
                  help='Deux categories eta (Eta1 + Eta1_2p4).')
parser.add_option('--onlyEta1', action='store_true', dest='onlyEta1', default=False,
                  help='Region centrale seule (Eta1).')
parser.add_option('--unblind', action='store_true', dest='unblind', default=False,
                  help='Fit sur vraies donnees. Sinon Asimov (-t -1).')
parser.add_option('--bkgOnly', action='store_true', dest='bkgOnly', default=False,
                  help='Modele background-only (fit_b). Par defaut : signal+background '
                       '(fit_s, --expectSignal 1), comme la note d\'analyse.')
parser.add_option('--dryRun', action='store_true', dest='dryRun', default=False,
                  help='Affiche les commandes sans les executer.')
parser.add_option('--keepPropBin', action='store_true', dest='keepPropBin', default=False,
                  help='Ne pas exclure les nuisances autoMCStats prop_bin* du plot.')
parser.add_option('--dropRate', action='store_true', dest='dropRate', default=False,
                  help='Exclure aussi les rateParam rateAll* du plot (matrice systs purs).')
parser.add_option('--noFreeze', action='store_true', dest='noFreeze', default=False,
                  help='Ne pas geler les nuisances commentees : elles restent dans '
                       'le fit et sont seulement retirees de l\'affichage.')
(options, args) = parser.parse_args()

splitEta    = options.splitEta
onlyEta1    = options.onlyEta1
unblind     = options.unblind
bkgOnly     = options.bkgOnly
dryRun      = options.dryRun
keepPropBin = options.keepPropBin
dropRate    = options.dropRate
noFreeze    = options.noFreeze

# Prefixes de nuisances a exclure du plot (filtrage a l'affichage, sans toucher
# la datacard : elles restent bien dans le fit).
DROP_PREFIXES = []
if not keepPropBin:
    DROP_PREFIXES.append("prop_bin")
if dropRate:
    DROP_PREFIXES.append("rateAll")

# Doivent matcher MakeDatacard_Shape.py
regionBckg  = '9fp10'
optionlabel = 'v2'

if splitEta:
    etaLabel = 'split_Eta1_Eta1_2p4'
elif onlyEta1:
    etaLabel = 'Eta1'
else:
    etaLabel = 'Eta2p4'

# Point(s) de masse pour lesquels tracer la matrice.
# Une matrice par masse : les nuisances signal (K, C, Fpix, ...) dependent du signal.
# La note d'analyse utilise 1800 GeV avec le modele signal+background.
MASS_POINTS = [1100, 1200, 1300, 1400, 1600, 1800, 2000, 2200, 2400, 2600]

# Repertoires
inCardsDir = "Datacards/gluino/shape_{}_{}_{}/".format(regionBckg, etaLabel, optionlabel)
outDir     = "Datacards/gluino/shape_{}_{}_{}/".format(regionBckg, etaLabel, optionlabel)
os.makedirs(outDir, exist_ok=True)

launch_dir = os.getcwd()   # racine du projet, ou les 'shapes' relatifs sont valides


# ---------------------------------------------------------------------------
## FUNCTIONS
# ---------------------------------------------------------------------------
def is_dropped(raw):
    """True si la nuisance doit etre retiree de l'affichage."""
    if any(raw.startswith(p) for p in DROP_PREFIXES):
        return True
    # nuisances desactivees : nom exact ou variante decorrelee <nom>_<eta>
    for n in FROZEN_NUIS:
        if raw == n or raw.startswith(n + '_'):
            return True
    return False

def run(cmd, cwd=None):
    """Execute une commande shell (ou l'affiche seulement en dryRun)."""
    print(">>> " + cmd + ("   [cwd={}]".format(cwd) if cwd else ""))
    if dryRun:
        return
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)


def make_workspace(cardName, mass):
    """text2workspace.py depuis launch_dir (shapes relatifs valides)."""
    cardTxt = inCardsDir + cardName + ".txt"
    wsAbs   = os.path.abspath(outDir + cardName + "_ws.root")
    run("text2workspace.py {} -m {} -o {}".format(cardTxt, mass, wsAbs),
        cwd=launch_dir)
    return wsAbs


def run_fitdiagnostics(wsAbs, cardName, mass):
    """
    FitDiagnostics avec --saveWithUncertainties.
    Deux axes independants :
      - modele : signal+background (defaut, fit_s, --expectSignal 1) ou
                 background-only (--bkgOnly, fit_b, --expectSignal 0)
      - donnees : Asimov (-t -1, defaut) ou vraies donnees (--unblind)
    La note d'analyse utilise le modele S+B -> defaut ici.
    """
    tag = "_{}".format(cardName)

    expect = "--expectSignal 0" if bkgOnly else "--expectSignal 1"
    asimov = "" if unblind else "-t -1 "

    # Gel des nuisances desactivees. On passe par rgx{} plutot que par les noms
    # bruts : cela couvre les variantes decorrelees (<nom>_Eta1, <nom>_Eta1_2p4)
    # et, si le nom n'existe pas dans la datacard, la regex ne matche rien au
    # lieu de faire echouer combine.
    freeze = ""
    if FROZEN_NUIS and not noFreeze:
        rgx = ",".join("rgx{{^{}(_.*)?$}}".format(n) for n in FROZEN_NUIS)
        freeze = "--freezeParameters '{}' ".format(rgx)

    cmd = ("combine -M FitDiagnostics {ws} -m {m} "
           "--saveWithUncertainties --robustFit 1 "
           "{freeze}{asimov}{expect} -n {tag}").format(
               ws=wsAbs, m=mass, freeze=freeze, asimov=asimov,
               expect=expect, tag=tag)
    run(cmd, cwd=os.path.abspath(outDir))
    
    return os.path.abspath(outDir + "fitDiagnostics{}.root".format(tag))   


def extract_correlation(fdFile):
    """
    Recupere le RooFitResult (fit_s ou fit_b) et renvoie son correlationHist().
    Filtre les prop_bin* (autoMCStats) sauf si --keepPropBin.
    Les labels des axes sont traduits en TLatex via pretty_label().
    """
    fitName = "fit_b" if bkgOnly else "fit_s"
    f = rt.TFile.Open(fdFile, "READ")
    if not f or f.IsZombie():
        raise IOError("Impossible d'ouvrir {}".format(fdFile))
    fit = f.Get(fitName)
    if not fit:
        f.Close()
        raise KeyError("{} absent de {}".format(fitName, fdFile))

    corrFull = fit.correlationHist()   # TH2D, symetrique, labels = noms de nuisances
    corrFull.SetDirectory(0)
    f.Close()

    # --- indices a garder (filtrage prop_bin / rateAll) ---
    n = corrFull.GetNbinsX()
    keep = []   # indices de bins (1-based) a garder
    for i in range(1, n + 1):
        lab = corrFull.GetXaxis().GetBinLabel(i)
        if is_dropped(lab):
            continue
        keep.append(i)

    m = len(keep)
    corr = rt.TH2D("corr_reduced", "", m, 0, m, m, 0, m)
    corr.SetDirectory(0)
    # correlationHist() de Combine range l'axe Y en MIROIR de l'axe X :
    #   le bin Y 'jy' de corrFull correspond au nuisance d'indice X (n+1-jy).
    # On respecte cette convention pour que la diagonale i==i vaille bien 1 et
    # que les labels X/Y s'alignent (X croissant en bas, Y decroissant a gauche).
    for a, ia in enumerate(keep):           # a : nouvel index X 0-based
        rawX  = corrFull.GetXaxis().GetBinLabel(ia)
        labX  = pretty_label(rawX)
        corr.GetXaxis().SetBinLabel(a + 1, labX)
        # label Y en ordre inverse
        corr.GetYaxis().SetBinLabel(m - a, labX)
        for b, ib in enumerate(keep):       # b : nouvel index X 0-based
            # bin Y source correspondant au nuisance ib : miroir sur l'axe Y d'origine
            iy_src = n + 1 - ib
            val = corrFull.GetBinContent(ia, iy_src)
            # bin Y destination, en miroir egalement
            corr.SetBinContent(a + 1, m - b, val)
    return corr


def draw_correlation(corr, cardName, mass):
    """Trace la matrice facon Run2 (COLZ TEXT, palette viridis)."""
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

    latex2 = rt.TLatex(0.70, 0.94, "#scale[1.2]{#bf{m_{#tilde{g}}=" + str(mass) + " GeV}}")
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
    corr.GetXaxis().LabelsOption("v")   # labels verticaux en bas
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

    print("Region eta      : {}".format(etaLabel))
    print("Modele          : {}".format("background-only (fit_b)" if bkgOnly
                                        else "signal+background (fit_s)"))
    print("Donnees         : {}".format("vraies donnees (unblind)" if unblind
                                        else "Asimov (-t -1)"))
    print("Exclusions      : {}".format(", ".join(DROP_PREFIXES) if DROP_PREFIXES
                                        else "aucune"))
    print("Cards dir       : {}".format(inCardsDir))
    print("Out dir         : {}".format(outDir))

    print("Gelees          : {}".format(", ".join(FROZEN_NUIS) if FROZEN_NUIS
                                        else "aucune"))
    if FROZEN_NUIS and noFreeze:
        print("                  (--noFreeze : retirees de l'affichage seulement)")
    print("-" * 60)

    for mass in MASS_POINTS:
        cardName = "Gluino{}_2024".format(mass)
        cardTxt  = inCardsDir + cardName + ".txt"
        if not os.path.exists(cardTxt) and not dryRun:
            print("SKIP {} : datacard absente ({})".format(cardName, cardTxt))
            continue

        print("\n=== {} (m = {} GeV) ===".format(cardName, mass))
        wsAbs  = make_workspace(cardName, mass)
        fdFile = run_fitdiagnostics(wsAbs, cardName, mass)

        if dryRun:
            continue

        corr = extract_correlation(fdFile)
        draw_correlation(corr, cardName, mass)
    
    

    print("\nTermine.")