import api from './api';

export async function getAdminDashboard() {
    const response = await api.get('/dashboard/stats');
    return response.data.dashboard;
}