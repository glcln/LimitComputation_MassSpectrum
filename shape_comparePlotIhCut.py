#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compare les expected median limits pour chaque coupure en Ih (Ih3p1 -> Ih4p0),
plus le cas de reference sans suffixe Ih, en split eta.
cut & count = trait plein, shape = pointille ; meme couleur par coupure Ih.
Superpose la xsec theorique NNLO+NNLL et l'analyse precedente.
"""

import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['cmr10', 'Computer Modern Roman', 'DejaVu Serif'],
    'mathtext.fontset': 'cm',
    'axes.formatter.use_mathtext': True,
})

import warnings
warnings.filterwarnings("ignore", message="The value of the smallest subnormal")

# ---------------------------------------------------------------------------
# Limites de l'analyse precedente (HEPData Fig.6 left) : gluino R-hadron
# masse_TeV -> xsec upper limit (pb) ; Mass method
# ---------------------------------------------------------------------------
prev_gluino_mass = {
    1.0: 0.00034599, 1.4: 0.00043043, 1.6: 0.00049703, 1.8: 0.00053713,
    2.0: 0.0006273,  2.2: 0.00074158, 2.4: 0.0008099,  2.6: 0.00085929,
}

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
labelName = "etaRebinPerso_Oldfit__PUppiMETcut"
regionBckg = "9fp10"

# Coupures en Ih a parcourir (chaque suffixe -> un etalabeldir)
IH_CUTS = [
    'Ih3p1', 'Ih3p2', 'Ih3p3', 'Ih3p4', 'Ih3p5',
    'Ih3p6', 'Ih3p7', 'Ih3p8', 'Ih3p9', 'Ih4p0',
]


def build_path(etalabeldir, labelName, isCac):
    """Construit le chemin .txt pour un split_Eta1_<etalabeldir>, cac ou shape."""
    etaLabel = 'split_Eta1_' + etalabeldir
    cac = "_cutandcount" if isCac else ""
    d = "MyNewDataCards/limit_shape_{r}_{e}{c}_{l}".format(r=regionBckg, e=etaLabel, c=cac, l=labelName)
    f = "limits_shape_{r}_{e}{c}_{l}.txt".format(r=regionBckg, e=etaLabel, c=cac, l=labelName)
    return os.path.join(d, f)


# Chaque cas = (etalabeldir, label_affiche, labelName)
# Reference sans suffixe Ih en premier, puis une entree par coupure Ih
CASES = [('Eta1_2p4', r"$|\eta|<1 + 1<\eta<2.4$", "etaRebinPerso_Oldfit__PUppiMETcut")]
for ih in IH_CUTS:
    val = ih.replace('Ih', '').replace('p', '.')   # Ih3p4 -> "3.4"
    CASES.append(('Eta1p2_2p4_' + ih, r"$I_h$ cut $" + val + r"$", labelName))

OUTPUT = "ExpectedCompare_IhCuts_cac_shape_" + labelName + ".pdf"
TITLE  = r"Expected median limits $-$ gluino R-hadron, 2024 (split $\eta$)"

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
# Plotting
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_yscale('log')

cmap = plt.get_cmap('viridis')
n_cases = len(CASES)


def plot_case(fname, color, lw, ls, marker):
    if not os.path.isfile(fname):
        print("WARNING: fichier manquant : {}".format(fname))
        return
    data = np.loadtxt(fname, comments='#')
    if data.ndim == 1:
        data = data.reshape(1, -1)
    masses  = data[:, 0]
    exp_med = data[:, 3]
    order   = np.argsort(masses)
    masses, exp_med = masses[order], exp_med[order]
    ax.plot(masses, exp_med, linestyle=ls, linewidth=lw,
            marker=marker, markersize=4, color=color)


for i, (etalabeldir, label, lbl) in enumerate(CASES):
    if i == 0:
        color, marker = 'black', 'o'
    else:
        color = cmap((i - 1) / max(1, n_cases - 2))
        marker = 's'
    # cut & count : trait plein ; shape : pointille
    plot_case(build_path(etalabeldir, lbl, isCac=True),  color, 2.0, '-',  marker)
    plot_case(build_path(etalabeldir, lbl, isCac=False), color, 1.8, '--', marker)

# ---------------------------------------------------------------------------
# Section efficace theorique + bande d'incertitude
# ---------------------------------------------------------------------------
theory_masses = np.array(sorted(theory_xsec.keys())) / 1000.0
theory_vals   = np.array([theory_xsec[int(m * 1000)][0] for m in theory_masses])
theory_unc    = np.array([theory_xsec[int(m * 1000)][1] for m in theory_masses])
theory_up     = theory_vals * (1.0 + theory_unc)
theory_dn     = theory_vals * (1.0 - theory_unc)

ax.fill_between(theory_masses, theory_dn, theory_up,
                color='royalblue', alpha=0.25, linewidth=0)
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
# Analyse precedente
# ---------------------------------------------------------------------------
pm = np.array(sorted(prev_gluino_mass.keys()))
ax.plot(pm, [prev_gluino_mass[m] for m in pm],
        linestyle='-', linewidth=1.5, marker='o', markersize=4,
        color='gray', alpha=0.8)

# ---------------------------------------------------------------------------
# Habillage
# ---------------------------------------------------------------------------
ax.set_xlabel(r'$m_{\tilde{g}}$ [TeV]', fontsize=16)
ax.set_ylabel(r'$\sigma$ [pb]', fontsize=16)
ax.tick_params(axis='both', which='both', direction='in',
               top=True, right=True, labelsize=13)
if TITLE:
    ax.set_title(TITLE, fontsize=16)

# Legende 1 : cas eta / coupure Ih (couleur + marker)
handles_case = []
for i, (etalabeldir, label, lbl) in enumerate(CASES):
    if i == 0:
        color, marker = 'black', 'o'
    else:
        color = cmap((i - 1) / max(1, n_cases - 2))
        marker = 's'
    handles_case.append(
        Line2D([0], [0], color=color, marker=marker, linestyle='',
               markersize=6, label=label))

# Legende 2 : mode cac / shape (style de trait, couleur neutre)
handles_mode = [
    Line2D([0], [0], color='black', linestyle='-',  linewidth=2, label='cut & count'),
    Line2D([0], [0], color='black', linestyle='--', linewidth=2, label='shape'),
]
# Theorie + analyse precedente
handles_extra = [
    Line2D([0], [0], color='royalblue', linewidth=6, alpha=0.25,
           label=r'$\sigma^{\mathrm{NNLO+NNLL}}_{\mathrm{th}} \pm 1\sigma_{\mathrm{th}}$'),
    Line2D([0], [0], color='gray', linestyle='-', marker='o', markersize=4,
           alpha=0.8, label=r'Prev. analysis (Mass method)'),
]

leg1 = ax.legend(handles=handles_case, fontsize=9, loc='upper right', ncol=2)
ax.add_artist(leg1)
ax.legend(handles=handles_mode + handles_extra, fontsize=9, loc='lower left')

ax.grid(True, which='both', linestyle=':', alpha=0.4)


fig.tight_layout()
fig.savefig(OUTPUT, dpi=150)
print("Figure sauvegardee : {}".format(OUTPUT))