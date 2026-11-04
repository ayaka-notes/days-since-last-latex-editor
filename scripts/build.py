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
    dated = sorted((r for r in rows if r['date']), key=lambda r: r['date'], reverse=True)
    latest = dated[0]
    out = ROOT / 'dist'
    (out / 'badges').mkdir(parents=True, exist_ok=True)
    days = (date.today() - date.fromisoformat(latest['date'])).days
    timeline = []
    for r in dated:
        timeline.append(f'<tr><th scope="row"><i>{esc(r["name"])}</i></th><td>{esc(r["date_basis"].lower())} <time datetime="{r["date"]}">{r["date"]}</time></td><td>{link(r["source"], "repository")}</td><td>{link(r["evidence"], "announcement", r["note"])}</td></tr>')
    directory = []
    for r in sorted(rows, key=lambda r: r['name'].casefold()):
        repo = repository(r['source'])
        m = snapshot['repositories'].get((repo or '').lower(), {})
        stale = bool(m.get('error'))
        star = m.get('stars')
        star_label = str(star) if star is not None else 'unavailable'
        if repo:
            fallback = 'badges/' + repo.replace('/', '--') + '.svg'
            svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="114" height="20" role="img" aria-label="stars: {esc(star_label)}"><rect width="114" height="20" rx="3" fill="#555"/><path d="M45 0h66q3 0 3 3v14q0 3-3 3H45z" fill="#28749b"/><g fill="white" text-anchor="middle" font-family="Verdana,sans-serif" font-size="11"><text x="23" y="14">stars</text><text x="79" y="14">{esc(star_label)}</text></g></svg>'
            (out / fallback).write_text(svg)
            # The text snapshot remains useful if Shields is blocked or has no image.
            badge = f'<a class="star-badge" href="{esc(r["source"])}/stargazers"><img loading="lazy" decoding="async" data-fallback="{esc(fallback)}" src="https://img.shields.io/github/stars/{esc(repo)}?style=flat&amp;label=stars&amp;cacheSeconds=3600" alt="GitHub stars for {esc(r["name"])}"><small>{esc(star_label)} at snapshot{" · stale" if stale else ""}</small></a>'
        else:
            badge = '<span class="muted">—</span>'
        license_id = m.get('license')
        license_text = license_id if license_id and license_id != 'NOASSERTION' else 'Not detected' if repo else 'See website'
        last = m.get('last_commit_at', '')
        last_text = last[:10] if last else 'Unverified'
        last_html = link(m.get('last_commit_url'), last_text) if last else last_text
        if stale or m.get('commit_error'):
            last_html += '<small>stale snapshot</small>'
        if isinstance(m.get('commits'), int):
            last_html += f'<small>{m["commits"]:,} commits</small>'
        if m.get('archived'):
            last_html += '<small>archived repository</small>'
        debut = r['date'] or ((r.get('discussion_debut') + ' · reported') if r.get('discussion_debut') not in ('', '—', None) else 'Unverified')
        ai = r.get('ai_integration') or 'Not reviewed'
        notes = r['note'] or r['description']
        links = ' · '.join(x for x in [link(r['website'], 'website'), link(r['source'], 'repository'), link(r['evidence'], 'evidence', notes)] if x)
        main_url = r['website'] or r['source'] or r['evidence']
        directory.append(f'<tr data-kind="{esc(r["kind"])}" data-stars="{star if star is not None else -1}" data-updated="{esc(last)}"><th scope="row">{link(main_url, r["name"])}<small>{esc(r["description"])}</small></th><td>{esc(r["kind"])}</td><td title="{esc(notes)}">{esc(debut)}</td><td>{badge}</td><td>{esc(license_text)}</td><td>{last_html}</td><td>{esc(ai)}</td><td class="links">{links}</td></tr>')
    checked = snapshot['generated_at']
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Days since last LaTeX editor</title><meta name="description" content="A growing, sourced directory of LaTeX editors, with a new-editor counter, GitHub stars, and links to the original announcements.">
<link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css"><script src="script.js" defer></script></head>
<body><header><a href="{REPO}">source code for this website</a><span>maintained by <a href="https://github.com/ayaka-notes">ayaka-notes</a></span></header>
<main><section class="counter" aria-labelledby="counter-title"><h1 id="counter-title">It has been</h1><div id="days" data-last-release="{latest['date']}">{days}</div><p id="sentence-end">days since the latest known new LaTeX editor</p><p class="counter-note">Latest dated entry: {link(latest['evidence'], latest['name'])} · {latest['date']}</p></section>
<div class="timeline-wrap"><table class="timeline"><caption class="sr-only">Dated new-editor introductions</caption><tbody>{''.join(timeline)}</tbody></table></div>
<p class="method-short">A small counter. A growing list. New editors, forks and editor extensions welcome.</p>
<details class="method"><summary>What resets the counter?</summary><p>Only a dated initial release or public introduction recorded in this list. Routine version updates do not reset it. Dates are UTC calendar days. Public introductions may come after a project's first release; the evidence link records exactly which event we found. This is a curated list, not a complete census of every new editor.</p><p>Undated projects remain in the directory. Repository creation dates and month-only dates from Discussion #146 do not reset the counter. Namesakes are kept separate. See the evidence for each date and submit corrections on GitHub.</p></details>
<section class="directory" aria-labelledby="directory-title"><h2 id="directory-title">LaTeX editors, old and new</h2><p class="intro">{len(rows)} entries · desktop, web, self-hosted, mobile and extensions</p>
<form class="filters" onsubmit="return false"><label>Find an editor <input id="search" type="search" placeholder="Name, platform, AI…" autocomplete="off"></label><label>Form <select id="kind"><option value="">All forms</option>{''.join(f'<option>{k}</option>' for k in sorted(KINDS))}</select></label><label>Sort <select id="sort"><option value="name">Name A–Z</option><option value="stars">Snapshot stars</option><option value="updated">Latest commit</option></select></label><button id="reset" type="reset">Reset</button></form>
<p id="result-count" aria-live="polite">Showing {len(rows)} editors</p><div class="table-wrap" tabindex="0" role="region" aria-label="Editor directory; scroll horizontally on small screens"><table id="directory-table"><thead><tr><th scope="col">Editor</th><th scope="col">Form</th><th scope="col">Debut / introduction</th><th scope="col">GitHub stars</th><th scope="col">Detected license</th><th scope="col">Last commit (UTC)</th><th scope="col">AI · reported¹</th><th scope="col">Links</th></tr></thead><tbody>{''.join(directory)}</tbody></table></div><p id="empty" hidden>No editors match. Try another search or reset the filters.</p>
<p class="snapshot-note">Repository snapshot: <time datetime="{esc(checked)}">{esc(checked)}</time>. Star badges refresh through Shields.io and may be cached for an hour or longer. Exact text counts and sorting use the dated snapshot. Commit counts cover default-branch history, including inherited fork commits. GitHub metadata refreshes on the daily build; a failed lookup keeps its earlier timestamp and is marked stale. A recent commit is not a maintenance guarantee.</p>
<p class="snapshot-note">¹ AI descriptions and month-only debut dates imported from <a href="https://github.com/ayaka-notes/ayakaleaf-pro/discussions/146">Discussion #146</a> are reported information, not independently audited capabilities. “Not detected” means GitHub did not identify a license, not that the project has no license. Links may point to release-only repositories. Inclusion is not an endorsement.</p></section>
</main><footer><a href="{REPO}/issues/new?template=editor.yml">add or correct an editor</a> · <a href="data.csv">download the data</a> · <a href="github-snapshot.json">GitHub snapshot</a><p>Inspired by <a href="https://days-since-last-typst-editor.samake.se/">Days since last Typst editor</a> by <a href="https://github.com/sermuns">Samuel “sermuns” Åkesson</a>. Same spirit, more LaTeX.</p></footer></body></html>'''
    out = ROOT / 'dist'
    out.mkdir(exist_ok=True)
    (out / 'index.html').write_text(page)
    for name in ('style.css', 'script.js', 'favicon.svg', 'data.csv', 'github-snapshot.json', 'discussion-146.json'):
        (out / name).write_bytes((ROOT / name).read_bytes())
    (out / '.nojekyll').touch()
    print(f'Built {len(rows)} editors, {len(dated)} dated introductions → dist/')


if __name__ == '__main__':
    build()
