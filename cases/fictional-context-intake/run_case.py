"""Execute fictional context variants, with identical supplied technical observations."""
import copy,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[1]))
from scripts.triage import triage

def answer(v):return dict(value=v,status='self_reported',source_id='brief',evidence_locator='BRIEF.md')
base=dict(schema_version='0.3',as_of='2026-10-16',sources={
 'brief':dict(kind='fictional_fixture',description='Invented business interview, not client evidence',observed_at='2026-10-16'),
 'crawl':dict(kind='fictional_fixture',description='Two invented HTTP observations; not a live crawl',observed_at='2026-10-16')},
 business_context=dict(objective='Recover qualified enquiries',owners={'engineering':'Web owner'},answers={k:answer(v) for k,v in dict(industry='Commercial solar installation',audience='Facilities managers',geography='Ontario',language='English',positioning='Small local specialist; unverified owner description',brand_lifecycle='Growth',product_lifecycle='Mature installation service',primary_objective='conversion',conversion_definition='Qualified quote request submitted',resources='One engineer, one day',constraints='No domain or URL migration',specific_problem='Quote form landing page returns 503',site_age='Three years',migration_history='No recent migration reported').items()}),
 rows=[dict(url='https://solar.example/quote',status=503,source_id='crawl',evidence_locator='BRIEF.md:technical observations',intent='index',importance='critical',effort=5,business_impact=answer('Only quote-request entry page for current campaign'),visibility_reason=answer('Owner confirms public acquisition page')),
 dict(url='https://solar.example/',canonical='https://solar.example',status=200,source_id='crawl',evidence_locator='BRIEF.md:technical observations',intent='unknown',importance='unknown')])
variants={'conversion':base}
aw=copy.deepcopy(base);aw['business_context']['objective']='Awareness of educational guide';aw['business_context']['answers']['primary_objective']=answer('awareness');aw['business_context']['answers']['specific_problem']=answer('Assess technical warnings during education campaign');aw['rows'][0]['importance']='low';aw['rows'][0]['business_impact']=answer('Quote page is peripheral to current education campaign; owner confirms low urgency');variants['awareness']=aw
ig=copy.deepcopy(base);ig['business_context']['answers']['specific_problem']={'status':'unknown','value':None};variants['industry-general']=ig
gf=copy.deepcopy(ig);gf['business_context']['answers']={};variants['generic-framework']=gf
for name,data in variants.items():
 (P/f'{name}.input.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 out=triage(data);(P/f'{name}.output.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 assert len(out['queue'])==1 and out['queue'][0]['rule']=='HTTP_ERROR'
 assert out['intake']['page_questions'] # unanswered homepage intent is visible despite no false canonical finding
 print(name,out['intake']['mode'],out['queue'][0]['priority'],out['queue'][0]['score'])
 assert out['queue'][0]['priority']=={'conversion':'P1','awareness':'P3','industry-general':'review','generic-framework':'review'}[name]
print('PASS: context changes supported urgency; general modes retain technical observation without fabricated scores; root canonical false positive absent.')
