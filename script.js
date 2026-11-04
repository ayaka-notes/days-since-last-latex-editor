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


}

if (typeof module !== 'undefined') module.exports = { daysSince };
