<script setup>
import { onMounted, ref } from 'vue';
import { useCartStore } from '@/stores/cartStore';
import { useNotification } from '@/composables/useNotifications';

const cartStore = useCartStore();
const { notify } = useNotification();

const updatingItemId = ref(null);
const removingItemId = ref(null);
const clearingCart = ref(false);

onMounted(async () => {
    try {
        await cartStore.fetchCart();
    } catch {
        // The store already sets its error message.
    }
});

function formatPrice(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(Number(value));
}

async function changeQuantity(item, quantity) {
    if (!Number.isInteger(quantity) || quantity < 1) {
        notify('Quantity must be at least 1.', 'warning');
        return;
    }

    if (quantity > item.product.stock) {
        notify(`Only ${item.product.stock} unit(s) are available.`, 'warning');
        return;
    }

    updatingItemId.value = item.id;

    try {
        await cartStore.updateItem(item.id, quantity);
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to update quantity.', 'danger');
    } finally {
        updatingItemId.value = null;
    }
}

async function removeItem(item) {
    removingItemId.value = item.id;

    try {
        await cartStore.removeItem(item.id);
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to remove item.', 'danger');
    } finally {
        removingItemId.value = null;
    }
}

async function handleClearCart() {
    clearingCart.value = true;

    try {
        await cartStore.emptyCart();
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to clear cart.', 'danger');
    } finally {
        clearingCart.value = false;
    }
}
</script>

<template>
    <main class="page-container cart-page">
        <!-- Page heading -->
        <header class="cart-page-header">
            <div>
                <p class="eyebrow">YOUR SELECTION</p>
                <h1 class="cart-page-title">Shopping Cart</h1>
                <p class="cart-page-subtitle">Review your items before placing your order.</p>
            </div>

            <button
                v-if="!cartStore.loading && cartStore.items.length > 0"
                class="btn btn-outline-danger clear-cart-button"
                :disabled="clearingCart"
                @click="handleClearCart"
            >
                {{ clearingCart ? 'Clearing...' : 'Clear Cart' }}
            </button>
        </header>

        <!-- Loading -->
        <section v-if="cartStore.loading" class="cart-state-panel">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading cart...</span>
            </div>
            <p class="mt-3 mb-0">Loading your cart...</p>
        </section>

        <!-- Empty cart -->
        <section v-else-if="cartStore.items.length === 0" class="cart-state-panel empty-cart-panel">
            <div class="empty-cart-icon" aria-hidden="true">🛍️</div>
            <h2>Your cart is empty</h2>
            <p>Looks like you haven't added anything yet.</p>

            <RouterLink :to="{ name: 'products' }" class="btn btn-primary">
                Explore Products
            </RouterLink>
        </section>

        <!-- Cart content -->
        <section v-else class="cart-layout">
            <!-- Cart items -->
            <div class="cart-items-section">
                <div class="cart-section-heading">
                    <h2>Your Items</h2>
                    <span class="cart-item-count">{{ cartStore.itemCount }} item(s)</span>
                </div>

                <article v-for="item in cartStore.items" :key="item.id" class="cart-item-card">
                    <!-- Product image -->
                    <RouterLink 
                        :to="{ name: 'product-details', params: { id: item.product.id } }"
                        class="cart-item-image"
                    >
                        <img 
                            v-if="item.product.image_url" 
                            :src="item.product.image_url" 
                            :alt="item.product.name" 
                        />

                        <div v-else class="cart-item-image-placeholder">
                            <span>No image</span>
                        </div>
                    </RouterLink>

                    <!-- Product information -->
                    <div class="cart-item-information">
                        <p class="cart-item-category">{{ item.product.category || 'General' }}</p>
                        <h3 class="cart-item-name">{{ item.product.name }}</h3>
                        <p class="cart-item-unit-price">{{ formatPrice(item.unit_price) }} <span>each</span></p>

                        <div
                            class="cart-stock-status"
                            :class="item.product.stock > 0 ? 'stock-available' : 'stock-unavailable'"
                        >
                            <span class="stock-status-dot"></span>
                            <span>
                                {{ item.product.stock > 0 ? `${item.product.stock} available` : 'Out of stock' }}
                            </span>
                        </div>
                    </div>

                    <!-- Quantity and item total -->
                    <div class="cart-item-controls">
                        <label class="quantity-label" :for="`quantity-${item.id}`">Quantity</label>

                        <div class="quantity-control">
                            <button
                                type="button"
                                class="quantity-button"
                                :disabled="updatingItemId === item.id || item.quantity <= 1"
                                :aria-label="`Decrease quantity of ${item.product.name}`"
                                @click="changeQuantity(item, item.quantity - 1)"
                            >
                                &minus;
                            </button>

                            <input
                                :id="`quantity-${item.id}`"
                                type="number"
                                class="quantity-input"
                                min="1"
                                :max="item.product.stock"
                                :value="item.quantity"
                                :disabled="updatingItemId === item.id || item.product.stock === 0"
                                @change="changeQuantity(item, Number($event.target.value))"
                            />

                            <button
                                type="button"
                                class="quantity-button"
                                :disabled="updatingItemId === item.id || item.quantity >= item.product.stock"
                                :aria-label="`Increase quantity of ${item.product.name}`"
                                @click="changeQuantity(item, item.quantity + 1)"
                            >
                                +
                            </button>
                        </div>

                        <p class="cart-item-subtotal">{{ formatPrice(item.subtotal) }}</p>

                        <button
                            type="button"
                            class="remove-item-button"
                            :disabled="removingItemId === item.id"
                            @click="removeItem(item)"
                        >
                            {{ removingItemId === item.id ? 'Removing...' : 'Remove item' }}
                        </button>
                    </div>
                </article>
            </div>

            <!-- Order summary -->
            <aside class="cart-summary-card">
                <div class="summary-heading">
                    <div>
                        <p class="eyebrow">SUMMARY</p>
                        <h2>Order Summary</h2>
                    </div>

                    <div class="summary-bag-icon" aria-hidden="true">🛒</div>
                </div>

                <div class="summary-row">
                    <span>Items</span>
                    <span>{{ cartStore.itemCount }}</span>
                </div>

                <div class="summary-row">
                    <span>Subtotal</span>
                    <span>{{ formatPrice(cartStore.totalAmount) }}</span>
                </div>

                <div class="summary-row summary-shipping">
                    <span>Shipping</span>
                    <span>Calculated at checkout</span>
                </div>

                <div class="summary-divider"></div>

                <div class="summary-total-row">
                    <span>Estimated Total</span>
                    <strong>{{ formatPrice(cartStore.totalAmount) }}</strong>
                </div>

                <RouterLink :to="{ name: 'checkout' }" class="btn btn-primary checkout-button">
                    Proceed to Checkout
                    <span aria-hidden="true">→</span>
                </RouterLink>

                <RouterLink :to="{ name: 'products' }" class="continue-shopping-link">
                    ← Continue Shopping
                </RouterLink>

                <div class="summary-assurance">
                    <span aria-hidden="true">✓</span>
                    <span>Review your order before payment</span>
                </div>
            </aside>
        </section>
    </main>
</template>

<style scoped>
.cart-page {
    max-width: 1320px;
}

/* Page header */
.cart-page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
}

.eyebrow {
    margin-bottom: 0.45rem;
    color: var(--brand, #4f7cff);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.1em;
}

.cart-page-title {
    margin-bottom: 0.45rem;
    color: var(--text-primary, #1d273b);
    font-size: clamp(1.8rem, 3vw, 2.5rem);
    font-weight: 800;
    letter-spacing: -0.04em;
}

.cart-page-subtitle {
    margin-bottom: 0;
    color: var(--text-secondary, #718096);
    font-size: 0.95rem;
}

.clear-cart-button {
    border-radius: 10px;
    padding: 0.65rem 1rem;
}

/* Main layout */
.cart-layout {
    display: grid;
    grid-template-columns: minmax(0, 1.7fr) minmax(290px, 0.9fr);
    align-items: start;
    gap: 1.5rem;
}

.cart-items-section {
    min-width: 0;
}

.cart-section-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.cart-section-heading h2 {
    margin: 0;
    color: var(--text-primary, #1d273b);
    font-size: 1.1rem;
    font-weight: 750;
}

.cart-item-count {
    padding: 0.35rem 0.7rem;
    border: 1px solid var(--border, #dfe6f1);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.65);
    color: var(--text-secondary, #718096);
    font-size: 0.78rem;
}

/* Individual cart item */
.cart-item-card {
    display: grid;
    grid-template-columns: 132px minmax(0, 1fr) 150px;
    gap: 1.1rem;
    align-items: center;
    padding: 1rem;
    margin-bottom: 1rem;
    border: 1px solid var(--border, #dfe6f1);
    border-radius: var(--radius-lg, 16px);
    background: rgba(255, 255, 255, 0.88);
    box-shadow: var(--shadow-sm, 0 3px 12px rgba(35, 54, 90, 0.05));
    transition:
        transform 160ms ease,
        box-shadow 160ms ease;
}

.cart-item-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md, 0 8px 22px rgba(35, 54, 90, 0.08));
}

.cart-item-image {
    display: flex;
    width: 132px;
    height: 132px;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border-radius: 12px;
    background: #fff;
}

.cart-item-image img {
    width: 100%;
    height: 100%;
    padding: 0.5rem;
    object-fit: contain;
}

.cart-item-image-placeholder {
    display: flex;
    width: 100%;
    height: 100%;
    align-items: center;
    justify-content: center;
    background: #f4f7fc;
    color: var(--text-secondary, #718096);
    font-size: 0.75rem;
}

.cart-item-information {
    min-width: 0;
}

.cart-item-category {
    margin-bottom: 0.4rem;
    color: var(--brand, #4f7cff);
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.cart-item-name {
    display: -webkit-box;
    overflow: hidden;
    margin-bottom: 0.65rem;
    color: var(--text-primary, #1d273b);
    font-size: 0.98rem;
    font-weight: 700;
    line-height: 1.45;
    line-clamp: 2;
    -webkit-box-orient: vertical;
}

.cart-item-unit-price {
    margin-bottom: 0.6rem;
    color: var(--text-primary, #1d273b);
    font-size: 0.9rem;
    font-weight: 650;
}

.cart-item-unit-price span {
    color: var(--text-secondary, #718096);
    font-size: 0.78rem;
    font-weight: 400;
}

.cart-stock-status {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.75rem;
    font-weight: 650;
}

.stock-status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: currentColor;
}

.stock-available {
    color: var(--success, #16845b);
}

.stock-unavailable {
    color: var(--danger, #c2414b);
}

/* Quantity and item subtotal */
.cart-item-controls {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

.quantity-label {
    align-self: flex-start;
    margin-bottom: 0.4rem;
    color: var(--text-secondary, #718096);
    font-size: 0.75rem;
    font-weight: 650;
}

.quantity-control {
    display: flex;
    width: 100%;
    height: 38px;
    align-items: center;
    overflow: hidden;
    border: 1px solid var(--border, #dfe6f1);
    border-radius: 9px;
    background: #fff;
}

.quantity-button {
    width: 32px;
    height: 100%;
    flex: 0 0 32px;
    border: 0;
    background: #f5f7fc;
    color: var(--text-primary, #1d273b);
    font-size: 1.1rem;
    transition: background 150ms ease;
}

.quantity-button:hover:not(:disabled) {
    background: #e8edfb;
}

.quantity-button:disabled {
    color: #aab3c2;
    cursor: not-allowed;
}

.quantity-input {
    width: 100%;
    min-width: 0;
    height: 100%;
    padding: 0;
    border: 0;
    outline: none;
    color: var(--text-primary, #1d273b);
    font-size: 0.85rem;
    text-align: center;
}

.quantity-input:focus {
    box-shadow: inset 0 0 0 1px var(--brand, #4f7cff);
}

.cart-item-subtotal {
    margin: 0.8rem 0 0.4rem;
    color: var(--text-primary, #1d273b);
    font-size: 1rem;
    font-weight: 800;
}

.remove-item-button {
    padding: 0;
    border: 0;
    background: transparent;
    color: var(--danger, #c2414b);
    font-size: 0.75rem;
    font-weight: 650;
}

.remove-item-button:hover:not(:disabled) {
    text-decoration: underline;
}

.remove-item-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* Order summary */
.cart-summary-card {
    position: sticky;
    top: 1.5rem;
    padding: 1.4rem;
    border: 1px solid var(--border, #dfe6f1);
    border-radius: var(--radius-lg, 16px);
    background: rgba(255, 255, 255, 0.92);
    box-shadow: var(--shadow-md, 0 8px 22px rgba(35, 54, 90, 0.07));
}

.summary-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.summary-heading .eyebrow {
    margin-bottom: 0.3rem;
}

.summary-heading h2 {
    margin: 0;
    color: var(--text-primary, #1d273b);
    font-size: 1.2rem;
    font-weight: 800;
}

.summary-bag-icon {
    display: grid;
    width: 42px;
    height: 42px;
    place-items: center;
    border-radius: 12px;
    background: var(--brand-soft, #e9efff);
    font-size: 1.2rem;
}

.summary-row {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.9rem;
    color: var(--text-secondary, #718096);
    font-size: 0.88rem;
}

.summary-row span:last-child {
    color: var(--text-primary, #1d273b);
    font-weight: 650;
    text-align: right;
}

.summary-shipping span:last-child {
    max-width: 140px;
    color: var(--text-secondary, #718096);
    font-size: 0.76rem;
    font-weight: 400;
}

.summary-divider {
    height: 1px;
    margin: 1.2rem 0;
    background: var(--border, #dfe6f1);
}

.summary-total-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.25rem;
    color: var(--text-primary, #1d273b);
    font-size: 0.9rem;
}

.summary-total-row strong {
    font-size: 1.2rem;
    font-weight: 850;
    text-align: right;
}

.checkout-button {
    display: flex;
    min-height: 48px;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    border: 0;
    border-radius: 10px;
    background: var(--brand, #4f7cff);
    font-weight: 750;
}

.checkout-button:hover {
    background: var(--brand-hover, #3868ef);
}

.continue-shopping-link {
    display: block;
    margin-top: 1rem;
    color: var(--brand, #4f7cff);
    font-size: 0.82rem;
    font-weight: 650;
    text-align: center;
    text-decoration: none;
}

.continue-shopping-link:hover {
    text-decoration: underline;
}

.summary-assurance {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.45rem;
    margin-top: 1.2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border, #dfe6f1);
    color: var(--text-secondary, #718096);
    font-size: 0.72rem;
}

.summary-assurance span:first-child {
    color: var(--success, #16845b);
    font-weight: 800;
}

/* Loading and empty states */
.cart-state-panel {
    display: flex;
    min-height: 350px;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    border: 1px dashed var(--border, #dfe6f1);
    border-radius: var(--radius-lg, 16px);
    background: rgba(255, 255, 255, 0.65);
    color: var(--text-secondary, #718096);
    text-align: center;
}

.empty-cart-icon {
    display: grid;
    width: 76px;
    height: 76px;
    place-items: center;
    margin-bottom: 1.2rem;
    border-radius: 24px;
    background: var(--brand-soft, #e9efff);
    font-size: 2rem;
}

.empty-cart-panel h2 {
    margin-bottom: 0.5rem;
    color: var(--text-primary, #1d273b);
    font-size: 1.4rem;
    font-weight: 800;
}

.empty-cart-panel p {
    margin-bottom: 1.25rem;
}

/* Responsive */
@media (max-width: 991px) {
    .cart-layout {
        grid-template-columns: 1fr;
    }

    .cart-summary-card {
        position: static;
    }
}

@media (max-width: 767px) {
    .cart-page-header {
        align-items: flex-start;
    }

    .cart-item-card {
        grid-template-columns: 96px minmax(0, 1fr);
        gap: 0.9rem;
    }

    .cart-item-image {
        width: 96px;
        height: 96px;
    }

    .cart-item-controls {
        grid-column: 2;
        display: grid;
        grid-template-columns: minmax(100px, 130px) 1fr;
        align-items: center;
        gap: 0.5rem 1rem;
    }

    .quantity-label {
        grid-column: 1 / -1;
        margin-bottom: 0;
    }

    .cart-item-subtotal {
        margin: 0;
        text-align: right;
    }

    .remove-item-button {
        grid-column: 1 / -1;
        justify-self: start;
    }
}

@media (max-width: 480px) {
    .cart-page-header {
        flex-direction: column;
    }

    .clear-cart-button {
        align-self: flex-start;
    }

    .cart-item-card {
        padding: 0.75rem;
    }

    .cart-item-name {
        font-size: 0.88rem;
    }

    .cart-item-controls {
        grid-template-columns: minmax(90px, 120px) 1fr;
    }
}
</style>