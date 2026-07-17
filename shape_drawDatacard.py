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

# Police LaTeX (Computer Modern) sans dépendre d'une installation LaTeX
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['cmr10', 'Computer Modern Roman', 'DejaVu Serif'],
    'mathtext.fontset': 'cm',
    'axes.formatter.use_mathtext': True,   # évite le warning cmr10 sur le signe moins
})

import warnings
warnings.filterwarnings("ignore", message="The value of the smallest subnormal")

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
parser = OptionParser()
parser.add_option('--unblind', action='store_true', default=False, dest='unblind',
                  help='Afficher la limite observée')
parser.add_option('-l', '--lumi', type='string', default='105.8', dest='lumi',
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
(options, args) = parser.parse_args()

isCutAndCount = options.cac
splitEta      = options.splitEta
onlyEta1 = options.onlyEta1

# ---------------------------------------------------------------------------
# Chemins  —  à adapter si nécessaire
# ---------------------------------------------------------------------------
regionBckg  = '9fp10'
optionlabel = 'etaRebinPerso_Oldfit__PUppiMETcut'
etalabeldir = 'Eta1_2p4'

# Meme etiquette de dossier que les scripts de generation et de run
if splitEta:
    etaLabel   = 'split_Eta1_' + etalabeldir
    etaDisplay = r'$|\eta|<1$ + $1<|\eta|<2.4$'   # joli libelle pour l'annotation
elif onlyEta1:
    etaLabel   = 'Eta1'
    etaDisplay = r'$|\eta|<1$'
else:
    etaLabel   = 'Eta2p4'
    etaDisplay = r'$|\eta|<2.4$'

odir = 'MyNewDataCards/limit_shape_{}_{}'.format(regionBckg, etaLabel) + ("_cutandcount" if isCutAndCount else "") + '_' + optionlabel
outPlot = os.path.join(odir, 'limits_shape_{}_{}'.format(regionBckg, etaLabel) + ("_cutandcount" if isCutAndCount else "") + '_' + optionlabel + '.pdf')


# Masse en GeV → sera convertie en TeV pour l'axe X
samples = [
    ('Gluino1100_2024', 1100),
    ('Gluino1200_2024', 1200),
    ('Gluino1300_2024', 1300),
    ('Gluino1400_2024', 1400),
    ('Gluino1600_2024', 1600),
    ('Gluino1800_2024', 1800),
    ('Gluino2000_2024', 2000),
    ('Gluino2200_2024', 2200),
    ('Gluino2400_2024', 2400),
    ('Gluino2600_2024', 2600),
]

# ---------------------------------------------------------------------------
# Sections efficaces théoriques NNLO+NNLL gluino (pb) + incertitudes relatives
# ---------------------------------------------------------------------------
# { masse_GeV : (xsec_pb, incertitude_relative_%) }
theory_xsec = {
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
theory_masses = np.array(sorted(theory_xsec.keys())) / 1000.0
theory_vals   = np.array([theory_xsec[int(m * 1000)][0] for m in theory_masses])
theory_unc    = np.array([theory_xsec[int(m * 1000)][1] for m in theory_masses])
theory_up     = theory_vals * (1.0 + theory_unc)
theory_dn     = theory_vals * (1.0 - theory_unc)

# ---------------------------------------------------------------------------
# Plotting — style CMS-like avec matplotlib
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 6))

ax.set_yscale('log')

# Bandes 2σ et 1σ
ax.fill_between(masses, exp_m2, exp_p2,
                color='#FFCC00', label=r'Expected $\pm 2\sigma$', linewidth=0)
ax.fill_between(masses, exp_m1, exp_p1,
                color='#00CC00', label=r'Expected $\pm 1\sigma$', linewidth=0)

# Médiane attendue
ax.plot(masses, exp_med, 'k--', linewidth=2, label='Expected limit (median)')

# Limite observée
if options.unblind and len(obs_lim) > 0:
    ax.plot(masses, np.array(obs_lim), 'k-', linewidth=2, marker='o',
            markersize=4, label='Observed limit')

# Courbe théorique + bande d'incertitude
ax.fill_between(theory_masses, theory_dn, theory_up,
                color='royalblue', alpha=0.25, linewidth=0,
                label=r'$\sigma^{\mathrm{NNLO+NNLL}}_{\mathrm{th}} \pm 1\sigma_{\mathrm{th}}$')
ax.plot(theory_masses, theory_vals, 'b-', linewidth=2)

# Ligne de masse exclue (intersection médiane × théorie)
# Interpolation log-linéaire pour trouver le croisement
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
        ax.axvline(x_cross, color='gray', linestyle=':', linewidth=1.5)
        ax.text(x_cross + 0.02, y_cross * 1.5,
                r'$m_{\tilde{g}} = %.2f$ TeV' % x_cross,
                fontsize=9, color='gray', rotation=90, va='bottom')
except Exception as e:
    print("WARNING: calcul d'intersection échoué : {}".format(e))

# Axes
ax.set_xlabel(r'$m_{\tilde{g}}$ [TeV]', fontsize=13, labelpad=8)
ax.set_ylabel(r'95% CL upper limit on $\sigma$ [pb]', fontsize=13, labelpad=8)
ax.set_xlim(masses[0] - 0.05, masses[-1] + 0.1)
ax.set_ylim(5e-6, 1.0)
ax.tick_params(axis='both', which='both', direction='in',
               top=True, right=True, labelsize=11)

# Légende
ax.legend(loc='upper right', fontsize=10, frameon=True, framealpha=0.9)

# Labels CMS
ax.text(0.01, 1.02, r'$\bf{CMS}$' + r' $\it{Preliminary}$',
        transform=ax.transAxes, fontsize=13, va='bottom')
ax.text(0.99, 1.02,
        r'$\sqrt{s} = 13.6\ \mathrm{TeV},\ ' + options.lumi + r'\ \mathrm{fb}^{-1}$',
        transform=ax.transAxes, fontsize=11, va='bottom', ha='right')

# Annotation shape analysis
ax.text(0.03, 0.05,
        ('Cut and Count method - ' if isCutAndCount else 'Shape Analysis - ') + regionBckg + ' (' + etaDisplay + ')\n'
        r'$pp \rightarrow \tilde{g}\tilde{g}$, stable gluino (R-hadron)',
        transform=ax.transAxes, fontsize=9, va='bottom',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

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