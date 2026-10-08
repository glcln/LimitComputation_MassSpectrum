"""
Plot the cross-section upper limits obtained by RunDatacards.

For one signal model (gluino, stop or stau) and one eta configuration, the
script reads the Combine AsymptoticLimits tree of each mass point, converts
the limit on the signal strength r into a limit on the cross section (r times
the theoretical cross section) and draws, as a function of the mass:

    - the median expected limit with its 68% and 95% bands
    - the observed limit (with --unblind only)
    - the NNLO+NNLL theoretical cross section with its uncertainty band
    - a vertical line at the mass where the median expected limit crosses the
      theoretical cross section, i.e. the expected excluded mass

Multiplying r by the theoretical cross section assumes that the signal
histograms of the datacards are normalised to the same cross sections.

Input
    <LIMITS_BASE>/<signal>/limit_shape_<regionBckg>_<etaLabel>[_cutandcount]_<optionlabel>/
        higgsCombine.<Sample>.AsymptoticLimits.mH120.root

Output, written in the input directory
    limits_shape_<signal>_<regionBckg>_<etaLabel>[_cutandcount]_<optionlabel>.pdf
    limits_shape_<signal>_<regionBckg>_<etaLabel>[_cutandcount]_<optionlabel>.txt
The text file holds one line per mass point: mass [TeV], then the -2 sigma,
-1 sigma, median, +1 sigma and +2 sigma expected limits [pb], and the observed
limit with --unblind. It is the input of shape_drawCompareSignal.py.

LIMITS_BASE is the Limits/ directory next to this script.

--signal, --cac, --splitEta, --onlyEta1 and the hardcoded regionBckg and
optionlabel settings must be the same as in CreateDatacards.py and
RunDatacards: the directory names are rebuilt here from the same
rules. optionlabel is rewritten in place by the driver
shape_ProduceLimitsForDifferentEtaCategory.py.

--unblind draws the observed limit stored by Combine. It is a limit on real
data only if the datacards were written by CreateDatacards.py --unblind;
otherwise data_obs is the background prediction.

Usage:
    python3 DrawDatacards.py                        # gluino, full tracker, shape
    python3 DrawDatacards.py --splitEta             # two eta categories
    python3 DrawDatacards.py --onlyEta1             # central region only
    python3 DrawDatacards.py --cac --signal stau    # cut-and-count, stau
    python3 DrawDatacards.py --unblind              # with the observed limit
"""

from optparse import OptionParser
import os
import sys
import warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import ROOT
from matplotlib.legend_handler import HandlerTuple

ROOT.gROOT.SetBatch(True)

# Sans-serif (Helvetica-like) fonts for the text and the math, close to the
# ROOT CMS style and without needing a LaTeX installation
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

warnings.filterwarnings("ignore", message="The value of the smallest subnormal")

# ---------------------------------------------------------------------------
## COMMAND LINE
# ---------------------------------------------------------------------------
parser = OptionParser()
parser.add_option('--unblind', action='store_true', default=False, dest='unblind',
                  help='Also draw the observed limit. Only meaningful for datacards '
                       'generated with --unblind.')
parser.add_option('-d', '--debug', type='int', default=0, dest='debug',
                  help='Verbosity: 1 prints the limits read for each mass point.')
parser.add_option('--cac', action='store_true', dest='cac', default=False,
                  help='Plot the cut-and-count limits instead of the shape ones.')
parser.add_option('--splitEta', action='store_true', dest='splitEta', default=False,
                  help='Must match the flag of the generation and run scripts: full '
                       'tracker Eta2p4 (off) or split Eta1/Eta1_2p4 (on).')
parser.add_option('--onlyEta1', action='store_true', dest='onlyEta1', default=False,
                  help='Must match the generation and run scripts: central region '
                       '|eta|<1 only (Eta1).')
parser.add_option('--signal', dest='signal', default='gluino',
                  type='choice', choices=['gluino', 'stop', 'stau'],
                  help='Must match the generation and run scripts: gluino, stop or stau.')
(options, args) = parser.parse_args()

if options.splitEta and options.onlyEta1:
    parser.error('--splitEta and --onlyEta1 are mutually exclusive')

isCutAndCount = options.cac
splitEta      = options.splitEta
onlyEta1      = options.onlyEta1
signalType    = options.signal
unblind       = options.unblind
debug         = options.debug

# ---------------------------------------------------------------------------
## CONFIGURATION
# ---------------------------------------------------------------------------
# Must match the settings of the generation and run scripts.
# optionlabel is rewritten in place by the driver
# shape_ProduceLimitsForDifferentEtaCategory.py, which looks for a one-line,
# single-quoted assignment: keep that form, and a single assignment in this
# file.
regionBckg  = '9fp10'
optionlabel = 'SigmaPtoverPt_0p5_EoP_0p1_v2'

# Root of the Combine results: the Limits/ directory next to this script
LIMITS_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Limits')

# Labels drawn above the frame
CMS_TEXT  = r'$\mathit{Private\ Work\ (CMS\ data)}$'
LUMI_TEXT = r'109 fb$^{-1}$ (13.6 TeV)'

# NNLO+NNLL theoretical cross sections at 13.6 TeV:
# { mass [GeV] : (cross section [pb], relative uncertainty) }
# The mass points to plot are the keys of these tables.
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

# Per-signal plot configuration:
#   label  : prefix of the Combine sample name, '<label><mass>_2024'
#   xsec   : table of theoretical cross sections
#   xlabel : x-axis title
#   ylim   : y-axis range [pb]
SIGNAL_PLOT_CONFIG = {
    'gluino': {
        'label'  : 'Gluino',
        'xsec'   : theory_xsec_gluino,
        'xlabel' : r'$m_{\tilde{g}}$ [TeV]',
        'ylim'   : (5e-6, 1.0),
    },
    'stop': {
        'label'  : 'Stop',
        'xsec'   : theory_xsec_stop,
        'xlabel' : r'$m_{\tilde{t}}$ [TeV]',
        'ylim'   : (5e-7, 1.0),
    },
    'stau': {
        'label'  : 'Stau',
        'xsec'   : theory_xsec_stau,
        'xlabel' : r'$m_{\tilde{\tau}}$ [TeV]',
        'ylim'   : (1e-7, 1.0),
    },
}


# ---------------------------------------------------------------------------
## FUNCTIONS
# ---------------------------------------------------------------------------
def read_limits(odir, label, theory_xsec):
    """
    Read the AsymptoticLimits tree of each mass point of `theory_xsec` and
    convert the limits on r into limits on the cross section [pb].

    Combine stores one entry per quantile in the `limit` tree, identified by
    quantileExpected: 0.025, 0.16, 0.5, 0.84 and 0.975 for the expected limit
    (-2 sigma, -1 sigma, median, +1 sigma, +2 sigma) and -1 for the observed
    one.

    A mass point whose file, tree or median expected limit is missing is
    skipped with a warning. Any other missing quantile is stored as NaN.

    Returns a dict of numpy arrays, one value per mass point kept, in
    increasing mass: 'mass' [TeV], 'exp_m2', 'exp_m1', 'exp_med', 'exp_p1',
    'exp_p2' and 'obs'.
    """
    quantiles = [('exp_m2', 0.025), ('exp_m1', 0.160), ('exp_med', 0.500),
                 ('exp_p1', 0.840), ('exp_p2', 0.975), ('obs', -1.0)]
    limits = {key: [] for key, _ in quantiles}
    limits['mass'] = []

    for mass_gev in sorted(theory_xsec):
        name  = '{}{}_2024'.format(label, mass_gev)
        fname = os.path.join(odir, 'higgsCombine.{}.AsymptoticLimits.mH120.root'.format(name))
        if not os.path.isfile(fname):
            print("WARNING: missing file: {}".format(fname))
            continue

        f = ROOT.TFile.Open(fname)
        tree = f.Get('limit')
        if not tree:
            print("WARNING: TTree 'limit' not found in {}".format(fname))
            f.Close()
            continue

        this_xsec = theory_xsec[mass_gev][0]

        # {quantile: cross-section limit}
        quant_map = {}
        for ev in tree:
            q = round(ev.quantileExpected, 3)
            quant_map[q] = ev.limit * this_xsec
        f.Close()

        if debug > 0:
            print("Mass {} GeV -> quantiles: {}".format(mass_gev, quant_map))

        if 0.500 not in quant_map:
            print("WARNING: median expected limit missing for {}".format(name))
            continue

        limits['mass'].append(mass_gev / 1000.0)
        for key, q in quantiles:
            limits[key].append(quant_map.get(q, np.nan))

    return {key: np.array(vals) for key, vals in limits.items()}


def find_crossing(masses, limit, theory_masses, theory_vals):
    """
    Mass at which the `limit` curve crosses the theory curve.

    Both curves are interpolated linearly in log(cross section) versus mass,
    the theory one being evaluated at the mass points of the limit. When the
    curves cross several times, the crossing at the highest mass is returned.

    Returns (mass, limit at that mass), or None if the curves do not cross.
    """
    log_lim = np.log(limit)
    log_th  = np.interp(masses, theory_masses, np.log(theory_vals))
    diff    = log_lim - log_th

    # Intervals between consecutive mass points where the difference changes sign
    sign_changes = np.where(np.diff(np.sign(diff)))[0]
    if len(sign_changes) == 0:
        return None

    # Linear interpolation of the difference inside the last such interval
    i = sign_changes[-1]
    x0, x1 = masses[i], masses[i+1]
    d0, d1 = diff[i], diff[i+1]
    x_cross = x0 - d0 * (x1 - x0) / (d1 - d0)
    y_cross = np.exp(np.interp(x_cross, masses, log_lim))
    return x_cross, y_cross


def write_limits_table(txt_out, limits, withObserved):
    """
    Write the limits as a text table, one line per mass point (format in the
    module docstring). The observed column is only written if `withObserved`.
    """
    with open(txt_out, 'w') as f:
        header = '# mass_TeV  exp_m2sigma  exp_m1sigma  exp_median  exp_p1sigma  exp_p2sigma'
        if withObserved:
            header += '  observed'
        f.write(header + '\n')
        for i, m in enumerate(limits['mass']):
            line = '{:.3f}  {:.6e}  {:.6e}  {:.6e}  {:.6e}  {:.6e}'.format(
                m, limits['exp_m2'][i], limits['exp_m1'][i], limits['exp_med'][i],
                limits['exp_p1'][i], limits['exp_p2'][i])
            if withObserved:
                line += '  {:.6e}'.format(limits['obs'][i])
            f.write(line + '\n')


if __name__ == '__main__':

    # --- Same eta label logic as in the generation and run scripts ---
    # etaDisplay is the text written on the plot
    if splitEta:
        etaLabel   = 'split_Eta1_Eta1_2p4'
        etaDisplay = r'$|\eta|<1$ & $1\leq|\eta|<2.4$'
    elif onlyEta1:
        etaLabel   = 'Eta1'
        etaDisplay = r'$|\eta|<1$'
    else:
        etaLabel   = 'Eta2p4'
        etaDisplay = r'$|\eta|<2.4$'

    # Directory of the Combine results, where the plot and the table are also written
    odir = os.path.join(LIMITS_BASE, signalType, 'limit_shape_{}_{}{}_{}'.format(regionBckg, etaLabel, "_cutandcount" if isCutAndCount else "", optionlabel))

    outPlot = os.path.join(odir, 'limits_shape_{}_{}_{}{}_{}.pdf'.format(signalType, regionBckg, etaLabel, "_cutandcount" if isCutAndCount else "", optionlabel))

    sigCfg      = SIGNAL_PLOT_CONFIG[signalType]
    theory_xsec = sigCfg['xsec']

    # --- Limits read from the Combine output ---
    limits = read_limits(odir, sigCfg['label'], theory_xsec)
    masses = limits['mass']
    if len(masses) == 0:
        sys.exit("No mass point loaded - check the directory '{}'.".format(odir))

    # --- Theory curve and its uncertainty band ---
    theory_mass_gev = sorted(theory_xsec)
    theory_masses   = np.array(theory_mass_gev) / 1000.0
    theory_vals     = np.array([theory_xsec[m][0] for m in theory_mass_gev])
    theory_unc      = np.array([theory_xsec[m][1] for m in theory_mass_gev])
    theory_up       = theory_vals * (1.0 + theory_unc)
    theory_dn       = theory_vals * (1.0 - theory_unc)

    # -----------------------------------------------------------------------
    # Plot, CMS-like style with matplotlib
    # -----------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.set_yscale('log')

    # 95% and 68% expected bands
    band95 = ax.fill_between(masses, limits['exp_m2'], limits['exp_p2'],
                             color='#FFCC00', linewidth=0)
    band68 = ax.fill_between(masses, limits['exp_m1'], limits['exp_p1'],
                             color='#00CC00', linewidth=0)

    # Median expected limit
    line_exp, = ax.plot(masses, limits['exp_med'], 'k--', linewidth=2)

    # Observed limit
    line_obs = None
    if unblind:
        line_obs, = ax.plot(masses, limits['obs'], 'k-', linewidth=2,
                            marker='o', markersize=4)

    # Theory curve and its uncertainty band
    band_th = ax.fill_between(theory_masses, theory_dn, theory_up,
                              color='royalblue', alpha=0.25, linewidth=0)
    line_th, = ax.plot(theory_masses, theory_vals, 'b-', linewidth=2)

    # Expected excluded mass: vertical line where the median expected limit
    # crosses the theory curve, with the mass written next to it
    Y_MIN, Y_MAX = sigCfg['ylim']

    crossing = find_crossing(masses, limits['exp_med'], theory_masses, theory_vals)
    if crossing is not None:
        x_cross, y_cross = crossing
        ax.vlines(x_cross, Y_MIN, y_cross,
                  color='gray', linestyle=':', linewidth=1.5)
        ax.text(x_cross + 0.02, Y_MIN * 1.5,
                r'$%.2f$ TeV' % x_cross,
                fontsize=12, color='gray', rotation=90, va='bottom')

    # Axes
    ax.set_xlabel(sigCfg['xlabel'], fontsize=17, labelpad=8, ha='right', x=1.0)
    ax.set_ylabel(r'95% CL upper limit on $\sigma$ [pb]', fontsize=17, labelpad=8, ha='right', y=1.0)
    ax.set_xlim(masses[0] - 0.05, masses[-1] + 0.1)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.tick_params(axis='both', which='both', direction='in',
                   top=True, right=True, labelsize=14)

    # Legend (the theory entry shows the line on top of its band)
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

    # CMS and luminosity labels above the frame
    ax.text(0, 1.04, CMS_TEXT,
                transform=ax.transAxes, fontsize=16, verticalalignment='top')
    ax.text(1, 1.05, LUMI_TEXT,
                transform=ax.transAxes, fontsize=16,
                verticalalignment='top', horizontalalignment='right')

    # Method and eta region, bottom left
    ax.text(0.03, 0.09,
            ('cut-and-count method' if isCutAndCount else 'shape analysis'),
            transform=ax.transAxes, fontsize=16, va='bottom',fontweight='bold')
    ax.text(0.03, 0.03,
            etaDisplay,
            transform=ax.transAxes, fontsize=16, va='bottom',fontweight='bold')

    fig.tight_layout()
    fig.savefig(outPlot, dpi=150, bbox_inches='tight')
    print("Plot saved: {}".format(outPlot))

    # --- Text table of the plotted values ---
    txt_out = outPlot.replace('.pdf', '.txt')
    write_limits_table(txt_out, limits, unblind)
    print("Values saved: {}".format(txt_out))