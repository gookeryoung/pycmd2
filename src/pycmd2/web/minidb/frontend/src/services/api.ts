import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getAllWorkspaces = () => {
  return api.get('/workspaces');
};

export const getWorkspace = (path) => {
  return api.get(`/workspaces/${path}`);
};

export const createWorkspace = (name, parentPath = null) => {
  return api.post('/workspaces', { name, parent_path: parentPath });
};

export const deleteWorkspace = (path) => {
  return api.delete(`/workspaces/${path}`);
};

export const addDataToWorkspace = (path, key, value) => {
  return api.post(`/workspaces/${path}/data`, { key, value });
};

export const removeDataFromWorkspace = (path, key) => {
  return api.delete(`/workspaces/${path}/data/${key}`);
};
