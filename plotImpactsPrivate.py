"""
Wrapper around the plotImpacts.py of Combine.

Replaces the "CMS Internal" logo by a free label (default: "Private work (CMS
data)") and can add a mass-point label at the top right.

No file of Combine is modified: the three drawing functions used by
plotImpacts.py (ModTDRStyle, DrawCMSLogo, DrawTitle) are replaced for the time
of the execution, then restored in a `finally`.

Every option that is not defined here is passed as it is to plotImpacts.py
(-i, -o, -t, --left-margin, --label-size, --blind, ...).

plotImpacts.py is looked for in the PATH, then in the scripts directory of the
CMSSW area ($CMSSW_BASE/bin/$SCRAM_ARCH); --orig-plotter gives its path
explicitly.

Usage:
    python3 plotImpactsPrivate.py -i Gluino2000_2024_impacts.json \
        -o Gluino2000_2024_impacts -t nuis_labels.json \
        --left-margin 0.45 --label-size 0.028 \
        --extra-label "m_{#tilde{g}} = 2000 GeV"

Position of the labels (band above the frame):
    [legend]  Private work (CMS data)     <extra>  r_hat = ...
The <extra> label is merged with the r_hat title when the latter is drawn;
otherwise (--blind) it is right-aligned on its own. If the two labels overlap,
reduce --header-size and/or widen the canvas with --canvas-width 900.

This script is called by NuisanceImpactParameter.py.
"""

import argparse
import importlib
import os
import runpy
import shutil
import sys

import ROOT

# Font of the "private work" label: 52 = italic helvetica (as "Internal"),
# 42 = regular helvetica.
PRIVATE_FONT = 52
EXTRA_FONT = 42

# -----------------------------------------------------------------------
## COMMAND LINE: only our own options are consumed, the rest goes to the plotter
# -----------------------------------------------------------------------
pre = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
pre.add_argument('--private-label', default='Private work (CMS data)',
                 help='Text replacing "CMS Internal" (empty = nothing).')
pre.add_argument('--extra-label', default='',
                 help='Extra right-aligned label, e.g. "m_{#tilde{g}} = 2000 GeV".')
pre.add_argument('--header-size', type=float, default=0.55,
                 help='Size of the labels, in units of the top margin (default 0.55; '
                      '0.608 is the size of the original "Internal").')
pre.add_argument('--canvas-width', type=int, default=None,
                 help='Canvas width in pixels (default: 700, or 900 with --checkboxes).')
pre.add_argument('--orig-plotter', default=None,
                 help='Path of the original plotImpacts.py (default: the one in the PATH).')
opts, rest = pre.parse_known_args()

sys.argv = [sys.argv[0]] + rest
isBlind = '--blind' in rest

# -----------------------------------------------------------------------
## Original plotter
# -----------------------------------------------------------------------
orig = opts.orig_plotter or shutil.which('plotImpacts.py')
if not orig and 'CMSSW_BASE' in os.environ and 'SCRAM_ARCH' in os.environ:
    # scripts directory of the CMSSW area, in case it is not in the PATH
    orig = os.path.join(os.environ['CMSSW_BASE'], 'bin', os.environ['SCRAM_ARCH'], 'plotImpacts.py')
if not orig or not os.path.isfile(orig):
    sys.exit('plotImpacts.py not found: set up the Combine environment or give '
             '--orig-plotter <path>.')

# -----------------------------------------------------------------------
## Plotting module of Combine (its name depends on the version)
# -----------------------------------------------------------------------
plot = None
for modname in ('HiggsAnalysis.CombinedLimit.util.plotting',
                'HiggsAnalysis.CombinedLimit.plotting',
                'CombineHarvester.CombineTools.plotting'):
    try:
        plot = importlib.import_module(modname)
        break
    except ImportError:
        continue
if plot is None:
    sys.exit('Plotting module of Combine not found (is the CMSSW environment set up?).')

_orig_ModTDRStyle = plot.ModTDRStyle
_orig_DrawCMSLogo = plot.DrawCMSLogo
_orig_DrawTitle = plot.DrawTitle


# -----------------------------------------------------------------------
## Drawing of the labels
# -----------------------------------------------------------------------
def drawHeader(pad, mainText, extraText, size):
    """Band above the frame: mainText left-aligned, extraText right-aligned.

    The pads of plotImpacts cover the whole canvas (only the margins change),
    so the NDC coordinates of the pad are those of the canvas.
    """
    pad.cd()
    l = pad.GetLeftMargin()
    t = pad.GetTopMargin()

    padRatio = (float(pad.GetWh()) * pad.GetAbsHNDC()) / (float(pad.GetWw()) * pad.GetAbsWNDC())
    if padRatio < 1.0:
        padRatio = 1.0

    y = 1.0 - t + 0.2 * t  # same offset as DrawCMSLogo / DrawTitle

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(ROOT.kBlack)
    latex.SetTextSize(size * t / padRatio)

    if mainText:
        latex.SetTextFont(PRIVATE_FONT)
        latex.SetTextAlign(11)
        latex.DrawLatex(l, y, mainText)

    if extraText:
        latex.SetTextFont(EXTRA_FONT)
        latex.SetTextAlign(31)
        latex.DrawLatex(1.0 - ROOT.gStyle.GetPadRightMargin(), y, extraText)


def ModTDRStyle(width=600, height=600, t=0.06, b=0.12, l=0.16, r=0.04):
    """Original style, with the canvas width of --canvas-width if given."""
    if opts.canvas_width:
        width = opts.canvas_width
    _orig_ModTDRStyle(width=width, height=height, t=t, b=b, l=l, r=r)


def DrawCMSLogo(pad, cmsText, extraText, iPosX, relPosX, relPosY, relExtraDY,
                extraText2='', cmsTextSize=0.8):
    """Replace the CMS logo and its subtitle by the "private work" label.

    The extra label is only drawn here when the r_hat title is absent
    (--blind); otherwise it is merged with it in DrawTitle.
    """
    drawHeader(pad, opts.private_label,
               opts.extra_label if isBlind else '',
               opts.header_size)


def DrawTitle(pad, text, align, textOffset=0.2, textSize=0.6):
    """Prefix the right-aligned title (r_hat) with the extra label."""
    if align == 3 and opts.extra_label and not isBlind:
        text = '{}   {}'.format(opts.extra_label, text)
        textSize = min(textSize, opts.header_size)
    _orig_DrawTitle(pad, text, align, textOffset, textSize)


# -----------------------------------------------------------------------
## Run the original plotter with the replaced functions
# -----------------------------------------------------------------------
try:
    plot.ModTDRStyle = ModTDRStyle
    plot.DrawCMSLogo = DrawCMSLogo
    plot.DrawTitle = DrawTitle
    runpy.run_path(orig, run_name='__main__')
finally:
    plot.ModTDRStyle = _orig_ModTDRStyle
    plot.DrawCMSLogo = _orig_DrawCMSLogo
    plot.DrawTitle = _orig_DrawTitle