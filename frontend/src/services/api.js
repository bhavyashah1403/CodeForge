import axios from 'axios';

/**
 * API Service for CodeForge Options Market Analytics
 *
 * Base URL is read from the VITE_API_BASE_URL environment variable.
 * Update .env to point to your backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Response interceptor for error handling ──────────────────────
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('[API Error]', error?.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ── API Endpoints ────────────────────────────────────────────────

export const fetchMarketSummary = (params = {}) =>
  api.get('/market-summary', { params });

export const fetchOpenInterest = (params = {}) =>
  api.get('/open-interest', { params });

export const fetchVolatilitySmile = (params = {}) =>
  api.get('/volatility-smile', { params });

export const fetchVolumeHeatmap = (params = {}) =>
  api.get('/volume-heatmap', { params });

export const fetchAIInsights = (params = {}) =>
  api.get('/ai-insights', { params });

export const fetchCumulativeOI = (params = {}) =>
  api.get('/cumulative-oi', { params });

export default api;
