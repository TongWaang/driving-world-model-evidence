"""Query task/input records without additional dependencies."""
from pathlib import Path
import argparse,json

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study',help='Study ID or system name, e.g. S04 or GenAD')
    parser.add_argument('--validation',help='Reference type, e.g. reactive_simulation')
    parser.add_argument('--status',choices=['D','P','X','NR'],help='At least one claim with this evidence status')
    parser.add_argument('--text',default='',help='Case-insensitive text search across complete records')
    args=parser.parse_args()
    sources=json.loads((ROOT/'data'/'sources.json').read_text(encoding='utf-8'))['sources']
    source_by_id={s['study_id']:s for s in sources}
    records=json.loads((ROOT/'data'/'evidence_register.json').read_text(encoding='utf-8'))['records']
    result=[]
    for record in records:
        source=source_by_id[record['study_id']]
        if args.study and args.study.lower() not in (source['study_id']+' '+source['system']).lower():
            continue
        if args.validation and record['V']!=args.validation:
            continue
        if args.status and not any(a['status']==args.status for a in record['assessments']):
            continue
        if args.text.lower() not in json.dumps(record,ensure_ascii=False).lower():
            continue
        result.append(dict(system=source['system'],source_url=source['inspected_url'],**record))
    print(json.dumps(dict(matched_records=len(result),records=result),indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
