"""Offline, intentionally narrow crawl triage. No network or writes."""
import json,sys

def triage(rows):
    result=[]
    for r in rows:
        if type(r.get('status')) is not int or type(r.get('indexable')) is not bool:
            raise ValueError('status must be int; indexable must be bool')
        status=r['status']; role=r.get('page_role','unknown')
        if status>=400:
            result.append({'url':r['url'],'rule':'HTTP_ERROR','priority':'high' if role=='lead' else 'medium','observation':f'HTTP {status}', 'owner':r.get('owner','unassigned'),'next_check':'Confirm intended destination; restore or choose a relevant redirect; recrawl.'})
        elif status==200 and r['indexable'] is False and role=='lead':
            result.append({'url':r['url'],'rule':'LEAD_NONINDEXABLE','priority':'review','observation':'Lead page marked non-indexable','owner':r.get('owner','unassigned'),'next_check':'Confirm intended visibility before any indexing change.'})
    return result

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('Usage: python scripts/triage.py examples/input.json')
    with open(sys.argv[1],encoding='utf-8') as f: data=json.load(f)
    print(json.dumps(triage(data['rows']),indent=2,ensure_ascii=False))
