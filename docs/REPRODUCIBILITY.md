# Reproducibility and verification boundary

Run `python scripts/validate.py` from the repository root. It also works with an absolute script path from another directory. Python 3.10 or newer is sufficient; no network, GPU, dataset download or third-party Python package is needed.

The validator checks source/task cross-links and required fields, computes changes in the four numerical contrasts, recomputes every expected Section 6.5 example value, and executes the tests in `tests/test_metrics.py`. Results are written deterministically to `reports/validation_report.json`. If `SHA256SUMS` exists, it additionally checks the release file hashes.

## What a passing result establishes

- The stored records are internally linked and structurally complete for the selected fields.
- The analytical example and displayed changes follow from their stored numeric inputs.
- The implementations handle practical-margin boundaries, predictor ties, unresolved reference labels, undefined denominators and selective abstention as specified.
- The standard finite-candidate regret bound and interval bounds pass the provided property checks.

## What requires source or empirical evidence

Manual source inspection is still required to verify transcribed table cells and interpret experiments. The code does not query papers and prove their content. A wrong source interpretation can be internally consistent.

The code does not train any audited neural model, replicate any driving benchmark, estimate physical counterfactual outcomes, construct simultaneous confidence intervals, or establish calibrated traffic response. It accepts intervals as supplied inputs. Statistical validity remains dependent on how those intervals and data were obtained.

The analytical observation errors and action costs are separately stipulated. Definition tests of Brier score or selective risk are not new driving results. The study is a critical purposive synthesis; sample counts do not estimate field-wide prevalence.

## Regenerating files

`python scripts/build_docs.py` regenerates the Markdown S1 and README from JSON. Optional `python scripts/render_s1_pdf.py` regenerates the readable S1 PDF and requires ReportLab. Only PDF regeneration needs this optional dependency. PDF page layout was visually checked for the prepared release.

`python scripts/package_release.py` creates a ZIP in the parent directory and writes SHA256SUMS. Run it only after validation and document generation. Regenerating or editing files after packaging invalidates the stored release checksums; create a fresh package after the changes.

## Provenance

This is a newly assembled, AI-assisted reconstruction requested after review of Revision 4. The original S1, machine-readable files and original script were not supplied. No historical search counts, independent second coder, new experiment or author identity is invented. The source-manuscript SHA256 identifies the local manuscript used without redistributing it.
