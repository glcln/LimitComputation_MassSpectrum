#!/usr/bin/env python3
"""
Wrapper autour du plotImpacts.py de Combine.

Remplace le logo "CMS Internal" par un label libre (defaut :
"Private work (CMS simulation/data)") et ajoute un label de point de masse
en haut a droite.

Aucun fichier de Combine n'est modifie : les trois fonctions de dessin
utilisees par plotImpacts.py (ModTDRStyle, DrawCMSLogo, DrawTitle) sont
patchees le temps de l'execution puis restaurees dans un finally.

Toutes les options non reconnues ici sont transmises telles quelles a
plotImpacts.py (-i, -o, -t, --left-margin, --label-size, --blind, ...).

Usage :
    python3 plotImpactsPrivate.py -i Gluino2000_2024_impacts.json \
        -o Gluino2000_2024_impacts -t nuis_labels.json \
        --left-margin 0.45 --label-size 0.028 \
        --extra-label "m_{#tilde{g}} = 2000 GeV"

Placement des labels (bande au-dessus du cadre) :
    [legende types]  Private work (CMS simulation/data)     <extra>  r_hat = ...
Le label <extra> est fusionne avec le titre r_hat quand celui-ci est trace,
sinon (--blind) il est cadre a droite tout seul. Si les deux labels se
chevauchent : reduire --header-size et/ou elargir avec --canvas-width 900.
"""

import argparse
import importlib
import os
import runpy
import shutil
import sys

import ROOT

# Chemin par defaut vers le plotImpacts.py d'origine (sinon $PATH).
DEFAULT_ORIG = ('/mnt/safe/ui3_1/cms/gcoulon/CMSSW_15_0_13_patch1/'
                'bin/el9_amd64_gcc12/plotImpacts.py')

# Police du label "private work" : 52 = helvetica italique (comme "Internal"),
# 42 = helvetica normal.
PRIVATE_FONT = 52
EXTRA_FONT = 42

# -----------------------------------------------------------------------
# CLI : on ne consomme que nos propres options, le reste part au plotter
# -----------------------------------------------------------------------
pre = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
pre.add_argument('--private-label', default='Private work (CMS data)',
                 help='Texte qui remplace "CMS Internal" (vide = rien).')
pre.add_argument('--extra-label', default='',
                 help='Label additionnel cadre a droite, ex: "m_{#tilde{g}} = 2000 GeV".')
pre.add_argument('--header-size', type=float, default=0.55,
                 help='Taille des labels, en unites de la marge haute (defaut 0.55, '
                      '0.608 = taille du "Internal" d origine).')
pre.add_argument('--canvas-width', type=int, default=None,
                 help='Largeur du canvas en pixels (defaut : 700, ou 900 avec --checkboxes).')
pre.add_argument('--orig-plotter', default=None,
                 help='Chemin du plotImpacts.py d origine.')
opts, rest = pre.parse_known_args()

sys.argv = [sys.argv[0]] + rest
isBlind = '--blind' in rest

# -----------------------------------------------------------------------
# Localisation du plotter d'origine
# -----------------------------------------------------------------------
orig = opts.orig_plotter or DEFAULT_ORIG
if not os.path.isfile(orig):
    orig = shutil.which('plotImpacts.py')
if not orig or not os.path.isfile(orig):
    sys.exit('plotImpacts.py introuvable : passer --orig-plotter <chemin>.')

# -----------------------------------------------------------------------
# Module de plotting de Combine (le nom a change selon les versions)
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
    sys.exit('Module de plotting de Combine introuvable (cmsenv fait ?).')

_orig_ModTDRStyle = plot.ModTDRStyle
_orig_DrawCMSLogo = plot.DrawCMSLogo
_orig_DrawTitle = plot.DrawTitle


# -----------------------------------------------------------------------
# Dessin des labels
# -----------------------------------------------------------------------
def drawHeader(pad, mainText, extraText, size):
    """Bande au-dessus du cadre : mainText cale a gauche, extraText a droite.

    Les pads de plotImpacts couvrent tout le canvas (seules les marges
    changent), donc les coordonnees NDC du pad sont celles du canvas.
    """
    pad.cd()
    l = pad.GetLeftMargin()
    t = pad.GetTopMargin()

    padRatio = (float(pad.GetWh()) * pad.GetAbsHNDC()) / (float(pad.GetWw()) * pad.GetAbsWNDC())
    if padRatio < 1.0:
        padRatio = 1.0

    y = 1.0 - t + 0.2 * t  # meme offset que DrawCMSLogo / DrawTitle

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
    if opts.canvas_width:
        width = opts.canvas_width
    _orig_ModTDRStyle(width=width, height=height, t=t, b=b, l=l, r=r)


def DrawCMSLogo(pad, cmsText, extraText, iPosX, relPosX, relPosY, relExtraDY,
                extraText2='', cmsTextSize=0.8):
    """Remplace le logo CMS + son sous-titre par le label "private work".

    Le label de masse n'est trace ici que si le titre r_hat est absent
    (--blind) ; sinon il est fusionne avec lui dans DrawTitle.
    """
    drawHeader(pad, opts.private_label,
               opts.extra_label if isBlind else '',
               opts.header_size)


def DrawTitle(pad, text, align, textOffset=0.2, textSize=0.6):
    """Prefixe le titre cadre a droite (r_hat) par le label de masse."""
    if align == 3 and opts.extra_label and not isBlind:
        text = '{}   {}'.format(opts.extra_label, text)
        textSize = min(textSize, opts.header_size)
    _orig_DrawTitle(pad, text, align, textOffset, textSize)


# -----------------------------------------------------------------------
# Execution du plotter d'origine avec les fonctions patchees
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
