"""
Driver for the full HSCP Run 3 statistical chain: datacard generation,
Combine execution and limit plotting, looped over every analysis
configuration.

For each background-prediction configuration, eta configuration and signal
model, the driver:
  1. patches the shared hardcoded settings (`etalabeldir`, `optionlabel`,
     `optionlabelForFile`) in the three analysis scripts,
  2. runs the requested steps (gen / run / draw) with the matching flags,
  3. restores the scripts to their original content.

The analysis scripts keep their configuration hardcoded, so patching is done
by rewriting the assignment lines in place. Originals are always restored,
including when a step fails or the driver is interrupted.

Usage:
    python3 shape_ProduceLimitsForDifferentEtaCategory.py                                # everything
    python3 shape_ProduceLimitsForDifferentEtaCategory.py --signal stau --steps draw     # redo one set of plots
    python3 shape_ProduceLimitsForDifferentEtaCategory.py --optionLabel CorrelationAdded_SigmaPtoverPt_0p5_EoP_0p1
    python3 shape_ProduceLimitsForDifferentEtaCategory.py --dryRun                       # print commands only
"""

import os
import re
import sys
import subprocess
from optparse import OptionParser

SIGNALS_ALL = ['gluino', 'stop', 'stau']
STEPS_ALL   = ['gen', 'run', 'draw']

parser = OptionParser()
parser.add_option('--signal', dest='signals', default=','.join(SIGNALS_ALL),
                  help="Signaux a traiter, separes par des virgules (defaut: tous).")
parser.add_option('--steps', dest='steps', default=','.join(STEPS_ALL),
                  help="Etapes a executer parmi gen,run,draw (defaut: toutes).")
parser.add_option('--dryRun', action='store_true', dest='dryRun', default=False,
                  help="Affiche les commandes sans les executer.")
parser.add_option('--optionLabel', dest='optionLabels', default='',
                  help="Sous-ensemble d'optionlabel a traiter, separes par des "
                       "virgules (defaut: tous ceux de OPTION_LABELS).")
(options, args) = parser.parse_args()

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
GEN_SCRIPT  = 'shape_createDatacard.py'
RUN_SCRIPT  = 'shape_runDatacard.py'
DRAW_SCRIPT = 'shape_drawDatacard.py'


CASES = [
    ('Eta2p4',               [], 'shape + |eta|<2.4'),
    ('Eta1_2p4', ['--splitEta'], 'shape + split Eta1/Eta1_2p4'),
    ('Eta1',     ['--onlyEta1'], 'shape + |eta|<1'),
    #('Eta1p2_2p4', ['--splitEta'],          'shape + split Eta1/Eta1p2_2p4'),
    #('Eta1p2_2p2', ['--splitEta'],          'shape + split Eta1/Eta1p2_2p2'),

    ('Eta2p4',   ['--cac'],                      'cut-and-count + |eta|<2.4'),
    ('Eta1_2p4',   ['--splitEta','--cac'],          'cut-and-count + split Eta1/Eta1_2p4'),
    ('Eta1',   ['--onlyEta1','--cac'],          'cut-and-count + |eta|<1'),
    #('Eta1p2_2p4', ['--splitEta','--cac'],          'cut-and-count + split Eta1/Eta1p2_2p4'),
    #('Eta1p2_2p2', ['--splitEta','--cac'],          'cut-and-count + split Eta1/Eta1p2_2p2'),
]

OPTION_LABELS = [
    ('SigmaPtoverPt_0p5_EoP_0p1_v2', '_SigmaPtoverPt_0p5_EoP_0p1'),
    ('v2',        ''),
]

# ---------------------------------------------------------------------------
# PATCH de la ligne etalabeldir
# ---------------------------------------------------------------------------
def _assign_re(varname):
    """Regex matching a single-quoted assignment `var = '...'` on one line."""
    return re.compile(r"^(\s*{}\s*=\s*)'[^']*'(.*)$".format(re.escape(varname)),
                      re.MULTILINE)

ASSIGN_RE = {v: _assign_re(v) for v in
             ('etalabeldir', 'optionlabel', 'optionlabelForFile')}

# Variables qui n'existent que dans certains scripts
OPTIONAL_VARS = {'optionlabelForFile'}


def patch_vars(path, assignments):
    """Rewrite the given `var = '...'` lines in `path`. Returns the original."""
    with open(path, 'r') as fh:
        original = fh.read()

    content = original
    for var, value in assignments.items():
        content, n = ASSIGN_RE[var].subn(
            lambda m: "{}'{}'{}".format(m.group(1), value, m.group(2)),
            content,
        )
        if n == 0 and var not in OPTIONAL_VARS:
            raise RuntimeError("Aucune ligne '{} = ...' dans {}".format(var, path))
        if n > 1:
            raise RuntimeError("{} assigne {} fois dans {} — ambigu".format(var, n, path))

    with open(path, 'w') as fh:
        fh.write(content)
    return original


def restore(path, original):
    with open(path, 'w') as fh:
        fh.write(original)


def run_step(script, flags, dryRun=False):
    cmd = [sys.executable, script] + flags
    print(">>> {}".format(' '.join(cmd)))
    if dryRun:
        return
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    scripts = [GEN_SCRIPT, RUN_SCRIPT, DRAW_SCRIPT]
    for s in scripts:
        if not os.path.isfile(s):
            sys.exit("Script introuvable : {} (lance depuis la racine du projet)".format(s))

    signals = [s.strip() for s in options.signals.split(',') if s.strip()]
    steps   = [s.strip() for s in options.steps.split(',')   if s.strip()]
    for s in signals:
        if s not in SIGNALS_ALL:
            sys.exit("Signal inconnu : {} (attendu : {})".format(s, SIGNALS_ALL))
    for s in steps:
        if s not in STEPS_ALL:
            sys.exit("Etape inconnue : {} (attendu : {})".format(s, STEPS_ALL))

    option_labels = OPTION_LABELS
    if options.optionLabels:
        wanted = [o.strip() for o in options.optionLabels.split(',') if o.strip()]
        option_labels = [p for p in OPTION_LABELS if p[0] in wanted]
        missing = set(wanted) - {p[0] for p in OPTION_LABELS}
        if missing:
            sys.exit("optionlabel inconnu(s) : {}".format(sorted(missing)))

    step_scripts = {'gen': GEN_SCRIPT, 'run': RUN_SCRIPT, 'draw': DRAW_SCRIPT}
    failures = []

    for optionlabel, optionlabelForFile in option_labels:
        for eta, flags, desc in CASES:
            originals = {}
            try:
                for s in scripts:
                    originals[s] = patch_vars(s, {
                        'etalabeldir'        : eta,
                        'optionlabel'        : optionlabel,
                        'optionlabelForFile' : optionlabelForFile,
                    })

                for signal in signals:
                    print("\n" + "=" * 70)
                    print("  [{}] {}".format(signal, desc))
                    print("  etalabeldir = {} | optionlabel = {}".format(eta, optionlabel))
                    print("  flags = {}".format(flags if flags else '(aucun)'))
                    print("=" * 70)

                    sig_flags = list(flags) + ['--signal', signal]
                    try:
                        for st in steps:
                            run_step(step_scripts[st], sig_flags, options.dryRun)
                    except subprocess.CalledProcessError as e:
                        print("ERREUR ({}) pour {} / {} -> suivant".format(e.returncode, signal, desc))
                        failures.append((optionlabel, signal, eta, desc, e.returncode))
            finally:
                for s, content in originals.items():
                    restore(s, content)

    print("\n" + "=" * 70)
    if failures:
        print("Termine avec {} echec(s) :".format(len(failures)))
        for optlbl, signal, eta, desc, rc in failures:
            print("  - {:7s} | {:10s} | {} | {} (code {})".format(signal, eta, desc, optlbl, rc))
    else:
        print("Termine sans erreur.")

if __name__ == '__main__':
    main()