import api from './api';

export async function signup(userData) {
    const response = await api.post('/auth/signup', userData);
    return response.data;
}

export async function login(credentials) {
    const response = await api.post('/auth/login', credentials);
    return response.data;
}

export async function getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
}