import api from './api';

export async function makeMockPayment(orderId, outcome = 'success') {
    const response = await api.post(`/payments/mock/${orderId}`, {
        outcome,
    });

    return response.data;
}