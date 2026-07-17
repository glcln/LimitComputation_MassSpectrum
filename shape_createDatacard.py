from optparse import OptionParser
import ROOT as rt
import sys
import os
import array
from collections import OrderedDict

rt.gROOT.SetBatch(True)

# Binning commun impose a tous les histos ecrits dans le .root Combine
REBINNING = array.array('d', [
    0., 20., 40., 60., 80., 100., 120., 140., 160., 180., 200.,
    220., 240., 260., 280., 300., 320., 340., 360., 380., 410.,
    440., 480., 530., 590., 660., 760., 880., 1030., 1210., 1440.,
    1730., 2000., 2500., 3200., 4000.,
])

# ---------------------------------------------------------------------------
## SETUP
# ---------------------------------------------------------------------------
parser = OptionParser()
parser.add_option('--cac', action='store_true', dest='cac', default=False,
                  help='Chose if cut and count method (True) or Shape (False)')
parser.add_option('--splitEta', action='store_true', dest='splitEta', default=False,
                  help='Decoupe le tracker en deux categories : central |eta|<1 (Eta1) et '
                       'forward 1<|eta|<2.4 (Eta1_2p4) (True), sinon tracker complet |eta|<2.4 '
                       '(Eta2p4) (False).')
parser.add_option('--onlyEta1', action='store_true', dest='onlyEta1', default=False,
                  help='Datacard avec uniquement la region centrale |eta|<1 (Eta1).')
(options, args) = parser.parse_args()

isCutAndCount = options.cac
splitEta      = options.splitEta
onlyEta1      = options.onlyEta1

# Mapping entre clés fpathPred et noms de systematics Combine (paires Up/Down)
BKG_SYST_MAP = {
    'eta'            : ('etaUp',    'etaDown'),
    'ih'             : ('ihUp',     'ihDown'),
    'mom'            : ('momUp',    'momDown'),
    'fitIh'          : ('fitihUp',  'fitihDown'),
    'fitMom'         : ('fitmomUp', 'fitmomDown'),
    #'nofit'          : ('nofit',    'nofit'),   # Up=Down=nofit (variation one-sided)
    'corrTemplateIh' : ('corrTemplateIh', 'corrTemplateIh'),  # Up=Down=corrTemplateIh (one-sided)
}

SIG_ONLY_SYSTS = {'PU', 'TriggerSF', 'K', 'C', 'Fpix', 'Jet'}

# Base du nom des histogrammes signal ; l'etiquette eta est ajoutee ensuite
# (ex : METanalysis_PseudoMETrescaled_Eta1, ..._Eta1_2p4, ..._Eta2p4)
SIG_LABEL_BASE = "METanalysis_TestPUppiMETCut_"

# --- Schema de correlation entre les deux categories eta (mode splitEta) ---
# Tout systematic NON liste ici est CORRELE entre les deux categories : un seul
# nuisance partage (meme nom dans les deux canaux).
# Tout systematic liste ici est DECORRELE : un nuisance par categorie, nomme
# <syst>_<eta> (ex: K_Eta1 et K_Eta1_2p4), comme dans l'ancien decoupage par annee.
# N'a aucun effet en mode tracker complet (un seul canal).
# Exemple suivant la convention de l'ancien decoupage par annee :
#   DECORRELATED_SYSTS = {'K', 'C', 'Fpix', 'fitIh', 'fitMom'}
DECORRELATED_SYSTS = set()


# ---------------------------------------------------------------------------
## FUNCTIONS
# ---------------------------------------------------------------------------
def integralHisto(h, xmin, xmax):
    return h.Integral(h.FindBin(xmin), h.FindBin(xmax))


def get_signal_systematics(root_path, label, fp_cut="9fp10"):
    """
    Load nominal and systematic histograms from a ROOT file.

    `label` contient deja l'etiquette eta, p.ex. :
        METanalysis_PseudoMETrescaled_Eta1
        METanalysis_PseudoMETrescaled_Eta1_2p4
        METanalysis_PseudoMETrescaled_Eta2p4

    Returns
    -------
    nominal : TH1
        The nominal histogram.
    systematics : dict
        Dictionary of {syst_name: TH1} for each systematic variation.
    """

    syst_names = [
        "PUUp", "PUDown",
        "TriggerSFUp", "TriggerSFDown",
        "KUp", "KDown",
        "CUp", "CDown",
        "FpixUp", "FpixDown",
        "JetUp", "JetDown",
    ]

    f = rt.TFile.Open(root_path, "READ")
    if not f or f.IsZombie():
        raise IOError(f"Cannot open ROOT file: {root_path}")

    base = f"{label}_{fp_cut}_SignalMass"

    nominal = f.Get(f"{base}_nominal")
    if not nominal:
        f.Close()
        raise KeyError(f"Histogram not found: {base}_nominal")
    nominal.SetDirectory(0)  # detach from file

    systematics = {}
    for syst in syst_names:
        h = f.Get(f"{base}_{syst}")
        if not h:
            print(f"Warning: histogram not found: {base}_{syst}")
            systematics[syst] = None
        else:
            h.SetDirectory(0)
            systematics[syst] = h

    f.Close()
    return nominal, systematics


def build_fpathPred(idirData, versionData, eta):
    """
    Construit le dictionnaire des chemins de fichiers de prediction bkg pour
    une region eta donnee ('Eta1', 'Eta1_2p4' ou 'Eta2p4').

    C'est ici que l'etiquette `end = '_<eta>_NewFit'` est injectee dans tous
    les noms de fichiers (et `'_<eta>_NoFit'` pour la variation nofit).
    """
    base = idirData + 'JetMET2024_V' + versionData
    end  = '_' + eta + '_OldFit_IhC'
    fpathPred = {
        'obs'            : base + '_rebinEta4_rebinIh4_rebinP2_EtaReweighting' + end + '.root',
        'nominal'        : base + '_rebinEta4_rebinIh4_rebinP2_EtaReweighting' + end + '.root',
        'etaUp'          : base + '_rebinEta2_rebinIh4_rebinP2_EtaReweighting' + end + '.root',
        'etaDown'        : base + '_rebinEta8_rebinIh4_rebinP2_EtaReweighting' + end + '.root',
        'ihUp'           : base + '_rebinEta4_rebinIh2_rebinP2_EtaReweighting' + end + '.root',
        'ihDown'         : base + '_rebinEta4_rebinIh8_rebinP2_EtaReweighting' + end + '.root',
        'momUp'          : base + '_rebinEta4_rebinIh4_rebinP1_EtaReweighting' + end + '.root',
        'momDown'        : base + '_rebinEta4_rebinIh4_rebinP4_EtaReweighting' + end + '.root',
        'fitihUp'        : base + '_rebinEta4_rebinIh4_rebinP2_fitIhUp_EtaReweighting' + end + '.root',
        'fitihDown'      : base + '_rebinEta4_rebinIh4_rebinP2_fitIhDown_EtaReweighting' + end + '.root',
        'fitmomUp'       : base + '_rebinEta4_rebinIh4_rebinP2_fitPUp_EtaReweighting' + end + '.root',
        'fitmomDown'     : base + '_rebinEta4_rebinIh4_rebinP2_fitPDown_EtaReweighting' + end + '.root',
        #'nofit'          : base + '_rebinEta4_rebinIh4_rebinP2_EtaReweighting' + '_' + eta + '_NoFit_IhC' + '.root',
        'corrTemplateIh' : base + '_rebinEta4_rebinIh4_rebinP2_corrTemplateIh_EtaReweighting' + end + '.root',
    }
    return fpathPred


def load_bkg_histograms(fpathPred, regionBckg, channel="Ch2024"):
    """
    Ouvre chaque fichier ROOT de prediction bkg et recupere le bon histogramme.

    fpathPred : dict { 'nominal': path, 'etaUp': path, 'etaDown': path, ... }

    Retourne:
        mass_plot : dict { 'nominal': TH1, 'etaUp': TH1, ... }
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
    Construit le fichier ROOT attendu par la datacard Combine.

    `categories` est une liste de dict (un par categorie eta). Chaque dict doit
    contenir : 'channel', 'sig_nominal', 'sig_variations', 'bkg_nominal',
    'mass_plot'.

    Pour chaque canal :
      - signal_<chan>, background_<chan>, data_obs_<chan>
      - signal_<chan>_<syst> pour chaque systematic signal
      - background_<chan>_<syst>Up/Down pour chaque systematic bkg
      - fallback signal sur le nominal pour les systs bkg sans contrepartie signal
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

        # Signal nominal
        _rebin(sig_nominal, "signal_{}".format(chan)).Write()

        # Bkg nominal + data_obs
        _rebin(bkg_nominal, "background_{}".format(chan)).Write()
        _rebin(bkg_nominal, "data_obs_{}".format(chan)).Write()

        # Systematics signal : PU, TriggerSF, K, C, Fpix
        for sysName, h_var in sig_variations.items():
            if h_var is not None:
                _rebin(h_var, "signal_{}_{}".format(chan, sysName)).Write()

        # Systematics bkg + fallback signal pour systs bkg-only
        for systCombName, (keyUp, keyDown) in BKG_SYST_MAP.items():
            h_bkg_up = mass_plot.get(keyUp)
            if h_bkg_up:
                _rebin(h_bkg_up, "background_{}_{}Up".format(chan, systCombName)).Write()
            h_bkg_down = mass_plot.get(keyDown)
            if h_bkg_down:
                _rebin(h_bkg_down, "background_{}_{}Down".format(chan, systCombName)).Write()

            syst_up_name   = "{}Up".format(systCombName)
            syst_down_name = "{}Down".format(systCombName)
            if syst_up_name not in sig_variations or sig_variations.get(syst_up_name) is None:
                _rebin(sig_nominal, "signal_{}_{}Up".format(chan, systCombName)).Write()
            if syst_down_name not in sig_variations or sig_variations.get(syst_down_name) is None:
                _rebin(sig_nominal, "signal_{}_{}Down".format(chan, systCombName)).Write()

    f.Close()
    print("ROOT file written: {}".format(rootFileName))
    return rootFileName


def _rebin(h, newname):
    """
    Rebinne h selon REBINNING et renvoie un clone detache portant `newname`.
    Le dernier argument de Rebin est le tableau de bords variables ; le nombre
    de nouveaux bins est len(REBINNING)-1.
    """
    h_re = h.Rebin(len(REBINNING) - 1, newname, REBINNING)
    h_re.SetDirectory(0)
    return h_re


# --- petits helpers pour la datacard -----------------------------------------
def _sig_bases(sig_variations):
    """Retourne l'ensemble des bases de systematics signal (sans Up/Down)."""
    bases = set()
    for key in sig_variations:
        if key.endswith('Up'):
            bases.add(key[:-len('Up')])
        elif key.endswith('Down'):
            bases.add(key[:-len('Down')])
    return bases


def _row(categories, present_channels, process):
    """
    Construit la liste des 2N colonnes (signal, background) pour une ligne de
    systematic. `process` vaut 'signal', 'background' ou 'both'.
    Une colonne vaut '1.0' si le canal est dans `present_channels` et que le
    process correspond, sinon '-'.
    """
    cols = []
    for cat in categories:
        s, b = '-', '-'
        if cat['channel'] in present_channels:
            if process in ('signal', 'both'):
                s = '1.0'
            if process in ('background', 'both'):
                b = '1.0'
        cols.extend([s, b])
    return cols


def _lnN_factor(cat, base, process):
    """
    Calcule le facteur lnN cut-and-count pour un systematic `base` dans une
    categorie donnee, en integrant les histos de variation sur la fenetre
    [xmin, xmax] et en normalisant au nominal.

    Retourne :
        None             -> systematic absent pour ce process/categorie ('-')
        (down, up)       -> systematic deux cotes (signal)
        valeur unique    -> systematic one-sided (bkg : nofit)
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
            # one-sided (ex: nofit) -> facteur unique, convention ancienne
            return up
        # deux cotes -> on combine en un facteur symetrique comme l'ancien script
        return max(abs(1 - dn), abs(1 - up)) + 1
    

def _fmt_lnN(val):
    """Met en forme une valeur lnN pour une colonne de datacard."""
    if val is None:
        return '-'
    if isinstance(val, tuple):
        return '{}/{}'.format(val[0], val[1])
    return str(val)


def MakeDatacard_Shape(outDataCardsDir, modelName, rootFileName, categories,
                       isCutAndCount_=False, thresh=10):
    """
    Ecrit la datacard Combine pour une (tracker complet) ou deux (split eta)
    categories.

    `categories` : liste de dict, un par categorie, contenant au moins :
        'channel'        : nom du bin Combine (ex: 'Ch2024' ou 'Ch2024_Eta1')
        'eta'            : etiquette eta ('Eta1', 'Eta1_2p4', 'Eta2p4')
        'sig_variations' : dict {systUp/Down: TH1 or None}
        'mass_plot'      : dict des histos bkg (cles de fpathPred)
        'signal_yield', 'bkg_yield', 'obs_yield' : floats (cut & count)

    En mode multi-categories, les colonnes sont ordonnees :
        [ (chan0,signal), (chan0,bkg), (chan1,signal), (chan1,bkg), ... ]
    """
    nChan    = len(categories)
    channels = [cat['channel'] for cat in categories]

    # --- Systematics signal reellement presents (Up ET Down), par canal ---
    sig_present = {}   # base -> set(channels)
    for cat in categories:
        chan = cat['channel']
        sv   = cat['sig_variations']
        for base in _sig_bases(sv):
            if sv.get(base + 'Up') is not None and sv.get(base + 'Down') is not None:
                sig_present.setdefault(base, set()).add(chan)

    # --- Systematics bkg presents (Up ET Down ecrits), par canal ---
    bkg_present = {}   # base -> set(channels)
    for cat in categories:
        chan = cat['channel']
        mp   = cat['mass_plot']
        for base, (keyUp, keyDown) in BKG_SYST_MAP.items():
            if mp.get(keyUp) is not None and mp.get(keyDown) is not None:
                bkg_present.setdefault(base, set()).add(chan)

    endname = "_cutandcount" if isCutAndCount_ else ""
    outPath = outDataCardsDir + modelName + endname + ".txt"
    text_file = open(outPath, "w")

    # --- en-tete ---
    text_file.write('imax {} \n'.format(nChan))
    text_file.write('jmax 1 \n')
    text_file.write('kmax * \n')

    if isCutAndCount_:
        text_file.write('shapes * * FAKE  \n')
    text_file.write('--------------- \n')
    if not isCutAndCount_:
        text_file.write('shapes * * {} $PROCESS_$CHANNEL $PROCESS_$CHANNEL_$SYSTEMATIC \n'.format(rootFileName))
    text_file.write('--------------- \n')

    # --- bin / observation ---
    text_file.write('bin \t ' + ' \t '.join(channels) + ' \n')
    if isCutAndCount_:
        obs = [str(cat['obs_yield']) for cat in categories]
        text_file.write('observation \t ' + ' \t '.join(obs) + ' \n')
    else:
        text_file.write('observation \t ' + ' \t '.join(['-1'] * nChan) + ' \n')
    text_file.write('------------------------------ \n')

    # --- bin (x2) / process / rate ---
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

    systType = 'lnN' if isCutAndCount_ else 'shape'

    # --- lumi : correle (meme periode de prise de donnees), signal seulement ---
    lumi_cols = []
    for cat in categories:
        lumi_cols += ['1.014', '-']
    text_file.write('lumi \t lnN \t ' + ' \t '.join(lumi_cols) + ' \n')

    # --- ecriture d'un systematic (correle ou decorrele) ---
    def write_syst(base, present, process):
        # Lignes decorrelees (un nuisance par categorie)
        if base in DECORRELATED_SYSTS and nChan > 1:
            for cat in categories:
                if cat['channel'] not in present:
                    continue
                name = '{}_{}'.format(base, cat['eta'])
                if isCutAndCount_:
                    cols = []
                    for c in categories:
                        if c['channel'] == cat['channel']:
                            f = _lnN_factor(c, base, process)
                            s = _fmt_lnN(f) if process == 'signal' else '-'
                            b = _fmt_lnN(f) if process == 'background' else '-'
                            cols.extend([s, b])
                        else:
                            cols.extend(['-', '-'])
                else:
                    cols = _row(categories, {cat['channel']}, process)
                text_file.write('{} \t {} \t '.format(name, systType) + ' \t '.join(cols) + ' \n')
            return

        # Ligne correlee (un seul nuisance)
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

    # Systematics signal (PU, TriggerSF, K, C, Fpix)
    for base in sorted(sig_present):
        write_syst(base, sig_present[base], 'signal')
    # Systematics bkg (eta, ih, mom, fitIh, fitMom, nofit)
    for base in sorted(bkg_present):
        write_syst(base, bkg_present[base], 'background')

    # --- rateParam + autoMCStats (shape uniquement), par canal ---
    if not isCutAndCount_:
        for cat in categories:
            # une normalisation libre par categorie (decorrelee entre les regions eta)
            rp = 'rateAll' if nChan == 1 else 'rateAll_{}'.format(cat['eta'])
            text_file.write('{} rateParam {} background 1.0 \n'.format(rp, cat['channel']))
        for cat in categories:
            text_file.write('{} autoMCStats {} \n'.format(cat['channel'], thresh))

    text_file.close()
    print("Datacard written: {}".format(outPath))


if __name__ == '__main__':

    # --- SETUP ---
    versionData   = '12p31'
    versionSignal = '19p8'
    regionBckg    = '9fp10'
    channel       = 'Ch2024'
    
    etalabeldir = 'Eta1_2p4'
    optionlabel = 'etaRebinPerso_Oldfit__PUppiMETcut'
    idirData    = '/safe/ui3_1/cms/gcoulon/CMSSW_15_0_13_patch1/src/TupleAnalysis/macros/DataMET_2024_V' + versionData + '__' + regionBckg + '_' + optionlabel + '/' + etalabeldir + '/'
    

    # --- Regions eta selon le booleen ---
    if splitEta:
        etaRegions = ['Eta1', etalabeldir]    # central |eta|<1 , forward 1<|eta|<2.4
        etaLabel   = 'split_Eta1_' + etalabeldir
    elif onlyEta1:
        etaRegions = ['Eta1']                # region centrale seule |eta|<1
        etaLabel   = 'Eta1'
    else:
        etaRegions = ['Eta2p4']              # tracker complet |eta|<2.4
        etaLabel   = 'Eta2p4'

    outDataCardsDir = "MyNewDataCards/datacards_shape_{}_{}_{}/".format(regionBckg, etaLabel, optionlabel)
    os.makedirs(outDataCardsDir, exist_ok=True)

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

    # --- SIGNAL ---
    baseSignal = '/safe/ui3_1/cms/gcoulon/CMSSW_15_0_13_patch1/src/TupleAnalysis/output/Gluino_V19/'
    fpath = {
        'Gluino1100_2024': baseSignal + 'Gluino_Run3_MET_madgraph_1100_V' + versionSignal + '_weighted.root',
        'Gluino1200_2024': baseSignal + 'Gluino_Run3_MET_madgraph_1200_V' + versionSignal + '_weighted.root',
        'Gluino1300_2024': baseSignal + 'Gluino_Run3_MET_madgraph_1300_V' + versionSignal + '_weighted.root',
        'Gluino1400_2024': baseSignal + 'Gluino_Run3_MET_madgraph_1400_V' + versionSignal + '_weighted.root',
        'Gluino1600_2024': baseSignal + 'Gluino_Run3_MET_madgraph_1600_V' + versionSignal + '_weighted.root',
        'Gluino1800_2024': baseSignal + 'Gluino_Run3_MET_madgraph_1800_V' + versionSignal + '_weighted.root',
        'Gluino2000_2024': baseSignal + 'Gluino_Run3_MET_madgraph_2000_V' + versionSignal + '_weighted.root',
        'Gluino2200_2024': baseSignal + 'Gluino_Run3_MET_madgraph_2200_V' + versionSignal + '_weighted.root',
        'Gluino2400_2024': baseSignal + 'Gluino_Run3_MET_madgraph_2400_V' + versionSignal + '_weighted.root',
        'Gluino2600_2024': baseSignal + 'Gluino_Run3_MET_madgraph_2600_V' + versionSignal + '_weighted.root'
    }

    # --- BOUCLE SUR LES SIGNAUX ---
    for signal, sig_path in fpath.items():

        # Pour chaque signal on construit la liste des categories (1 ou 2)
        categories = []
        for eta in etaRegions:

            # Nom du canal Combine pour cette categorie
            chan = "{}_{}".format(channel, eta) if eta != 'Eta2p4' else channel

            # --- SIGNAL pour cette region eta ---
            # le label porte l'etiquette eta : ..._Eta1, ..._Eta1_2p4, ..._Eta2p4
            
            #TEMPORARY
            sig_label = SIG_LABEL_BASE + eta
            #sig_label = SIG_LABEL_BASE + eta.replace('Eta1p2', 'Eta1', 1)
            #TEMPORARY
            
            sig_nominal, sig_variations = get_signal_systematics(sig_path, sig_label, regionBckg)

            # --- BKG pour cette region eta (chemins propres a l'eta) ---
            fpathPred = build_fpathPred(idirData, versionData, eta)
            mass_plot = load_bkg_histograms(fpathPred, regionBckg, channel)

            # --- Fenetre en masse sur le signal nominal ---
            mean   = sig_nominal.GetMean()
            stddev = sig_nominal.GetStdDev()
            xmin   = max(mean - stddev, 300)
            xmax   = mean + 2 * stddev
            # print("Signal: {} ({}); mass range: [{:.1f}, {:.1f}]".format(signal, eta, xmin, xmax))

            # --- Integrales dans la fenetre ---
            signal_yield = integralHisto(sig_nominal, xmin, xmax)
            bkg_yield    = integralHisto(mass_plot['nominal'], xmin, xmax)
            # obs_yield  = integralHisto(mass_plot['obs'],     xmin, xmax)
            obs_yield    = integralHisto(mass_plot['nominal'], xmin, xmax)

            categories.append({
                'channel'        : chan,
                'eta'            : eta,
                'sig_nominal'    : sig_nominal,
                'sig_variations' : sig_variations,
                'bkg_nominal'    : mass_plot['nominal'],
                'mass_plot'      : mass_plot,
                'signal_yield'   : signal_yield,
                'bkg_yield'      : bkg_yield,
                'obs_yield'      : obs_yield,
                'xmin'           : xmin,
                'xmax'           : xmax,
            })

       # --- Fichier ROOT pour Combine (shape uniquement) ---
        if not isCutAndCount:
            rootFileName = prepare_shape_rootfile(outDataCardsDir, signal, categories)
        else:
            rootFileName = "FAKE"   # non utilise en cut-and-count, juste pour la signature

        # --- Datacard (1 ou 2 categories) ---
        MakeDatacard_Shape(
            outDataCardsDir, signal, rootFileName, categories,
            isCutAndCount
        )
