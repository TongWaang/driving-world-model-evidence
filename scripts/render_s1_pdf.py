"""Optional PDF renderer. Requires ReportLab; validation does not require it."""
from functools import partial
from pathlib import Path
from xml.sax.saxutils import escape
import json
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle,getSampleStyleSheet
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle

ROOT=Path(__file__).resolve().parents[1]

def load(name):
    return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))

def main():
    sources=load('sources.json')['sources']
    records=load('evidence_register.json')['records']
    contrasts=load('numerical_contrasts.json')['contrasts']
    codebook=load('codebook.json')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SupplementTitle',fontName='Helvetica-Bold',fontSize=21,leading=25,textColor=colors.black,spaceAfter=14))
    styles.add(ParagraphStyle(name='SupplementSubtitle',fontName='Helvetica',fontSize=11.5,leading=16,textColor=colors.black,spaceAfter=14))
    styles.add(ParagraphStyle(name='Section',fontName='Helvetica-Bold',fontSize=14,leading=18,textColor=colors.black,spaceBefore=16,spaceAfter=8,keepWithNext=True))
    styles.add(ParagraphStyle(name='Study',fontName='Helvetica-Bold',fontSize=12,leading=15,textColor=colors.black,spaceBefore=13,spaceAfter=7,keepWithNext=True))
    styles.add(ParagraphStyle(name='Text',fontName='Helvetica',fontSize=10,leading=14,textColor=colors.black,spaceAfter=7))
    styles.add(ParagraphStyle(name='Record',fontName='Helvetica-Bold',fontSize=10,leading=14,textColor=colors.black,spaceBefore=9,spaceAfter=5,keepWithNext=True))
    styles.add(ParagraphStyle(name='Cell',fontName='Helvetica',fontSize=9,leading=12,textColor=colors.black,spaceAfter=0))
    def p(text,style='Text'):
        return Paragraph(escape(str(text)),styles[style])
    def linked(text,url):
        return Paragraph(f'<link href="{escape(url)}" color="#1f4e79">{escape(text)}</link>',styles['Text'])
    def table(rows,widths,header=True):
        data=[[p(x,'Cell') for x in row] for row in rows]
        result=Table(data,colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
        commands=[('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#d9d9d9')),
                  ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8),
                  ('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]
        if header:
            commands += [('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8edf2'))]
        result.setStyle(TableStyle(commands))
        result.spaceAfter=8
        return result
    story=[p('Supplementary Material S1','SupplementTitle'),
           p('A Critical Review of Evaluation Evidence for Autonomous Driving World Models','SupplementSubtitle'),
           p('Release 1.0.0 | Prepared 2 November 2026 | 17 systems | 35 task/input records | 4 numerical contrasts'),
           p('Scope and provenance','Section'),
           p('This newly assembled supplement reconstructs the register described in Revision 4 using the supplied manuscript and targeted primary-source checking. The original S1, historical extraction log and original script were not supplied. This AI-assisted reconstruction does not establish that the same files or workflow existed earlier.'),
           p('The sample is purposive. Task records are not independent studies. No independent second-coder audit, model-training replication, new driving rollout or physical-road validation is claimed. Missing quality fields mean not extracted, not necessarily absent from a paper.'),
           p('Retrieval and extraction','Section'),
           p('The 17 named seed systems were retrieved through exact-title primary records, official proceedings and linked author manuscripts. Relevant methods, action interfaces and endpoint-specific evaluation passages were checked. Inspected versions control the locators below; equivalence to a later publication is not assumed. Present reconstruction operations are recorded in data/retrieval_provenance.json.'),
           p('The unit is study x task/input variant x specified claim. Source-reported endpoints are paraphrased. Stronger use questions introduced by this review are recorded separately and must not be attributed to the original authors.'),
           p('Codebook','Section'),
           table([['Axis','Meaning']]+[[k,v] for k,v in codebook['axes'].items()],[45,450]),
           table([['Status','Claim-specific meaning']]+[[k,v] for k,v in codebook['evidence_status'].items()],[45,450]),
           p('D is directness, not high experimental quality. X is not incapability and NR is not a negative result. No total maturity score is assigned.'),
           p('Source index','Section'),
           table([['ID','System','Inspected version']]+[[s['study_id'],s['system'],s['inspected_version']] for s in sources],[42,107,346]),
           p('Task and input register','Section')]
    for source in sources:
        source_title=p(source['title']+f'. Manuscript reference [{source["manuscript_reference"]}].')
        source_title.keepWithNext=True
        source_link=linked('Primary source: '+source['inspected_version'],source['inspected_url'])
        source_link.keepWithNext=True
        story.extend([p(source['study_id']+' '+source['system'],'Study'),
                      source_title,source_link])
        for r in [r for r in records if r['study_id']==source['study_id']]:
            story.extend([p(r['record_id']+' '+r['task_variant'],'Record'),
                          table([['Field','Recorded interface']]+[[k,r[k]+('; '+r['reference_environment'] if k=='V' else '')] for k in ['R','A','I','U','V']],[57,438]),
                          p('Locator: '+r['source_locators']+'.')])
            if r['information_conditions']:
                story.append(p('Information: '+r['information_conditions']+'.'))
            for a in r['assessments']:
                prefix='Source endpoint (paraphrased)' if a['origin']=='source_reported_endpoint' else 'Additional review question'
                story.append(p(f'{prefix}: {a["claim"]}. Status {a["status"]}.'))
            story.append(p('Boundary: '+r['interpretation_boundary']))
    story.extend([p('Numerical transfer register','Section'),
                  p('These are author-reported within-study contrasts, not new experiments. Percent metrics use a 0-100 scale. Absolute changes in these metrics are percentage-point changes. Displayed rounding is retained; no missing interval or significance result is inferred.')])
    for c in contrasts:
        story.extend([p(c['contrast_id']+' '+next(s['system'] for s in sources if s['study_id']==c['study_id']),'Study'),
                      linked(c['version']+' | '+c['locator'],c['source_url']),
                      p('Dataset and inputs: '+c['dataset']+'.'),
                      p('Baseline: '+c['baseline_condition']+'.'),
                      p('Comparison: '+c['comparison_condition']+'.'),
                      table([['Metric','Unit','Baseline','Comparison']]+[[m['metric'],m['unit'],str(m['baseline']),str(m['comparison'])] for m in c['metrics']],[190,100,95,110]),
                      p('Aggregation: '+c['aggregation']+'.'),p('Boundary: '+c['boundary'])])
    story.extend([p('Analytical example and executable checks','Section'),
        p('The Section 6.5 merge example stipulates collision probabilities, maneuver penalties and observation errors. Costs are maneuver penalty plus 100 times collision probability. Reference costs are 4.0, 1.2 and 3.0. Model A selects keep speed with regret 2.8; model B selects brake with regret 0. Average observation errors are 0.0149 and 0.0302. The eligible-pair ranking errors are 2/3 and 0, and hazardous false-clearance rates are 1 and 0.'),
        p('The separately stipulated observation and cost values establish only a logical non-implication. They are not sampled outcomes of the audited systems. data/analytical_example.json stores inputs and expected values.'),
        p('Run python scripts/validate.py to recompute the example, validate cross-links, calculate numerical changes and run definition/property checks. The script checks strict margin eligibility, half-error ties, unresolved hazard labels, undefined denominators, selective abstention and regret intervals. It does not automatically establish the correctness of source-paper claims.'),
        p('Confidence intervals are supplied inputs to definition utilities, not estimated by this implementation. Joint coverage, independence and physical validity require separate evidence. Brier and selective-risk tests are deterministic implementation checks, not new driving results.'),
        p('Files and correction policy','Section'),
        p('The companion repository contains the Markdown S1, source-linked JSON register, codebook, numerical transfer file, analytical inputs, query tool, validator, tests and validation report. docs/DATA_DICTIONARY.md explains fields; docs/REPRODUCIBILITY.md describes the verification boundary. Changes should identify a record ID, source version and passage, proposed correction and rationale, and preserve historical releases.')])
    output=ROOT/'docs'/'S1.pdf'
    def footer(canvas,doc):
        canvas.saveState()
        canvas.setFont('Helvetica',8)
        canvas.setFillColor(colors.HexColor('#555555'))
        canvas.drawString(50,30,'Supplementary Material S1 | Release 1.0.0')
        canvas.drawRightString(A4[0]-50,30,f'Page {doc.page}')
        canvas.restoreState()
    doc=SimpleDocTemplate(str(output),pagesize=A4,rightMargin=50,leftMargin=50,topMargin=44,bottomMargin=48,
                          title='Supplementary Material S1 - Driving world model evaluation evidence',author='',invariant=1)
    doc.build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=partial(Canvas,invariant=1))
    print(output)

if __name__=='__main__':
    main()
