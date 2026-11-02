import api from './api';

export async function getProducts() {
    const response = await api.get('/products/');
    return response.data.products;
}

export async function getProductById(productId) {
    const response = await api.get(`/products/${productId}`);
    return response.data.product;
}

export async function getAdminProducts() {
    const response = await api.get('/products/admin');
    return response.data.products;
}

export async function updateProduct(productId, productData) {
    const response = await api.patch(`/products/${productId}`, productData);
    return response.data.product;
}

export async function createProduct(productData) {
    const response = await api.post('/products/', productData);
    return response.data.product;
}

export async function deleteProduct(productId) {
    const response = await api.delete(`/products/${productId}`);
    return response.data;
}