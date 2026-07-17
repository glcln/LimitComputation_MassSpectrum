#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Produit une serie de plots cumulatifs (build-up pour presentation) :
  step1 : xsec theorique Run2 + limite analyse precedente (Run2)
  step2 : + xsec theorique Run3 + cut&count |eta|<1
  step3 : + cut&count |eta|<2.4
  step4 : + cut&count |eta|<1 + 1<eta<2.4
  step5 : + shape des 3 memes categories
  step6 : + lignes verticales aux intersections limite/xsec
          (Run2 en gris, Eta1_2p4 x Run3 en vert)

Format attendu des fichiers .txt :
# mass_TeV  exp_m2sigma  exp_m1sigma  exp_median  exp_p1sigma  exp_p2sigma
"""

import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Police LaTeX (Computer Modern) sans dependre d'une installation LaTeX
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
# ---------------------------------------------------------------------------
prev_gluino_mass = {
    1.0: 0.00034599, 1.4: 0.00043043, 1.6: 0.00049703, 1.8: 0.00053713,
    2.0: 0.0006273,  2.2: 0.00074158, 2.4: 0.0008099,  2.6: 0.00085929,
}

# ---------------------------------------------------------------------------
# Sections efficaces theoriques
# ---------------------------------------------------------------------------
theory_xsec = {   # Run 3
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
# Fichiers de limites
# ---------------------------------------------------------------------------
labelName = "etaRebinPerso_Oldfit__PUppiMETcut"

def cac_path(tag):
    d = "MyNewDataCards/limit_shape_9fp10_{0}_cutandcount_{1}".format(tag, labelName)
    return "{0}/limits_shape_9fp10_{1}_cutandcount_{2}.txt".format(d, tag, labelName)

def shape_path(tag):
    d = "MyNewDataCards/limit_shape_9fp10_{0}_{1}".format(tag, labelName)
    return "{0}/limits_shape_9fp10_{1}_{2}.txt".format(d, tag, labelName)

CASES = {
    'Eta1':     (r"$|\eta|<1$",              'black', 'o'),
    'Eta2p4':   (r"$|\eta|<2.4$",            'red',   's'),
    'Eta1_2p4': (r"$|\eta|<1 + 1<\eta<2.4$", 'green', '^'),
}
TAGS = {
    'Eta1':     "Eta1",
    'Eta2p4':   "Eta2p4",
    'Eta1_2p4': "split_Eta1_Eta1_2p4",
}

TITLE = ""

# Mode utilise pour la ligne d'exclusion Run 3 ('cac' ou 'shape')
EXCL_MODE = 'shape'

# Bornes d'axes (utilisees aussi pour les lignes verticales)
X_LIM = (0.9, 2.7)
Y_LIM = (1e-5, 1e0)

# ---------------------------------------------------------------------------
# Chargement / dessin
# ---------------------------------------------------------------------------
def load_limits(fname):
    if not os.path.isfile(fname):
        print("WARNING: fichier manquant : {}".format(fname))
        return None, None
    data = np.loadtxt(fname, comments='#')
    if data.ndim == 1:
        data = data.reshape(1, -1)
    order = np.argsort(data[:, 0])
    return data[order, 0], data[order, 3]

def theory_arrays(xsec_dict):
    m = np.array(sorted(xsec_dict.keys())) / 1000.0
    v = np.array([xsec_dict[int(x * 1000)][0] for x in m])
    return m, v

def draw_xsec(ax, xsec_dict, color, label):
    m   = np.array(sorted(xsec_dict.keys())) / 1000.0
    v   = np.array([xsec_dict[int(x * 1000)][0] for x in m])
    unc = np.array([xsec_dict[int(x * 1000)][1] for x in m])
    ax.fill_between(m, v * (1.0 - unc), v * (1.0 + unc),
                    color=color, alpha=0.25, linewidth=0)
    ax.plot(m, v, color=color, linewidth=2)
    return Line2D([0], [0], color=color, linewidth=6, alpha=0.4, label=label)

def draw_prev_limit(ax):
    pm = np.array(sorted(prev_gluino_mass.keys()))
    ax.plot(pm, [prev_gluino_mass[x] for x in pm],
            linestyle='-', linewidth=1.5, marker='o', markersize=4,
            color='gray', alpha=0.8)
    return Line2D([0], [0], color='gray', linestyle='-', marker='o',
                  markersize=4, alpha=0.8, label=r'EXO-18-002 (CLs method)')

def draw_limit(ax, case, mode):
    """mode = 'cac' ou 'shape'"""
    label, color, marker = CASES[case]
    fname = cac_path(TAGS[case]) if mode == 'cac' else shape_path(TAGS[case])
    masses, exp_med = load_limits(fname)
    if masses is None:
        return None
    ls = '-' if mode == 'cac' else '--'
    ax.plot(masses, exp_med, linestyle=ls, linewidth=2,
            marker=marker, markersize=5, color=color)
    return None

# ---------------------------------------------------------------------------
# Intersection limite / theorie (interpolation lineaire en log-log)
# ---------------------------------------------------------------------------
def find_intersection(lim_m, lim_v, th_m, th_v):
    """
    Retourne (masse, xsec) du dernier croisement (masse la plus haute)
    entre la courbe de limite et la courbe theorique, ou (None, None).
    Interpolation lineaire en log(xsec) vs masse.
    """
    lo = max(lim_m.min(), th_m.min())
    hi = min(lim_m.max(), th_m.max())
    if lo >= hi:
        return None, None

    grid = np.linspace(lo, hi, 5000)
    log_lim = np.interp(grid, lim_m, np.log(lim_v))
    log_th  = np.interp(grid, th_m,  np.log(th_v))
    diff = log_lim - log_th

    idx = np.where(np.diff(np.sign(diff)) != 0)[0]
    if len(idx) == 0:
        return None, None

    i = idx[-1]  # dernier croisement = limite en masse
    # interpolation lineaire du zero entre grid[i] et grid[i+1]
    x0, x1 = grid[i], grid[i + 1]
    d0, d1 = diff[i], diff[i + 1]
    m_int = x0 - d0 * (x1 - x0) / (d1 - d0)
    y_int = np.exp(np.interp(m_int, th_m, np.log(th_v)))
    return m_int, y_int

def draw_exclusion_line(ax, m_int, y_int, color):
    """Ligne verticale pointillee de l'intersection a l'axe X + valeur en texte vertical."""
    if m_int is None:
        print("WARNING: pas d'intersection trouvee ({})".format(color))
        return
    ax.vlines(m_int, Y_LIM[0], y_int,
              color=color, linestyle=':', linewidth=1.8, alpha=0.9)
    ax.text(m_int - 0.015 * (X_LIM[1] - X_LIM[0]), Y_LIM[0] * 2.5,
            r'{:.2f} TeV'.format(m_int),
            color=color, fontsize=12, rotation=90,
            verticalalignment='bottom', horizontalalignment='right')

# ---------------------------------------------------------------------------
# Definition cumulative des steps
# ---------------------------------------------------------------------------
STEPS = [
    # step 1 : Run 2 seul
    [('xsecRun2',), ('prev',)],
    # step 2 : + Run 3 + cac Eta1
    [('xsecRun3',), ('limit', 'Eta1', 'cac')],
    # step 3 : + cac Eta2p4
    [('limit', 'Eta2p4', 'cac')],
    # step 4 : + cac Eta1_2p4
    [('limit', 'Eta1_2p4', 'cac')],
    # step 5 : + shape des 3
    [('limit', 'Eta1', 'shape'),
     ('limit', 'Eta2p4', 'shape'),
     ('limit', 'Eta1_2p4', 'shape')],
]

def make_plot(step_max, output, draw_exclusion=False):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_yscale('log')

    extra_handles = []
    eta_cases_drawn = []
    modes_drawn = set()

    for step in STEPS[:step_max]:
        for layer in step:
            kind = layer[0]
            if kind == 'xsecRun2':
                extra_handles.append(draw_xsec(
                    ax, theory_xsecRun2, 'darkorange',
                    r'$\sigma^{\mathrm{NNLO+NNLL}}_{\mathrm{th}}$ (13 TeV) $\pm 1\sigma_{\mathrm{th}}$'))
            elif kind == 'xsecRun3':
                extra_handles.append(draw_xsec(
                    ax, theory_xsec, 'royalblue',
                    r'$\sigma^{\mathrm{NNLO+NNLL}}_{\mathrm{th}}$ (13.6 TeV) $\pm 1\sigma_{\mathrm{th}}$'))
            elif kind == 'prev':
                extra_handles.append(draw_prev_limit(ax))
            elif kind == 'limit':
                _, case, mode = layer
                draw_limit(ax, case, mode)
                if case not in eta_cases_drawn:
                    eta_cases_drawn.append(case)
                modes_drawn.add(mode)

    # -----------------------------------------------------------------------
    # Lignes verticales d'exclusion (step6)
    # -----------------------------------------------------------------------
    if draw_exclusion:
        # 1) Run 2 : limite precedente x xsec Run 2 (gris)
        pm = np.array(sorted(prev_gluino_mass.keys()))
        pv = np.array([prev_gluino_mass[x] for x in pm])
        th2_m, th2_v = theory_arrays(theory_xsecRun2)
        m2, y2 = find_intersection(pm, pv, th2_m, th2_v)
        draw_exclusion_line(ax, m2, y2, 'gray')

        # 2) Run 3 : limite Eta1_2p4 x xsec Run 3 (vert)
        fname = (cac_path(TAGS['Eta1_2p4']) if EXCL_MODE == 'cac'
                 else shape_path(TAGS['Eta1_2p4']))
        lm, lv = load_limits(fname)
        if lm is not None:
            th3_m, th3_v = theory_arrays(theory_xsec)
            m3, y3 = find_intersection(lm, lv, th3_m, th3_v)
            draw_exclusion_line(ax, m3, y3, 'green')

    # Habillage
    ax.set_xlabel(r'$m_{\tilde{g}}$ [TeV]', fontsize=18)
    ax.set_ylabel(r'$\sigma$ [pb]', fontsize=18)
    ax.tick_params(axis='both', which='both', direction='in',
                   top=True, right=True, labelsize=14)
    if TITLE:
        ax.set_title(TITLE, fontsize=18)

    # Legende 1 : cas eta (couleur + marker)
    if eta_cases_drawn:
        handles_eta = [
            Line2D([0], [0], color=CASES[c][1], marker=CASES[c][2],
                   linestyle='', markersize=6, label=CASES[c][0])
            for c in eta_cases_drawn
        ]
        leg1 = ax.legend(handles=handles_eta, fontsize=11, loc='upper right')
        ax.add_artist(leg1)

    # Legende 2 : mode (uniquement si les deux modes sont presents)
    handles_mode = []
    if 'cac' in modes_drawn and 'shape' in modes_drawn:
        handles_mode = [
            Line2D([0], [0], color='black', linestyle='-',  linewidth=2, label='cut & count'),
            Line2D([0], [0], color='black', linestyle='--', linewidth=2, label='shape'),
        ]

    ax.legend(handles=handles_mode + extra_handles, fontsize=11, loc='lower left')

    ax.grid(True, which='both', linestyle=':', alpha=0.4)

    ax.text(0, 1.04, r'$\mathit{Private\ Work\ (CMS\ data)}$',
            transform=ax.transAxes, fontsize=14, verticalalignment='top')
    
    if step_max == 1:
        lumi_text = r'110 fb$^{-1}$ (13 TeV)'
    else:
        lumi_text = r'109 fb$^{-1}$ (13.6 TeV)'
    ax.text(1, 1.05, lumi_text,
            transform=ax.transAxes, fontsize=16,
            verticalalignment='top', horizontalalignment='right')

    # Axes fixes pour que les plots soient superposables en presentation
    ax.set_xlim(*X_LIM)
    ax.set_ylim(*Y_LIM)

    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    print("Figure sauvegardee : {}".format(output))


if __name__ == "__main__":
    for n in range(1, len(STEPS) + 1):
        make_plot(n, "ExpectedCompare_{0}_step{1}.pdf".format(labelName, n))
    # step6 : contenu du step5 + lignes verticales d'exclusion
    make_plot(len(STEPS),
              "ExpectedCompare_{0}_step6.pdf".format(labelName),
              draw_exclusion=True)