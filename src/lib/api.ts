import axios from 'axios';

const API_BASE_URL = 'https://campulse-mvp-1-be-production.up.railway.app/';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
  withCredentials: false, // Important: set to true if backend requires credentials
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// User APIs
export const userAPI = {
  signup: (data: { username: string; password: string; email: string; fullName: string }) =>
    api.post('/user/signup', data),
  login: (data: { username: string; password: string }) =>
    api.post('/user/login', data),
  forgotPassword: (username: string) =>
    api.post(`/user/forget-password/${username}`),
};

// Profile APIs
export const profileAPI = {
  create: (data: any) => api.post('/profile/', data),
  update: (data: any) => api.put('/profile/', data),
  get: (username: string) => api.get(`/profile/${username}`),
};

// Project APIs
export const projectAPI = {
  upload: (data: any) => api.post('/project/project', data),
  delete: (id: number) => api.delete(`/project/project/${id}`),
  getAll: () => api.get('/project/projects'),
  apply: (data: any) => api.post('/project/project/apply', data),
  getApplications: (username: string) => api.get(`/project/project/applied/${username}`),
  getMyApplications: (username: string) => api.get(`/project/project/my-applications/${username}`),
  acceptApplicant: (data: any) => api.post('/project/project/accept', data),
};

// Ideas APIs
export const ideasAPI = {
  add: (data: any) => api.post('/project/idea', data),
  getAll: () => api.get('/project/ideas'),
  getByTitle: (title: string) => api.get(`/project/idea/${title}`),
  delete: (title: string) => api.delete(`/project/idea/${title}`),
  addComment: (data: any) => api.post('/project/comment', data),
  getComments: (title: string) => api.get(`/project/comments/${title}`),
  deleteComment: (id: number) => api.delete(`/project/comment/${id}`),
};

// Miscellaneous Project APIs (Teams)
export const teamsAPI = {
  create: (data: any) => api.post('/project/misc/project', data),
  getAll: () => api.get('/project/misc/projects'),
  apply: (data: any) => api.post('/project/misc/project/apply', data),
  getApplications: (teamName: string) => api.get(`/project/misc/project/applications/${teamName}`),
  acceptApplicant: (applicationId: number) => api.post(`/project/misc/project/accept/${applicationId}`),
  delete: (teamName: string) => api.delete(`/project/misc/project/${teamName}`),
};

// Feed APIs
export const feedAPI = {
  upload: (data: any) => api.post('/feed/feed', data),
  update: (data: any) => api.put('/feed/feed', data),
  delete: (id: number) => api.delete(`/feed/feed/${id}`),
  getAll: () => api.get('/feed/feeds'),
  getByUsername: (username: string) => api.get(`/feed/feeds/${username}`),
  addComment: (data: any) => api.post('/feed/comments', data),
  updateComment: (data: any) => api.put('/feed/comments', data),
  deleteComment: (id: number) => api.delete(`/feed/comments/${id}`),
  getComments: (feedId: number) => api.get(`/feed/comments/${feedId}`),
};

// Group APIs
export const groupAPI = {
  getAllGroups: (username: string) => api.get(`/group/${username}`),
};


// Notification APIs
export const notificationAPI = {
  create: (data) => api.post('/notification/create', null, { params: data }),
  getUserNotifications: (receiver) => api.get(`/notification/user/${receiver}`),
};


// Chat API (WebSocket endpoint)
export const CHAT_WS_URL = 'wss://localhost:8081/ws-chat';
