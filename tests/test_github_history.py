import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from refresh_github import first_root, oldest_root


def commit(sha, when, parents):
    return {'sha': sha, 'parents': parents, 'commit': {'committer': {'date': when}}}


class HistoryTests(unittest.TestCase):
    def test_backdated_child_does_not_beat_real_root(self):
        backdated = commit('child', '2007-03-01T05:53:59Z', [{'sha': 'parent-in-2014'}])
        root = commit('root', '2013-08-08T15:42:14Z', [])
        later_root = commit('import', '2014-02-12T10:40:42Z', [])
        self.assertEqual(oldest_root([later_root, root, backdated]), root)

    def test_non_root_tail_triggers_a_wider_history_lookup(self):
        backdated = commit('child', '2007-03-01T05:53:59Z', [{'sha': 'parent-in-2014'}])
        root = commit('root', '2013-08-08T15:42:14Z', [])
        with patch('refresh_github.fetch', return_value=([root, backdated], {})) as fetch:
            self.assertEqual(first_root('overleaf/overleaf', [backdated], 28830), root)
            fetch.assert_called_once_with('repos/overleaf/overleaf/commits?per_page=100&page=289')

    def test_missing_root_is_not_guessed_from_timestamp(self):
        child = commit('child', '2020-01-01T00:00:00Z', [{'sha': 'parent'}])
        with patch('refresh_github.fetch', return_value=([child], {})):
            with self.assertRaises(ValueError):
                first_root('example/repo', [child], 20)
