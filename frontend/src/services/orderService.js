import api from './api';

export async function checkoutOrder(shippingAddress) {
    const response = await api.post('/orders/checkout', {
        shipping_address: shippingAddress,
    });

    return response.data.order;
}

export async function getMyOrders() {
    const response = await api.get('/orders/');
    return response.data.orders;
}

export async function getOrderById(orderId) {
    const response = await api.get(`/orders/${orderId}`);
    return response.data.order;
}

export async function getAllOrders() {
    const response = await api.get('/orders/admin');
    return response.data.orders;
}

export async function shipOrder(orderId) {
    const response = await api.patch(`/orders/${orderId}/ship`);
    return response.data.order;
}

export async function confirmOrderDelivery(orderId) {
    const response = await api.patch(`/orders/${orderId}/confirm-delivery`);
    return response.data.order;
}

export async function modifyUnpaidOrder(orderId) {
    const response = await api.post(`/orders/${orderId}/modify`);
    return response.data;
}