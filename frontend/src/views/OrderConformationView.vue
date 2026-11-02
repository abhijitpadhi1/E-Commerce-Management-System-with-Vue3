<script setup>
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { getOrderById, modifyUnpaidOrder } from '@/services/orderService';
import { makeMockPayment } from '@/services/paymentService';
import { useNotification } from '@/composables/useNotifications';

const route = useRoute();
const router = useRouter();
const { notify } = useNotification();

const order = ref(null);
const loading = ref(true);
const paying = ref(false);
const modifyingOrder = ref(false);

async function loadOrder() {
    loading.value = true;

    try {
        order.value = await getOrderById(route.params.orderId);
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to load order details.', 'danger');
    } finally {
        loading.value = false;
    }
}

async function modifyOrder() {
    if (!order.value) return;
    modifyingOrder.value = true;

    try {
        const result = await modifyUnpaidOrder(order.value.id);
        if (result.unavailable_items?.length) {
            const unavailableNames = result.unavailable_items.map((item) => item.product_name).join(', ');
            notify(
                `Some products are no longer available and were not restored: ${unavailableNames}`,
                'warning',
                10000,
            );
        } else {
            notify(result.message || 'Order items restored to your cart.', 'success');
        }
        await router.push('/cart');
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to modify this order.', 'danger');
    } finally {
        modifyingOrder.value = false;
    }
}

function formatOrderDate(dateString) {
    if (!dateString) return 'Date unavailable';

    return new Intl.DateTimeFormat('en-IN', {
        dateStyle: 'medium',
        timeStyle: 'short',
    }).format(new Date(dateString));
}

async function payNow(outcome = 'success') {
    if (!order.value || paying.value) return;
    paying.value = true;

    try {
        const response = await makeMockPayment(order.value.id, outcome);

        order.value.status = response.order.status;
        order.value.payment_status = response.order.payment_status;

        if (response.payment.payment_status === 'SUCCESS') {
            notify('Mock payment successful!', 'success');
        } else {
            notify('Mock payment failed. You can try again.', 'warning');
        }
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to process payment.', 'danger');
    } finally {
        paying.value = false;
    }
}

onMounted(loadOrder);
</script>

<template>
    <main class="order-confirmation-page container py-5">
        <!-- Loading -->
        <div v-if="loading" class="state-card">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading</span>
            </div>
            <p class="mt-3 mb-0">Loading your order details...</p>
        </div>

        <!-- Order details -->
        <section v-else-if="order" class="confirmation-card">
            <!-- Status header -->
            <div
                class="confirmation-header"
                :class="order.payment_status === 'PAID' ? 'is-success' : 'is-pending'"
            >
                <div class="status-icon">
                    <span v-if="order.payment_status === 'PAID'">✓</span>
                    <span v-else>🛍</span>
                </div>

                <p class="eyebrow">
                    {{ order.payment_status === 'PAID' ? 'Payment confirmed' : 'Order received' }}
                </p>

                <h1>
                    {{
                        order.payment_status === 'PAID'
                            ? 'Thank you for your purchase!'
                            : 'Your order is created'
                    }}
                </h1>

                <p class="header-description">
                    {{
                        order.payment_status === 'PAID'
                            ? 'Your payment has been recorded. We’ll keep you updated as your order progresses.'
                            : 'Your items are reserved in this order. Complete the mock payment to continue.'
                    }}
                </p>
            </div>

            <div class="confirmation-content">
                <!-- Order metadata -->
                <div class="order-meta">
                    <div>
                        <span class="meta-label">Order number</span>
                        <strong>#{{ order.id }}</strong>
                    </div>

                    <div>
                        <span class="meta-label">Order date</span>
                        <strong>{{ formatOrderDate(order.created_at) }}</strong>
                    </div>

                    <div>
                        <span class="meta-label">Order status</span>
                        <span
                            class="status-badge"
                            :class="{
                                'badge-success': order.status === 'DELIVERED',
                                'badge-primary': order.status === 'PROCESSING',
                                'badge-info': order.status === 'SHIPPED',
                                'badge-warning': order.status === 'PENDING_PAYMENT',
                                'badge-danger': order.status === 'CANCELLED',
                            }"
                        >
                            {{ order.status.replaceAll('_', ' ') }}
                        </span>
                    </div>

                    <div>
                        <span class="meta-label">Payment</span>
                        <span
                            class="status-badge"
                            :class="order.payment_status === 'PAID' ? 'badge-success' : 'badge-warning'"
                        >
                            {{ order.payment_status.replaceAll('_', ' ') }}
                        </span>
                    </div>
                </div>

                <!-- Items -->
                <section class="detail-section">
                    <div class="section-heading">
                        <h2>Order summary</h2>
                        <span>{{ order.items?.length || 0 }} item(s)</span>
                    </div>

                    <div class="order-items">
                        <div
                            v-for="item in order.items"
                            :key="item.id"
                            class="order-item"
                        >
                            <div class="item-description">
                                <span class="item-name">{{ item.product_name }}</span>
                                <span class="item-quantity">Quantity: {{ item.quantity }}</span>
                            </div>

                            <strong class="item-price">
                                ₹{{ Number(item.sub_total).toFixed(2) }}
                            </strong>
                        </div>
                    </div>

                    <div class="total-row">
                        <span>Total paid / payable</span>
                        <strong>₹{{ Number(order.total_amount).toFixed(2) }}</strong>
                    </div>
                </section>

                <!-- Shipping -->
                <section class="detail-section">
                    <div class="section-heading">
                        <h2>Shipping address</h2>
                    </div>

                    <div class="address-panel">
                        <span class="address-icon">⌖</span>
                        <p>{{ order.shipping_address }}</p>
                    </div>
                </section>

                <!-- Mock payment notice -->
                <div
                    v-if="order.payment_status !== 'PAID'"
                    class="mock-payment-notice"
                >
                    <span class="notice-icon">ⓘ</span>
                    <div>
                        <strong>Mock payment environment</strong>
                        <p>No real money will be transferred. This payment is simulated for project testing.</p>
                    </div>
                </div>

                <!-- Actions -->
                <div class="action-area">
                    <button
                        v-if="order.payment_status !== 'PAID' && order.status !== 'CANCELLED'"
                        class="btn btn-success action-primary"
                        :disabled="paying"
                        @click="payNow('success')"
                    >
                        <span
                            v-if="paying"
                            class="spinner-border spinner-border-sm me-2"
                            role="status"
                        ></span>
                        {{ paying ? 'Processing payment...' : 'Pay Now' }}
                    </button>

                    <button
                        v-if="order.status === 'PENDING_PAYMENT' && order.payment_status === 'PENDING'"
                        class="btn btn-outline-primary"
                        :disabled="modifyingOrder"
                        @click="modifyOrder"
                    >
                        {{ modifyingOrder ? 'Preparing cart...' : 'Modify Order' }}
                    </button>

                    <RouterLink :to="{ name: 'orders' }" class="btn btn-outline-secondary">
                        View My Orders
                    </RouterLink>

                    <RouterLink :to="{ name: 'products' }" class="btn btn-primary">
                        Continue Shopping
                    </RouterLink>
                </div>
            </div>
        </section>

        <!-- Order unavailable -->
        <section v-else class="state-card">
            <div class="empty-icon">!</div>
            <h1 class="h4">Order details unavailable</h1>
            <p>We couldn’t retrieve this order. It may not exist or you may not have access to it.</p>

            <RouterLink :to="{ name: 'orders' }" class="btn btn-primary">
                Go to My Orders
            </RouterLink>
        </section>
    </main>
</template>

<style scoped>
.order-confirmation-page {
    max-width: 1000px;
    color: var(--text-primary);
}

.confirmation-card,
.state-card {
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface, rgba(255, 255, 255, 0.72));
    box-shadow: var(--shadow-md);
}

.confirmation-header {
    padding: 2.75rem 2rem 2.5rem;
    text-align: center;
    border-bottom: 1px solid var(--border);
}

.confirmation-header.is-success {
    background: var(--success-soft, rgba(25, 135, 84, 0.09));
}

.confirmation-header.is-pending {
    background: var(--brand-soft);
}

.status-icon {
    display: grid;
    width: 68px;
    height: 68px;
    margin: 0 auto 1.25rem;
    place-items: center;
    border-radius: 50%;
    background: var(--surface, rgba(255, 255, 255, 0.8));
    color: var(--success);
    font-size: 2rem;
    font-weight: 700;
    box-shadow: var(--shadow-sm);
}

.is-pending .status-icon {
    color: var(--brand);
}

.eyebrow {
    margin-bottom: 0.5rem;
    color: var(--text-secondary);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.confirmation-header h1 {
    margin-bottom: 0.75rem;
    font-size: clamp(1.6rem, 4vw, 2.25rem);
    font-weight: 750;
}

.header-description {
    max-width: 580px;
    margin: 0 auto;
    color: var(--text-secondary);
    line-height: 1.65;
}

.confirmation-content {
    padding: 2rem;
}

.order-meta {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
    padding: 1.25rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface-muted, rgba(128, 128, 128, 0.05));
}

.order-meta > div {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.4rem;
    min-width: 0;
}

.meta-label {
    color: var(--text-secondary);
    font-size: 0.8rem;
}

.order-meta strong {
    overflow-wrap: anywhere;
    font-size: 0.95rem;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.35rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
}

.badge-success {
    color: #146c43;
    background: rgba(25, 135, 84, 0.13);
}

.badge-primary {
    color: #084298;
    background: rgba(13, 110, 253, 0.12);
}

.badge-info {
    color: #055160;
    background: rgba(13, 202, 240, 0.15);
}

.badge-warning {
    color: #856404;
    background: rgba(255, 193, 7, 0.18);
}

.badge-danger {
    color: #842029;
    background: rgba(220, 53, 69, 0.12);
}

.detail-section {
    margin-top: 2rem;
}

.section-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
}

.section-heading h2 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 700;
}

.section-heading > span {
    color: var(--text-secondary);
    font-size: 0.85rem;
}

.order-items {
    border-top: 1px solid var(--border);
}

.order-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 1rem 0;
    border-bottom: 1px solid var(--border);
}

.item-description {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    min-width: 0;
}

.item-name {
    font-weight: 600;
    overflow-wrap: anywhere;
}

.item-quantity {
    color: var(--text-secondary);
    font-size: 0.85rem;
}

.item-price {
    flex-shrink: 0;
    font-size: 0.95rem;
}

.total-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding-top: 1.25rem;
    font-size: 1rem;
}

.total-row strong {
    font-size: 1.4rem;
}

.address-panel {
    display: flex;
    align-items: flex-start;
    gap: 0.85rem;
    padding: 1rem 1.1rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface-muted, rgba(128, 128, 128, 0.05));
}

.address-icon {
    color: var(--brand);
    font-size: 1.25rem;
    line-height: 1.2;
}

.address-panel p {
    margin: 0;
    color: var(--text-secondary);
    line-height: 1.6;
    white-space: pre-line;
}

.mock-payment-notice {
    display: flex;
    gap: 0.8rem;
    margin-top: 1.75rem;
    padding: 1rem;
    border: 1px solid rgba(13, 110, 253, 0.2);
    border-radius: var(--radius-lg);
    background: rgba(13, 110, 253, 0.06);
}

.notice-icon {
    color: var(--brand);
    font-size: 1.2rem;
}

.mock-payment-notice strong {
    display: block;
    margin-bottom: 0.25rem;
    font-size: 0.9rem;
}

.mock-payment-notice p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.85rem;
    line-height: 1.5;
}

.action-area {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-top: 2rem;
}

.action-area .btn {
    min-height: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.action-primary {
    min-width: 170px;
}

.state-card {
    max-width: 650px;
    margin: 2rem auto;
    padding: 3rem 1.5rem;
    text-align: center;
}

.state-card p {
    max-width: 440px;
    margin: 0.75rem auto 1.5rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

.empty-icon {
    display: grid;
    width: 54px;
    height: 54px;
    margin: 0 auto 1rem;
    place-items: center;
    border-radius: 50%;
    background: var(--brand-soft);
    color: var(--brand);
    font-size: 1.5rem;
    font-weight: 700;
}

@media (max-width: 576px) {
    .order-confirmation-page {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
    }

    .confirmation-header {
        padding: 2rem 1.25rem;
    }

    .confirmation-content {
        padding: 1.25rem;
    }

    .order-meta {
        gap: 1rem 0.75rem;
        padding: 1rem;
    }

    .order-item {
        align-items: flex-start;
    }

    .total-row {
        align-items: flex-start;
        flex-direction: column;
        gap: 0.35rem;
    }

    .action-area {
        flex-direction: column;
    }

    .action-area .btn {
        width: 100%;
    }
}
</style>