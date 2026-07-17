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

# Un cas = (etalabeldir, [flags], description)
# Liste vide de flags = tracker complet |eta|<2.4 en shape

CASES = [
    ('Eta2p4',   [],                      'shape + |eta|<2.4'),
    ('Eta1_2p4',   ['--splitEta'],          'shape + split Eta1/Eta1_2p4'),
    ('Eta1',   ['--onlyEta1'],          'shape + |eta|<1'),
    ('Eta1p2_2p4', ['--splitEta'],          'shape + split Eta1/Eta1p2_2p4'),
    ('Eta1p2_2p2', ['--splitEta'],          'shape + split Eta1/Eta1p2_2p2'),
]

# CASES = [
#     ('Eta2p4',   ['--cac'],                      'cut-and-count + |eta|<2.4'),
#     ('Eta1_2p4',   ['--splitEta','--cac'],          'cut-and-count + split Eta1/Eta1_2p4'),
#     ('Eta1',   ['--onlyEta1','--cac'],          'cut-and-count + |eta|<1'),
#     ('Eta1p2_2p4', ['--splitEta','--cac'],          'cut-and-count + split Eta1/Eta1p2_2p4'),
#     ('Eta1p2_2p2', ['--splitEta','--cac'],          'cut-and-count + split Eta1/Eta1p2_2p2'),
# ]

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


def run_step(script, flags):
    cmd = [sys.executable, script] + flags
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

    for eta, flags, desc in CASES:
        print("\n" + "=" * 70)
        print("  {}".format(desc))
        print("  etalabeldir = {} | flags = {}".format(eta, flags if flags else '(aucun)'))
        print("=" * 70)

        originals = {}
        try:
            for s in scripts:
                originals[s] = patch_etalabeldir(s, eta)

            run_step(GEN_SCRIPT,  flags)
            run_step(RUN_SCRIPT,  flags)
            run_step(DRAW_SCRIPT, flags)

        except subprocess.CalledProcessError as e:
            print("ERREUR ({}) pour {} [{}] -> suivant".format(e.returncode, eta, desc))
        finally:
            for s, content in originals.items():
                restore(s, content)

    print("\nTermine.")


if __name__ == '__main__':
    main()