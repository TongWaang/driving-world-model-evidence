# Driving world model evaluation evidence

Supplementary materials for **A Critical Review of Evaluation Evidence for Autonomous Driving World Models**.

**Start here:** [Read S1](docs/S1.md) | [Download S1 PDF](docs/S1.pdf) | [Evidence JSON](data/evidence_register.json) | [Numerical contrasts](data/numerical_contrasts.json) | [Verification results](reports/validation_report.json)

Version 1.0.0 - prepared 2 November 2026. **17 systems, 35 task/input records, four within-study contrasts and eight transcribed metric pairs.**

This release reconstructs the supplement described in Revision 4 from the manuscript and targeted primary-source checking. 

## Connected-driving revision (Deep Revised, 3 November 2026)

The manuscript has since been revised and retitled **World Models for Connected Driving through Distributed Prediction and Evidence Assessment**. This repository now additionally hosts the code and data for that revision's numerical material:

- [`scripts/numerical_illustration.py`](scripts/numerical_illustration.py) — standalone, dependency-free executable for Equation (2) (temporal-support acceptance) and Equation (3) (deadline-aware value of information), matching manuscript Section 7.5.
- [`reports/numerical_illustration_results.txt`](reports/numerical_illustration_results.txt) — the exact console output produced by the script.
- [`data/core_evidence_audit.csv`](data/core_evidence_audit.csv) — the four-system targeted audit of Appendix A / Table 4 (World4V2X, V2X-WAM, offline MARL, OmniV2X).

Run it with:

```bash
python scripts/numerical_illustration.py
```

The sections below remain the v1.0.0 evidence package for the earlier *critical review* revision (17 systems). The new files are additive: `SHA256SUMS` and the `v1.0.0` archive cover only the earlier release files.

## Browse by system

| ID | System | Main distinction |
| --- | --- | --- |
| S01 | [DriveDreamer](docs/S1.md#s01-drivedreamer) | Video generation versus logged action prediction |
| S02 | [Drive-WM](docs/S1.md#s02-drive-wm) | Supplied candidates and image-derived rewards |
| S03 | [Vista](docs/S1.md#s03-vista) | Action adherence versus perturbation reward |
| S04 | [GenAD](docs/S1.md#s04-genad) | Conditioned forecasting versus frozen-encoder planning |
| S05 | [OccWorld](docs/S1.md#s05-occworld) | Oracle/camera inputs and joint ego output |
| S06 | [Copilot4D](docs/S1.md#s06-copilot4d) | Supplied future ego poses |
| S07 | [MILE](docs/S1.md#s07-mile) | Camera-based reactive policy execution |
| S08 | [Think2Drive](docs/S1.md#s08-think2drive) | Privileged-input policy execution |
| S09 | [UniSim](docs/S1.md#s09-unisim) | Sensor rendering and external actor behavior |
| S10 | [NeuRAD](docs/S1.md#s10-neurad) | Novel-view sensor rendering |
| S11 | [DriveArena](docs/S1.md#s11-drivearena) | Generated images and external traffic response |
| S12 | [LAW](docs/S1.md#s12-law) | Auxiliary prediction across input/evaluation settings |
| S13 | [World4Drive](docs/S1.md#s13-world4drive) | Intention candidates and latent-matching selector |
| S14 | [WoTE](docs/S1.md#s14-wote) | Online future-state evaluation and CARLA integration |
| S15 | [WorldRFT](docs/S1.md#s15-worldrft) | Policy refinement and logged/non-reactive endpoints |
| S16 | [TrafficBots](docs/S1.md#s16-trafficbots) | Multi-agent policies and rollout diagnostics |
| S17 | [SceneDiffuser](docs/S1.md#s17-scenediffuser) | Scene constraints, logged validity and joint rollout |

## Run the checks

Python 3.10 or newer; no third-party dependencies are needed for validation or querying.

```bash
python scripts/validate.py
python scripts/query.py --study GenAD
python scripts/query.py --validation reactive_simulation
python scripts/query.py --status NR --text intervention
```

The validator checks structure, arithmetic, mathematical properties and optional file hashes. The numerical source cells were checked against primary sources during preparation; a passing script does not automatically prove literature-transcription accuracy.

## Files

- [S1](docs/S1.md) and [PDF](docs/S1.pdf): readable methods, codebook, source list, task variants and contrasts.
- [Evidence register](data/evidence_register.json): claim-specific five-axis records.
- [Sources](data/sources.json): inspected versions, locators and publication links.
- [Numerical contrasts](data/numerical_contrasts.json): source cells, conditions, units and boundaries.
- [Analytical inputs](data/analytical_example.json): stipulated Section 6.5 example.
- [Retrieval provenance](data/retrieval_provenance.json): actual reconstruction operations and limitations.
- [Definitions and tests](scripts/metrics.py): executable reporting definitions; [tests](tests/test_metrics.py).
- [Reproducibility](docs/REPRODUCIBILITY.md), [field definitions](docs/DATA_DICTIONARY.md), and [Chinese guide](docs/README_zh.md).

## Interpretation

D means a direct test of the specified endpoint, not high experimental quality. P means proxy or selected qualitative evidence. X means a different endpoint, not demonstrated incapability. NR means unresolved, not a negative result. Reviewer-added stronger use questions are explicitly separated from source-reported endpoints. Counts describe this purposive sample, not field-wide prevalence.

## Version and citation

Cite the associated manuscript using its final bibliographic record and identify the repository release or commit used. The manuscript itself and third-party paper PDFs are not redistributed here. Authors of cited works retain their rights. No reuse license has been selected for this release.
