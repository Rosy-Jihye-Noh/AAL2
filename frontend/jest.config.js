/**
 * Jest Configuration for AAL Frontend Tests
 */
module.exports = {
  // Test environment
  testEnvironment: 'jsdom',
  
  // Setup files
  setupFilesAfterEnv: ['<rootDir>/__tests__/setup.js'],
  
  // Test file patterns
  testMatch: [
    '**/__tests__/**/*.test.js',
    '**/__tests__/**/*.spec.js'
  ],
  
  // Module name mapping (for imports)
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/js/$1',
    '^@utils/(.*)$': '<rootDir>/js/utils/$1',
    '^@features/(.*)$': '<rootDir>/js/features/$1',
    '^@config/(.*)$': '<rootDir>/js/config/$1'
  },
  
  // Transform settings (no transformation needed for vanilla JS)
  transform: {},
  
  // Coverage settings
  collectCoverageFrom: [
    'js/**/*.js',
    '!js/**/*.min.js',
    '!**/node_modules/**'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'html', 'lcov'],
  coverageThreshold: {
    global: {
      branches: 50,
      functions: 50,
      lines: 50,
      statements: 50
    }
  },
  
  // Ignore patterns
  testPathIgnorePatterns: [
    '/node_modules/',
    '/coverage/'
  ],
  
  // Verbose output
  verbose: true,
  
  // Clear mocks between tests
  clearMocks: true,
  
  // Restore mocks after each test
  restoreMocks: true,
  
  // Global timeout
  testTimeout: 10000
};
