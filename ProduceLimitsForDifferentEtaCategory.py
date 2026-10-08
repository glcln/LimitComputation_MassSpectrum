"""
Driver of the HSCP Run 3 statistical chain: datacard generation, Combine
execution and limit plotting, looped over all the analysis configurations.

For each background-prediction option (OPTION_LABELS), each method and eta
configuration (CASES) and each signal model, the driver runs the requested
steps, in this order:

    gen     CreateDatacards.py    datacards, shape files and yield table
    run     RunDatacards.py       Combine AsymptoticLimits
    draw    DrawDatacards.py      limit plot and table

The background-prediction option is hardcoded in the three scripts
(optionlabel, plus optionlabelForFile in the generation script). Before the
steps of one option are run, the driver rewrites these assignment lines in the
scripts; their original content is restored afterwards, also when a step
fails or when the driver is interrupted (Ctrl-C, kill, closed terminal).
As the scripts are modified while the driver runs:
  - do not run two instances of the driver on the same scripts, and do not
    edit or launch the three scripts by hand in the meantime;
  - if the driver is killed with `kill -9`, the scripts keep the last option
    written in them.

A step that fails ends the steps of that signal and configuration; the driver
goes on with the next one, lists the failures at the end and then exits with
status 1.

--unblind is passed to the gen and draw steps (the run step has no such
option: Combine computes the observed limit on whatever data the datacards
hold). Blinded and unblinded results are written to the same directories and
overwrite each other, so gen, run and draw must be redone together when the
blinding changes.

Usage:
    python3 ProduceLimitsForDifferentEtaCategory.py                              # everything
    python3 ProduceLimitsForDifferentEtaCategory.py --signal stau --steps draw   # redo one set of plots
    python3 ProduceLimitsForDifferentEtaCategory.py --optionLabel v2             # one option only
    python3 ProduceLimitsForDifferentEtaCategory.py --dryRun                     # print the commands only
    python3 ProduceLimitsForDifferentEtaCategory.py --unblind                    # with the observed data
"""

import os
import re
import signal
import sys
import subprocess
from optparse import OptionParser

SIGNALS_ALL = ['gluino', 'stop', 'stau']
STEPS_ALL   = ['gen', 'run', 'draw']

# ---------------------------------------------------------------------------
## COMMAND LINE
# ---------------------------------------------------------------------------
parser = OptionParser()
parser.add_option('--signal', dest='signals', default=','.join(SIGNALS_ALL),
                  help="Comma-separated list of signals to process (default: all).")
parser.add_option('--steps', dest='steps', default=','.join(STEPS_ALL),
                  help="Comma-separated list of steps among gen,run,draw (default: all).")
parser.add_option('--optionLabel', dest='optionLabels', default='',
                  help="Comma-separated subset of the optionlabel values to process "
                       "(default: all those of OPTION_LABELS).")
parser.add_option('--unblind', action='store_true', dest='unblind', default=False,
                  help="Use the observed data: passed to the gen and draw steps.")
parser.add_option('--dryRun', action='store_true', dest='dryRun', default=False,
                  help="Print the commands without running them. The scripts are "
                       "not modified.")
(options, args) = parser.parse_args()

# ---------------------------------------------------------------------------
## CONFIGURATION
# ---------------------------------------------------------------------------
# The three scripts are taken next to this driver
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# step -> script
STEP_SCRIPTS = {
    'gen'  : os.path.join(BASE_DIR, 'CreateDatacards.py'),
    'run'  : os.path.join(BASE_DIR, 'RunDatacards.py'),
    'draw' : os.path.join(BASE_DIR, 'DrawDatacards.py'),
}

# step -> settings rewritten in its script before it is run
STEP_PATCHED_VARS = {
    'gen'  : ['optionlabel', 'optionlabelForFile'],
    'run'  : ['optionlabel'],
    'draw' : ['optionlabel'],
}

# Steps whose script takes --unblind
UNBLIND_STEPS = ['gen', 'draw']

# Method and eta configurations: (flags passed to the three scripts, description)
CASES = [
    ([],                      'shape + |eta|<2.4'),
    (['--splitEta'],          'shape + split Eta1/Eta1_2p4'),
    (['--onlyEta1'],          'shape + |eta|<1'),

    (['--cac'],               'cut-and-count + |eta|<2.4'),
    (['--splitEta', '--cac'], 'cut-and-count + split Eta1/Eta1_2p4'),
    (['--onlyEta1', '--cac'], 'cut-and-count + |eta|<1'),
]

# Background-prediction options: (optionlabel, optionlabelForFile)
OPTION_LABELS = [
    ('SigmaPtoverPt_0p5_EoP_0p1_v2', '_SigmaPtoverPt_0p5_EoP_0p1'),
    ('v2',        ''),
]


# ---------------------------------------------------------------------------
## FUNCTIONS
# ---------------------------------------------------------------------------
def _assign_re(varname):
    """Regex matching a one-line, single-quoted assignment `var = '...'`."""
    return re.compile(r"^(\s*{}\s*=\s*)'[^']*'(.*)$".format(re.escape(varname)),
                      re.MULTILINE)


def patch_vars(path, assignments, write=True):
    """
    Rewrite the `var = '...'` lines of the file `path` with the values of
    `assignments` ({var: value}) and return the original content of the file.

    Each variable must be assigned exactly once in the file, otherwise a
    RuntimeError is raised and the file is left untouched. With write=False
    the file is only checked, not modified.
    """
    with open(path, 'r') as fh:
        original = fh.read()

    content = original
    for var, value in assignments.items():
        content, n = _assign_re(var).subn(
            lambda m: "{}'{}'{}".format(m.group(1), value, m.group(2)),
            content,
        )
        if n == 0:
            raise RuntimeError("No line `{} = '...'` in {}".format(var, path))
        if n > 1:
            raise RuntimeError("{} is assigned {} times in {}: ambiguous".format(var, n, path))

    if write:
        with open(path, 'w') as fh:
            fh.write(content)
    return original


def restore(path, original):
    """Write the original content back to `path`."""
    with open(path, 'w') as fh:
        fh.write(original)


def run_step(script, flags, dryRun=False):
    """Run one script with the same Python interpreter; raises CalledProcessError if it fails."""
    cmd = [sys.executable, script] + flags
    print(">>> {}".format(' '.join(cmd)), flush=True)
    if dryRun:
        return
    subprocess.run(cmd, check=True)


def _raise_exit(signum, frame):
    """Turn a termination signal into SystemExit, so that the scripts get restored."""
    sys.exit(128 + signum)


# ---------------------------------------------------------------------------
## MAIN
# ---------------------------------------------------------------------------
def main():
    signals = [s.strip() for s in options.signals.split(',') if s.strip()]
    steps   = [s.strip() for s in options.steps.split(',')   if s.strip()]
    for s in signals:
        if s not in SIGNALS_ALL:
            sys.exit("Unknown signal: {} (expected: {})".format(s, SIGNALS_ALL))
    for s in steps:
        if s not in STEPS_ALL:
            sys.exit("Unknown step: {} (expected: {})".format(s, STEPS_ALL))
    # Always in the order gen, run, draw
    steps = [s for s in STEPS_ALL if s in steps]

    for s in steps:
        if not os.path.isfile(STEP_SCRIPTS[s]):
            sys.exit("Script not found: {}".format(STEP_SCRIPTS[s]))

    option_labels = OPTION_LABELS
    if options.optionLabels:
        wanted = [o.strip() for o in options.optionLabels.split(',') if o.strip()]
        option_labels = [p for p in OPTION_LABELS if p[0] in wanted]
        missing = set(wanted) - {p[0] for p in OPTION_LABELS}
        if missing:
            sys.exit("Unknown optionlabel: {}".format(sorted(missing)))

    # Ctrl-C already raises KeyboardInterrupt; make kill and a closed terminal
    # raise too, so that the `finally` below restores the scripts
    signal.signal(signal.SIGTERM, _raise_exit)
    signal.signal(signal.SIGHUP,  _raise_exit)

    failures = []

    for optionlabel, optionlabelForFile in option_labels:
        values = {
            'optionlabel'        : optionlabel,
            'optionlabelForFile' : optionlabelForFile,
        }
        originals = {}
        try:
            # Write this option in the scripts of the requested steps
            for st in steps:
                script = STEP_SCRIPTS[st]
                originals[script] = patch_vars(
                    script, {v: values[v] for v in STEP_PATCHED_VARS[st]},
                    write=not options.dryRun)

            for flags, desc in CASES:
                for sig in signals:
                    print("\n" + "=" * 70)
                    print("  [{}] {}".format(sig, desc))
                    print("  optionlabel = {}".format(optionlabel))
                    print("  flags = {}".format(flags if flags else '(none)'))
                    print("=" * 70)

                    try:
                        for st in steps:
                            step_flags = list(flags) + ['--signal', sig]
                            if options.unblind and st in UNBLIND_STEPS:
                                step_flags.append('--unblind')
                            run_step(STEP_SCRIPTS[st], step_flags, options.dryRun)
                    except subprocess.CalledProcessError as e:
                        print("ERROR: step '{}' failed with status {} for {} / {} -> next".format(st, e.returncode, sig, desc))
                        failures.append((optionlabel, sig, desc, st, e.returncode))
        except RuntimeError as e:
            # A setting could not be rewritten: stop here (scripts restored below)
            sys.exit("ERROR: {}".format(e))
        finally:
            if not options.dryRun:
                for script, content in originals.items():
                    restore(script, content)

    print("\n" + "=" * 70)
    if failures:
        print("Done with {} failure(s):".format(len(failures)))
        for optlbl, sig, desc, st, rc in failures:
            print("  - {:7s} | {} | {} | step {} (status {})".format(sig, desc, optlbl, st, rc))
        sys.exit(1)
    print("Done without error.")

if __name__ == '__main__':
    main()