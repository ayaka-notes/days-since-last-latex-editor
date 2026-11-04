'use strict';

function daysSince(isoDate, now = new Date()) {
  const today = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
  const then = Date.parse(`${isoDate}T00:00:00Z`);
  return Math.max(0, Math.floor((today - then) / 86400000));
}

if (typeof document !== 'undefined') {
  const counter = document.getElementById('days');
  function refreshCounter() {
    const days = daysSince(counter.dataset.lastRelease);
    counter.textContent = days;
    document.getElementById('sentence-end').textContent = `${days === 1 ? 'day' : 'days'} since the latest known new LaTeX editor`;
  }
  refreshCounter();
  setInterval(refreshCounter, 60000);

  const search = document.getElementById('search');
  const kind = document.getElementById('kind');
  const sort = document.getElementById('sort');
  const tbody = document.querySelector('#directory-table tbody');
  const rows = Array.from(tbody.rows);
  const name = row => row.querySelector('th a').textContent;
  function filter() {
    const query = search.value.trim().toLocaleLowerCase();
    let shown = 0;
    rows.forEach(row => {
      row.hidden = !(row.textContent.toLocaleLowerCase().includes(query) && (!kind.value || row.dataset.kind === kind.value));
      if (!row.hidden) shown++;
    });
    document.getElementById('result-count').textContent = `Showing ${shown} of ${rows.length} editors`;
    document.getElementById('empty').hidden = shown !== 0;
  }
  function reorder() {
    const compare = sort.value === 'stars' ? (a, b) => Number(b.dataset.stars) - Number(a.dataset.stars) : sort.value === 'updated' ? (a, b) => b.dataset.updated.localeCompare(a.dataset.updated) : () => 0;
    [...rows].sort((a, b) => compare(a, b) || name(a).localeCompare(name(b))).forEach(row => tbody.append(row));
  }
  search.addEventListener('input', filter);
  kind.addEventListener('change', filter);
  sort.addEventListener('change', reorder);
  document.querySelector('form').addEventListener('reset', () => {
    search.value = ''; kind.value = ''; sort.value = 'name';
    filter(); reorder();
  });
  document.querySelectorAll('.star-badge img').forEach(img => {
    const fallback = () => {
      if (img.dataset.fallback) {
        img.src = img.dataset.fallback;
        delete img.dataset.fallback;
        img.title = 'Snapshot badge; live badge service unavailable';
      } else img.hidden = true;
    };
    img.addEventListener('error', fallback);
    if (img.complete && img.naturalWidth === 0) fallback();
  });
}

if (typeof module !== 'undefined') module.exports = { daysSince };
