"""
Lecture des fichiers ROOT produits par combine (AsymptoticLimits)
et tracé de la courbe de limite en section efficace pour la shape
analysis HSCP Run3 Gluino 2024.

Usage:
    python drawtest.py [--unblind] [--debug 1] [--lumi 27.0] [--cac] [--splitEta]
"""

from optparse import OptionParser
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import ROOT
from matplotlib.legend_handler import HandlerTuple

# Police LaTeX (Computer Modern) sans dépendre d'une installation LaTeX
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'TeX Gyre Heros', 'Arial', 'DejaVu Sans'],
    'mathtext.fontset': 'custom',
    'mathtext.rm': 'sans',
    'mathtext.it': 'sans:italic',
    'mathtext.bf': 'sans:bold',
    'mathtext.default': 'regular',
    'axes.formatter.use_mathtext': True,
})

import warnings
warnings.filterwarnings("ignore", message="The value of the smallest subnormal")

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
parser = OptionParser()
parser.add_option('--unblind', action='store_true', default=False, dest='unblind',
                  help='Afficher la limite observée')
parser.add_option('-l', '--lumi', type='string', default='109', dest='lumi',
                  help='Luminosité intégrée en fb-1 (pour le label)')
parser.add_option('-d', '--debug', type='int', default=0, dest='debug',
                  help='Niveau de verbosité')
parser.add_option('--cac', action='store_true', dest='cac', default=False,
                  help='Chose if cut and count method (True) or Shape (False)')
parser.add_option('--splitEta', action='store_true', dest='splitEta', default=False,
                  help='Doit correspondre au meme booleen des scripts de generation/run : '
                       'tracker complet Eta2p4 (False) ou split Eta1/Eta1_2p4 (True).')
parser.add_option('--onlyEta1', action='store_true', dest='onlyEta1', default=False,
                  help='Doit correspondre aux scripts de generation/run : region '
                       'centrale seule |eta|<1 (Eta1).')
parser.add_option('--signal', dest='signal', default='gluino',
                  type='choice', choices=['gluino', 'stop', 'stau'],
                  help='Doit correspondre aux scripts de generation/run.')
(options, args) = parser.parse_args()

isCutAndCount = options.cac
splitEta      = options.splitEta
onlyEta1      = options.onlyEta1
signalType    = options.signal

# ---------------------------------------------------------------------------
# Chemins  —  à adapter si nécessaire
# ---------------------------------------------------------------------------
regionBckg  = '9fp10'
optionlabel = 'SigmaPtoverPt_0p5_EoP_0p1_v2'
etalabeldir = 'Eta2p4'

LIMITS_BASE = '/safe/ui3_1/cms/gcoulon/CMSSW_15_0_13_patch1/src/HSCPLimit/LimitComputation_MassSpectrum/Limits'

# Meme etiquette de dossier que les scripts de generation et de run
if splitEta:
    etaLabel   = 'split_Eta1_' + etalabeldir
    etaDisplay = r'$|\eta|<1$ & $1\leq|\eta|<2.4$'   # joli libelle pour l'annotation
elif onlyEta1:
    etaLabel   = 'Eta1'
    etaDisplay = r'$|\eta|<1$'
else:
    etaLabel   = 'Eta2p4'
    etaDisplay = r'$|\eta|<2.4$'

odir = os.path.join(LIMITS_BASE, signalType, 'limit_shape_{}_{}{}_{}'.format(regionBckg, etaLabel, "_cutandcount" if isCutAndCount else "", optionlabel))

outPlot = os.path.join(odir, 'limits_shape_{}_{}_{}{}_{}.pdf'.format(signalType, regionBckg, etaLabel, "_cutandcount" if isCutAndCount else "", optionlabel))

# ---------------------------------------------------------------------------
# Sections efficaces théoriques NNLO+NNLL
# ---------------------------------------------------------------------------
# { masse_GeV : (xsec_pb, incertitude_relative_%) }
theory_xsec_gluino = {
    1100: (2.450E-01, 0.1007),
    1200: (1.288E-01, 0.1074),
    1300: (6.978E-02, 0.1145),
    1400: (3.883E-02, 0.1231),
    1600: (1.282E-02, 0.1475),
    1800: (4.524E-03, 0.1844),
    2000: (1.684E-03, 0.2432),
    2200: (6.535E-04, 0.3302),
    2400: (2.627E-04, 0.4536),
    2600: (1.089E-04, 0.6161),
}

theory_xsec_stop = {
    700: (9.905000E-02, 0.0640),
    800: (4.193000E-02, 0.0698),
    900: (1.903000E-02, 0.0778),
    1000: (9.123000E-03, 0.0857),
    1200: (2.373000E-03, 0.1076),
    1400: (6.976000E-04, 0.1359),
    1600: (2.236000E-04, 0.1770),
    1800: (7.654000E-05, 0.2332),
    2000: (2.752000E-05, 0.3111),
    2200: (1.029000E-05, 0.4152),
    2400: (3.957000E-06, 0.5556),
    2600: (1.556000E-06, 0.7333),
}

theory_xsec_stau = {
     247: (1.472533E-02, 0.0205),
     308: (6.163604E-03, 0.0221),
     432: (1.474467E-03, 0.0302),
     557: (4.561581E-04, 0.0346),
     651: (2.095727E-04, 0.0370),
     745: (1.036057E-04, 0.0396),
     871: (4.263775E-05, 0.0447),
    1029: (1.526866E-05, 0.0520),
    1218: (4.956323E-06, 0.0616),
    1409: (1.715460E-06, 0.0732),
    1599: (6.262536E-07, 0.0868),
}

SIGNAL_PLOT_CONFIG = {
    'gluino': {
        'label'  : 'Gluino',
        'masses' : [1100, 1200, 1300, 1400, 1600, 1800, 2000, 2200, 2400, 2600],
        'xsec'   : theory_xsec_gluino,
        'xlabel' : r'$m_{\tilde{g}}$ [TeV]',
        'ylim'   : (5e-6, 1.0),
    },
    'stop': {
        'label'  : 'Stop',
        'masses' : [700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600],
        'xsec'   : theory_xsec_stop,
        'xlabel' : r'$m_{\tilde{t}}$ [TeV]',
        'ylim'   : (5e-7, 1.0),
    },
    'stau': {
        'label'  : 'Stau',
        'masses' : [247, 308, 432, 557, 651, 745, 871, 1029, 1218, 1409, 1599],
        'xsec'   : theory_xsec_stau,
        'xlabel' : r'$m_{\tilde{\tau}}$ [TeV]',
        'ylim'   : (1e-7, 1.0),
    },
}

sigCfg      = SIGNAL_PLOT_CONFIG[signalType]
theory_xsec = sigCfg['xsec']          # le reste du script utilise ce nom
samples     = [('{}{}_2024'.format(sigCfg['label'], m), m) for m in sigCfg['masses']]


# ---------------------------------------------------------------------------
# Lecture des fichiers ROOT combine
# ---------------------------------------------------------------------------
masses    = []
exp_m2    = []
exp_m1    = []
exp_med   = []
exp_p1    = []
exp_p2    = []
obs_lim   = []

ROOT.gROOT.SetBatch(True)

for name, mass_gev in samples:
    fname = os.path.join(odir, 'higgsCombine.{}.AsymptoticLimits.mH120.root'.format(name))
    if not os.path.isfile(fname):
        print("WARNING: fichier manquant : {}".format(fname))
        continue

    f = ROOT.TFile.Open(fname)
    tree = f.Get('limit')
    if not tree:
        print("WARNING: TTree 'limit' introuvable dans {}".format(fname))
        f.Close()
        continue

    this_xsec = theory_xsec.get(mass_gev, (1.0, 0.0))[0]
    mass_tev  = mass_gev / 1000.0

    # Quantiles stockés par combine
    quant_map = {}
    for ev in tree:
        q = round(tree.quantileExpected, 3)
        quant_map[q] = tree.limit * this_xsec

    if options.debug > 0:
        print("Mass {} GeV → quantiles : {}".format(mass_gev, quant_map))

    # On vérifie qu'on a bien les 5 quantiles attendus
    if 0.500 not in quant_map:
        print("WARNING: quantile médian manquant pour {}".format(name))
        f.Close()
        continue

    masses.append(mass_tev)
    exp_m2.append(quant_map.get(0.025, np.nan))
    exp_m1.append(quant_map.get(0.160, np.nan))
    exp_med.append(quant_map.get(0.500, np.nan))
    exp_p1.append(quant_map.get(0.840, np.nan))
    exp_p2.append(quant_map.get(0.975, np.nan))

    if options.unblind:
        obs_lim.append(quant_map.get(-1.0, np.nan))  # quantileExpected == -1 → observed

    f.Close()

if len(masses) == 0:
    sys.exit("Aucun point de masse chargé — vérifier le répertoire '{}'.".format(odir))

masses  = np.array(masses)
exp_m2  = np.array(exp_m2)
exp_m1  = np.array(exp_m1)
exp_med = np.array(exp_med)
exp_p1  = np.array(exp_p1)
exp_p2  = np.array(exp_p2)

# Courbe théorique + bande d'incertitude
theory_mass_gev = sorted(theory_xsec)
theory_masses   = np.array(theory_mass_gev) / 1000.0
theory_vals     = np.array([theory_xsec[m][0] for m in theory_mass_gev])
theory_unc      = np.array([theory_xsec[m][1] for m in theory_mass_gev])
theory_up       = theory_vals * (1.0 + theory_unc)
theory_dn       = theory_vals * (1.0 - theory_unc)

# ---------------------------------------------------------------------------
# Plotting — style CMS-like avec matplotlib
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 6))

ax.set_yscale('log')

# Bandes 2σ et 1σ
band95 = ax.fill_between(masses, exp_m2, exp_p2,
                         color='#FFCC00', linewidth=0)
band68 = ax.fill_between(masses, exp_m1, exp_p1,
                         color='#00CC00', linewidth=0)

# Médiane attendue
line_exp, = ax.plot(masses, exp_med, 'k--', linewidth=2)

# Limite observée
line_obs = None
if options.unblind and len(obs_lim) > 0:
    line_obs, = ax.plot(masses, np.array(obs_lim), 'k-', linewidth=2,
                        marker='o', markersize=4)

# Courbe théorique + bande d'incertitude
band_th = ax.fill_between(theory_masses, theory_dn, theory_up,
                          color='royalblue', alpha=0.25, linewidth=0)
line_th, = ax.plot(theory_masses, theory_vals, 'b-', linewidth=2)

# Ligne de masse exclue (intersection médiane × théorie)
# Interpolation log-linéaire pour trouver le croisement
Y_MIN, Y_MAX = sigCfg['ylim']

try:
    log_exp  = np.log(exp_med)
    log_th   = np.interp(masses, theory_masses, np.log(theory_vals))
    diff     = log_exp - log_th
    # Cherche le zéro par signe
    sign_changes = np.where(np.diff(np.sign(diff)))[0]
    if len(sign_changes) > 0:
        i = sign_changes[-1]
        # Interpolation linéaire entre les deux points
        x0, x1 = masses[i], masses[i+1]
        d0, d1 = diff[i], diff[i+1]
        x_cross = x0 - d0 * (x1 - x0) / (d1 - d0)
        y_cross = np.exp(np.interp(x_cross, masses, log_exp))
        ax.vlines(x_cross, Y_MIN, y_cross,
                  color='gray', linestyle=':', linewidth=1.5)
        ax.text(x_cross + 0.02, Y_MIN * 1.5,
                r'$%.2f$ TeV' % x_cross,
                fontsize=12, color='gray', rotation=90, va='bottom')
except Exception as e:
    print("WARNING: calcul d'intersection échoué : {}".format(e))

# Axes
ax.set_xlabel(sigCfg['xlabel'], fontsize=17, labelpad=8, ha='right', x=1.0)
ax.set_ylabel(r'95% CL upper limit on $\sigma$ [pb]', fontsize=17, labelpad=8, ha='right', y=1.0)
ax.set_xlim(masses[0] - 0.05, masses[-1] + 0.1)
ax.set_ylim(Y_MIN, Y_MAX)
ax.tick_params(axis='both', which='both', direction='in',
               top=True, right=True, labelsize=14)

# Légende
handles = [line_exp]
labels  = ['Expected']

if line_obs is not None:
    handles.append(line_obs)
    labels.append('Observed')

handles += [band68, band95, (line_th, band_th)]
labels  += [r'$\pm 68\%$',
            r'$\pm 95\%$',
            r'$\sigma^{\mathrm{NNLO+NNLL}}_{\mathrm{th}} \pm 1\sigma_{\mathrm{th}}$']

ax.legend(handles, labels, loc='upper right', fontsize=14,
          frameon=True, framealpha=0.9,
          handler_map={tuple: HandlerTuple(ndivide=1)})

# Labels CMS
ax.text(0, 1.04, r'$\mathit{Private\ Work\ (CMS\ data)}$',
            transform=ax.transAxes, fontsize=16, verticalalignment='top')
ax.text(1, 1.05, r'109 fb$^{-1}$ (13.6 TeV)',
            transform=ax.transAxes, fontsize=16,
            verticalalignment='top', horizontalalignment='right')

# Annotation shape analysis
ax.text(0.03, 0.09,
        ('cut-and-count method' if isCutAndCount else 'shape analysis'),
        transform=ax.transAxes, fontsize=16, va='bottom',fontweight='bold')
ax.text(0.03, 0.03,
        etaDisplay,
        transform=ax.transAxes, fontsize=16, va='bottom',fontweight='bold')

fig.tight_layout()
fig.savefig(outPlot, dpi=150, bbox_inches='tight')
print("Plot saved: {}".format(outPlot))

# Sauvegarde texte des valeurs
txt_out = outPlot.replace('.pdf', '.txt')
with open(txt_out, 'w') as f:
    header = '# mass_TeV  exp_m2sigma  exp_m1sigma  exp_median  exp_p1sigma  exp_p2sigma'
    if options.unblind:
        header += '  observed'
    f.write(header + '\n')
    for i, m in enumerate(masses):
        line = '{:.3f}  {:.6e}  {:.6e}  {:.6e}  {:.6e}  {:.6e}'.format(
            m, exp_m2[i], exp_m1[i], exp_med[i], exp_p1[i], exp_p2[i])
        if options.unblind and len(obs_lim) > i:
            line += '  {:.6e}'.format(obs_lim[i])
        f.write(line + '\n')
print("Valeurs sauvegardées : {}".format(txt_out))