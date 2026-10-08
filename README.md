# LimitComputation_MassSpectrum

Statistical interpretation of the CMS Run 3 search for Heavy Stable Charged
Particles (HSCP) with the mass-spectrum approach: Combine datacards, expected
limits, significance and fit diagnostics for gluino, stop and stau signals,
on the 2024 data (109 fb^-1 at 13.6 TeV).

The code derives from the Run 2 package
(https://github.com/dapparu/LimitComputation_MassSpectrum); only the Run 3
chain, made of the `shape_*.py` scripts, is kept here.

## Requirements

- A CMSSW area with Combine (`combine`, `text2workspace.py`) and
  CombineHarvester (`combineTool.py`, `plotImpacts.py`), after `cmsenv`:
  - https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/
  - https://cms-analysis.github.io/CombineHarvester/
- Python 3 with PyROOT, numpy and matplotlib.

The scripts can be launched from any directory: they read and write the
`Datacards/`, `Limits/` and `Results/` directories located next to them.

## Inputs

Only `CreateDatacards.py` reads the analysis inputs. Their locations are
hardcoded at the top of that script and must be adapted:

- `BASE_SIGNAL_DIR`: signal mass histograms, one file per mass point
  (see `SIGNAL_CONFIG` for the file names and mass points);
- `BASE_BKG_DIR`: background prediction, one file per systematic variation,
  named `JetMET2024_V<version>_<eta><option>_<variation>.root`
  (see `BKG_FILE_SUFFIX`).

## Configurations

| Choice | Values |
|---|---|
| Signal (`--signal`) | `gluino` (default), `stop`, `stau` |
| Eta configuration | full tracker \|eta\|<2.4 (default), central region \|eta\|<1 (`--onlyEta1`), two categories \|eta\|<1 and 1<=\|eta\|<2.4 (`--splitEta`) |
| Method | shape analysis of the mass spectrum (default), cut-and-count in a mass window (`--cac`) |
| Background-prediction option | `optionlabel`: `SigmaPtoverPt_0p5_EoP_0p1_v2` (default) or `v2` |

## Main chain

`ProduceLimitsForDifferentEtaCategory.py` runs the three steps below for
every option, method, eta configuration and signal:

```bash
python3 ProduceLimitsForDifferentEtaCategory.py              # everything
python3 ProduceLimitsForDifferentEtaCategory.py --dryRun     # print the commands only
python3 ProduceLimitsForDifferentEtaCategory.py --signal stau --steps draw
python3 ProduceLimitsForDifferentEtaCategory.py --optionLabel v2
```

| Step | Script | Output |
|---|---|---|
| `gen` | `CreateDatacards.py` | `Datacards/<signal>/shape_<region>_<etaLabel>_<optionlabel>/`: datacards, shape ROOT files, yield table |
| `run` | `RunDatacards.py` | `Limits/<signal>/limit_shape_<region>_<etaLabel>[_cutandcount]_<optionlabel>/`: Combine AsymptoticLimits trees |
| `draw` | `DrawDatacards.py` | limit plot (`.pdf`) and table (`.txt`), in the same directory |

Each script can also be run on its own, with the same flags (`--signal`,
`--splitEta`, `--onlyEta1`, `--cac`). In these three scripts the
background-prediction option is the hardcoded `optionlabel` setting, which the
driver rewrites in place while it runs (and restores afterwards).

## Other scripts

They are run by hand, after the datacards (and, for the first one, the limit
tables) have been produced. `--optionLabel` selects the background-prediction
option.

| Script | Purpose |
|---|---|
| `DrawCompareSignal.py` | summary plot per signal: expected limits of the three eta configurations, Run 2 observed limit and theoretical cross sections; written to `Results/` |
| `Significance.py` | expected significance versus mass |
| `NuisanceImpactParameter.py` | nuisance parameter impacts (uses `plotImpactsPrivate.py`, a wrapper around the `plotImpacts.py` of Combine) |
| `CorrelationMatrix.py` | correlation matrix of the nuisance parameters, from FitDiagnostics |

The docstring at the top of each script describes its inputs, outputs and
options; `--help` lists the options.

## Blinding

By default nothing uses the observed data: the datacards are written with the
background prediction in place of the data, and the significance, impact and
correlation studies run on Asimov datasets.

`--unblind` switches to the observed data. In `CreateDatacards.py` it
writes the observed mass spectrum in the datacards; in `DrawDatacards.py`
it draws the observed limit. The driver passes it to both steps. Blinded and
unblinded results are written to the same directories and overwrite each
other, so the three steps must be redone together when the blinding changes.

## Other files

- `tdrstyle.py`: CMS plotting style used by `Significance.py`.
- `xsec/`: reference material that is not read by the scripts: SUSY cross
  sections at 13 TeV (from https://github.com/fuenfundachtzig/xsec) and the
  HEPData record of the Run 2 limits (EXO-18-002).