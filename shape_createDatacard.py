"""
Build the Combine datacards, and their shape ROOT files, for the HSCP Run 3
mass-spectrum analysis.

For one signal model (gluino, stop or stau) and one eta configuration, the
script loops over the signal mass points and writes, for each of them:

    <Sample>.root              rebinned signal, background and data_obs mass
                               histograms with all their systematic variations
                               (shape mode only)
    <Sample>.txt               shape datacard (default mode)
    <Sample>_cutandcount.txt   counting-experiment datacard (--cac)

and, once per run, the table yields_<regionBckg>_<etaLabel>.txt with the
signal, background and observed yields in the mass window of each mass point.
<Sample> is '<Label><mass>_2024', e.g. Gluino2000_2024.

Eta configurations (--splitEta and --onlyEta1 are mutually exclusive)
    (default)     one category, full tracker |eta| < 2.4     etaLabel = 'Eta2p4'
    --onlyEta1    one category, central region |eta| < 1     etaLabel = 'Eta1'
    --splitEta    two categories, central region 'Eta1' and the forward region
                  named by the etalabeldir setting (e.g. 'Eta1_2p4')
                                          etaLabel = 'split_Eta1_<etalabeldir>'

Inputs
    signal        <BASE_SIGNAL_DIR><dir><pattern>, one file per mass point
                  (see SIGNAL_CONFIG)
    background    <idirData>JetMET2024_V<version>_<eta><option>_<variation>.root,
                  one file per variation (see BKG_FILE_SUFFIX)

Output directory
    <DATACARDS_BASE>/<signal>/shape_<regionBckg>_<etaLabel>_<optionlabel>/
    where DATACARDS_BASE is the Datacards/ directory next to this script.

Blinding
    By default the observed data are not used: data_obs (shape mode), the
    observation (cut-and-count mode) and the observed yield of the table are
    all set to the nominal background prediction. With --unblind they are
    taken from the observed mass spectrum instead.

The `shapes` line of the datacards holds the absolute path of the ROOT file:
the datacards can be run from any directory, but moving them requires editing
that line.

All analysis settings are hardcoded in the CONFIGURATION section below. The
etalabeldir, optionlabel and optionlabelForFile settings are rewritten in
place by the driver shape_ProduceLimitsForDifferentEtaCategory.py. regionBckg,
etalabeldir and optionlabel must have the same values in shape_runDatacard.py
and shape_drawDatacard.py, which rebuild the directory names from them.

Usage:
    python3 shape_createDatacard.py                           # gluino, full tracker, shape
    python3 shape_createDatacard.py --cac --signal stau       # cut-and-count, stau
    python3 shape_createDatacard.py --unblind                 # with the observed data
    # the next two need etalabeldir set accordingly (see CONFIGURATION)
    python3 shape_createDatacard.py --onlyEta1 --signal stop  # central region, stop
    python3 shape_createDatacard.py --splitEta                # two eta categories
"""

from optparse import OptionParser
import ROOT as rt
import sys
import os
import ctypes
import re
import array
from collections import OrderedDict

rt.gROOT.SetBatch(True)

# ---------------------------------------------------------------------------
## COMMAND LINE
# ---------------------------------------------------------------------------
parser = OptionParser()
parser.add_option('--cac', action='store_true', dest='cac', default=False,
                  help='Write cut-and-count datacards (counting experiment in a mass '
                       'window) instead of shape datacards.')
parser.add_option('--splitEta', action='store_true', dest='splitEta', default=False,
                  help='Use two eta categories, central |eta|<1 (Eta1) and forward '
                       '1<|eta|<2.4 (Eta1_2p4), instead of the full tracker |eta|<2.4 '
                       '(Eta2p4).')
parser.add_option('--onlyEta1', action='store_true', dest='onlyEta1', default=False,
                  help='Datacard with the central region |eta|<1 (Eta1) only.')
parser.add_option('--signal', dest='signal', default='gluino',
                  type='choice', choices=['gluino', 'stop', 'stau'],
                  help='Signal sample: gluino (default), stop or stau.')
parser.add_option('--unblind', action='store_true', dest='unblind', default=False,
                  help='Use the observed mass spectrum as data. By default the data are '
                       'replaced by the nominal background prediction (blinded).')
(options, args) = parser.parse_args()

if options.splitEta and options.onlyEta1:
    parser.error('--splitEta and --onlyEta1 are mutually exclusive')

isCutAndCount = options.cac
splitEta      = options.splitEta
onlyEta1      = options.onlyEta1
signalType    = options.signal
unblind       = options.unblind

# ---------------------------------------------------------------------------
## CONFIGURATION
# ---------------------------------------------------------------------------
versionData = '12p35'     # version tag of the background prediction files
regionBckg  = '9fp10'     # region tag, part of histogram and directory names
channel     = 'Ch2024'    # base name of the Combine bins

# The three settings below are rewritten in place by the driver
# shape_ProduceLimitsForDifferentEtaCategory.py, which looks for one-line,
# single-quoted assignments: keep that form, and a single assignment of each
# in this file.
#   etalabeldir        : sub-directory of the background prediction files and,
#                        with --splitEta, name of the forward eta region.
#                        The driver uses 'Eta2p4' for the full tracker, 'Eta1'
#                        with --onlyEta1 and 'Eta1_2p4' with --splitEta.
#   optionlabel        : tag of the background prediction, part of the input
#                        and output directory names
#   optionlabelForFile : the same option as it appears in the file and
#                        histogram names ('' when there is none)
etalabeldir = 'Eta2p4'
optionlabel = 'SigmaPtoverPt_0p5_EoP_0p1_v2'
optionlabelForFile = '_SigmaPtoverPt_0p5_EoP_0p1'

# Root of the output tree, <DATACARDS_BASE>/<signal>/shape_<...>/: the
# Datacards/ directory next to this script
DATACARDS_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Datacards')

# Root of the signal histogram files
BASE_SIGNAL_DIR = '/safe/ui3_1/cms/gcoulon/CMSSW_15_0_13_patch1/src/TupleAnalysis/output/'

# Root of the background prediction files
BASE_BKG_DIR = '/safe/ui3_1/cms/gcoulon/CMSSW_15_0_13_patch1/src/TupleAnalysis/macros/'

# Directory of the background prediction files. With --splitEta the files of
# both categories are read from this same directory.
idirData = BASE_BKG_DIR + 'data2024_V' + versionData + '__' + regionBckg + '_' + optionlabel + '/' + etalabeldir + '/'

# Per-signal configuration:
#   dir     : directory of the signal histogram files
#   pattern : file name, with {mass} in GeV and {ver} = 'version'
#   version : version tag of the signal files
#   label   : prefix of the Combine sample name, '<label><mass>_2024'
#   masses  : mass points [GeV]
# shape_runDatacard.py runs on the datacards it finds, so it holds no copy of
# these lists.
SIGNAL_CONFIG = {
    'gluino': {
        'dir'     : BASE_SIGNAL_DIR + 'Gluino_V19/',
        'pattern' : 'Gluino_Run3_MET_madgraph_{mass}_V{ver}_weighted.root',
        'version' : '19p12',
        'label'   : 'Gluino',
        'masses'  : [1100, 1200, 1300, 1400, 1600, 1800, 2000, 2200, 2400, 2600],
    },
    'stop': {
        'dir'     : BASE_SIGNAL_DIR + 'Stop_V21/',
        'pattern' : 'Stop_Run3_MET_madgraph_{mass}_V{ver}_weighted.root',
        'version' : '21p0',
        'label'   : 'Stop',
        'masses'  : [700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600],
    },
    'stau': {
        'dir'     : BASE_SIGNAL_DIR + 'Stau_V20/',
        'pattern' : 'Stau_Run3_MET_{mass}_V{ver}_weighted.root',
        'version' : '20p0',
        'label'   : 'Stau',
        'masses'  : [247, 308, 432, 557, 651, 745, 871, 1029, 1218, 1409, 1599],
    },
}

# Base name of the signal histograms. The full name is
#   <SIG_LABEL_BASE><optionlabelForFile>_<eta>_<regionBckg>_SignalMass_<variation>
# e.g. METanalysis_TestPUppiMETCut_Eta1_9fp10_SignalMass_nominal
SIG_LABEL_BASE = "METanalysis_TestPUppiMETCut"

# Background systematics: Combine nuisance name -> (Up key, Down key), the keys
# being those of BKG_FILE_SUFFIX below. When Up and Down are the same key the
# source is one-sided: a single variation exists, and the Down template is
# obtained by mirroring it around the nominal (see _mirror).
BKG_SYST_MAP = {
    'eta'            : ('etaUp',    'etaDown'),
    'ih'             : ('ihUp',     'ihDown'),
    'mom'            : ('momUp',    'momDown'),
    'fitIh'          : ('fitihUp',  'fitihDown'),
    'fitMom'         : ('fitmomUp', 'fitmomDown'),
    'corrTemplateIh' : ('corrTemplateIh', 'corrTemplateIh'),  # one-sided
    'corrTemplate1oP' : ('corrTemplate1oP', 'corrTemplate1oP'),  # one-sided
}

# Background prediction files: key -> suffix of the file name
# (JetMET2024_V<version>_<eta><option>_<suffix>.root). 'obs' and 'nominal'
# point to the same file but read different histograms (see
# load_bkg_histograms).
BKG_FILE_SUFFIX = OrderedDict([
    ('obs'             , 'nominal'),
    ('nominal'         , 'nominal'),
    ('etaUp'           , 'binEtaUp'),
    ('etaDown'         , 'binEtaDown'),
    ('ihUp'            , 'binIhUp'),
    ('ihDown'          , 'binIhDown'),
    ('momUp'           , 'binMomUp'),
    ('momDown'         , 'binMomDown'),
    ('fitihUp'         , 'fitIhUp'),
    ('fitihDown'       , 'fitIhDown'),
    ('fitmomUp'        , 'fitMomUp'),
    ('fitmomDown'      , 'fitMomDown'),
    ('corrTemplateIh'  , 'corrTemplateIh'),
    ('corrTemplate1oP' , 'corrTemplate1oP'),
])

# Flat normalisation uncertainties (lnN) applied to the signal in every
# category and correlated between categories: integrated luminosity and Fpix.
HARDCODED_LNN = OrderedDict([
    ('lumi', '1.014'),
    ('Fpix', '1.016'),
])

# Common variable binning (mass in GeV) applied to every histogram written to
# the Combine shape file. The edges should coincide with bin edges of the input
# histograms.
REBINNING = array.array('d', [
    0., 20., 40., 60., 80., 100., 120., 140., 160., 180., 200.,
    220., 240., 260., 280., 300., 320., 340., 360., 380., 410.,
    440., 480., 530., 590., 660., 760., 880., 1030., 1210., 1440.,
    1730., 2000., 2500., 3200., 4000.,
])

# Mass window used for the cut-and-count datacard and the yield table, built
# from the mean and standard deviation (sigma) of the nominal signal shape:
#   [mean - NSIGMA_LOW * sigma, mean + NSIGMA_HIGH * sigma]
# with a lower edge of at least MASS_WINDOW_MIN GeV.
MASS_WINDOW_NSIGMA_LOW  = 1
MASS_WINDOW_NSIGMA_HIGH = 2
MASS_WINDOW_MIN         = 300


# ---------------------------------------------------------------------------
## FUNCTIONS
# ---------------------------------------------------------------------------
def integralHisto(h, xmin, xmax):
    """
    Integral of `h` from the bin containing xmin to the bin containing xmax,
    both included. Whole bins are summed, so the effective window extends to
    the outer edges of these two bins.
    """
    return h.Integral(h.FindBin(xmin), h.FindBin(xmax))


def get_signal_systematics(root_path, label, fp_cut="9fp10"):
    """
    Read the nominal signal mass histogram and its systematic variations.

    The histograms are named <label>_<fp_cut>_SignalMass_<variation>, where
    `label` already carries the eta tag, e.g.:
        METanalysis_TestPUppiMETCut_Eta1
        METanalysis_TestPUppiMETCut_Eta1_2p4
        METanalysis_TestPUppiMETCut_Eta2p4

    Returns
    -------
    nominal : TH1
        The nominal histogram, detached from the file.
    systematics : dict
        {variation: TH1 or None} for the Up and Down variations of PU,
        TriggerSF, K, C and Jet. A missing histogram is stored as None (with a
        warning) and the systematic is then left out of the datacard.

    Raises IOError if the file cannot be opened and KeyError if the nominal
    histogram is missing.
    """

    syst_names = [
        "PUUp", "PUDown",
        "TriggerSFUp", "TriggerSFDown",
        "KUp", "KDown",
        "CUp", "CDown",
        "JetUp", "JetDown",
    ]

    f = rt.TFile.Open(root_path, "READ")
    if not f or f.IsZombie():
        raise IOError("Cannot open ROOT file: {}".format(root_path))

    base = "{}_{}_SignalMass".format(label, fp_cut)

    nominal = f.Get("{}_nominal".format(base))
    if not nominal:
        f.Close()
        raise KeyError("Histogram not found: {}_nominal".format(base))
    nominal.SetDirectory(0)  # detach from file

    systematics = {}
    for syst in syst_names:
        h = f.Get("{}_{}".format(base, syst))
        if not h:
            print("Warning: histogram not found: {}_{}".format(base, syst))
            systematics[syst] = None
        else:
            h.SetDirectory(0)
            systematics[syst] = h

    f.Close()
    return nominal, systematics


def build_fpathPred(idirData, versionData, eta, option=""):
    """
    Paths of the background prediction files of one eta region, one per key of
    BKG_FILE_SUFFIX.
    File name: <idirData>JetMET2024_V<versionData>_<eta><option>_<suffix>.root
    """
    base = idirData + 'JetMET2024_V' + versionData + '_' + eta + option
    return {key: '{}_{}.root'.format(base, suf)
            for key, suf in BKG_FILE_SUFFIX.items()}


def load_bkg_histograms(fpathPred, regionBckg):
    """
    Read one mass histogram from each background prediction file.

    fpathPred : dict {key: path}, as returned by build_fpathPred

    The 'obs' key reads mass_obs_<regionBckg> (observed mass spectrum), every
    other key reads mass_predBC_<regionBckg> (background prediction).

    Returns a dict {key: TH1} of histograms detached from their files. A
    missing histogram only gives a warning and its key is left out of the
    dict. A file that cannot be opened stops the script when PyROOT raises
    OSError (recent versions); if TFile.Open returns a null pointer instead,
    the file is skipped with a warning, like a missing histogram.
    """
    mass_plot = {}
    for key, fpath in fpathPred.items():
        f = rt.TFile.Open(fpath)
        if not f or f.IsZombie():
            print("WARNING: Cannot open bkg file: {}".format(fpath))
            continue
        if key == 'obs':
            hname = "mass_obs_{}".format(regionBckg)
        else:
            hname = "mass_predBC_{}".format(regionBckg)
        h = f.Get(hname)
        if not h:
            print("WARNING: {} not found in {}".format(hname, fpath))
            f.Close()
            continue
        h_clone = h.Clone("{}_loaded".format(key))
        h_clone.SetDirectory(0)
        mass_plot[key] = h_clone
        f.Close()

    return mass_plot


def prepare_shape_rootfile(outDir, modelName, categories):
    """
    Write the shape ROOT file read by the Combine datacard of one mass point.

    `categories` is a list of dicts, one per eta category, each holding the
    keys 'channel', 'sig_nominal', 'sig_variations', 'bkg_nominal', 'data_obs'
    and 'mass_plot'.

    For each channel <chan>, the file contains (all rebinned with REBINNING):
      - signal_<chan>, background_<chan> : nominal templates
      - data_obs_<chan> : the 'data_obs' histogram of the category, i.e. the
        nominal background when blinded, the observed spectrum with --unblind
      - signal_<chan>_<syst>Up/Down : signal systematics found in the signal file
      - background_<chan>_<syst>Up/Down : background systematics of BKG_SYST_MAP;
        for a one-sided source the Down template is the mirror of the Up one

    These names follow the `shapes` line of the datacard:
    $PROCESS_$CHANNEL and $PROCESS_$CHANNEL_$SYSTEMATIC.

    Returns the path of the ROOT file.
    """
    rootFileName = outDir + modelName + ".root"
    f = rt.TFile(rootFileName, "RECREATE")
    f.cd()

    for cat in categories:
        chan           = cat['channel']
        sig_nominal    = cat['sig_nominal']
        sig_variations = cat['sig_variations']
        bkg_nominal    = cat['bkg_nominal']
        mass_plot      = cat['mass_plot']

        # Nominal signal
        _rebin(sig_nominal, "signal_{}".format(chan)).Write()

        # Nominal background
        _rebin(bkg_nominal, "background_{}".format(chan)).Write()

        # Data: background prediction when blinded, observed spectrum otherwise
        _rebin(cat['data_obs'], "data_obs_{}".format(chan)).Write()

        # Signal systematics: PU, TriggerSF, K, C, Jet (sysName ends with Up/Down)
        for sysName, h_var in sig_variations.items():
            if h_var is not None:
                _rebin(h_var, "signal_{}_{}".format(chan, sysName)).Write()

        # Background systematics
        for systCombName, (keyUp, keyDown) in BKG_SYST_MAP.items():
            h_bkg_up = mass_plot.get(keyUp)
            if h_bkg_up:
                _rebin(h_bkg_up, "background_{}_{}Up".format(chan, systCombName)).Write()

            if keyUp == keyDown:
                # One-sided source: Down is the mirror of Up around the nominal
                if h_bkg_up:
                    _mirror(bkg_nominal, h_bkg_up,
                            "background_{}_{}Down".format(chan, systCombName)).Write()
            else:
                h_bkg_down = mass_plot.get(keyDown)
                if h_bkg_down:
                    _rebin(h_bkg_down, "background_{}_{}Down".format(chan, systCombName)).Write()

    f.Close()
    print("ROOT file written: {}".format(rootFileName))
    return rootFileName


def _rebin(h, newname):
    """
    Rebin `h` with the REBINNING edges and return the result as a new
    histogram named `newname`, detached from any file. `h` is left untouched.
    """
    h_re = h.Rebin(len(REBINNING) - 1, newname, REBINNING)
    h_re.SetDirectory(0)
    return h_re

def _mirror(h_nom, h_var, newname):
    """
    Down template of a one-sided systematic, mirrored around the nominal:
    down = 2 * nominal - variation in each bin (underflow and overflow
    included), with negative contents set to 0. The bin errors are those of
    the varied histogram. Both inputs are rebinned first.
    """
    h_dn  = _rebin(h_nom, newname)
    h_var_re = _rebin(h_var, newname + "_tmpvar")
    for i in range(0, h_dn.GetNbinsX() + 2):
        v = 2.0 * h_dn.GetBinContent(i) - h_var_re.GetBinContent(i)
        h_dn.SetBinContent(i, max(v, 0.0))
        h_dn.SetBinError(i, h_var_re.GetBinError(i))
    return h_dn


# --- small helpers for the datacard ------------------------------------------
def _sig_bases(sig_variations):
    """Names of the signal systematics, without their Up/Down suffix."""
    bases = set()
    for key in sig_variations:
        if key.endswith('Up'):
            bases.add(key[:-len('Up')])
        elif key.endswith('Down'):
            bases.add(key[:-len('Down')])
    return bases


def _row(categories, present_channels, process):
    """
    Columns of a shape-systematic line: two per category, (signal, background).
    `process` is 'signal' or 'background'.
    A column is '1.0' when the channel of the category is in `present_channels`
    and the process matches, '-' otherwise.
    """
    cols = []
    for cat in categories:
        s, b = '-', '-'
        if cat['channel'] in present_channels:
            if process == 'signal':
                s = '1.0'
            if process == 'background':
                b = '1.0'
        cols.extend([s, b])
    return cols


def _lnN_factor(cat, base, process):
    """
    lnN factor of the systematic `base` in one category, for the cut-and-count
    datacard: ratio of the varied yield to the nominal yield, both integrated
    over the mass window [xmin, xmax] of the category.

    Returns:
        None          -> systematic not available for this process/category,
                         or zero nominal yield (written as '-')
        (down, up)    -> two-sided systematic (signal, or background with
                         distinct Up and Down variations)
        up            -> one-sided background systematic (single factor)
    """
    xmin, xmax = cat['xmin'], cat['xmax']

    if process == 'signal':
        sv = cat['sig_variations']
        h_up, h_dn = sv.get(base + 'Up'), sv.get(base + 'Down')
        if h_up is None or h_dn is None:
            return None
        nom = integralHisto(cat['sig_nominal'], xmin, xmax)
        if nom == 0:
            return None
        up = integralHisto(h_up, xmin, xmax) / nom
        dn = integralHisto(h_dn, xmin, xmax) / nom
        return (dn, up)

    else:  # background
        keyUp, keyDown = BKG_SYST_MAP[base]
        mp = cat['mass_plot']
        h_up, h_dn = mp.get(keyUp), mp.get(keyDown)
        if h_up is None or h_dn is None:
            return None
        nom = integralHisto(cat['bkg_nominal'], xmin, xmax)
        if nom == 0:
            return None
        up = integralHisto(h_up, xmin, xmax) / nom
        dn = integralHisto(h_dn, xmin, xmax) / nom
        if keyUp == keyDown:
            # one-sided (e.g. corrTemplateIh) -> single factor
            return up
        # two-sided -> asymmetric lnN down/up, as for the signal
        return (dn, up)


def _fmt_lnN(val):
    """
    Format a value returned by _lnN_factor as a datacard column: '-',
    'down/up' or a single number.
    """
    if val is None:
        return '-'
    if isinstance(val, tuple):
        return '{}/{}'.format(val[0], val[1])
    return str(val)

def _integral_and_error(h, xmin, xmax):
    """Same integral as integralHisto, returned with its statistical error."""
    err = ctypes.c_double(0.0)
    val = h.IntegralAndError(h.FindBin(xmin), h.FindBin(xmax), err)
    return val, err.value


def _quad_syst(cat, process):
    """
    Quadratic sum of the systematic uncertainties of one category on the yield
    in the mass window, separately for the up and down sides.

    The sign of a deviation decides which side it contributes to: a source
    whose two variations both raise the yield only enters the up side. One-sided
    systematics (e.g. corrTemplateIh) are symmetrised, consistently with the
    mirroring done in _mirror(). For the signal, the HARDCODED_LNN
    uncertainties are added to both sides.

    Returns (rel_up, rel_down), relative uncertainties.
    """
    up2, dn2 = 0.0, 0.0

    if process == 'signal':
        bases = sorted(_sig_bases(cat['sig_variations']))
    else:
        bases = sorted(BKG_SYST_MAP)

    for base in bases:
        f = _lnN_factor(cat, base, process)
        if f is None:
            continue
        if isinstance(f, tuple):
            d1, d2 = f[0] - 1.0, f[1] - 1.0
        else:
            d1, d2 = f - 1.0, 1.0 - f
        up2 += max(d1, d2, 0.0) ** 2
        dn2 += min(d1, d2, 0.0) ** 2

    if process == 'signal':
        for val in HARDCODED_LNN.values():
            d = abs(float(val) - 1.0)
            up2 += d * d
            dn2 += d * d

    return up2 ** 0.5, dn2 ** 0.5


def collect_yields(signal, categories):
    """
    Rows of the yield table for one mass point, one row per category.

    Each row gives the signal, background and observed yields in the mass
    window of the category, with their statistical and systematic
    uncertainties and the total ones (statistical and systematic in
    quadrature). The mass is read from the sample name. The observed yield is
    the 'obs_yield' of the category, the same number as in the cut-and-count
    datacard: the background prediction when blinded, the observed count with
    --unblind. Column order: see write_yield_file.
    """
    m = re.search(r'(\d+)', signal)
    mass = int(m.group(1)) if m else 0

    rows = []
    for cat in categories:
        xmin, xmax = cat['xmin'], cat['xmax']

        sig, sig_stat = _integral_and_error(cat['sig_nominal'], xmin, xmax)
        bkg, bkg_stat = _integral_and_error(cat['bkg_nominal'], xmin, xmax)
        obs = cat['obs_yield']

        sig_up, sig_dn = _quad_syst(cat, 'signal')
        bkg_up, bkg_dn = _quad_syst(cat, 'background')

        sig_totUp = (sig * sig_up) ** 2 + sig_stat ** 2
        sig_totDn = (sig * sig_dn) ** 2 + sig_stat ** 2
        bkg_totUp = (bkg * bkg_up) ** 2 + bkg_stat ** 2
        bkg_totDn = (bkg * bkg_dn) ** 2 + bkg_stat ** 2

        rows.append([
            mass, cat['eta'], xmin, xmax,
            sig, sig_stat, sig * sig_up, sig * sig_dn,
            bkg, bkg_stat, bkg * bkg_up, bkg * bkg_dn,
            obs, obs ** 0.5,
            sig_totUp ** 0.5, sig_totDn ** 0.5, bkg_totUp ** 0.5, bkg_totDn ** 0.5
        ])
    return rows


def write_yield_file(outPath, rows):
    """
    Write the yield table as a text file with one header line, the rows being
    sorted by mass and then by eta category.
    """
    cols = ['mass', 'eta', 'xmin', 'xmax',
            'sig', 'sig_stat', 'sig_systUp', 'sig_systDn',
            'bkg', 'bkg_stat', 'bkg_systUp', 'bkg_systDn',
            'obs', 'obs_stat',
            'sig_totUp', 'sig_totDn', 'bkg_totUp', 'bkg_totDn'
            ]
    fmt_head = '#{:>7} {:>10}' + ' {:>12}' * 16 + '\n'
    fmt_row  = ' {:>7d} {:>10}' + ' {:>12.5g}' * 16 + '\n'

    with open(outPath, 'w') as f:
        f.write(fmt_head.format(*cols))
        for r in sorted(rows, key=lambda x: (x[0], x[1])):
            f.write(fmt_row.format(*r))
    print("Yield table written: {}".format(outPath))


def write_datacard(outDataCardsDir, modelName, rootFileName, categories,
                   isCutAndCount_=False, thresh=10):
    """
    Write the Combine datacard of one mass point, with one category (full
    tracker or central region) or two (eta split).

    `categories`: list of dicts, one per category, holding at least:
        'channel'        : Combine bin name (e.g. 'Ch2024' or 'Ch2024_Eta1')
        'eta'            : eta tag ('Eta1', 'Eta1_2p4', 'Eta2p4')
        'sig_variations' : dict {<syst>Up/Down: TH1 or None}
        'mass_plot'      : dict of the background histograms (keys of fpathPred)
        'signal_yield', 'bkg_yield', 'obs_yield' : floats (cut-and-count)
        'sig_nominal', 'bkg_nominal', 'xmin', 'xmax' : inputs of the lnN
                           factors (cut-and-count)

    Shape mode (default): rates and observation are -1, i.e. taken from the
    histograms of `rootFileName`; systematics are of type `shape`; each
    category gets a freely floating background normalisation (rateParam) and
    bin-by-bin statistical uncertainties (autoMCStats, threshold `thresh`).
    Output: <modelName>.txt

    Cut-and-count mode (isCutAndCount_=True): counting experiment in the mass
    window; rates and observation are the yields of the categories and the
    systematics are lnN factors (see _lnN_factor); no rateParam, no
    autoMCStats; `rootFileName` is not used. Output: <modelName>_cutandcount.txt

    A systematic is written for the channels where both its Up and Down
    variations are available, as a single nuisance parameter correlated
    between the categories.

    With several categories, the columns are ordered:
        [ (chan0,signal), (chan0,bkg), (chan1,signal), (chan1,bkg), ... ]
    """
    nChan    = len(categories)
    channels = [cat['channel'] for cat in categories]

    # --- Signal systematics available (Up AND Down), per channel ---
    sig_present = {}   # base -> set(channels)
    for cat in categories:
        chan = cat['channel']
        sv   = cat['sig_variations']
        for base in _sig_bases(sv):
            if sv.get(base + 'Up') is not None and sv.get(base + 'Down') is not None:
                sig_present.setdefault(base, set()).add(chan)

    # --- Background systematics available (Up AND Down loaded), per channel ---
    bkg_present = {}   # base -> set(channels)
    for cat in categories:
        chan = cat['channel']
        mp   = cat['mass_plot']
        for base, (keyUp, keyDown) in BKG_SYST_MAP.items():
            if mp.get(keyUp) is not None and mp.get(keyDown) is not None:
                bkg_present.setdefault(base, set()).add(chan)

    endname  = "_cutandcount" if isCutAndCount_ else ""
    outPath  = outDataCardsDir + modelName + endname + ".txt"
    systType = 'lnN' if isCutAndCount_ else 'shape'

    with open(outPath, "w") as text_file:

        # --- header: imax channels, 2 processes (jmax 1), nuisances counted by Combine ---
        text_file.write('imax {} \n'.format(nChan))
        text_file.write('jmax 1 \n')
        text_file.write('kmax * \n')

        # Counting experiment: no shape file. Shape mode: one ROOT file for all
        # processes and channels.
        if isCutAndCount_:
            text_file.write('shapes * * FAKE  \n')
        text_file.write('--------------- \n')
        if not isCutAndCount_:
            text_file.write('shapes * * {} $PROCESS_$CHANNEL $PROCESS_$CHANNEL_$SYSTEMATIC \n'.format(rootFileName))
        text_file.write('--------------- \n')

        # --- bin / observation (-1 = integral of the data_obs histogram) ---
        text_file.write('bin \t ' + ' \t '.join(channels) + ' \n')
        if isCutAndCount_:
            obs = [str(cat['obs_yield']) for cat in categories]
            text_file.write('observation \t ' + ' \t '.join(obs) + ' \n')
        else:
            text_file.write('observation \t ' + ' \t '.join(['-1'] * nChan) + ' \n')
        text_file.write('------------------------------ \n')

        # --- bin (x2) / process / rate (-1 = integral of the template) ---
        # Signal is process 0, background process 1.
        bin_row, pname_row, pid_row, rate_row = [], [], [], []
        for cat in categories:
            bin_row   += [cat['channel'], cat['channel']]
            pname_row += ['signal', 'background']
            pid_row   += ['0', '1']
            if isCutAndCount_:
                rate_row += [str(cat['signal_yield']), str(cat['bkg_yield'])]
            else:
                rate_row += ['-1', '-1']
        text_file.write('bin \t '     + ' \t '.join(bin_row)   + ' \n')
        text_file.write('process \t ' + ' \t '.join(pname_row) + ' \n')
        text_file.write('process \t ' + ' \t '.join(pid_row)   + ' \n')
        text_file.write('rate \t '    + ' \t '.join(rate_row)  + ' \n')
        text_file.write('------------------------------ \n')

        # --- hardcoded lnN systematics: signal only, correlated between categories ---
        for systName, systVal in HARDCODED_LNN.items():
            cols = []
            for cat in categories:
                cols += [systVal, '-']
            text_file.write('{} \t lnN \t '.format(systName) + ' \t '.join(cols) + ' \n')

        # --- one line, hence one nuisance, per systematic: correlated between categories ---
        def write_syst(base, present, process):
            if isCutAndCount_:
                cols = []
                for cat in categories:
                    if cat['channel'] in present:
                        f = _lnN_factor(cat, base, process)
                        s = _fmt_lnN(f) if process == 'signal' else '-'
                        b = _fmt_lnN(f) if process == 'background' else '-'
                    else:
                        s, b = '-', '-'
                    cols.extend([s, b])
            else:
                cols = _row(categories, present, process)
            text_file.write('{} \t {} \t '.format(base, systType) + ' \t '.join(cols) + ' \n')

        # Signal systematics (PU, TriggerSF, K, C, Jet)
        for base in sorted(sig_present):
            write_syst(base, sig_present[base], 'signal')
        # Background systematics (eta, ih, mom, fitIh, fitMom, corrTemplateIh, corrTemplate1oP)
        for base in sorted(bkg_present):
            write_syst(base, bkg_present[base], 'background')

        # --- rateParam + autoMCStats (shape mode only), per channel ---
        if not isCutAndCount_:
            for cat in categories:
                # one free background normalisation per category, starting at 1 and
                # bounded to [0,5] (decorrelated between the eta regions)
                rp = 'rateAll' if nChan == 1 else 'rateAll_{}'.format(cat['eta'])
                text_file.write('{} rateParam {} background 1.0 [0,5]\n'.format(rp, cat['channel']))
            for cat in categories:
                text_file.write('{} autoMCStats {} \n'.format(cat['channel'], thresh))

    print("Datacard written: {}".format(outPath))


if __name__ == '__main__':

    # --- Eta regions and output label, from the command-line flags ---
    if splitEta:
        # The forward region must be disjoint from the central one
        if etalabeldir in ('Eta2p4', 'Eta1'):
            sys.exit("--splitEta needs etalabeldir set to the forward eta region "
                     "(e.g. 'Eta1_2p4'), not '{}': the two categories would "
                     "overlap.".format(etalabeldir))
        etaRegions = ['Eta1', etalabeldir]    # central |eta|<1 , forward 1<|eta|<2.4
        etaLabel   = 'split_Eta1_' + etalabeldir
    elif onlyEta1:
        etaRegions = ['Eta1']                # central region only, |eta|<1
        etaLabel   = 'Eta1'
    else:
        etaRegions = ['Eta2p4']              # full tracker, |eta|<2.4
        etaLabel   = 'Eta2p4'

    outDataCardsDir = os.path.join(DATACARDS_BASE, signalType, 'shape_{}_{}_{}'.format(regionBckg, etaLabel, optionlabel)) + os.sep
    os.makedirs(outDataCardsDir, exist_ok=True)
    print("Output dir: {}".format(outDataCardsDir))

    if isCutAndCount:
        print("Cut and count method selected")
    else:
        print("Shape method selected")
    if splitEta:
        print("Eta split selected -> categories: {}".format(etaRegions))
    elif onlyEta1:
        print("Only central region selected -> Eta1")
    else:
        print("Full tracker selected -> Eta2p4")
    if unblind:
        print("UNBLINDED: data taken from the observed mass spectrum")
    else:
        print("Blinded: data replaced by the nominal background prediction")

    # --- SIGNAL ---
    # Ordered {sample name: signal file}, sample name = '<label><mass>_2024'
    sigCfg = SIGNAL_CONFIG[signalType]
    fpath = OrderedDict(
        ('{}{}_2024'.format(sigCfg['label'], m),
         sigCfg['dir'] + sigCfg['pattern'].format(mass=m, ver=sigCfg['version']))
        for m in sigCfg['masses']
    )
    print("Signal sample: {} ({} mass points)".format(signalType, len(fpath)))

    yield_rows = []

    # --- LOOP OVER THE MASS POINTS ---
    for signal, sig_path in fpath.items():

        # Build the list of categories (one or two) of this mass point
        categories = []
        for eta in etaRegions:

            # Combine bin name of this category: 'Ch2024' for the full tracker,
            # 'Ch2024_<eta>' otherwise
            chan = "{}_{}".format(channel, eta) if eta != 'Eta2p4' else channel

            # --- SIGNAL of this eta region ---
            # the label carries the option and the eta tag: ..._Eta1, ..._Eta1_2p4, ..._Eta2p4
            sig_label = SIG_LABEL_BASE + optionlabelForFile + '_' + eta

            sig_nominal, sig_variations = get_signal_systematics(sig_path, sig_label, regionBckg)

            # --- BACKGROUND of this eta region (files specific to the eta region) ---
            fpathPred = build_fpathPred(idirData, versionData, eta, optionlabelForFile)
            mass_plot = load_bkg_histograms(fpathPred, regionBckg)
            if 'nominal' not in mass_plot:
                sys.exit("Nominal background prediction not found for {}: {}\n"
                         "(check etalabeldir, optionlabel and optionlabelForFile)".format(eta, fpathPred['nominal']))

            # --- DATA of this eta region ---
            # Blinded (default): the nominal background prediction stands in
            # for the data. With --unblind: the observed mass spectrum.
            if unblind:
                if 'obs' not in mass_plot:
                    sys.exit("--unblind: observed mass spectrum not found for {}: {}".format(eta, fpathPred['obs']))
                data_obs = mass_plot['obs']
                if data_obs.Integral() == 0:
                    print("WARNING: --unblind but the observed mass spectrum of {} is empty "
                          "(blinded input file?)".format(eta))
            else:
                data_obs = mass_plot['nominal']

            # --- Mass window, from the nominal signal shape before rebinning ---
            # (see MASS_WINDOW_* above). Used for the cut-and-count datacard
            # and the yield table.
            mean   = sig_nominal.GetMean()
            stddev = sig_nominal.GetStdDev()
            xmin   = max(mean - MASS_WINDOW_NSIGMA_LOW * stddev, MASS_WINDOW_MIN)
            xmax   = mean + MASS_WINDOW_NSIGMA_HIGH * stddev
            # print("Signal: {} ({}); mass range: [{:.1f}, {:.1f}]".format(signal, eta, xmin, xmax))

            # --- Yields in the mass window ---
            signal_yield = integralHisto(sig_nominal, xmin, xmax)
            bkg_yield    = integralHisto(mass_plot['nominal'], xmin, xmax)
            obs_yield    = integralHisto(data_obs, xmin, xmax)

            categories.append({
                'channel'        : chan,
                'eta'            : eta,
                'sig_nominal'    : sig_nominal,
                'sig_variations' : sig_variations,
                'bkg_nominal'    : mass_plot['nominal'],
                'data_obs'       : data_obs,
                'mass_plot'      : mass_plot,
                'signal_yield'   : signal_yield,
                'bkg_yield'      : bkg_yield,
                'obs_yield'      : obs_yield,
                'xmin'           : xmin,
                'xmax'           : xmax,
            })

        # --- ROOT file for Combine (shape mode only) ---
        if not isCutAndCount:
            rootFileName = prepare_shape_rootfile(outDataCardsDir, signal, categories)
        else:
            rootFileName = None

        # --- Datacard (one or two categories) ---
        write_datacard(outDataCardsDir, signal, rootFileName, categories, isCutAndCount)
        yield_rows += collect_yields(signal, categories)

    # --- Yield table, all mass points ---
    write_yield_file(outDataCardsDir + "yields_{}_{}.txt".format(regionBckg, etaLabel), yield_rows)