/**
 * Test Data Fixtures for E2E Tests
 */

// Test user credentials
export const testUsers = {
  shipper: {
    email: 'shipper@test.com',
    password: 'TestShipper123!',
    name: 'Test Shipper',
    company: 'Test Shipping Co.',
    role: 'shipper'
  },
  forwarder: {
    email: 'forwarder@test.com',
    password: 'TestForwarder123!',
    name: 'Test Forwarder',
    company: 'Test Forwarding Co.',
    role: 'forwarder'
  }
};

// Sample quote request data
export const sampleQuoteRequests = {
  oceanFCL: {
    tradeMode: 'export',
    shippingType: 'ocean',
    loadType: 'FCL',
    pol: 'KRPUS',
    pod: 'USLAX',
    containerType: '40HC',
    containerQty: 2
  },
  airFreight: {
    tradeMode: 'export',
    shippingType: 'air',
    loadType: 'AIR',
    pol: 'KRICN',
    pod: 'USJFK',
    cargoWeight: 500,
    cargoCbm: 3.5
  },
  trucking: {
    tradeMode: 'domestic',
    shippingType: 'truck',
    loadType: 'FTL',
    pickupAddress: 'Seoul, Korea',
    deliveryAddress: 'Busan, Korea',
    truckType: '5T_WING'
  }
};

// Port data for selection
export const ports = {
  korea: [
    { code: 'KRPUS', name: 'Busan' },
    { code: 'KRICN', name: 'Incheon' },
    { code: 'KRKAN', name: 'Gwangyang' }
  ],
  usa: [
    { code: 'USLAX', name: 'Los Angeles' },
    { code: 'USNYC', name: 'New York' },
    { code: 'USJFK', name: 'JFK Airport' }
  ],
  europe: [
    { code: 'NLRTM', name: 'Rotterdam' },
    { code: 'DEHAM', name: 'Hamburg' },
    { code: 'GBFXT', name: 'Felixstowe' }
  ]
};

// Market data test cases
export const marketDataTests = {
  exchangeRate: {
    type: 'exchange_rate',
    currency: 'USD',
    expectedFields: ['date', 'value', 'change']
  },
  shippingIndices: {
    indices: ['BDI', 'SCFI', 'CCFI'],
    expectedFields: ['date', 'value', 'change_rate']
  },
  economicIndicators: {
    types: ['gdp', 'inflation', 'interest_rate'],
    expectedFields: ['period', 'value']
  }
};
