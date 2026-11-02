"""Generate the readable S1 and repository index from the JSON records."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def load(name):
    return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))

def cell(value):
    return str(value).replace('|',' / ').replace('\n',' ')

def generate():
    sources=load('sources.json')['sources']
    records=load('evidence_register.json')['records']
    codebook=load('codebook.json')
    contrasts=load('numerical_contrasts.json')['contrasts']
    prov=load('retrieval_provenance.json')
    intro='''# Supplementary Material S1

## Scope and provenance

This supplement accompanies *A Critical Review of Evaluation Evidence for Autonomous Driving World Models* and reconstructs the register described in Revision 4. Release 1.0.0 was prepared on 2 November 2026 from the supplied manuscript and targeted primary-source checking. It contains 17 core systems, 35 task/input records and four within-study numerical contrasts.

The original historical extraction log and executable files were not supplied. The present files are a newly assembled, AI-assisted reconstruction, not evidence that this exact workflow or code existed before this release. No independent second-coder audit, model-training replication, new driving rollout or physical-road validation is claimed. All classifications are claim-specific interpretations.

The 17-system sample follows the manuscript rather than an exhaustive database search. Task variants are not independent studies. Missing quality fields mean not extracted, not necessarily absent from the source. A future author or independent audit may revise classifications through versioned changes.

## Retrieval and extraction

The reconstruction starts with the manuscript's named seed systems, follows exact-title primary records and official proceedings or linked author manuscripts, and checks the relevant method and evaluation passages. Full query families, present-day operations and access limitations are recorded in [retrieval_provenance.json](../data/retrieval_provenance.json). Database-wide screening counts and the original search history are unavailable and are not reconstructed.

The unit is study x task/input variant x specified claim. The five axes below describe an interface; they do not form a universal maturity ladder. The register separately records source-reported endpoints and reviewer-added stronger use questions. A stronger use question does not imply that the original authors claimed that capability.

## Codebook

| Field | Meaning |
| --- | --- |
'''
    lines=[intro]
    for k,v in codebook['axes'].items():
        lines.append(f'| {k} | {v} |')
    lines.extend(['','| Status | Claim-specific meaning |','| --- | --- |'])
    for k,v in codebook['evidence_status'].items():
        lines.append(f'| {k} | {v} |')
    lines.extend(['','Directness is distinct from experimental quality. D does not imply strong uncertainty estimates, matched compute, independent simulator assumptions or physical transfer. X and NR must not be read as negative experimental findings.','',
                  'Reference-process labels distinguish logged, selected qualitative, non-reactive simulation, reactive simulation, sensor-reference, hybrid-execution and behavior-rollout evaluations. They describe the inspected test rather than inheriting every use of the term closed-loop in a source.','',
                  '## Source index','','| ID | System and manuscript reference | Inspected version |','| --- | --- | --- |'])
    for s in sources:
        lines.append(f'| {s["study_id"]} | [{s["system"]}](#{s["study_id"].lower()}-{s["system"].lower()}) [{s["manuscript_reference"]}] | {s["inspected_version"]} |')
    lines.extend(['','Primary-source versions are frozen in [sources.json](../data/sources.json). A publication link identifies the bibliographic work; it is not an assertion that a later proceedings version is identical to the inspected preprint. The inspected version controls the locators and interpretations below.','',
                  '## Task and input register',''])
    for s in sources:
        lines.extend([f'### {s["study_id"]} {s["system"]}','',f'{s["title"]}. Manuscript reference [{s["manuscript_reference"]}].',
                      '',f'Inspected: [{s["inspected_version"]}]({s["inspected_url"]}); [publication record]({s["publication_url"]}).',''])
        for r in [x for x in records if x['study_id']==s['study_id']]:
            lines.extend([f'**{r["record_id"]} {r["task_variant"]}**','',
                          '| Axis | Recorded interface |','| --- | --- |'])
            for key in ['R','A','I','U','V']:
                value=r[key]+(f'; {r["reference_environment"]}' if key=='V' else '')
                lines.append(f'| {key} | {cell(value)} |')
            if r['information_conditions']:
                lines.extend(['',f'Information conditions: {r["information_conditions"]}.'])
            lines.extend(['',f'Source locator: {r["source_locators"]}.'])
            for a in r['assessments']:
                origin='Source-reported endpoint, paraphrased' if a['origin']=='source_reported_endpoint' else 'Additional use question introduced by this review'
                lines.extend(['',f'{origin}: {a["claim"]}. Status **{a["status"]}**.'])
            lines.extend(['',f'Interpretation boundary: {r["interpretation_boundary"]}',''])
    lines.extend(['## Numerical transfer register','',
                  'All values below are transcribed author-reported values, not newly trained model results. Percent-valued metrics are stored on the percent scale: a change from 0.10% to 0.05% is -0.05 percentage points and -50% relative change. Rounded equality does not imply equality of unrounded values. No uncertainty interval is reconstructed.',''])
    for c in contrasts:
        lines.extend([f'### {c["contrast_id"]} {c["study_id"]}','',
                      f'Source: [{c["version"]}]({c["source_url"]}); {c["locator"]}.',
                      '',f'Dataset and inputs: {c["dataset"]}.',
                      '',f'Baseline: {c["baseline_condition"]}. Comparison: {c["comparison_condition"]}.',
                      '',f'Aggregation: {c["aggregation"]}.','',
                      '| Metric | Unit | Baseline | Comparison |','| --- | --- | --- | --- |'])
        for m in c['metrics']:
            lines.append(f'| {m["metric"]} | {m["unit"]} | {m["baseline"]} | {m["comparison"]} |')
        lines.extend(['',c['boundary'],''])
    lines.extend(['## Analytical example and checks','',
                  'The Section 6.5 merge example is a stipulated construction. Its observation errors and action costs are separately specified. It illustrates a logical non-implication and does not measure how often the mismatch occurs. Inputs and expected manuscript values are in [analytical_example.json](../data/analytical_example.json).','',
                  'Running `python scripts/validate.py` recomputes all example values, validates structural cross-links, calculates numerical changes and runs boundary/property tests. It writes [validation_report.json](../reports/validation_report.json). The script cannot independently verify the truth of source-paper claims or replace manual table inspection.','',
                  'The checks cover strict practical-margin eligibility, half-error ties, unresolved hazard labels, undefined denominators, selective abstention and interval-regret containment. Supplied intervals are treated as inputs; no simultaneous-confidence construction is estimated by this code. Brier and selective-risk implementations are definition utilities with deterministic tests, not new driving results.','',
                  '## Reuse and correction','',
                  'Read [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the verification boundary and [DATA_DICTIONARY.md](DATA_DICTIONARY.md) for fields. Corrections should identify the study/task ID, inspected source version and passage, affected claim, proposed code and rationale. Preserve historical releases and change the data and generated S1 together.',''])
    s1='\n'.join(lines)
    (ROOT/'docs'/'S1.md').write_text(s1,encoding='utf-8')
    index=['# Driving world model evaluation evidence','',
           'Supplementary materials for **A Critical Review of Evaluation Evidence for Autonomous Driving World Models**.','',
           '**Start here:** [Read S1](docs/S1.md) | [Download S1 PDF](docs/S1.pdf) | [Evidence JSON](data/evidence_register.json) | [Numerical contrasts](data/numerical_contrasts.json) | [Verification results](reports/validation_report.json)','',
           'Version 1.0.0 - prepared 2 November 2026. **17 systems, 35 task/input records, four within-study contrasts and eight transcribed metric pairs.**','',
           'This release reconstructs the supplement described in Revision 4 from the manuscript and targeted primary-source checking. It is a newly assembled, AI-assisted register and implementation, not a recovered historical extraction log. No independent second-coder audit or new driving experiment is claimed.','',
           '## Browse by system','','| ID | System | Main distinction |','| --- | --- | --- |']
    distinctions=['Video generation versus logged action prediction','Supplied candidates and image-derived rewards','Action adherence versus perturbation reward','Conditioned forecasting versus frozen-encoder planning','Oracle/camera inputs and joint ego output','Supplied future ego poses','Camera-based reactive policy execution','Privileged-input policy execution','Sensor rendering and external actor behavior','Novel-view sensor rendering','Generated images and external traffic response','Auxiliary prediction across input/evaluation settings','Intention candidates and latent-matching selector','Online future-state evaluation and CARLA integration','Policy refinement and logged/non-reactive endpoints','Multi-agent policies and rollout diagnostics','Scene constraints, logged validity and joint rollout']
    for s,d in zip(sources,distinctions):
        index.append(f'| {s["study_id"]} | [{s["system"]}](docs/S1.md#{s["study_id"].lower()}-{s["system"].lower()}) | {d} |')
    index.extend(['','## Run the checks','',
                  'Python 3.10 or newer; no third-party dependencies are needed for validation or querying.','',
                  '```bash','python scripts/validate.py','python scripts/query.py --study GenAD','python scripts/query.py --validation reactive_simulation','python scripts/query.py --status NR --text intervention','```','',
                  'The validator checks structure, arithmetic, mathematical properties and optional file hashes. The numerical source cells were checked against primary sources during preparation; a passing script does not automatically prove literature-transcription accuracy.','',
                  '## Files','',
                  '- [S1](docs/S1.md) and [PDF](docs/S1.pdf): readable methods, codebook, source list, task variants and contrasts.',
                  '- [Evidence register](data/evidence_register.json): claim-specific five-axis records.',
                  '- [Sources](data/sources.json): inspected versions, locators and publication links.',
                  '- [Numerical contrasts](data/numerical_contrasts.json): source cells, conditions, units and boundaries.',
                  '- [Analytical inputs](data/analytical_example.json): stipulated Section 6.5 example.',
                  '- [Retrieval provenance](data/retrieval_provenance.json): actual reconstruction operations and limitations.',
                  '- [Definitions and tests](scripts/metrics.py): executable reporting definitions; [tests](tests/test_metrics.py).',
                  '- [Reproducibility](docs/REPRODUCIBILITY.md), [field definitions](docs/DATA_DICTIONARY.md), and [Chinese guide](docs/README_zh.md).','',
                  '## Interpretation','',
                  'D means a direct test of the specified endpoint, not high experimental quality. P means proxy or selected qualitative evidence. X means a different endpoint, not demonstrated incapability. NR means unresolved, not a negative result. Reviewer-added stronger use questions are explicitly separated from source-reported endpoints. Counts describe this purposive sample, not field-wide prevalence.','',
                  '## Version and citation','',
                  'Cite the associated manuscript using its final bibliographic record and identify the repository release or commit used. The manuscript itself and third-party paper PDFs are not redistributed here. Authors of cited works retain their rights. No reuse license has been selected for this release.',''])
    (ROOT/'README.md').write_text('\n'.join(index),encoding='utf-8')
    print(f'Generated readable S1 and index from {len(records)} records')

if __name__=='__main__':
    generate()
