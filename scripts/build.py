#!/usr/bin/env python3
"""Build a dependency-free, crawlable directory from reviewed CSV data."""
import csv
import html
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/ayaka-notes/days-since-last-latex-editor'
KINDS = {'Desktop', 'Web', 'Self-hosted', 'Extension', 'Mobile'}


def esc(value):
    return html.escape(str(value or ''), quote=True)


def repository(url):
    p = urlparse(url)
    parts = p.path.strip('/').split('/')
    return '/'.join(parts) if p.hostname == 'github.com' and len(parts) == 2 else None


def validate(rows):
    names = set()
    repos = set()
    for row in rows:
        assert row['name'].strip() and row['name'].casefold() not in names, f"Duplicate name: {row['name']}"
        names.add(row['name'].casefold())
        assert row['kind'] in KINDS, row['kind']
        for key in ('website', 'source', 'evidence'):
            if row[key]:
                p = urlparse(row[key])
                assert p.scheme in ('http', 'https') and p.hostname and not p.username, row[key]
        assert row['source'] or row['website'] or row['evidence'], row['name']
        repo = repository(row['source'])
        if repo:
            assert repo.casefold() not in repos, f'Duplicate repository: {repo}'
            repos.add(repo.casefold())
        if row['date']:
            assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', row['date']), row['date']
            assert date.fromisoformat(row['date']) <= date.today(), row['date']
            assert row['evidence'] and row['date_basis'] != 'Date unverified', row['name']


def link(url, label, title=''):
    return f'<a href="{esc(url)}" title="{esc(title)}">{esc(label)}</a>' if url else ''


def build():
    rows = list(csv.DictReader((ROOT / 'data.csv').open()))
    validate(rows)
    snapshot = json.loads((ROOT / 'github-snapshot.json').read_text())
    reddit_path = ROOT / 'reddit-sources.json'
    reddit = json.loads(reddit_path.read_text())['editors'] if reddit_path.exists() else {}
    dated = sorted((r for r in rows if r['date']), key=lambda r: r['date'], reverse=True)
    latest = dated[0]
    out = ROOT / 'dist'
    out.mkdir(parents=True, exist_ok=True)
    days = (date.today() - date.fromisoformat(latest['date'])).days
    ordered = dated + sorted((r for r in rows if not r['date']), key=lambda r: r['name'].casefold())
    timeline = []
    for r in ordered:
        repo = repository(r['source'])
        m = snapshot['repositories'].get((repo or '').lower(), {})
        counts = '<span class="muted">—</span>'
        if repo:
            stars = f"{m['stars']:,}" if isinstance(m.get('stars'), int) else '—'
            forks = f"{m['forks']:,}" if isinstance(m.get('forks'), int) else '—'
            stamp = m.get('checked_at', 'unavailable')
            stale = ' · stale snapshot' if m.get('error') else ''
            counts = f'<span class="repo-counts" title="GitHub snapshot: {esc(stamp)}{stale}">{link(r["source"] + "/stargazers", "★ " + stars, "Stars")} · {link(r["source"] + "/forks", "⑂ " + forks, "Forks")}{" *" if stale else ""}</span>'
        debut = f'{esc(r["date_basis"].lower())} <time datetime="{r["date"]}">{r["date"]}</time>' if r['date'] else '<span class="muted">date unverified</span>'
        sources = []
        seen = set()
        if r['date']:
            sources.append(link(r['evidence'], 'announcement', r['note']))
            seen.add(r['evidence'])
        for post in reddit.get(r['name'], []):
            if post['url'] in seen:
                continue
            label = 'Reddit'
            if post['status'] == 'removed':
                label += ' (removed)'
            elif post['status'] == 'deleted':
                label += ' (deleted)'
            elif post['status'] == 'unverified':
                label += ' (unverified)'
            sources.append(link(post['url'], label, post.get('note', '')))
            seen.add(post['url'])
        if not sources and r['evidence'] and r['evidence'] not in (r['source'], r['website']):
            sources.append(link(r['evidence'], 'source', r['note']))
        main_url = r['website'] or r['source'] or r['evidence']
        timeline.append(f'<tr><th scope="row"><i>{link(main_url, r["name"], r["description"])}</i></th><td class="date">{debut}</td><td>{link(r["source"], "repository")}</td><td class="sources">{" · ".join(sources)}</td><td>{counts}</td></tr>')
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Days since last LaTeX editor</title><meta name="description" content="A growing list of LaTeX editors, with release dates, GitHub stars and original announcements.">
<link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css"><script src="script.js" defer></script></head>
<body><header><a href="{REPO}">source code for this website</a><span>maintained by <a href="https://github.com/ayaka-notes">ayaka-notes</a></span></header>
<main><section class="counter" aria-labelledby="counter-title"><h1 id="counter-title">It has been</h1><div id="days" data-last-release="{latest['date']}">{days}</div><p id="sentence-end">days since the latest known new LaTeX editor</p></section>
<div class="timeline-wrap" tabindex="0" role="region" aria-label="All LaTeX editors; scroll horizontally on small screens"><table class="timeline"><caption class="sr-only">All {len(rows)} LaTeX editors, newest verified introductions first</caption><thead class="sr-only"><tr><th>Editor</th><th>Date</th><th>Repository</th><th>Announcement and discussion</th><th>Stars / Forks</th></tr></thead><tbody>{''.join(timeline)}</tbody></table></div>
</main><footer><p>{len(rows)} editors · {len(dated)} dated introductions · <a href="{REPO}/issues/new?template=editor.yml">add or correct an editor</a></p>
<details class="method"><summary>Dates and sources</summary><p>Dates refer to the linked initial release or public introduction, not repository creation or routine updates. Undated projects are still included. This is a curated list, not a complete census.</p><p>Reddit links may be introductions or later discussions. Removed posts are kept when surviving public comments identify the project; they do not establish a launch date. Unavailable content and deleted accounts are not reconstructed.</p><p>Star and fork counts refresh daily through GitHub Actions. An asterisk marks an older retained value after a failed lookup. Snapshot: {esc(snapshot['generated_at'])}. <a href="data.csv">Editor data</a> · <a href="reddit-sources.json">Reddit sources</a> · <a href="github-snapshot.json">GitHub snapshot</a></p></details>
<p>Inspired by <a href="https://days-since-last-typst-editor.samake.se/">Days since last Typst editor</a> by <a href="https://github.com/sermuns">Samuel “sermuns” Åkesson</a>.</p></footer></body></html>'''
    (out / 'index.html').write_text(page)
    for name in ('style.css', 'script.js', 'favicon.svg', 'data.csv', 'github-snapshot.json', 'discussion-146.json', 'reddit-sources.json', 'research-audit.json'):
        if (ROOT / name).exists():
            (out / name).write_bytes((ROOT / name).read_bytes())
    (out / '.nojekyll').touch()
    print(f'Built {len(rows)} editors in one list, {len(dated)} dated introductions → dist/')


if __name__ == '__main__':
    build()
