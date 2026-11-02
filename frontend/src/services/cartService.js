import api from './api'

export async function getCart() {
    const response = await api.get('/cart/')
    return response.data.cart
}

export async function addCartItem(productId, quantity = 1) {
    const response = await api.post('/cart/items', {
        product_id: productId,
        quantity,
    })

    return response.data
}

export async function updateCartItem(itemId, quantity) {
    const response = await api.patch(`/cart/items/${itemId}`, {
        quantity,
    })

    return response.data
}

export async function removeCartItem(itemId) {
    const response = await api.delete(`/cart/items/${itemId}`)
    return response.data
}

export async function clearCart() {
    const response = await api.delete('/cart/')
    return response.data
}