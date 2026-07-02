#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plot la limite attendue mediane (exp_median) issue de plusieurs fichiers .txt
sur un meme graphique, et superpose la section efficace theorique NNLO+NNLL
avec sa bande d'incertitude.

Format attendu des fichiers .txt :
# mass_TeV  exp_m2sigma  exp_m1sigma  exp_median  exp_p1sigma  exp_p2sigma
1.100  7.205280e-04  ...  1.618028e-03  ...  ...
"""

import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Police LaTeX (Computer Modern) sans dépendre d'une installation LaTeX
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['cmr10', 'Computer Modern Roman', 'DejaVu Serif'],
    'mathtext.fontset': 'cm',
    'axes.formatter.use_mathtext': True,   # évite le warning cmr10 sur le signe moins
})

import warnings
warnings.filterwarnings("ignore", message="The value of the smallest subnormal")

#etalabel = "Eta1" 
#etalabel = "split_Eta1_Eta1_2p4"
etalabel = "Eta2p4"

etalabel2 = "split_Eta1_Eta1p2_2p2"
etalabel3 = "split_Eta1_Eta1p2_2p4"



INPUT_FILES = [
    ("MyNewDataCards/limit_shape_9fp10_" + etalabel + "_cutandcount/limits_shape_9fp10_" + etalabel + "_cutandcount.txt", r"standard"),
    ("MyNewDataCards/limit_shape_9fp10_" + etalabel + "_cutandcount_etaAbs/limits_shape_9fp10_" + etalabel + "_cutandcount_etaAbs.txt", r"$|\eta|$"),
    ("MyNewDataCards/limit_shape_9fp10_" + etalabel + "_cutandcount_etaAbs_etaRebinPerso/limits_shape_9fp10_" + etalabel + "_cutandcount_etaAbs_etaRebinPerso.txt", r"$|\eta| + \eta_{\mathrm{rebin}}$"),
    ("MyNewDataCards/limit_shape_9fp10_" + etalabel + "_cutandcount_etaAbs_etaRebinPerso_1oPRebinBig/limits_shape_9fp10_" + etalabel + "_cutandcount_etaAbs_etaRebinPerso_1oPRebinBig.txt", r"$|\eta| + \eta_{\mathrm{rebin}} + 1/p_{\mathrm{rebin}}$"),
    ("MyNewDataCards/limit_shape_9fp10_" + etalabel + "_cutandcount_etaAbs_etaRebinPerso_1oPRebinBig_Oldfit/limits_shape_9fp10_" + etalabel + "_cutandcount_etaAbs_etaRebinPerso_1oPRebinBig_Oldfit.txt", r"$|\eta| + \eta_{\mathrm{rebin}} + 1/p_{\mathrm{rebin, old fit}}$"),
    
    #("MyNewDataCards/limit_shape_9fp10_" + etalabel2 + "_cutandcount_etaAbs_etaRebinPerso_1oPRebinBig_Oldfit_EtaCategory/limits_shape_9fp10_" + etalabel2 + "_cutandcount_etaAbs_etaRebinPerso_1oPRebinBig_Oldfit_EtaCategory.txt", r"$|\eta| + \eta_{\mathrm{rebin}} + 1/p_{\mathrm{rebin, old fit}} + 1.2<|\eta_\mathrm{cat.}|<2.2$"),
    #("MyNewDataCards/limit_shape_9fp10_" + etalabel3 + "_cutandcount_etaAbs_etaRebinPerso_1oPRebinBig_Oldfit_EtaCategory/limits_shape_9fp10_" + etalabel3 + "_cutandcount_etaAbs_etaRebinPerso_1oPRebinBig_Oldfit_EtaCategory.txt", r"$|\eta| + \eta_{\mathrm{rebin}} + 1/p_{\mathrm{rebin, old fit}} + 1.2<|\eta_\mathrm{cat.}|<2.4$"),
]

# ---------------------------------------------------------------------------
# A EDITER : sortie et titre
# ---------------------------------------------------------------------------
OUTPUT = "ExpectedCompare_" + etalabel + ".pdf"
TITLE  = r"Expected median limits -- gluino R-hadron, 2024" 

# ---------------------------------------------------------------------------
# Section efficace theorique : masse_GeV -> (xsec_pb, incertitude_relative)
# ---------------------------------------------------------------------------
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
# Plotting — style CMS-like avec matplotlib
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_yscale('log')

colors  = ['black', 'red', 'green', 'orange', 'purple', 'cyan', 'magenta', 'brown', 'olive', 'teal']
markers = ['o', 's', '^', 'v', 'D', 'P', 'X', '*', '<', '>']

for i, (fname, label) in enumerate(INPUT_FILES):
    if not os.path.isfile(fname):
        print("WARNING: fichier manquant : {}".format(fname))
        continue

    # Colonne 0 = mass_TeV, colonne 3 = exp_median
    data = np.loadtxt(fname, comments='#')
    if data.ndim == 1:
        data = data.reshape(1, -1)

    masses  = data[:, 0]
    exp_med = data[:, 3]

    order   = np.argsort(masses)
    masses  = masses[order]
    exp_med = exp_med[order]

    ax.plot(masses, exp_med,
            linestyle='--', linewidth=2,
            marker=markers[i % len(markers)], markersize=5,
            color=colors[i], label=label)

# ---------------------------------------------------------------------------
# Section efficace theorique + bande d'incertitude (toujours tracee)
# ---------------------------------------------------------------------------
theory_masses = np.array(sorted(theory_xsec.keys())) / 1000.0
theory_vals   = np.array([theory_xsec[int(m * 1000)][0] for m in theory_masses])
theory_unc    = np.array([theory_xsec[int(m * 1000)][1] for m in theory_masses])
theory_up     = theory_vals * (1.0 + theory_unc)
theory_dn     = theory_vals * (1.0 - theory_unc)

ax.fill_between(theory_masses, theory_dn, theory_up,
                color='royalblue', alpha=0.25, linewidth=0,
                label=r'$\sigma^{\mathrm{NNLO+NNLL}}_{\mathrm{th}} \pm 1\sigma_{\mathrm{th}}$')
ax.plot(theory_masses, theory_vals, 'b-', linewidth=2)

# ---------------------------------------------------------------------------
# Habillage
# ---------------------------------------------------------------------------
ax.set_xlabel(r'$m_{\tilde{g}}$ [TeV]', fontsize=16)
ax.set_ylabel(r'$\sigma$ [pb]', fontsize=16)
ax.tick_params(axis='both', which='both', direction='in',
               top=True, right=True, labelsize=13)
if TITLE:
    ax.set_title(TITLE, fontsize=18)
ax.legend(fontsize=12, loc='best')
ax.grid(True, which='both', linestyle=':', alpha=0.4)

fig.tight_layout()
fig.savefig(OUTPUT, dpi=150)
print("Figure sauvegardee : {}".format(OUTPUT))