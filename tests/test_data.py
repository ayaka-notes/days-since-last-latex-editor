import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import validate, esc


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

    def test_unsafe_links_are_rejected(self):
        row = dict(self.rows[0], website='javascript:alert(1)')
        with self.assertRaises(AssertionError):
            validate([row])
        self.assertEqual(esc('<script>"'), '&lt;script&gt;&quot;')


if __name__ == '__main__':
    unittest.main()
