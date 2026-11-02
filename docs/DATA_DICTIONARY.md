# Data dictionary

All JSON files use UTF-8, schema version 1.0, stable study IDs S01-S17 and stable task IDs Sxx-Tyy. Empty or null values must not be interpreted as zero.

| File | Main collection | Meaning |
| --- | --- | --- |
| sources.json | sources | One bibliographic/inspection record per core system |
| evidence_register.json | records | One study-task/input-claim grouping; several claims can share an interface |
| numerical_contrasts.json | contrasts | Four paired comparisons and eight metric pairs |
| analytical_example.json | models | Stipulated inputs and expected Section 6.5 calculations |
| codebook.json | axes and evidence_status | Five-axis definitions and claim-status rules |
| retrieval_provenance.json | operations | Actual reconstruction operations and unavailable historical information |

## Evidence records

| Field | Meaning |
| --- | --- |
| record_id / study_id | Stable task/input key and parent source key |
| task_variant | Specific input or evaluation setting |
| R | Predicted representation or decoded observations |
| A | Supplied action conditions and/or ego outputs |
| I | Mechanism producing scene or actor response |
| U | Stage/role of prediction use, such as auxiliary training, online selection or simulation |
| V | Inspected reference-process category |
| reference_environment | Dataset or simulator associated with the record |
| information_conditions | Oracle, privileged, future or other notable information supplied |
| source_reported_endpoint | Paraphrased endpoint, not a verbatim author quotation |
| assessments | Claim, origin and D/P/X/NR status |
| source_locators | Section, appendix, figure or table to inspect in the frozen version |
| interpretation_boundary | Why the direct endpoint does not automatically establish a stronger use |
| experimental_quality | Selected quality fields; null means not extracted, not absent from source |
| provenance | Creation date, reconstruction basis and historical-log availability |

An assessment with origin `reviewer_added_use_question` is a question introduced by this review, not an assertion that the original authors made that claim. Multiple assessments and records must not be counted as independent empirical studies.

## Numerical contrasts

Baseline and comparison values preserve the source's displayed precision. `percent` means a value on a 0-100 scale, including small values such as 0.10 for 0.10%. The validator reports absolute differences in percentage points for these metrics. It does not turn rounded table values into confidence intervals or significance tests.

`source_cells` identify the original rows and columns. The source URL and version identify the inspected artifact. Differences between inspected preprints and formal publications are not assumed away.
