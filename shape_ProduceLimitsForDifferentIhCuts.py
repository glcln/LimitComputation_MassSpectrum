import os
import re
import sys
import subprocess

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
GEN_SCRIPT  = 'shape_createDatacard.py'
RUN_SCRIPT  = 'shape_runDatacard.py'
DRAW_SCRIPT = 'shape_drawDatacard.py'

FLAGS = ['--splitEta', '--cac']

ETA_LABEL_DIRS = [
    'Eta1p2_2p4_Ih3p1',
    'Eta1p2_2p4_Ih3p2',
    'Eta1p2_2p4_Ih3p3',
    'Eta1p2_2p4_Ih3p4',
    'Eta1p2_2p4_Ih3p5',
    'Eta1p2_2p4_Ih3p6',
    'Eta1p2_2p4_Ih3p7',
    'Eta1p2_2p4_Ih3p8',
    'Eta1p2_2p4_Ih3p9',
    'Eta1p2_2p4_Ih4p0',
]

# ---------------------------------------------------------------------------
# PATCH de la ligne etalabeldir
# ---------------------------------------------------------------------------
ETA_LINE_RE = re.compile(r"^(\s*etalabeldir\s*=\s*)'[^']*'(.*)$", re.MULTILINE)


def patch_etalabeldir(path, value):
    with open(path, 'r') as fh:
        original = fh.read()
    new_content, n = ETA_LINE_RE.subn(
        lambda m: "{}'{}'{}".format(m.group(1), value, m.group(2)),
        original,
    )
    if n == 0:
        raise RuntimeError("Aucune ligne 'etalabeldir = ...' dans {}".format(path))
    with open(path, 'w') as fh:
        fh.write(new_content)
    return original


def restore(path, original):
    with open(path, 'w') as fh:
        fh.write(original)


def run_step(script):
    cmd = [sys.executable, script] + FLAGS
    print(">>> {}".format(' '.join(cmd)))
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------------------
# BOUCLE PRINCIPALE
# ---------------------------------------------------------------------------
def main():
    scripts = [GEN_SCRIPT, RUN_SCRIPT, DRAW_SCRIPT]
    for s in scripts:
        if not os.path.isfile(s):
            sys.exit("Script introuvable : {} (lance depuis la racine du projet)".format(s))

    for eta in ETA_LABEL_DIRS:
        print("\n" + "=" * 70)
        print("  etalabeldir = {}".format(eta))
        print("=" * 70)

        originals = {}
        try:
            for s in scripts:
                originals[s] = patch_etalabeldir(s, eta)

            run_step(GEN_SCRIPT)
            run_step(RUN_SCRIPT)
            run_step(DRAW_SCRIPT)

        except subprocess.CalledProcessError as e:
            print("ERREUR ({}) pour {} -> suivant".format(e.returncode, eta))
        finally:
            for s, content in originals.items():
                restore(s, content)

    print("\nTermine.")


if __name__ == '__main__':
    main()
