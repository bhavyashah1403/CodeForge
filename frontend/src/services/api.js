import axios from 'axios';

/**
 * API Service for CodeForge Options Market Analytics
 *
 * Uses Vite proxy in dev (/api -> http://localhost:8000/api)
 * In production, set VITE_API_BASE_URL to your backend URL.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
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
  api.get('/key-metrics', { params: { expiry: params.expiry } });

export const fetchOpenInterest = (params = {}) =>
  api.get('/oi-distribution', { params: { expiry: params.expiry } });

export const fetchVolatilitySmile = (params = {}) =>
  api.get('/volatility-smile', { params: { expiry: params.expiry } });

export const fetchVolumeHeatmap = (params = {}) =>
  api.get('/oi-heatmap', { params: { expiry: params.expiry } });

export const fetchAIInsights = (params = {}) =>
  api.get('/ai-insights', { params: { expiry: params.expiry } });

export const fetchCumulativeOI = (params = {}) =>
  api.get('/pcr', { params: { expiry: params.expiry } });

export const fetchAnomalies = (params = {}) =>
  api.get('/anomalies', { params: { expiry: params.expiry, n: params.n || 50 } });

export const fetchAnomalyScatter = (params = {}) =>
  api.get('/anomaly-scatter', { params: { expiry: params.expiry } });

export const fetchVolumeSpikes = (params = {}) =>
  api.get('/volume-spikes', { params: { expiry: params.expiry } });

export const fetchGreeks = (params = {}) =>
  api.get('/greeks', { params: { expiry: params.expiry } });

export const fetchMaxPain = (params = {}) =>
  api.get('/max-pain', { params: { expiry: params.expiry } });

export const fetchVolatilitySurface = (params = {}) =>
  api.get('/volatility-surface', { params: { expiry: params.expiry } });

export const fetchVolumeSurface = (params = {}) =>
  api.get('/volume-surface', { params: { expiry: params.expiry } });

export const fetchMetrics = () =>
  api.get('/metrics');

export const fetchSpotPrice = (params = {}) =>
  api.get('/spot-price', { params: { expiry: params.expiry } });

export const fetchExpiries = () =>
  api.get('/expiries');

export const fetchPatternAnalysis = (params = {}) =>
  api.get('/pattern-analysis', { params: { expiry: params.expiry } });

export default api;
