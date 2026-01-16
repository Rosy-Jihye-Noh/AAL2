/**
 * Jest Setup File for AAL Frontend Tests
 * This file runs before each test file
 */

// Extend expect with jest-dom matchers
require('@testing-library/jest-dom');

// Mock window.API_CONFIG
global.API_CONFIG = {
  MAIN_API_BASE: 'http://localhost:5000',
  QUOTE_API_BASE: 'http://localhost:8001',
  AUTH_API_BASE: 'http://localhost:5000/api/auth',
  FORWARDER_API_BASE: 'http://localhost:8001/api/forwarder'
};

// Mock window.API_BASE
global.API_BASE = 'http://localhost:5000/api';

// Mock fetch API
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve('')
  })
);

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};
global.sessionStorage = sessionStorageMock;

// Mock Chart.js (if used)
global.Chart = jest.fn().mockImplementation(() => ({
  destroy: jest.fn(),
  update: jest.fn(),
  data: { datasets: [] }
}));

// Mock console methods to suppress noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  // Keep error for debugging
  error: console.error
};

// Mock requestAnimationFrame
global.requestAnimationFrame = jest.fn(cb => setTimeout(cb, 0));
global.cancelAnimationFrame = jest.fn(id => clearTimeout(id));

// Mock performance.now
global.performance = {
  now: jest.fn(() => Date.now())
};

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
  document.body.innerHTML = '';
});
