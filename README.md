# Days since last LaTeX editor

A small counter and a growing directory of LaTeX editors, inspired by
[Days since last Typst editor](https://days-since-last-typst-editor.samake.se/).

The first catalog contains 110 entries, including every project linked in
[Ayakaleaf Pro Discussion #146](https://github.com/ayaka-notes/ayakaleaf-pro/discussions/146),
LocTex from the supplied Reddit introduction, and traditional editors such as
TeXstudio, Texmaker, TeXworks, TeXShop, Kile and LyX.

## Run locally

Python 3.12+ is sufficient to build. No frontend packages or bundler are needed.

```sh
python scripts/build.py
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`. All directory content is generated as static HTML;
JavaScript only updates the counter, filters and sorts. All paths are relative
so GitHub project Pages work without a custom domain.

## Update data

Edit `data.csv`; the site is rebuilt on every push to `main`.

| Field | Meaning |
| --- | --- |
| `name`, `kind` | Display name and Desktop / Web / Self-hosted / Mobile / Extension |
| `website`, `source`, `evidence` | Official site, repository, and supporting source |
| `description`, `note` | Short description and qualifications |
| `date`, `date_basis` | Exact UTC date and the initial release/public introduction it refers to |
| `discussion_debut`, `ai_integration` | Reported information imported from Discussion #146 |
| `discussion_license`, `discussion_status` | Original comparison labels preserved for provenance, not asserted as current state |

Only exact, reviewed introduction dates reset the counter. Repository creation,
ordinary version updates, and month-only dates do not. Unknown dates remain
visible. A first retained release is not proof that no earlier release existed.
The two Folio projects and two Scribe projects remain separate. The LatexDo
desktop repository is used for its desktop app; the original link is preserved
in `discussion-146.json`.

`github-snapshot.json` records stars, forks, detected SPDX license, default-branch
commit date, commit count (when available), and per-repository retrieval times.
Commit count covers the default branch's reachable history, including inherited
fork history; it is not a measure of original work. Refresh with:

```sh
GH_TOKEN="$(gh auth token)" python scripts/refresh_github.py
python scripts/build.py
```

The workflow refreshes metadata daily at 02:17 UTC (10:17 Asia/Taipei), on pushes,
and on manual runs. The Actions token stays server-side. Shields.io star images
also refresh independently, with upstream caching; snapshot sorting and exact
text values can therefore differ from badges. No browser-side API token is used.
Failed API lookups retain old values with their original timestamp and an error.
The page distinguishes archival status and observed commit dates from subjective
“active/stalled” judgments. AI labels imported from the comparison are reported,
not a feature audit.

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
