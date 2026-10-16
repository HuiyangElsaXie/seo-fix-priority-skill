"""Actionable handoff CLI and review boundary regressions; fictional inputs only."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('actionable_report', ROOT / 'scripts/six_dimension_report.py')
reporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reporter)

class ActionableHandoffTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads((ROOT / 'cases/six-dimension/snapshot.json').read_text())
        self.context = json.loads((ROOT / 'cases/six-dimension/context.json').read_text())
        self.snapshot['pages'][0]['jsonld'] = [{'valid_json': False, 'raw_excerpt': '{broken'}]

    def reviewed(self):
        report = reporter.build_report(self.snapshot, self.context)
        f = next(f for f in report['findings'] if f['root_cause_key'].startswith('JSONLD_SHAPE|'))
        return {'reviewer': 'Fictional QA reviewer', 'date': '2026-10-16', 'source': 'Fictional manual inspection',
                'input_fingerprint': report['input_fingerprint'], 'decisions': [{
                    'issue_id': f['issue_id'], 'evidence_ids': f['evidence_ids'], 'decision': 'confirmed_fix',
                    'rationale': 'Fictional raw block is invalid JSON.', 'intended_behavior': 'This intended block must parse.',
                    'business_context_basis': 'Fictional owner requires accurate descriptive markup; urgency unmeasured.',
                    'steps': ['Repair the exact invalid JSON block and save its replacement.'],
                    'acceptance': ['The replacement block parses successfully with a JSON parser.']}]}

    def test_stale_input_fingerprint_is_rejected(self):
        review = self.reviewed()
        self.snapshot['pages'][0]['title'] = 'Changed since review'
        with self.assertRaisesRegex(ValueError, 'fingerprint'):
            reporter.build_report(self.snapshot, self.context, review=review)

    def test_review_cannot_predate_evidence(self):
        review = self.reviewed()
        review['date'] = '2026-10-01'
        with self.assertRaisesRegex(ValueError, 'precede'):
            reporter.build_report(self.snapshot, self.context, review=review)

    def test_undated_evidence_cannot_confirm_fix(self):
        self.snapshot['pages'][0].pop('fetched_at', None)
        review = self.reviewed()
        with self.assertRaisesRegex(ValueError, 'dated evidence'):
            reporter.build_report(self.snapshot, self.context, review=review)

    def test_markdown_contains_executable_plan_and_provenance(self):
        r = reporter.build_report(self.snapshot, self.context, review=self.reviewed())
        md = reporter.markdown(r)
        for expected in ('Proposed role:', 'Dependencies:', 'Acceptance:', 'Why this next:',
                         'Fictional QA reviewer', 'not independently verified', 'exact_input_fingerprint'):
            self.assertIn(expected, md)
        self.assertNotIn('unassigned', md)
        self.assertEqual(len(r['actionable_handoff']['buckets']['confirmed_fix']), 1)

    def test_gaps_are_deduplicated_by_dimension(self):
        r = reporter.build_report({'schema_version': '1.0', 'pages': []})
        tasks = r['actionable_handoff']['buckets']['needs_verification']
        for dim in reporter.DIMENSIONS:
            self.assertLessEqual(sum(t['dimension'] == dim and t['issue_id'] is None for t in tasks), 1)
        self.assertFalse(r['actionable_handoff']['buckets']['confirmed_fix'])
        self.assertEqual(r['actionable_handoff']['status'], 'verification_required')

    def test_review_cli_outputs_and_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as d:
            paths = {name: Path(d) / (name + '.json') for name in ('snapshot', 'context', 'review')}
            for name, data in [('snapshot', self.snapshot), ('context', self.context), ('review', self.reviewed())]:
                paths[name].write_text(json.dumps(data))
            out = Path(d) / 'report'
            cmd = [sys.executable, str(ROOT / 'scripts/six_dimension_report.py'), str(paths['snapshot']),
                   '--context', str(paths['context']), '--review', str(paths['review']), '--out', str(out)]
            run = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            saved = (out / 'report.json').read_bytes()
            self.assertEqual(json.loads(saved)['final_review_status']['decision_count'], 1)
            self.assertNotEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            self.assertEqual(saved, (out / 'report.json').read_bytes())

if __name__ == '__main__':
    unittest.main()
