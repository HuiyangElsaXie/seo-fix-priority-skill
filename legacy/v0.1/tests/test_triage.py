import unittest,json
from pathlib import Path
from scripts.triage import triage
ROOT=Path(__file__).resolve().parents[1]
class Checks(unittest.TestCase):
 def test_fixture(self):
  d=json.loads((ROOT/'examples/input.json').read_text()); result=triage(d['rows'])
  self.assertEqual(len(result),1);self.assertEqual(result[0]['priority'],'high')
 def test_private_page_not_false_positive(self):
  self.assertEqual(triage([{'url':'https://example.com/private','status':200,'indexable':False,'page_role':'private'}]),[])
 def test_lead_nonindexable_needs_review(self):
  self.assertEqual(triage([{'url':'https://example.com/lead','status':200,'indexable':False,'page_role':'lead'}])[0]['priority'],'review')
 def test_invalid_boolean(self):
  with self.assertRaises(ValueError):triage([{'url':'https://example.com','status':200,'indexable':'false'}])
 def test_empty_input(self): self.assertEqual(triage([]),[])
if __name__=='__main__': unittest.main()
