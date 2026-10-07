"""
Run Combine on the datacards written by shape_createDatacard.py.

For one signal model (gluino, stop or stau) and one eta configuration, the
script runs `combine -M AsymptoticLimits` on every datacard found in the input
directory, one mass point after the other. Combine is run from the output
directory, so its result tree is written there directly.

Input
    <DATACARDS_BASE>/<signal>/shape_<regionBckg>_<etaLabel>_<optionlabel>/
        <Sample>.txt                (shape, default)
        <Sample>_cutandcount.txt    (--cac)

Output
    <LIMITS_BASE>/<signal>/limit_shape_<regionBckg>_<etaLabel>[_cutandcount]_<optionlabel>/
        higgsCombine.<Sample>.AsymptoticLimits.mH120.root
    ("mH120" is the default Combine mass label; the mass point is in <Sample>.)

DATACARDS_BASE and LIMITS_BASE are the Datacards/ and Limits/ directories next
to this script.

--signal, --splitEta, --onlyEta1 and the hardcoded regionBckg, optionlabel and
etalabeldir settings must be the same as in shape_createDatacard.py: the
directory names are rebuilt here from the same rules. optionlabel and
etalabeldir are rewritten in place by the driver
shape_ProduceLimitsForDifferentEtaCategory.py.

With blinded datacards (the default of shape_createDatacard.py) data_obs is
the background prediction, so the "observed" limit of the output tree is not
a limit on real data.

All mass points are processed even if Combine fails for some of them; the
script then exits with an error listing the failed mass points.

The expected significance is computed by shape_significance.py.

Usage:
    python3 shape_runDatacard.py                        # gluino, full tracker, shape
    python3 shape_runDatacard.py --cac --signal stau    # cut-and-count, stau
    # the next two need etalabeldir set as in shape_createDatacard.py
    python3 shape_runDatacard.py --onlyEta1             # central region only
    python3 shape_runDatacard.py --splitEta             # two eta categories
"""

from optparse import OptionParser
import glob
import os
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
## COMMAND LINE
# ---------------------------------------------------------------------------
parser = OptionParser()
parser.add_option('--cac', action='store_true', dest='cac', default=False,
                  help='Run on the cut-and-count datacards instead of the shape ones.')
parser.add_option('--splitEta', action='store_true', dest='splitEta', default=False,
                  help='Must match the flag of the generation script: full tracker '
                       'Eta2p4 (off) or split Eta1/Eta1_2p4 (on).')
parser.add_option('--onlyEta1', action='store_true', dest='onlyEta1', default=False,
                  help='Must match the generation script: central region |eta|<1 '
                       'only (Eta1).')
parser.add_option('--signal', dest='signal', default='gluino',
                  type='choice', choices=['gluino', 'stop', 'stau'],
                  help='Must match the generation script: gluino, stop or stau.')
(options, args) = parser.parse_args()

if options.splitEta and options.onlyEta1:
    parser.error('--splitEta and --onlyEta1 are mutually exclusive')

isCutAndCount = options.cac
splitEta      = options.splitEta
onlyEta1      = options.onlyEta1
signalType    = options.signal

# ---------------------------------------------------------------------------
## CONFIGURATION
# ---------------------------------------------------------------------------
# Must match the settings of the datacard generation script.
# optionlabel and etalabeldir are rewritten in place by the driver
# shape_ProduceLimitsForDifferentEtaCategory.py, which looks for one-line,
# single-quoted assignments: keep that form, and a single assignment of each
# in this file.
regionBckg  = '9fp10'
optionlabel = 'SigmaPtoverPt_0p5_EoP_0p1_v2'
etalabeldir = 'Eta2p4'

# Roots of the input (datacards) and output (Combine results) trees: the
# Datacards/ and Limits/ directories next to this script
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
DATACARDS_BASE = os.path.join(BASE_DIR, 'Datacards')
LIMITS_BASE    = os.path.join(BASE_DIR, 'Limits')


# ---------------------------------------------------------------------------
## FUNCTIONS
# ---------------------------------------------------------------------------
def mass_of(sample):
    """Mass point of a sample: the first number of its name (0 if none)."""
    m = re.search(r'(\d+)', sample)
    return int(m.group(1)) if m else 0


def find_samples(idir, cutAndCount):
    """
    Names of the samples that have a datacard in `idir`, sorted by mass.

    A sample <Sample> has a shape datacard <Sample>.txt and/or a cut-and-count
    datacard <Sample>_cutandcount.txt: only the kind selected by `cutAndCount`
    is considered. The yield tables (yields_*.txt) written next to the
    datacards are skipped.
    """
    suffix = '_cutandcount.txt' if cutAndCount else '.txt'
    samples = []
    for path in glob.glob(os.path.join(idir, '*.txt')):
        fname = os.path.basename(path)
        if fname.startswith('yields_'):
            continue
        if fname.endswith('_cutandcount.txt') != cutAndCount:
            continue
        samples.append(fname[:-len(suffix)])
    return sorted(samples, key=lambda s: (mass_of(s), s))


if __name__ == '__main__':

    if isCutAndCount:
        print("Running cut and count limits")
    else:
        print("Running shape limits")

    # Same eta label logic as in the generation script
    if splitEta:
        etaLabel = 'split_Eta1_' + etalabeldir
    elif onlyEta1:
        etaLabel = 'Eta1'
    else:
        etaLabel = 'Eta2p4'

    # Input directory: shape and cut-and-count datacards live side by side
    idir = os.path.join(DATACARDS_BASE, signalType, 'shape_{}_{}_{}'.format(regionBckg, etaLabel, optionlabel))

    # Output directory: one per method (shape / cut-and-count)
    odir = os.path.join(LIMITS_BASE, signalType, 'limit_shape_{}_{}{}_{}'.format(regionBckg, etaLabel, "_cutandcount" if isCutAndCount else "", optionlabel))

    if not os.path.isdir(idir):
        sys.exit("Datacard directory not found: {}".format(idir))
    os.makedirs(odir, exist_ok=True)
    print("Datacards: {}".format(idir))
    print("Limits   : {}".format(odir))

    # One datacard per mass point, named after the sample ('<Label><mass>_2024')
    endname = "_cutandcount" if isCutAndCount else ""
    samples = find_samples(idir, isCutAndCount)
    if not samples:
        sys.exit("No {} datacard found in {}".format("cut-and-count" if isCutAndCount else "shape", idir))
    print("Signal sample: {} -> {} mass points".format(signalType, len(samples)))

    failed = []
    for sample in samples:
        print("Processing: {}".format(sample))

        # Asymptotic CLs limits on the signal strength r.
        #   -n .<sample>          label of the output file
        #   --rRelAcc/--rAbsAcc   relative / absolute accuracy required on r
        #   --rMin/--rMax         range of r
        run_combine = (
            "combine -M AsymptoticLimits"
            " -n .{name}"
            " -d {idir}/{name}{endname}.txt"
            " --rRelAcc 0.000005 --rAbsAcc 0.000005"
            " --rMin -1000.0 --rMax 1000.0"
        ).format(name=sample, idir=idir, endname=endname)
        print("Running: {}".format(run_combine), flush=True)

        # Combine writes its output in its working directory: run it from odir
        status = subprocess.run(run_combine, shell=True, cwd=odir).returncode
        if status != 0:
            print("ERROR: combine exited with status {} for {}".format(status, sample))
            failed.append(sample)

    # A non-zero exit status lets the driver report the failure
    if failed:
        sys.exit("Combine failed for {} of {} mass points: {}".format(len(failed), len(samples), ', '.join(failed)))