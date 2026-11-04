const { test } = require('node:test');
const assert = require('node:assert/strict');
const { daysSince } = require('../script.js');
test('counter advances on UTC calendar days, regardless of local offset', () => {
  assert.equal(daysSince('2026-11-01', new Date('2026-11-04T00:01:00Z')), 3);
  assert.equal(daysSince('2026-11-01', new Date('2026-11-03T17:01:00-07:00')), 3);
});
test('leap day and year boundaries', () => {
  assert.equal(daysSince('2024-02-28', new Date('2024-03-01T00:00:00Z')), 2);
  assert.equal(daysSince('2025-12-31', new Date('2026-01-01T00:00:00Z')), 1);
});
test('a clock behind the introduction never produces a negative counter', () => {
  assert.equal(daysSince('2026-11-01', new Date('2026-10-31T23:00:00Z')), 0);
});
