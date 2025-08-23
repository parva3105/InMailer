// Frontend configuration
export const config = {
  // API Configuration
  apiUrl: process.env.REACT_APP_API_URL || 'https://inmailer.onrender.com',
  
  // Google OAuth Configuration
  googleClientId: process.env.REACT_APP_GOOGLE_CLIENT_ID || '502741004777-i80atbmb80r61sssl9u4li6u7ml6cqhf.apps.googleusercontent.com',
  
  // App Configuration
  appName: 'InMailer',
  appVersion: '1.0.0',
  
  // Feature Flags
  features: {
    emailAttachments: true,
    templateVariables: true,
    bulkEmail: true,
    emailTracking: false
  }
};

// Helper function to get full API URL
export const getApiUrl = (endpoint: string): string => {
  const baseUrl = config.apiUrl.replace(/\/$/, ''); // Remove trailing slash
  const cleanEndpoint = endpoint.replace(/^\//, ''); // Remove leading slash
  return `${baseUrl}/${cleanEndpoint}`;
};

// Common API endpoints
export const apiEndpoints = {
  health: '/api/health',
  dashboard: '/api/dashboard/stats',
  templates: '/api/templates',
  userStats: '/api/user/stats',
  auth: {
    google: '/auth/google',
    callback: '/auth/google/callback'
  }
};
