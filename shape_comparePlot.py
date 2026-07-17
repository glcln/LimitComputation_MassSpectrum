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

# ---------------------------------------------------------------------------
# Limites de l'analyse precedente (HEPData Fig.6 left) : gluino R-hadron
# masse_TeV -> xsec upper limit (pb)
# group 0 = Mass method, group 1 = Ionization method
# ---------------------------------------------------------------------------
prev_gluino_mass = {
    1.0: 0.00034599, 1.4: 0.00043043, 1.6: 0.00049703, 1.8: 0.00053713,
    2.0: 0.0006273,  2.2: 0.00074158, 2.4: 0.0008099,  2.6: 0.00085929,
}


# MAIN

labelName = "etaRebinPerso_Oldfit__PUppiMETcut"

INPUT_FILES = [
    ("MyNewDataCards/limit_shape_9fp10_Eta1_cutandcount_etaRebinPerso_Oldfit__PUppiMETcut/limits_shape_9fp10_Eta1_cutandcount_etaRebinPerso_Oldfit__PUppiMETcut.txt", r"$|\eta|<1$"),
    ("MyNewDataCards/limit_shape_9fp10_Eta2p4_cutandcount_etaRebinPerso_Oldfit__PUppiMETcut/limits_shape_9fp10_Eta2p4_cutandcount_etaRebinPerso_Oldfit__PUppiMETcut.txt", r"$|\eta|<2.4$"),
    ("MyNewDataCards/limit_shape_9fp10_split_Eta1_Eta1_2p4_cutandcount_etaRebinPerso_Oldfit__PUppiMETcut/limits_shape_9fp10_split_Eta1_Eta1_2p4_cutandcount_etaRebinPerso_Oldfit__PUppiMETcut.txt", r"$|\eta|<1 + 1<\eta<2.4$"),
    ("MyNewDataCards/limit_shape_9fp10_split_Eta1_Eta1p2_2p4_cutandcount_etaRebinPerso_Oldfit__PUppiMETcut/limits_shape_9fp10_split_Eta1_Eta1p2_2p4_cutandcount_etaRebinPerso_Oldfit__PUppiMETcut.txt", r"$|\eta|<1 + 1.2<\eta<2.4$"),
    ("MyNewDataCards/limit_shape_9fp10_split_Eta1_Eta1p2_2p2_cutandcount_etaRebinPerso_Oldfit__PUppiMETcut/limits_shape_9fp10_split_Eta1_Eta1p2_2p2_cutandcount_etaRebinPerso_Oldfit__PUppiMETcut.txt", r"$|\eta|<1 + 1.2<\eta<2.2$"),
    
    ("MyNewDataCards/limit_shape_9fp10_Eta1_etaRebinPerso_Oldfit__PUppiMETcut/limits_shape_9fp10_Eta1_etaRebinPerso_Oldfit__PUppiMETcut.txt", r"$|\eta|<1$"),
    ("MyNewDataCards/limit_shape_9fp10_Eta2p4_etaRebinPerso_Oldfit__PUppiMETcut/limits_shape_9fp10_Eta2p4_etaRebinPerso_Oldfit__PUppiMETcut.txt", r"$|\eta|<2.4$"),
    ("MyNewDataCards/limit_shape_9fp10_split_Eta1_Eta1_2p4_etaRebinPerso_Oldfit__PUppiMETcut/limits_shape_9fp10_split_Eta1_Eta1_2p4_etaRebinPerso_Oldfit__PUppiMETcut.txt", r"$|\eta|<1 + 1<\eta<2.4$"),
    ("MyNewDataCards/limit_shape_9fp10_split_Eta1_Eta1p2_2p4_etaRebinPerso_Oldfit__PUppiMETcut/limits_shape_9fp10_split_Eta1_Eta1p2_2p4_etaRebinPerso_Oldfit__PUppiMETcut.txt", r"$|\eta|<1 + 1.2<\eta<2.4$"),
    ("MyNewDataCards/limit_shape_9fp10_split_Eta1_Eta1p2_2p2_etaRebinPerso_Oldfit__PUppiMETcut/limits_shape_9fp10_split_Eta1_Eta1p2_2p2_etaRebinPerso_Oldfit__PUppiMETcut.txt", r"$|\eta|<1 + 1.2<\eta<2.2$"),
]

# ---------------------------------------------------------------------------
# A EDITER : sortie et titre
# ---------------------------------------------------------------------------
OUTPUT = "ExpectedCompare_" + labelName + ".pdf"
TITLE  = r"Expected median limits $-$ gluino R-hadron, 2024" 

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

theory_xsecRun2 = {
    1400: (0.0284, 0.1231),
    1600: (0.00887, 0.1475),
    1800: (0.00293, 0.1844),
    2000: (0.00101, 0.2432),
    2200: (0.000356, 0.3302),
    2400: (0.000128, 0.4536),
    2600: (4.62e-05, 0.6161),
}

# ---------------------------------------------------------------------------
# Plotting — style CMS-like avec matplotlib
# cut-and-count = trait plein, shape = pointillé
# même couleur/marker pour le même cas eta
# ---------------------------------------------------------------------------
from matplotlib.lines import Line2D

fig, ax = plt.subplots(figsize=(8, 6))
ax.set_yscale('log')

colors  = ['black', 'red', 'green', 'orange', 'purple', 'cyan', 'magenta', 'brown', 'olive', 'teal']
markers = ['o', 's', '^', 'v', 'D', 'P', 'X', '*', '<', '>']

# 5 cas eta : les 5 premiers fichiers sont cac, les 5 suivants shape (même ordre)
N_CASES = 5

# Labels des cas eta (pris sur les 5 premiers fichiers)
case_labels = [INPUT_FILES[j][1] for j in range(N_CASES)]

for i, (fname, label) in enumerate(INPUT_FILES):
    if not os.path.isfile(fname):
        print("WARNING: fichier manquant : {}".format(fname))
        continue

    case_idx  = i % N_CASES
    is_cac    = i < N_CASES
    linestyle = '-' if is_cac else '--'

    # Colonne 0 = mass_TeV, colonne 3 = exp_median
    data = np.loadtxt(fname, comments='#')
    if data.ndim == 1:
        data = data.reshape(1, -1)

    masses  = data[:, 0]
    exp_med = data[:, 3]

    order   = np.argsort(masses)
    masses  = masses[order]
    exp_med = exp_med[order]

    # pas de label ici : légendes gérées manuellement
    ax.plot(masses, exp_med,
            linestyle=linestyle, linewidth=2,
            marker=markers[case_idx], markersize=5,
            color=colors[case_idx])
    
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

theory_masses2 = np.array(sorted(theory_xsecRun2.keys())) / 1000.0
theory_vals2   = np.array([theory_xsecRun2[int(m * 1000)][0] for m in theory_masses2])
theory_unc2    = np.array([theory_xsecRun2[int(m * 1000)][1] for m in theory_masses2])
theory_up2     = theory_vals2 * (1.0 + theory_unc2)
theory_dn2     = theory_vals2 * (1.0 - theory_unc2)

ax.fill_between(theory_masses2, theory_dn2, theory_up2,
                color='darkorange', alpha=0.25, linewidth=0)
ax.plot(theory_masses2, theory_vals2, color='darkorange', linewidth=2)

# ---------------------------------------------------------------------------
# Superposition des limites de l'analyse precedente (gluino uniquement)
# ---------------------------------------------------------------------------
pm = np.array(sorted(prev_gluino_mass.keys()))
ax.plot(pm, [prev_gluino_mass[m] for m in pm],
        linestyle='-', linewidth=1.5, marker='o', markersize=4,
        color='gray', alpha=0.8,
        label=r'Prev. analysis (Mass method)')

# ---------------------------------------------------------------------------
# Habillage
# ---------------------------------------------------------------------------
ax.set_xlabel(r'$m_{\tilde{g}}$ [TeV]', fontsize=16)
ax.set_ylabel(r'$\sigma$ [pb]', fontsize=16)
ax.tick_params(axis='both', which='both', direction='in',
               top=True, right=True, labelsize=13)
if TITLE:
    ax.set_title(TITLE, fontsize=18)

# Légende 1 : cas eta (couleur + marker), trait neutre
handles_eta = [
    Line2D([0], [0], color=colors[j], marker=markers[j], linestyle='',
           markersize=6, label=case_labels[j])
    for j in range(N_CASES)
]
# Légende 2 : distinction cac / shape (style de trait, couleur neutre)
handles_mode = [
    Line2D([0], [0], color='black', linestyle='-',  linewidth=2, label='cut & count'),
    Line2D([0], [0], color='black', linestyle='--', linewidth=2, label='shape'),
]
# Théorie + analyse précédente
handles_extra = [
    Line2D([0], [0], color='royalblue', linewidth=6, alpha=0.25,
           label=r'$\sigma^{\mathrm{NNLO+NNLL}}_{\mathrm{th}} \pm 1\sigma_{\mathrm{th}}$'),
    Line2D([0], [0], color='gray', linestyle='-', marker='o', markersize=4,
           alpha=0.8, label=r'Prev. analysis (Mass method)'),
]

leg1 = ax.legend(handles=handles_eta, fontsize=11, loc='upper right')
ax.add_artist(leg1)
ax.legend(handles=handles_mode + handles_extra, fontsize=11, loc='lower left')

ax.grid(True, which='both', linestyle=':', alpha=0.4)

fig.tight_layout()
fig.savefig(OUTPUT, dpi=150)
print("Figure sauvegardee : {}".format(OUTPUT))