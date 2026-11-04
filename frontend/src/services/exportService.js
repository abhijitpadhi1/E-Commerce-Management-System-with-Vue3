import api from "./api";

export async function requestOrderHistoryExport(format) {
    const response = await api.post('/exports/orders', { format });
    return response.data;
}

export async function getOrderHistoryExportStatus(taskId) {
    const response = await api.get(`/exports/orders/${taskId}/status`);
    return response.data;
}