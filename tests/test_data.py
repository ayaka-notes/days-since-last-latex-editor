import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import validate, esc, unmaintained


class DataTests(unittest.TestCase):
    def setUp(self):
        with (ROOT / 'data.csv').open() as handle:
            self.rows = list(csv.DictReader(handle))

    def test_catalog_is_valid(self):
        validate(self.rows)

    def test_all_discussion_repositories_are_represented(self):
        import json
        imported = json.loads((ROOT / 'discussion-146.json').read_text())
        # latexdo was later split into a desktop repo; retain the original as an alias.
        aliases = {'https://github.com/latexdo/latexdo': 'https://github.com/latexdo/latexdo-desktop', 'https://github.com/cu1ch3n/papilot': 'https://github.com/PapilotAI/papilot'}
        sources = {r['source'].lower().rstrip('/') for r in self.rows}
        for record in imported['records']:
            url = record['url'].rstrip('/')
            if url.startswith('https://github.com/'):
                self.assertIn(aliases.get(url, url).lower(), sources, record['Project'])

    def test_unverified_dates_never_reset_counter(self):
        row = dict(self.rows[0], date='2026-10-01', date_basis='Date unverified')
        with self.assertRaises(AssertionError):
            validate([row])

    def test_inactivity_uses_calendar_months_and_known_commits(self):
        from datetime import date
        today = date(2026, 11, 4)
        self.assertTrue(unmaintained({'last_commit_at': '2026-08-04T10:00:00Z'}, today))
        self.assertFalse(unmaintained({'last_commit_at': '2026-08-05T10:00:00Z'}, today))
        self.assertFalse(unmaintained({}, today))
        self.assertFalse(unmaintained({'last_commit_at': '2020-01-01T00:00:00Z', 'error': 'lookup failed'}, today))
        self.assertTrue(unmaintained({'last_commit_at': '2024-02-29T00:00:00Z'}, date(2024, 5, 31)))

    def test_unsafe_links_are_rejected(self):
        row = dict(self.rows[0], website='javascript:alert(1)')
        with self.assertRaises(AssertionError):
            validate([row])
        self.assertEqual(esc('<script>"'), '&lt;script&gt;&quot;')

    def test_development_branch_activity_prevents_false_inactivity(self):
        from datetime import date
        metadata = {'last_commit_at': '2026-06-04T09:22:49Z', 'activity_commit_at': '2026-11-04T12:30:24Z'}
        self.assertFalse(unmaintained(metadata, date(2026, 11, 4)))
        self.assertTrue(unmaintained(metadata, date(2027, 2, 4)))
        metadata['activity_error'] = 'lookup failed'
        self.assertFalse(unmaintained(metadata, date(2027, 2, 4)))


if __name__ == '__main__':
    unittest.main()
