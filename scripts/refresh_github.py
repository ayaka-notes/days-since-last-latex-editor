#!/usr/bin/env python3
"""Refresh public metadata; never infer debut dates or product status."""
import csv
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from build import repository

ROOT = Path(__file__).resolve().parents[1]


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def fetch(path):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'days-since-last-latex-editor', 'X-GitHub-Api-Version': '2022-11-28'}
    token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    request = urllib.request.Request('https://api.github.com/' + path, headers=headers)
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response), response.headers


def refresh():
    target = ROOT / 'github-snapshot.json'
    previous = json.loads(target.read_text()) if target.exists() else {'repositories': {}}
    repos = sorted({repo for row in csv.DictReader((ROOT / 'data.csv').open()) if (repo := repository(row['source']))})

    def one(repo):
        old = previous['repositories'].get(repo.lower(), {})
        try:
            m, _ = fetch('repos/' + repo)
            result = dict(name=m['full_name'], stars=m['stargazers_count'], forks=m['forks_count'], license=(m.get('license') or {}).get('spdx_id'), archived=m['archived'], created_at=m['created_at'], pushed_at=m['pushed_at'], url=m['html_url'], checked_at=now())
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
            # Keep the old observation time alongside its error; never refresh stale timestamps.
            return repo.lower(), {**old, 'error': f'Metadata lookup failed: {type(exc).__name__}', 'attempted_at': now()}
        try:
            commits, headers = fetch('repos/' + repo + '/commits?per_page=1')
            if commits:
                result['last_commit_at'] = commits[0]['commit']['committer']['date']
                result['last_commit_url'] = commits[0]['html_url']
                last = re.search(r'<([^>]+)>; rel="last"', headers.get('Link', ''))
                result['commits'] = int(urllib.parse.parse_qs(urllib.parse.urlparse(last.group(1)).query)['page'][0]) if last else len(commits)
                result['commit_checked_at'] = now()
                try:
                    if last:
                        oldest, _ = fetch(last.group(1).removeprefix('https://api.github.com/'))
                    else:
                        oldest = commits
                    if oldest:
                        result['first_commit_at'] = oldest[-1]['commit']['committer']['date']
                        result['first_commit_url'] = oldest[-1]['html_url']
                        result['first_commit_sha'] = oldest[-1]['sha']
                        result['first_commit_checked_at'] = now()
                except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
                    for key in ('first_commit_at', 'first_commit_url', 'first_commit_sha', 'first_commit_checked_at'):
                        if key in old:
                            result[key] = old[key]
                    result['first_commit_error'] = f'First commit lookup failed: {type(exc).__name__}'
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
            for key in ('last_commit_at', 'last_commit_url', 'commits', 'commit_checked_at', 'first_commit_at', 'first_commit_url', 'first_commit_sha', 'first_commit_checked_at'):
                if key in old:
                    result[key] = old[key]
            result['commit_error'] = f'Commit lookup failed: {type(exc).__name__}'
        return repo.lower(), result

    with ThreadPoolExecutor(max_workers=5) as pool:
        results = dict(pool.map(one, repos))
    errors = sum('error' in r for r in results.values())
    target.write_text(json.dumps({'generated_at': now(), 'repositories': results}, ensure_ascii=False, indent=2) + '\n')
    print(f'GitHub metadata refreshed: {len(results) - errors}/{len(results)} repositories; {errors} retained/unknown.')
    # A temporary API failure should not take down a previously valid directory.
    if errors == len(results):
        print('::warning::All GitHub lookups failed; the site will clearly label retained data as stale.')


if __name__ == '__main__':
    refresh()
