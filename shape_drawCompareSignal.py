#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plot recapitulatif des limites, une figure par signal (gluino, stop, stau).

Chaque figure contient :
  - les 3 limites attendues en shape : |eta|<1, |eta|<2.4, split |eta|<1 & 1<=eta<2.4
  - la limite observee de l'analyse Run 2 (HEPData)
  - les xsec theoriques NNLO+NNLL a 13 TeV (Run 2) et 13.6 TeV (Run 3)
  - les lignes verticales d'exclusion (croisement limite / xsec) :
    Run 2 en gris, meilleure categorie Run 3 dans sa propre couleur

A lancer apres shape_runAll.py (les .txt de limites doivent deja exister).

Format attendu des fichiers .txt :
# mass  exp_m2sigma  exp_m1sigma  exp_median  exp_p1sigma  exp_p2sigma

Usage :
    python shape_drawCompare.py
    python shape_drawCompare.py --signal stau
    python shape_drawCompare.py --label CorrelationAdded_SigmaPtoverPt_0p5_EoP_0p1
    python shape_drawCompare.py --cac            # meme plot en cut-and-count
    python shape_drawCompare.py --noVLines       # sans les lignes verticales
"""

import os
import sys
from optparse import OptionParser

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerTuple

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
# CONFIG
# ---------------------------------------------------------------------------
LABEL_DEFAULT = "SigmaPtoverPt_0p5_EoP_0p1_v2"
#LABEL_DEFAULT = "v2"
BASE_DIR      = "Limits"
OUTDIR_DEFAULT = "."

LUMI_TEXT = r'109 fb$^{-1}$ (13.6 TeV)'
CMS_TEXT  = r'$\mathit{Private\ Work\ (CMS\ data)}$'

# (cle, tag dans le nom de fichier, label legende, couleur, marker)
CASES = [
    ('Eta1',     'Eta1',                r'$|\eta|<1$',                   'black', 'o'),
    ('Eta2p4',   'Eta2p4',              r'$|\eta|<2.4$',                 'red',   's'),
    ('Eta1_2p4', 'split_Eta1_Eta1_2p4', r'$|\eta|<1$ & $1\leq\eta<2.4$', 'green', '^'),
]


# ---------------------------------------------------------------------------
# Limites de l'analyse precedente : https://www.hepdata.net/record/ins2840007
# (HEPData Fig.6) -- limites observees
# ---------------------------------------------------------------------------
prev_gluino_mass = {  # masses en TeV
    1.0: 0.00034599,
    1.4: 0.00043043,
    1.6: 0.00049703,
    1.8: 0.00053713,
    2.0: 0.0006273,
    2.2: 0.00074158,
    2.4: 0.0008099,
    2.6: 0.00085929,
}

prev_stop_mass = {  # masses en TeV
    1.0: 0.00028836,
    1.2: 0.000279,
    1.4: 0.00029444,
    1.6: 0.0003249,
    1.8: 0.00035268,
    2.0: 0.00037891,
    2.2: 0.00038428,
    2.4: 0.00041033,
    2.6: 0.00039226,
}

prev_stau_mass = {  # masses en GeV (converties automatiquement)
    308: 0.0011409,
    432: 0.0002058,
    557: 0.00015886,
    651: 0.00021287,
    745: 9.6597e-05,
    871: 6.6865e-05,
    1029: 6.3903e-05,
}


# ---------------------------------------------------------------------------
# Sections efficaces theoriques : masse [GeV] -> (xsec [pb], incertitude rel.)
# ---------------------------------------------------------------------------
theory_xsec_gluino_Run2 = {
    1400: (0.0284,   0.1231),
    1600: (0.00887,  0.1475),
    1800: (0.00293,  0.1844),
    2000: (0.00101,  0.2432),
    2200: (0.000356, 0.3302),
    2400: (0.000128, 0.4536),
    2600: (4.62e-05, 0.6161),
}

theory_xsec_gluino_Run3 = {
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

theory_xsec_stop_Run2 = {
     700: (8.323585E-02, 0.0656),
     800: (3.482106E-02, 0.0726),
     900: (1.561394E-02, 0.0806),
    1000: (7.394922E-03, 0.0908),
    1200: (1.876224E-03, 0.1137),
    1400: (5.371476E-04, 0.1471),
    1600: (1.677825E-04, 0.1954),
    1800: (5.585480E-05, 0.2626),
    2000: (1.955884E-05, 0.3543),
    2200: (7.097783E-06, 0.4790),
    2400: (2.646281E-06, 0.6433),
    2600: (1.006327E-06, 0.8596),
}

theory_xsec_stop_Run3 = {
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

theory_xsec_stau_Run2 = {
     247: (1.354211E-02, 0.0205),
     308: (5.618027E-03, 0.0221),
     432: (1.320809E-03, 0.0302),
     557: (4.003381E-04, 0.0346),
     651: (1.816412E-04, 0.0370),
     745: (8.774500E-05, 0.0396),
     871: (3.557834E-05, 0.0447),
    1029: (1.249423E-05, 0.0520),
    1218: (3.917976E-06, 0.0616),
    1409: (1.306042E-06, 0.0732),
    1599: (4.624559E-07, 0.0868),
}

theory_xsec_stau_Run3 = {
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

# ---------------------------------------------------------------------------
# Config par signal (bornes d'axes a ajuster au besoin)
# ---------------------------------------------------------------------------
SIGNALS = {
    'gluino': {
        'xlabel'      : r'$m_{\tilde{g}}$ [TeV]',
        'theory_run2' : theory_xsec_gluino_Run2,
        'theory_run3' : theory_xsec_gluino_Run3,
        'prev'        : prev_gluino_mass,
        'xlim'        : (0.9, 2.7),
        'ylim'        : (1e-5, 1e0),
    },
    'stop': {
        'xlabel'      : r'$m_{\tilde{t}}$ [TeV]',
        'theory_run2' : theory_xsec_stop_Run2,
        'theory_run3' : theory_xsec_stop_Run3,
        'prev'        : prev_stop_mass,
        'xlim'        : (0.6, 2.7),
        'ylim'        : (1e-6, 1e0),
    },
    'stau': {
        'xlabel'      : r'$m_{\tilde{\tau}}$ [TeV]',
        'theory_run2' : theory_xsec_stau_Run2,
        'theory_run3' : theory_xsec_stau_Run3,
        'prev'        : prev_stau_mass,
        'xlim'        : (0.2, 1.7),
        'ylim'        : (1e-7, 1e-1),
    },
}
SIGNALS_ALL = ['gluino', 'stop', 'stau']


# ---------------------------------------------------------------------------
# Resolution des chemins de fichiers de limites
# ---------------------------------------------------------------------------
def limit_file(signal, tag, label, cac=False):
    """Cherche le .txt de limites en essayant les conventions de nommage."""
    mode = 'cutandcount_' if cac else ''
    stems = [
        "{0}_{1}{2}".format(tag, mode, label),   # signal avant le tag
        "{0}_{1}{2}".format(tag, mode, label),   # signal apres le tag
        "{0}_{1}{2}".format(tag, mode, label),               # sans signal (legacy)
    ]
    tried = []
    for dstem in stems:
        d = "{0}/{1}/limit_shape_9fp10_{2}".format(BASE_DIR, signal, dstem)
        for fstem in stems:
            path = "{0}/limits_shape_{1}_9fp10_{2}.txt".format(d, signal, fstem)
            tried.append(path)
            if os.path.isfile(path):
                return path
    print("WARNING: aucun fichier de limites pour {0} / {1}".format(signal, tag))
    print("         essaye (entre autres) : {0}".format(tried[0]))
    return None


# ---------------------------------------------------------------------------
# Chargement / helpers
# ---------------------------------------------------------------------------
def to_TeV(masses):
    """Les fichiers/dicos peuvent etre en GeV : on normalise en TeV."""
    masses = np.asarray(masses, dtype=float)
    return masses / 1000.0 if np.max(masses) > 10.0 else masses


def load_limits(fname):
    """Retourne (masses [TeV], limite mediane attendue [pb])."""
    if fname is None or not os.path.isfile(fname):
        return None, None
    data = np.loadtxt(fname, comments='#')
    if data.ndim == 1:
        data = data.reshape(1, -1)
    order = np.argsort(data[:, 0])
    m, v = to_TeV(data[order, 0]), data[order, 3]
    good = v > 0
    return m[good], v[good]


def theory_arrays(xsec_dict):
    keys = sorted(xsec_dict.keys())
    m   = to_TeV(keys)
    v   = np.array([xsec_dict[k][0] for k in keys])
    unc = np.array([xsec_dict[k][1] for k in keys])
    return m, v, unc


def prev_arrays(prev_dict):
    keys = sorted(prev_dict.keys())
    return to_TeV(keys), np.array([prev_dict[k] for k in keys])


# ---------------------------------------------------------------------------
# Dessin
# ---------------------------------------------------------------------------
def draw_xsec(ax, xsec_dict, color, label):
    m, v, unc = theory_arrays(xsec_dict)
    ax.fill_between(m, v * (1.0 - unc), v * (1.0 + unc),
                    color=color, alpha=0.25, linewidth=0)
    ax.plot(m, v, color=color, linewidth=2)
    return Line2D([0], [0], color=color, linewidth=6, alpha=0.4, label=label)


def draw_prev_limit(ax, prev_dict):
    pm, pv = prev_arrays(prev_dict)
    ax.plot(pm, pv, linestyle='-', linewidth=1.5, marker='o', markersize=4,
            color='gray', alpha=0.8)
    return Line2D([0], [0], color='gray', linestyle='-', marker='o',
                  markersize=4, alpha=0.8,
                  label=r'HSCP Run-2 obs. (Full CL$_{\rm s}$)')


def draw_limit(ax, masses, values, color, marker, cac=False):
    ax.plot(masses, values, linestyle='-' if cac else '--', linewidth=2,
            marker=marker, markersize=5, color=color)


# ---------------------------------------------------------------------------
# Intersection limite / theorie (interpolation lineaire en log-log)
# ---------------------------------------------------------------------------
def find_intersection(lim_m, lim_v, th_m, th_v):
    """Dernier croisement (masse la plus haute) entre limite et theorie."""
    lo = max(lim_m.min(), th_m.min())
    hi = min(lim_m.max(), th_m.max())
    if lo >= hi:
        return None, None

    grid = np.linspace(lo, hi, 5000)
    diff = np.interp(grid, lim_m, np.log(lim_v)) - np.interp(grid, th_m, np.log(th_v))

    idx = np.where(np.diff(np.sign(diff)) != 0)[0]
    if len(idx) == 0:
        return None, None

    i = idx[-1]
    x0, x1 = grid[i], grid[i + 1]
    d0, d1 = diff[i], diff[i + 1]
    m_int = x0 - d0 * (x1 - x0) / (d1 - d0)
    y_int = np.exp(np.interp(m_int, th_m, np.log(th_v)))
    return m_int, y_int


def draw_exclusion_line(ax, m_int, y_int, color, xlim, ylim):
    """Ligne verticale pointillee jusqu'a l'axe X + valeur en texte vertical."""
    if m_int is None:
        return
    ax.vlines(m_int, ylim[0], y_int,
              color=color, linestyle=':', linewidth=1.8, alpha=0.9)
    ax.text(m_int - 0.015 * (xlim[1] - xlim[0]), ylim[0] * 2.5,
            r'{:.2f} TeV'.format(m_int),
            color=color, fontsize=12, rotation=90,
            verticalalignment='bottom', horizontalalignment='right')


# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
def make_plot(signal, label, cac=False, outdir=OUTDIR_DEFAULT, vlines=True):
    cfg = SIGNALS[signal]
    xlim, ylim = cfg['xlim'], cfg['ylim']

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_yscale('log')

    # 1) xsec theoriques
    h_xsec2 = draw_xsec(ax, cfg['theory_run2'], 'darkorange',
                        r'$\sigma^{\mathrm{NNLO+NNLL}}_{\mathrm{th}}$ (13 TeV) $\pm 1\sigma_{\mathrm{th}}$')
    h_xsec3 = draw_xsec(ax, cfg['theory_run3'], 'royalblue',
                        r'$\sigma^{\mathrm{NNLO+NNLL}}_{\mathrm{th}}$ (13.6 TeV) $\pm 1\sigma_{\mathrm{th}}$')

    # 2) limite Run 2
    h_prev = draw_prev_limit(ax, cfg['prev'])

    # 3) limites Run 3 (une par categorie en eta)
    drawn = []
    for key, tag, leg, color, marker in CASES:
        lm, lv = load_limits(limit_file(signal, tag, label, cac))
        if lm is None or len(lm) == 0:
            continue
        draw_limit(ax, lm, lv, color, marker, cac)
        drawn.append((key, leg, color, marker, lm, lv))

    if not drawn:
        print("Aucune limite trouvee pour {0} -> figure ignoree".format(signal))
        plt.close(fig)
        return None

    # -----------------------------------------------------------------------
    # Lignes verticales d'exclusion
    # -----------------------------------------------------------------------
    summary = {'run2': None, 'run3': None, 'run3_case': None}

    th2_m, th2_v, _ = theory_arrays(cfg['theory_run2'])
    th3_m, th3_v, _ = theory_arrays(cfg['theory_run3'])

    pm, pv = prev_arrays(cfg['prev'])
    m2, y2 = find_intersection(pm, pv, th2_m, th2_v)
    summary['run2'] = m2
    if vlines:
        draw_exclusion_line(ax, m2, y2, 'gray', xlim, ylim)

    best = None  # (m_int, y_int, couleur, cas)
    for key, leg, color, marker, lm, lv in drawn:
        m3, y3 = find_intersection(lm, lv, th3_m, th3_v)
        if m3 is not None and (best is None or m3 > best[0]):
            best = (m3, y3, color, key)
    if best is not None:
        summary['run3'], summary['run3_case'] = best[0], best[3]
        if vlines:
            draw_exclusion_line(ax, best[0], best[1], best[2], xlim, ylim)

    # -----------------------------------------------------------------------
    # Habillage
    # -----------------------------------------------------------------------
    ax.set_xlabel(cfg['xlabel'], fontsize=17, labelpad=8, ha='right', x=1.0)
    ax.set_ylabel(r'95% CL upper limit on $\sigma$ [pb]',
                  fontsize=17, labelpad=8, ha='right', y=1.0)
    ax.tick_params(axis='both', which='both', direction='in',
                   top=True, right=True, labelsize=14)

    # Legende 1 : categories en eta
    ls = '-' if cac else '--'
    handles_eta = [Line2D([0], [0], color=c, marker=mk, linestyle=ls,
                          linewidth=2, markersize=6, label=leg)
                   for _, leg, c, mk, _, _ in drawn]
    title_eta = r'Asymptotic CL$_{\rm s}$' + (' (cut-and-count)' if cac else ' (shape)')
    leg1 = ax.legend(handles=handles_eta, fontsize=11, loc='upper right',
                     title=title_eta, title_fontsize=12)
    ax.add_artist(leg1)

    # Legende 2 : reference Run 2 + xsec theoriques
    grouped, labels = [], []
    for h in (h_xsec3, h_prev, h_xsec2):
        labels.append(h.get_label())
        if h is h_prev:
            grouped.append(h)
        else:
            c = h.get_color()
            grouped.append((mpatches.Patch(color=c, alpha=0.25),
                            Line2D([0], [0], color=c, linewidth=2)))
    ax.legend(grouped, labels, fontsize=11, loc='lower left',
              handler_map={tuple: HandlerTuple(ndivide=1)})

    ax.grid(True, which='both', linestyle=':', alpha=0.4)
    ax.text(0, 1.04, CMS_TEXT, transform=ax.transAxes,
            fontsize=16, verticalalignment='top')
    ax.text(1, 1.05, LUMI_TEXT, transform=ax.transAxes, fontsize=16,
            verticalalignment='top', horizontalalignment='right')

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)

    fig.tight_layout()
    if outdir and not os.path.isdir(outdir):
        os.makedirs(outdir)
    mode = 'cutandcount' if cac else 'shape'
    output = os.path.join(outdir, "ExpectedCompare_{0}_{1}_{2}.pdf".format(signal, mode, label))
    fig.savefig(output, dpi=150)
    plt.close(fig)
    print("Figure sauvegardee : {0}".format(output))
    return summary


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    parser = OptionParser()
    parser.add_option('--signal', dest='signals', default=','.join(SIGNALS_ALL),
                      help="Signaux a tracer, separes par des virgules (defaut: tous).")
    parser.add_option('--label', dest='label', default=LABEL_DEFAULT,
                      help="optionlabel utilise dans les noms de fichiers.")
    parser.add_option('--outDir', dest='outdir', default=OUTDIR_DEFAULT,
                      help="Repertoire de sortie des figures.")
    parser.add_option('--cac', action='store_true', dest='cac', default=False,
                      help="Trace les limites cut-and-count au lieu du shape.")
    parser.add_option('--noVLines', action='store_false', dest='vlines', default=True,
                      help="Desactive les lignes verticales d'exclusion.")
    (opts, _) = parser.parse_args()

    signals = [s.strip() for s in opts.signals.split(',') if s.strip()]
    for s in signals:
        if s not in SIGNALS:
            sys.exit("Signal inconnu : {0} (attendu : {1})".format(s, SIGNALS_ALL))

    results = {}
    for s in signals:
        print("\n" + "=" * 70)
        print("  {0}".format(s))
        print("=" * 70)
        results[s] = make_plot(s, opts.label, opts.cac, opts.outdir, opts.vlines)

    print("\n" + "=" * 70)
    print("  Masses exclues (croisement limite / xsec theorique)")
    print("=" * 70)
    for s in signals:
        r = results.get(s)
        if r is None:
            print("  {0:7s} : -".format(s))
            continue
        run2 = "{0:.2f} TeV".format(r['run2']) if r['run2'] else "-"
        run3 = "{0:.2f} TeV ({1})".format(r['run3'], r['run3_case']) if r['run3'] else "-"
        print("  {0:7s} : Run 2 = {1:20s} Run 3 = {2}".format(s, run2, run3))


if __name__ == '__main__':
    main()