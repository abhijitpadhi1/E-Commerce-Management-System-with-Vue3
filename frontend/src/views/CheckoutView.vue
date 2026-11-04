<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useCartStore } from '@/stores/cartStore';
import { checkoutOrder } from '@/services/orderService';
import { useNotification } from '@/composables/useNotifications';

const router = useRouter();
const cartStore = useCartStore();
const { notify } = useNotification();

const shippingAddress = ref('');
const submitting = ref(false);

const formattedSubtotal = computed(() => formatPrice(cartStore.totalAmount));

function formatPrice(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(Number(value));
}


async function submitCheckout() {
    const address = shippingAddress.value.trim();
    if (!address) {
        notify('Please enter your shipping address.', 'warning');
        return;
    }
    if (address.length < 10) {
        notify('Please enter a complete shipping address.', 'warning');
        return;
    }

    submitting.value = true;

    try {
        const order = await checkoutOrder(address);
        cartStore.resetCart();
        notify('Order created successfully!', 'success');

        router.push({
            name: 'order-confirmation',
            params: { orderId: order.id },
        });
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to place your order.', 'danger');
    } finally {
        submitting.value = false;
    }
}
</script>

<template>
    <main class="page-container checkout-page">
        <!-- Header -->
        <header class="checkout-header">
            <div>
                <p class="eyebrow">ALMOST THERE</p>
                <h1 class="checkout-title">Checkout</h1>
                <p class="checkout-subtitle">Confirm your delivery address and review your order.</p>
            </div>

            <div class="checkout-step">
                <span class="step-number">2</span>
                <span>Checkout</span>
            </div>
        </header>

        <!-- Empty cart -->
        <section v-if="cartStore.items.length === 0" class="checkout-empty-state">
            <div class="empty-icon" aria-hidden="true">🛍️</div>
            <h2>Your cart is empty</h2>
            <p>Add some products before proceeding to checkout.</p>
            <RouterLink :to="{ name: 'products' }" class="btn btn-primary">
                Browse Products
            </RouterLink>
        </section>

        <!-- Checkout content -->
        <section v-else class="checkout-layout">
            <!-- Shipping form -->
            <div class="checkout-main">
                <section class="checkout-panel">
                    <div class="panel-heading">
                        <div class="panel-heading-icon" aria-hidden="true">⌖</div>
                        <div>
                            <h2>Shipping Address</h2>
                            <p>Where should we deliver your order?</p>
                        </div>
                    </div>

                    <form @submit.prevent="submitCheckout">
                        <div class="mb-4">
                            <label for="shippingAddress" class="form-label">Complete delivery address</label>
                            <textarea
                                id="shippingAddress"
                                v-model="shippingAddress"
                                class="form-control shipping-address-input"
                                rows="5"
                                placeholder="House / Flat number, street, locality, city, state, PIN code..."
                                minlength="10"
                                required
                            ></textarea>
                            <div class="form-text">
                                Include enough detail so your order can be delivered correctly.
                            </div>
                        </div>

                        <div class="address-tip">
                            <span aria-hidden="true">ⓘ</span>
                            <p>Please double-check your address before placing the order.</p>
                        </div>

                        <button type="submit" class="btn btn-primary place-order-button" :disabled="submitting">
                        <span v-if="submitting">
                            <span 
                                class="spinner-border spinner-border-sm me-2" 
                                role="status" 
                                aria-hidden="true"
                            ></span>
                            Placing Order...
                        </span>

                        <span v-else>
                            Place Order
                            <span class="button-arrow" aria-hidden="true">→</span>
                        </span>
                        </button>
                    </form>
                </section>

                <div class="checkout-security-note">
                    <span aria-hidden="true">✓</span>
                    Your order details will be saved securely.
                </div>
            </div>

            <!-- Order summary -->
            <aside class="checkout-summary">
                <div class="summary-heading">
                    <div>
                        <p class="eyebrow">YOUR SELECTION</p>
                        <h2>Order Summary</h2>
                    </div>
                    <span class="summary-count">{{ cartStore.itemCount }} item(s)</span>
                </div>

                <div class="summary-items">
                    <div v-for="item in cartStore.items" :key="item.id" class="summary-item">
                        <div class="summary-item-image">
                            <img
                                v-if="item.product.image_url"
                                :src="item.product.image_url"
                                :alt="item.product.name"
                            />
                            <span v-else aria-hidden="true">□</span>
                            <span class="summary-item-quantity">{{ item.quantity }}</span>
                        </div>

                        <div class="summary-item-details">
                            <h3>{{ item.product.name }}</h3>
                            <p>{{ item.product.category || 'General' }}</p>
                        </div>

                        <strong class="summary-item-price">
                            {{ formatPrice(Number(item.unit_price) * item.quantity) }}
                        </strong>
                    </div>
                </div>

                <div class="summary-calculations">
                    <div class="summary-row">
                        <span>Subtotal</span>
                        <span>{{ formattedSubtotal }}</span>
                    </div>

                    <div class="summary-row">
                        <span>Discount</span>
                        <span class="discount-value">Applied after order creation</span>
                    </div>

                    <div class="summary-row">
                        <span>Shipping</span>
                        <span class="shipping-value">Calculated at checkout</span>
                    </div>

                    <div class="summary-divider"></div>

                    <div class="summary-total">
                        <span>Subtotal before discount</span>
                        <strong>{{ formattedSubtotal }}</strong>
                    </div>
                </div>

                <div class="summary-payment-note">
                    <span aria-hidden="true">✓</span>
                    <span>
                        The best eligible offer will be applied automatically when you place your order.
                        Your final payable amount will appear on the confirmation page.
                    </span>
                </div>
            </aside>
        </section>
    </main>
</template>

<style scoped>
.checkout-page {
    max-width: 1320px;
}

/* Header */
.checkout-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
}

.eyebrow {
    margin-bottom: 0.4rem;
    color: var(--brand, #4f7cff);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.1em;
}

.checkout-title {
    margin-bottom: 0.45rem;
    color: var(--text-primary, #1d273b);
    font-size: clamp(1.8rem, 3vw, 2.5rem);
    font-weight: 800;
    letter-spacing: -0.04em;
}

.checkout-subtitle {
    margin-bottom: 0;
    color: var(--text-secondary, #718096);
    font-size: 0.95rem;
}

.checkout-step {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.6rem 0.9rem;
    border: 1px solid var(--border, #dfe6f1);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.65);
    color: var(--text-secondary, #718096);
    font-size: 0.8rem;
    font-weight: 650;
}

.step-number {
    display: grid;
    width: 25px;
    height: 25px;
    place-items: center;
    border-radius: 50%;
    background: var(--brand, #4f7cff);
    color: #fff;
    font-size: 0.75rem;
    font-weight: 800;
}

/* Layout */
.checkout-layout {
    display: grid;
    grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.9fr);
    align-items: start;
    gap: 1.5rem;
}

.checkout-main {
    min-width: 0;
}

/* Shipping panel */
.checkout-panel {
    padding: clamp(1.2rem, 3vw, 2rem);
    border: 1px solid var(--border, #dfe6f1);
    border-radius: var(--radius-lg, 16px);
    background: rgba(255, 255, 255, 0.9);
    box-shadow: var(--shadow-sm, 0 3px 12px rgba(35, 54, 90, 0.05));
}

.panel-heading {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    margin-bottom: 1.75rem;
}

.panel-heading-icon {
    display: grid;
    width: 46px;
    height: 46px;
    flex: 0 0 46px;
    place-items: center;
    border-radius: 14px;
    background: var(--brand-soft, #e9efff);
    color: var(--brand, #4f7cff);
    font-size: 1.5rem;
}

.panel-heading h2 {
    margin-bottom: 0.25rem;
    color: var(--text-primary, #1d273b);
    font-size: 1.15rem;
    font-weight: 800;
}

.panel-heading p {
    margin-bottom: 0;
    color: var(--text-secondary, #718096);
    font-size: 0.82rem;
}

.form-label {
    color: var(--text-primary, #1d273b);
    font-size: 0.85rem;
    font-weight: 700;
}

.shipping-address-input {
    min-height: 140px;
    padding: 0.9rem 1rem;
    line-height: 1.6;
    resize: vertical;
}

.form-text {
    color: var(--text-secondary, #718096);
    font-size: 0.76rem;
}

.address-tip {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.8rem 0.9rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(79, 124, 255, 0.16);
    border-radius: 10px;
    background: rgba(79, 124, 255, 0.05);
    color: var(--brand, #4f7cff);
}

.address-tip p {
    margin: 0;
    color: var(--text-secondary, #718096);
    font-size: 0.78rem;
    line-height: 1.5;
}

.place-order-button {
    display: flex;
    width: 100%;
    min-height: 50px;
    justify-content: center;
    align-items: center;
    gap: 0.5rem;
    border-radius: 10px;
    font-weight: 750;
}

.button-arrow {
    margin-left: 0.4rem;
    font-size: 1.1rem;
}

/* Security note */
.checkout-security-note {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 1rem;
    color: var(--text-secondary, #718096);
    font-size: 0.78rem;
}

.checkout-security-note span {
    color: var(--success, #16845b);
    font-weight: 800;
}

/* Summary */
.checkout-summary {
    position: sticky;
    top: 1.5rem;
    overflow: hidden;
    border: 1px solid var(--border, #dfe6f1);
    border-radius: var(--radius-lg, 16px);
    background: rgba(255, 255, 255, 0.94);
    box-shadow: var(--shadow-md, 0 8px 22px rgba(35, 54, 90, 0.07));
}

.summary-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    padding: 1.3rem 1.4rem;
    border-bottom: 1px solid var(--border, #dfe6f1);
}

.summary-heading .eyebrow {
    margin-bottom: 0.3rem;
}

.summary-heading h2 {
    margin: 0;
    color: var(--text-primary, #1d273b);
    font-size: 1.15rem;
    font-weight: 800;
}

.summary-count {
    padding: 0.35rem 0.65rem;
    border: 1px solid var(--border, #dfe6f1);
    border-radius: 999px;
    color: var(--text-secondary, #718096);
    font-size: 0.72rem;
    white-space: nowrap;
}

/* Summary products */
.summary-items {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-height: 340px;
    overflow-y: auto;
    padding: 1.2rem 1.4rem;
}

.summary-item {
    display: grid;
    grid-template-columns: 54px minmax(0, 1fr) auto;
    align-items: center;
    gap: 0.75rem;
}

.summary-item-image {
    position: relative;
    display: flex;
    width: 54px;
    height: 54px;
    align-items: center;
    justify-content: center;
    overflow: visible;
    border: 1px solid var(--border, #dfe6f1);
    border-radius: 10px;
    background: #fff;
}

.summary-item-image img {
    width: 100%;
    height: 100%;
    padding: 0.3rem;
    border-radius: 10px;
    object-fit: contain;
}

.summary-item-quantity {
    position: absolute;
    top: -7px;
    right: -7px;
    display: grid;
    min-width: 19px;
    height: 19px;
    place-items: center;
    padding-inline: 0.25rem;
    border: 2px solid #fff;
    border-radius: 999px;
    background: var(--brand, #4f7cff);
    color: #fff;
    font-size: 0.65rem;
    font-weight: 800;
}

.summary-item-details {
    min-width: 0;
}

.summary-item-details h3 {
    display: -webkit-box;
    overflow: hidden;
    margin-bottom: 0.25rem;
    color: var(--text-primary, #1d273b);
    font-size: 0.8rem;
    font-weight: 700;
    line-height: 1.4;
    line-clamp: 2;
    -webkit-box-orient: vertical;
}

.summary-item-details p {
    margin: 0;
    color: var(--text-secondary, #718096);
    font-size: 0.7rem;
}

.summary-item-price {
    color: var(--text-primary, #1d273b);
    font-size: 0.78rem;
    font-weight: 750;
    white-space: nowrap;
}

/* Summary totals */
.summary-calculations {
    padding: 1.2rem 1.4rem;
    border-top: 1px solid var(--border, #dfe6f1);
}

.summary-row {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.85rem;
    color: var(--text-secondary, #718096);
    font-size: 0.82rem;
}

.summary-row span:last-child {
    color: var(--text-primary, #1d273b);
    font-weight: 650;
    text-align: right;
}

.discount-value {
    color: var(--success, #198754);
    font-size: 0.85rem;
    font-weight: 600;
}

.shipping-value {
    max-width: 140px;
    color: var(--text-secondary, #718096) !important;
    font-size: 0.72rem;
    font-weight: 400 !important;
}

.summary-divider {
    height: 1px;
    margin: 1.1rem 0;
    background: var(--border, #dfe6f1);
}

.summary-total {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    color: var(--text-primary, #1d273b);
    font-size: 0.9rem;
}

.summary-total strong {
    font-size: 1.2rem;
    font-weight: 850;
    text-align: right;
}

.summary-payment-note {
    display: flex;
    align-items: flex-start;
    gap: 0.55rem;
    padding: 1rem 1.4rem;
    border-top: 1px solid var(--border, #dfe6f1);
    background: rgba(79, 124, 255, 0.04);
    color: var(--text-secondary, #718096);
    font-size: 0.73rem;
    line-height: 1.5;
}

.summary-payment-note span:first-child {
    color: var(--success, #16845b);
    font-weight: 800;
}

/* Empty state */
.checkout-empty-state {
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

.empty-icon {
    display: grid;
    width: 76px;
    height: 76px;
    place-items: center;
    margin-bottom: 1.2rem;
    border-radius: 24px;
    background: var(--brand-soft, #e9efff);
    font-size: 2rem;
}

.checkout-empty-state h2 {
    margin-bottom: 0.5rem;
    color: var(--text-primary, #1d273b);
    font-size: 1.4rem;
    font-weight: 800;
}

.checkout-empty-state p {
    margin-bottom: 1.25rem;
}

/* Responsive */
@media (max-width: 991px) {
    .checkout-layout {
        grid-template-columns: 1fr;
    }

    .checkout-summary {
        position: static;
    }
}

@media (max-width: 575px) {
    .checkout-header {
        align-items: flex-start;
    }

    .checkout-step {
        padding: 0.45rem 0.6rem;
        font-size: 0.72rem;
    }

    .summary-heading,
    .summary-items,
    .summary-calculations,
    .summary-payment-note {
        padding-inline: 1rem;
    }
}
</style>