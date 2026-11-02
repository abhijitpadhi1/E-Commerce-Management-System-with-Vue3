import { ref, computed } from 'vue';
import { defineStore } from 'pinia';

import * as api from '@/services/cartService';

export const useCartStore = defineStore('cart', () => {
    // state
    const items = ref([]);
    const loading = ref(false);
    const errorMessage = ref('');

    // getters
    const itemCount = computed(() => items.value.reduce((total, item) => total + item.quantity, 0));
    const totalAmount = computed(() => items.value.reduce(
        (total, item) => total + Number(item.unit_price) * item.quantity, 0
    ));

    // actions
    async function fetchCart() {
        loading.value = true;
        errorMessage.value = '';

        try {
            const cart = await api.getCart();
            items.value = cart.items;
        } catch (error) {
            errorMessage.value = error.response?.data?.message || 'Unable to load cart.';
            throw error;
        } finally {
            loading.value = false;
        }
    }

    async function addItem(productId, quantity = 1) {
        await api.addCartItem(productId, quantity);
        await fetchCart();
    }

    async function updateItem(itemId, quantity) {
        await api.updateCartItem(itemId, quantity);
        await fetchCart();
    }

    async function removeItem(itemId) {
        await api.removeCartItem(itemId);
        await fetchCart();
    }

    async function emptyCart() {
        await api.clearCart();
        items.value = [];
    }

    function resetCart() {
        items.value = [];
        errorMessage.value = '';
    }

    return {
        items, loading, errorMessage,
        itemCount, totalAmount,
        fetchCart, addItem, updateItem, removeItem, emptyCart, resetCart,
    }
})