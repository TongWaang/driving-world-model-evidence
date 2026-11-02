"""Validate package structure, manuscript arithmetic, and optional checksums.

Run from any working directory: python path/to/scripts/validate.py
No network requests or non-standard packages are needed.
"""
from pathlib import Path
import hashlib, json, math, sys, unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.analysis import compute_example
from scripts.metrics import hazardous_false_clearance, ranking_error, regret_interval, selective_risk


def read(name):
    return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))


def require(condition,message):
    if not condition:
        raise ValueError(message)


def main():
    sources=read('sources.json')['sources']
    register=read('evidence_register.json')
    records=register['records']
    contrasts=read('numerical_contrasts.json')['contrasts']
    codebook=read('codebook.json')
    source_ids={x['study_id'] for x in sources}
    record_ids={x['record_id'] for x in records}
    require(len(sources)==len(source_ids)==17,'Expected 17 distinct core studies')
    require(len(records)==len(record_ids),'Duplicate task/input IDs')
    require({r['study_id'] for r in records}==source_ids,'Every study must have task records')
    require(len(contrasts)==4,'Expected four within-study contrasts')
    require(len(register['source_manuscript_sha256'])==64,'Missing source-manuscript checksum')
    for source in sources:
        require(source['inspected_url'].startswith('https://'),'Invalid inspected source URL')
        require(source['inspected_version'] and source['locators'],'Missing source version or locator')
    for r in records:
        require(all(r.get(k) for k in ['R','A','I','U','V','source_locators','interpretation_boundary']),f'Incomplete record {r["record_id"]}')
        require(r['V'] in codebook['reference_types'],'Unknown reference type')
        require(r['provenance']['original_historical_extraction_log_available'] is False,'Historical provenance must not be fabricated')
        for a in r['assessments']:
            require(a['status'] in codebook['evidence_status'],'Unknown evidence status')
            require(a['origin'] in ['source_reported_endpoint','reviewer_added_use_question'],'Unknown claim origin')
    changes=[]
    for c in contrasts:
        require(c['study_id'] in source_ids,'Unknown contrast study')
        require(c['source_url'].startswith('https://') and c['locator'],'Missing numerical provenance')
        for m in c['metrics']:
            a,b=m['baseline'],m['comparison']
            require(all(isinstance(v,(int,float)) and math.isfinite(v) for v in [a,b]),'Invalid numeric value')
            require(m['preferred_direction'] in ['higher','lower'],'Invalid direction')
            require(len(m['source_cells'])==2,'Missing source-cell mapping')
            delta=b-a
            changes.append(dict(contrast_id=c['contrast_id'],metric=m['metric'],unit=m['unit'],
                baseline=a,comparison=b,absolute_change=round(delta,10),
                relative_change_percent=round(100*delta/a,10) if a else None,
                change_unit='percentage_points' if m['unit']=='percent' else m['unit']))
    example=read('analytical_example.json')
    calculated=compute_example(example)
    for found,expected in zip(calculated['reference_costs'],example['expected']['reference_costs']):
        require(math.isclose(found,expected,abs_tol=1e-12),'Reference cost differs from manuscript example')
    for name in example['models']:
        for key,expected in example['expected'][name].items():
            found=calculated['models'][name][key]
            require(found==expected if isinstance(expected,str) else math.isclose(found,expected,abs_tol=1e-12),f'Example {name}/{key} differs')
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py',top_level_dir=str(ROOT))
    test_result=unittest.TextTestRunner(verbosity=1).run(suite)
    require(test_result.wasSuccessful(),'Definition boundary tests failed')
    report=dict(package_version='1.0.0',status='PASS',
        counts=dict(core_studies=len(sources),task_input_records=len(records),contrasts=len(contrasts),transcribed_metric_pairs=len(changes)),
        source_table_check='Manual source checks are recorded; this script does not automatically establish primary-source truth.',
        checks=dict(schema_and_cross_links='PASS',analytical_example='PASS',boundary_tests='PASS'),
        test_count=test_result.testsRun,analytical_example=calculated,numerical_changes=changes,
        illustrative_boundary_cases=dict(
            no_hazard_denominator=hazardous_false_clearance([(0,0.01),(0.01,0.04)],[True,True],0.02),
            unresolved_practical_order=ranking_error([2,0],[0,2],0.5,{(0,1):(0.1,2.0)}),
            interval_regret=regret_interval([(3,5),(1,2),(2,4)],0),
            empty_selective_set=selective_risk([0.8,0.4],[1,0],[0.9])[0]),
        scope='Arithmetic, structure and implementation definitions only; no model-training or driving-outcome replication.')
    output=ROOT/'reports'/'validation_report.json'
    # Stable output: no local paths, host names or current timestamps.
    output.write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    manifest=ROOT/'SHA256SUMS'
    if manifest.exists():
        for line in manifest.read_text(encoding='utf-8').splitlines():
            digest,relative=line.split('  ',1)
            target=ROOT/relative
            require(target.is_file(),f'Missing manifest file: {relative}')
            require(hashlib.sha256(target.read_bytes()).hexdigest()==digest,f'Checksum mismatch: {relative}')
        print('SHA256 manifest: PASS')
    print(json.dumps(dict(status=report['status'],counts=report['counts'],boundary_tests=report['test_count']),indent=2))
    return 0


if __name__=='__main__':
    try:
        raise SystemExit(main())
    except (ValueError,KeyError,TypeError) as error:
        print(f'FAIL: {error}',file=sys.stderr)
        raise SystemExit(1)
