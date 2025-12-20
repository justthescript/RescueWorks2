import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const register = (data) => api.post('/auth/register', data);
export const login = (data) => api.post('/auth/login', data, {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  transformRequest: [(data) => {
    return Object.keys(data).map(key => `${key}=${encodeURIComponent(data[key])}`).join('&');
  }]
});
export const getCurrentUser = () => api.get('/auth/me');

// Animals (Sprint 1)
export const createAnimal = (data) => api.post('/animals/', data);
export const uploadAnimalPhoto = (animalId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post(`/animals/${animalId}/upload-photo`, formData);
};
export const getAnimals = (params) => api.get('/animals/', { params });
export const getAnimal = (id) => api.get(`/animals/${id}`);
export const updateAnimal = (id, data) => api.patch(`/animals/${id}`, data);
export const deleteAnimal = (id) => api.delete(`/animals/${id}`);

// Foster Management (Sprint 2)
export const createFosterProfile = (data) => api.post('/foster/profiles', data);
export const getFosterProfiles = (params) => api.get('/foster/profiles', { params });
export const getMyFosterProfile = () => api.get('/foster/profiles/me');
export const updateMyFosterProfile = (data) => api.patch('/foster/profiles/me', data);
export const getSuggestedMatches = (params) => api.get('/foster/matches', { params });
export const createPlacement = (data) => api.post('/foster/placements', data);
export const getPlacements = (params) => api.get('/foster/placements', { params });
export const updatePlacement = (id, data) => api.patch(`/foster/placements/${id}`, data);
export const getFosterDashboard = () => api.get('/foster/dashboard');

// Operations (Sprint 3)
export const createCareUpdate = (data) => api.post('/operations/care-updates', data);
export const getCareUpdates = (params) => api.get('/operations/care-updates', { params });
export const searchAnimals = (params) => api.get('/operations/search/animals', { params });
export const getAnimalReport = (params) => api.get('/operations/reports/animals', { params });
export const getFosterPerformanceReport = () => api.get('/operations/reports/foster-performance');
export const getDashboardSummary = () => api.get('/operations/reports/dashboard-summary');

// Admin (Sprint 4)
export const getUsers = () => api.get('/admin/users');
export const updateUserRole = (userId, role) => api.patch(`/admin/users/${userId}/role`, null, { params: { role } });
export const updateUserStatus = (userId, is_active) => api.patch(`/admin/users/${userId}/status`, null, { params: { is_active } });
export const getSystemConfig = () => api.get('/admin/config');
export const createSystemConfig = (data) => api.post('/admin/config', data);
export const updateSystemConfig = (key, data) => api.patch(`/admin/config/${key}`, data);
export const getOrganizationInfo = () => api.get('/admin/organization');

export default api;
