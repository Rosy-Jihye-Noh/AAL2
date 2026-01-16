/**
 * Unit Tests for helpers.js utility functions
 */

// Import helpers (we'll need to adjust the path based on how they're exported)
// For now, we'll test the functions by loading them globally

// Mock the helpers.js file
const fs = require('fs');
const path = require('path');
const vm = require('vm');

// Load and execute helpers.js in a sandboxed context
const helpersPath = path.join(__dirname, '../../js/utils/helpers.js');
const helpersCode = fs.readFileSync(helpersPath, 'utf8');

// Create a context with necessary globals
const context = {
  window: {},
  document: {
    createElement: (tag) => ({
      textContent: '',
      innerHTML: '',
      set textContent(val) { this._text = val; this.innerHTML = val.replace(/</g, '&lt;').replace(/>/g, '&gt;'); },
      get textContent() { return this._text; }
    })
  },
  console: { log: jest.fn() },
  performance: { now: () => Date.now() },
  requestAnimationFrame: (cb) => setTimeout(cb, 0),
  Number: Number,
  Math: Math,
  Date: Date,
  String: String,
  Array: Array,
  Map: Map,
  Set: Set,
  parseInt: parseInt,
  isNaN: isNaN
};

// Make context properties available
vm.createContext(context);
vm.runInContext(helpersCode, context);

// Extract functions from window
const {
  formatDateForAPI,
  formatInterestDateForAPI,
  toYYYYMMDD,
  parseYYYYMMDD,
  daysInMonth,
  makeDateSafe,
  weekdayKoShort,
  formatGDPNumber,
  formatGDPChange,
  escapeHtml,
  fillMissingDates,
  findClosestDate,
  dedupeAndSortTargets
} = context.window;


// ============================================================
// DATE FORMATTING TESTS
// ============================================================

describe('formatDateForAPI', () => {
  test('converts YYYY-MM-DD to YYYYMMDD', () => {
    expect(formatDateForAPI('2024-01-15')).toBe('20240115');
  });

  test('converts date with different month', () => {
    expect(formatDateForAPI('2024-12-31')).toBe('20241231');
  });

  test('handles empty string', () => {
    expect(formatDateForAPI('')).toBe('');
  });

  test('handles string without dashes', () => {
    expect(formatDateForAPI('20240115')).toBe('20240115');
  });
});

describe('formatInterestDateForAPI', () => {
  test('converts YYYY-MM to YYYYMM01', () => {
    expect(formatInterestDateForAPI('2024-01')).toBe('20240101');
  });

  test('converts YYYY-12 to 20241201', () => {
    expect(formatInterestDateForAPI('2024-12')).toBe('20241201');
  });

  test('handles empty string', () => {
    expect(formatInterestDateForAPI('')).toBe('');
  });

  test('handles null/undefined', () => {
    expect(formatInterestDateForAPI(null)).toBe('');
    expect(formatInterestDateForAPI(undefined)).toBe('');
  });
});

describe('toYYYYMMDD', () => {
  test('converts Date to YYYYMMDD string', () => {
    const date = new Date(2024, 0, 15); // January 15, 2024
    expect(toYYYYMMDD(date)).toBe('20240115');
  });

  test('pads single digit month', () => {
    const date = new Date(2024, 0, 1); // January 1, 2024
    expect(toYYYYMMDD(date)).toBe('20240101');
  });

  test('pads single digit day', () => {
    const date = new Date(2024, 5, 5); // June 5, 2024
    expect(toYYYYMMDD(date)).toBe('20240605');
  });

  test('handles December', () => {
    const date = new Date(2024, 11, 31); // December 31, 2024
    expect(toYYYYMMDD(date)).toBe('20241231');
  });
});

describe('parseYYYYMMDD', () => {
  test('parses valid YYYYMMDD string', () => {
    const result = parseYYYYMMDD('20240115');
    expect(result.getFullYear()).toBe(2024);
    expect(result.getMonth()).toBe(0); // January
    expect(result.getDate()).toBe(15);
  });

  test('returns null for invalid length', () => {
    expect(parseYYYYMMDD('2024011')).toBeNull();
    expect(parseYYYYMMDD('202401150')).toBeNull();
  });

  test('returns null for empty string', () => {
    expect(parseYYYYMMDD('')).toBeNull();
  });

  test('returns null for null/undefined', () => {
    expect(parseYYYYMMDD(null)).toBeNull();
    expect(parseYYYYMMDD(undefined)).toBeNull();
  });
});

describe('daysInMonth', () => {
  test('returns 31 for January', () => {
    expect(daysInMonth(2024, 0)).toBe(31);
  });

  test('returns 28 for February (non-leap year)', () => {
    expect(daysInMonth(2023, 1)).toBe(28);
  });

  test('returns 29 for February (leap year)', () => {
    expect(daysInMonth(2024, 1)).toBe(29);
  });

  test('returns 30 for April', () => {
    expect(daysInMonth(2024, 3)).toBe(30);
  });

  test('returns 31 for December', () => {
    expect(daysInMonth(2024, 11)).toBe(31);
  });
});

describe('makeDateSafe', () => {
  test('returns valid date for normal input', () => {
    const result = makeDateSafe(2024, 0, 15);
    expect(result.getDate()).toBe(15);
  });

  test('clamps day to last day of month', () => {
    const result = makeDateSafe(2024, 1, 31); // Feb 31 -> Feb 29 (leap year)
    expect(result.getDate()).toBe(29);
  });

  test('clamps to 28 for non-leap February', () => {
    const result = makeDateSafe(2023, 1, 31); // Feb 31 -> Feb 28
    expect(result.getDate()).toBe(28);
  });
});

describe('weekdayKoShort', () => {
  test('returns 일 for Sunday', () => {
    const sunday = new Date(2024, 0, 7); // January 7, 2024 is Sunday
    expect(weekdayKoShort(sunday)).toBe('일');
  });

  test('returns 월 for Monday', () => {
    const monday = new Date(2024, 0, 8);
    expect(weekdayKoShort(monday)).toBe('월');
  });

  test('returns 토 for Saturday', () => {
    const saturday = new Date(2024, 0, 6);
    expect(weekdayKoShort(saturday)).toBe('토');
  });
});


// ============================================================
// NUMBER FORMATTING TESTS
// ============================================================

describe('formatGDPNumber', () => {
  test('formats number with Korean locale', () => {
    const result = formatGDPNumber(1000000);
    expect(result).toContain('1,000,000');
  });

  test('formats decimal with max 1 digit', () => {
    const result = formatGDPNumber(1234.567);
    expect(result).toMatch(/1,234\.?\d?/);
  });

  test('returns dash for NaN', () => {
    expect(formatGDPNumber(NaN)).toBe('-');
  });

  test('returns dash for Infinity', () => {
    expect(formatGDPNumber(Infinity)).toBe('-');
  });

  test('handles zero', () => {
    expect(formatGDPNumber(0)).toBe('0');
  });
});

describe('formatGDPChange', () => {
  test('adds + for positive numbers', () => {
    const result = formatGDPChange(100);
    expect(result).toMatch(/\+/);
  });

  test('no + for negative numbers', () => {
    const result = formatGDPChange(-100);
    expect(result).not.toMatch(/\+/);
    expect(result).toContain('-');
  });

  test('no sign for zero', () => {
    const result = formatGDPChange(0);
    expect(result).toBe('0');
  });

  test('returns dash for NaN', () => {
    expect(formatGDPChange(NaN)).toBe('-');
  });
});


// ============================================================
// HTML ESCAPE TESTS
// ============================================================

describe('escapeHtml', () => {
  test('escapes less than sign', () => {
    const result = escapeHtml('<script>');
    expect(result).not.toContain('<');
    expect(result).toContain('&lt;');
  });

  test('escapes greater than sign', () => {
    const result = escapeHtml('</script>');
    expect(result).toContain('&gt;');
  });

  test('handles normal text', () => {
    expect(escapeHtml('Hello World')).toBe('Hello World');
  });

  test('handles empty string', () => {
    expect(escapeHtml('')).toBe('');
  });
});


// ============================================================
// ARRAY UTILITY TESTS
// ============================================================

describe('dedupeAndSortTargets', () => {
  test('removes duplicates by idx', () => {
    const targets = [
      { idx: 1, label: 'A' },
      { idx: 1, label: 'B' }, // Duplicate idx
      { idx: 2, label: 'C' }
    ];
    const result = dedupeAndSortTargets(targets);
    expect(result.length).toBe(2);
  });

  test('sorts by idx ascending', () => {
    const targets = [
      { idx: 3, label: 'C' },
      { idx: 1, label: 'A' },
      { idx: 2, label: 'B' }
    ];
    const result = dedupeAndSortTargets(targets);
    expect(result[0].idx).toBe(1);
    expect(result[1].idx).toBe(2);
    expect(result[2].idx).toBe(3);
  });

  test('handles empty array', () => {
    const result = dedupeAndSortTargets([]);
    expect(result).toEqual([]);
  });

  test('filters out invalid entries', () => {
    const targets = [
      { idx: 1, label: 'A' },
      null,
      { idx: 2, label: 'B' },
      { label: 'C' } // Missing idx
    ];
    const result = dedupeAndSortTargets(targets);
    expect(result.length).toBe(2);
  });
});

describe('findClosestDate', () => {
  test('finds exact match', () => {
    const dates = ['20240101', '20240102', '20240103'];
    const result = findClosestDate(dates, '20240102');
    expect(result).toBe('20240102');
  });

  test('finds closest date when exact not found', () => {
    const dates = ['20240101', '20240105', '20240110'];
    const result = findClosestDate(dates, '20240103');
    expect(['20240101', '20240105']).toContain(result);
  });

  test('returns null for empty array', () => {
    const result = findClosestDate([], '20240101');
    expect(result).toBeNull();
  });

  test('returns null for null array', () => {
    const result = findClosestDate(null, '20240101');
    expect(result).toBeNull();
  });
});

describe('fillMissingDates', () => {
  test('fills missing dates with previous value', () => {
    const data = [
      { date: '20240101', value: 100 },
      { date: '20240103', value: 150 }
    ];
    const result = fillMissingDates(data, '20240101', '20240103');
    
    expect(result.length).toBe(3);
    expect(result[1].date).toBe('20240102');
    expect(result[1].value).toBe(100); // Filled with previous value
  });

  test('marks actual vs filled data', () => {
    const data = [
      { date: '20240101', value: 100 },
      { date: '20240103', value: 150 }
    ];
    const result = fillMissingDates(data, '20240101', '20240103');
    
    expect(result[0].isActual).toBe(true);
    expect(result[1].isActual).toBe(false);
    expect(result[2].isActual).toBe(true);
  });

  test('handles empty data array', () => {
    const result = fillMissingDates([], '20240101', '20240103');
    expect(result).toEqual([]);
  });

  test('handles date format with dashes', () => {
    const data = [
      { date: '20240101', value: 100 }
    ];
    const result = fillMissingDates(data, '2024-01-01', '2024-01-02');
    expect(result.length).toBe(2);
  });
});


// ============================================================
// Run tests
// ============================================================
