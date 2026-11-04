# Days since last LaTeX editor

A small counter and a growing directory of LaTeX editors, inspired by
[Days since last Typst editor](https://days-since-last-typst-editor.samake.se/).

The catalog contains 114 entries, including every project linked in
[Ayakaleaf Pro Discussion #146](https://github.com/ayaka-notes/ayakaleaf-pro/discussions/146),
LocTex from the supplied Reddit introduction, Overleaf Workshop discovered through Trendshift, and traditional editors such as
TeXstudio, Texmaker, TeXworks, TeXShop, Kile and LyX.

## Run locally

Python 3.12+ is sufficient to build. No frontend packages or bundler are needed.

```sh
python scripts/build.py
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`. All directory content is generated as static HTML;
JavaScript only updates the counter. The page has one compact chronological list,
with stars and forks together in one additional column. A status column after the name marks repositories with no commit on the default or explicitly reviewed development branch
in three calendar months as red `unmaintained`. Unknown or failed commit lookups
are not classified. This is an automatic activity rule, not a declaration of
abandonment. No AI labels or extended comparison table are displayed. All paths are relative
so GitHub project Pages work without a custom domain.

## Update data

Edit `data.csv`; the site is rebuilt on every push to `main`.

| Field | Meaning |
| --- | --- |
| `name`, `kind` | Display name and Desktop / Web / Self-hosted / Mobile / Extension |
| `website`, `source`, `evidence` | Official site, repository, and supporting source |
| `description`, `note` | Short description and qualifications |
| `date`, `date_basis` | Reviewed date (YYYY, YYYY-MM or YYYY-MM-DD) and the event it refers to |
| `discussion_debut`, `ai_integration` | Reported information imported from Discussion #146 |
| `discussion_license`, `discussion_status` | Original comparison labels preserved for provenance, not asserted as current state |

Reviewed dates take precedence for display and ordering. The counter uses exact days only,
falling back to the first verified public root commit when no reviewed date is known. Repository creation,
ordinary version updates and month-only dates do not reset it. Unknown dates remain
visible. When no reviewed date is known, the list uses the oldest verified root commit in the public default-branch history, linked to that commit. Timestamp-sorted API results are checked for parents; a backdated non-root commit is not treated as an initial commit. If no root can be verified, the fallback is omitted.
Fork history can include upstream commits. Projects without public GitHub history
may use a reported month/year from Discussion #146. Both are explicitly labelled.
Year/month-only dates never reset the counter, and are displayed at their original precision. A first retained release is not proof that no earlier release existed. Public root commits do not establish the date of private or omitted history. Overleaf uses the officially documented founding year (2011); Overleaf CE uses the ShareLaTeX open-source announcement (2014-02-21).
The two Folio projects and two Scribe projects remain separate. The LatexDo
desktop repository is used for its desktop app; the original link is preserved
in `discussion-146.json`.

`github-snapshot.json` records stars, forks, detected SPDX license, default-branch
commit dates (oldest and latest), commit count (when available), and per-repository retrieval times.
`activity_branch` in `data.csv` optionally names a reviewed development branch for maintenance checks (for example, BlaBlaTex uses `develop`). This never changes the first-commit fallback or release date. The branch is refreshed daily; a failed lookup does not mark the project unmaintained. Hosted and self-hosted editions may share an upstream repository, as with Overleaf and Overleaf CE.

Commit count covers the default branch's reachable history, including inherited
fork history; it is not a measure of original work. Refresh with:

```sh
GH_TOKEN="$(gh auth token)" python scripts/refresh_github.py
python scripts/build.py
```

The workflow refreshes metadata daily at 02:17 UTC (10:17 Asia/Taipei), on pushes,
and on manual runs. The Actions token stays server-side. Stars and forks appear
as plain numbers in one column. Failed lookups retain earlier values and mark
those counts with an asterisk; hover for the original observation timestamp.

## Categories

The existing status column shows one category per editor: `SaaS`,
`Selfhosted`, or `Local`. A local editor takes precedence over an
optional server deployment. Browser editors that work on the user's device
are local; a static demo alone is not SaaS. Merely running a server stack on a
laptop does not establish a local editor. SaaS describes a vendor-operated
service and may have free or subscription plans. The SaaS label is red, using
the same font size and weight as the surrounding text.

`category_evidence`, `category_note` and `category_checked_at` keep the source
and rationale beside each reviewed classification in `data.csv`. When an editor
is marked `unmaintained`, that label replaces the category in the status cell.
It uses the normal font size and weight with red text only.

## Reddit and introduction research

All 110 original entries were searched individually on 2026-11-04. The expanded
catalog has 38 dated initial releases/public introductions and 37 entries with
reviewed Reddit links. `reddit-sources.json` keeps the minimal source records;
`research-audit.json` records the individual queries and retained outcomes.

A search result is not enough to associate namesakes. Matched posts must identify
the same project, repository or official domain. Ordinary user discussions and
removed posts do not establish initial release dates. Indexed post text is not
a guarantee that the live post remains available. The removed Typeward thread is linked because surviving comments explicitly identify it;
no removal reason or deleted account identity is inferred. The supplied LocTex
link is retained as unverified because its body and date were unavailable.

Initial-release records were checked against official GitHub releases. Routine
updates, engine-only assets and ambiguous earliest retained versions are not
promoted to initial releases. Trendshift is a discovery source, not a date or
star-count authority. The imported Discussion #146 comparison fields remain in
the source data for provenance, but are not shown on the page.

## Deploy to GitHub Pages

Create a public repository named `ayaka-notes/days-since-last-latex-editor`, push
this checkout to `main`, and set **Settings → Pages → Source → GitHub Actions**.
The included workflow validates the catalog, refreshes metrics, builds `dist/`,
uploads it with `actions/upload-pages-artifact`, and publishes with
`actions/deploy-pages`. Pull requests run checks without deploying.

No PAT secret is needed for the workflow. Only `contents: read` is granted to the
build job; the deployment job gets `pages: write` and `id-token: write`.

## Validation

```sh
python -m unittest discover -s tests
node --test tests/dates.test.cjs
python scripts/build.py
```

Checks cover duplicate identities, URL safety, every imported GitHub project,
date evidence, UTC boundaries, leap days and future clock skew.

## Credits

The original site's code was reviewed: it builds HTML from CSV using Typst and
uses a cyan background, a centered day counter and a compact chronological list.
This independent implementation preserves that treatment, adds a searchable
directory, and uses Python's standard library. Upstream is licensed WTFPL v2;
see `NOTICE`. This implementation is MIT licensed.
