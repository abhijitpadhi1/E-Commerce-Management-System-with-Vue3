<script setup>
import { onMounted, ref, computed } from 'vue';
import { getAllOrders, shipOrder } from '@/services/orderService';
import { useNotification } from '@/composables/useNotifications';

const orders = ref([]);
const loading = ref(true);
const updatingOrderId = ref(null);
const selectedFilter = ref('ALL');

const { notify } = useNotification();

async function loadOrders() {
    loading.value = true;

    try {
        orders.value = await getAllOrders();
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to load orders.', 'danger');
    } finally {
        loading.value = false;
    }
}

async function markAsShipped(orderId) {
    if (updatingOrderId.value !== null) return;
    updatingOrderId.value = orderId;

    try {
        const updatedOrder = await shipOrder(orderId);
        const index = orders.value.findIndex((order) => order.id === updatedOrder.id);

        if (index !== -1) {
            orders.value[index] = {
                ...orders.value[index],
                ...updatedOrder,
            };
        }

        notify(`Order #${orderId} marked as shipped.`, 'success');
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to ship this order.', 'danger');
    } finally {
        updatingOrderId.value = null;
    }
}

function formatOrderDate(dateString) {
    if (!dateString) return 'Date unavailable';

    return new Intl.DateTimeFormat('en-IN', {
        dateStyle: 'medium',
        timeStyle: 'short',
    }).format(new Date(dateString));
}

function statusClass(status) {
    const classes = {
        PENDING_PAYMENT: 'status-pending',
        PROCESSING: 'status-processing',
        SHIPPED: 'status-shipped',
        DELIVERED: 'status-delivered',
        CANCELLED: 'status-cancelled',
    };

    return classes[status] || 'status-default';
}

const filteredOrders = computed(() => {
    if (selectedFilter.value === 'ALL') return orders.value;
    return orders.value.filter((order) => order.status === selectedFilter.value);
});

const orderCounts = computed(() => ({
    ALL: orders.value.length,
    PENDING_PAYMENT: orders.value.filter((order) => order.status === 'PENDING_PAYMENT').length,
    PROCESSING: orders.value.filter((order) => order.status === 'PROCESSING').length,
    SHIPPED: orders.value.filter((order) => order.status === 'SHIPPED').length,
    DELIVERED: orders.value.filter((order) => order.status === 'DELIVERED').length,
}));
    
onMounted(loadOrders);
</script>

<template>
    <main class="admin-orders-page container py-5">
        <!-- Header -->
        <header class="page-header">
            <div>
                <p class="eyebrow">Store management</p>
                <h1>Order Management</h1>
                <p class="page-description">Review customer orders and manage fulfilment and dispatch.</p>
            </div>

            <button
                class="btn btn-outline-primary refresh-button"
                :disabled="loading"
                @click="loadOrders"
            >
                <span
                    v-if="loading"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                ></span>
                {{ loading ? 'Refreshing...' : '↻ Refresh Orders' }}
            </button>
        </header>

        <!-- Summary -->
        <section v-if="!loading && orders.length" class="summary-grid">
            <div class="summary-card">
                <span class="summary-label">Total Orders</span>
                <strong>{{ orderCounts.ALL }}</strong>
            </div>

            <div class="summary-card">
                <span class="summary-label">Awaiting Payment</span>
                <strong class="text-warning">{{ orderCounts.PENDING_PAYMENT }}</strong>
            </div>

            <div class="summary-card">
                <span class="summary-label">Processing</span>
                <strong class="text-primary">{{ orderCounts.PROCESSING }}</strong>
            </div>

            <div class="summary-card">
                <span class="summary-label">Shipped</span>
                <strong class="text-info">{{ orderCounts.SHIPPED }}</strong>
            </div>

            <div class="summary-card">
                <span class="summary-label">Delivered</span>
                <strong class="text-success">{{ orderCounts.DELIVERED }}</strong>
            </div>
        </section>

        <!-- Filters -->
        <section v-if="!loading && orders.length" class="filter-section">
            <div class="filter-heading">
                <h2>Orders</h2>
                <span>{{ filteredOrders.length }} shown</span>
            </div>

            <div class="filter-tabs">
                <button
                    v-for="filter in [
                        { value: 'ALL', label: 'All Orders' },
                        { value: 'PENDING_PAYMENT', label: 'Pending Payment' },
                        { value: 'PROCESSING', label: 'Processing' },
                        { value: 'SHIPPED', label: 'Shipped' },
                        { value: 'DELIVERED', label: 'Delivered' },
                    ]"
                    :key="filter.value"
                    class="filter-tab"
                    :class="{ active: selectedFilter === filter.value }"
                    @click="selectedFilter = filter.value"
                >
                    {{ filter.label }}
                    <span>{{ orderCounts[filter.value] }}</span>
                </button>
            </div>
        </section>

        <!-- Loading -->
        <section v-if="loading" class="state-card">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading orders</span>
            </div>
            <p class="mt-3 mb-0">Loading customer orders...</p>
        </section>

        <!-- Empty -->
        <section v-else-if="orders.length === 0" class="state-card">
            <div class="empty-icon">▤</div>
            <h2>No orders yet</h2>
            <p>Customer orders will appear here after the first purchase.</p>
        </section>

        <!-- Filter has no matches -->
        <section v-else-if="filteredOrders.length === 0" class="state-card">
            <div class="empty-icon">⌕</div>
            <h2>No matching orders</h2>
            <p>There are currently no orders with this status.</p>
            <button class="btn btn-outline-primary" @click="selectedFilter = 'ALL'">
                Show All Orders
            </button>
        </section>

        <!-- Order cards -->
        <section v-else class="orders-list">
            <article v-for="order in filteredOrders" :key="order.id" class="order-card">
                <div class="order-card-header">
                    <div class="order-heading">
                        <span class="order-number">Order #{{ order.id }}</span>
                        <span class="order-date">{{ formatOrderDate(order.created_at) }}</span>
                    </div>

                    <span class="status-badge" :class="statusClass(order.status)">
                        {{ order.status.replaceAll('_', ' ') }}
                    </span>
                </div>

                <div class="order-card-body">
                    <div class="order-detail">
                        <span class="detail-label">Items</span>
                        <strong>{{ order.items?.length ?? 0 }}</strong>
                    </div>

                    <div class="order-detail">
                        <span class="detail-label">Order total</span>
                        <strong class="order-total">
                            ₹{{ Number(order.total_amount).toFixed(2) }}
                        </strong>
                    </div>

                    <div class="order-detail">
                        <span class="detail-label">Payment status</span>
                        <span
                            class="payment-badge"
                            :class="order.payment_status === 'PAID' ? 'payment-paid' : 'payment-pending'"
                        >
                            {{ order.payment_status.replaceAll('_', ' ') }}
                        </span>
                    </div>
                </div>

                <div class="order-card-footer">
                    <div class="fulfilment-message">
                        <template v-if="order.status === 'PENDING_PAYMENT'">
                            Awaiting successful customer payment.
                        </template>
                        <template v-else-if="order.status === 'PROCESSING'">
                            Payment received. Ready for dispatch.
                        </template>
                        <template v-else-if="order.status === 'SHIPPED'">
                            Order has been dispatched.
                        </template>
                        <template v-else-if="order.status === 'DELIVERED'">
                            Customer has confirmed delivery.
                        </template>
                        <template v-else-if="order.status === 'CANCELLED'">
                            This order has been cancelled.
                        </template>
                        <template v-else>
                            Review the order status before taking action.
                        </template>
                    </div>

                    <button
                        v-if="order.payment_status === 'PAID' && order.status === 'PROCESSING'"
                        class="btn btn-success ship-button"
                        :disabled="updatingOrderId === order.id"
                        @click="markAsShipped(order.id)"
                    >
                        <span
                            v-if="updatingOrderId === order.id"
                            class="spinner-border spinner-border-sm me-2"
                            role="status"
                        ></span>
                        {{ updatingOrderId === order.id ? 'Updating...' : '✓ Mark as Shipped' }}
                    </button>

                    <span v-else class="action-complete">
                        <span>✓</span>
                        {{ order.status === 'DELIVERED' ? 'Fulfilled' : 'No action required' }}
                    </span>
                </div>
            </article>
        </section>
    </main>
</template>

<style scoped>
.admin-orders-page {
    max-width: 1200px;
    color: var(--text-primary);
}

.page-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.eyebrow {
    margin-bottom: 0.4rem;
    color: var(--text-secondary);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.page-header h1 {
    margin-bottom: 0.5rem;
    font-size: clamp(1.8rem, 4vw, 2.5rem);
    font-weight: 750;
}

.page-description {
    margin: 0;
    color: var(--text-secondary);
    line-height: 1.6;
}

.refresh-button {
    flex-shrink: 0;
    min-height: 42px;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 0.85rem;
    margin-bottom: 2rem;
}

.summary-card {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    padding: 1rem 1.15rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface, rgba(255, 255, 255, 0.72));
    box-shadow: var(--shadow-sm);
}

.summary-label {
    color: var(--text-secondary);
    font-size: 0.78rem;
    font-weight: 600;
}

.summary-card strong {
    font-size: 1.7rem;
    font-weight: 800;
}

.filter-section {
    margin-bottom: 1.25rem;
}

.filter-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.9rem;
}

.filter-heading h2 {
    margin: 0;
    font-size: 1.15rem;
    font-weight: 750;
}

.filter-heading span {
    color: var(--text-secondary);
    font-size: 0.82rem;
}

.filter-tabs {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    padding-bottom: 0.25rem;
}

.filter-tab {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    flex-shrink: 0;
    padding: 0.6rem 0.85rem;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: var(--surface, rgba(255, 255, 255, 0.72));
    color: var(--text-secondary);
    font-size: 0.8rem;
    font-weight: 650;
    transition: all 0.2s ease;
}

.filter-tab span {
    display: inline-grid;
    min-width: 21px;
    height: 21px;
    place-items: center;
    border-radius: 50%;
    background: var(--surface-muted, rgba(128, 128, 128, 0.12));
    font-size: 0.7rem;
}

.filter-tab:hover {
    border-color: var(--brand);
    color: var(--brand);
}

.filter-tab.active {
    border-color: var(--brand);
    background: var(--brand);
    color: white;
}

.filter-tab.active span {
    background: rgba(255, 255, 255, 0.2);
    color: white;
}

.order-card,
.state-card {
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface, rgba(255, 255, 255, 0.72));
    box-shadow: var(--shadow-sm);
}

.order-card {
    margin-bottom: 1rem;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.order-card:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

.order-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 1.1rem 1.35rem;
    border-bottom: 1px solid var(--border);
    background: var(--surface-muted, rgba(128, 128, 128, 0.04));
}

.order-heading {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
}

.order-number {
    font-weight: 750;
}

.order-date {
    color: var(--text-secondary);
    font-size: 0.82rem;
}

.status-badge,
.payment-badge {
    display: inline-flex;
    align-items: center;
    width: fit-content;
    padding: 0.4rem 0.7rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    white-space: nowrap;
}

.status-pending,
.payment-pending {
    background: rgba(255, 193, 7, 0.18);
    color: #856404;
}

.status-processing {
    background: rgba(13, 110, 253, 0.12);
    color: #084298;
}

.status-shipped {
    background: rgba(13, 202, 240, 0.15);
    color: #055160;
}

.status-delivered,
.payment-paid {
    background: rgba(25, 135, 84, 0.13);
    color: #146c43;
}

.status-cancelled {
    background: rgba(220, 53, 69, 0.12);
    color: #842029;
}

.status-default {
    background: var(--surface-muted, rgba(128, 128, 128, 0.1));
    color: var(--text-secondary);
}

.order-card-body {
    display: flex;
    flex-wrap: wrap;
    gap: 2.5rem;
    padding: 1.35rem;
}

.order-detail {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
}

.detail-label {
    color: var(--text-secondary);
    font-size: 0.8rem;
}

.order-detail strong {
    font-size: 1rem;
}

.order-detail .order-total {
    font-size: 1.25rem;
}

.order-card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.25rem;
    padding: 1rem 1.35rem;
    border-top: 1px solid var(--border);
}

.fulfilment-message {
    color: var(--text-secondary);
    font-size: 0.85rem;
    line-height: 1.5;
}

.ship-button {
    min-height: 40px;
    flex-shrink: 0;
}

.action-complete {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--text-secondary);
    font-size: 0.8rem;
    font-weight: 600;
}

.action-complete span {
    color: var(--success, #198754);
}

.state-card {
    padding: 3rem 1.5rem;
    text-align: center;
}

.state-card p {
    max-width: 450px;
    margin: 0.75rem auto 1.5rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

.empty-icon {
    margin-bottom: 1rem;
    color: var(--brand);
    font-size: 2.5rem;
}

.state-card h2 {
    font-size: 1.3rem;
    font-weight: 750;
}

@media (max-width: 900px) {
    .summary-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }
}

@media (max-width: 650px) {
    .page-header {
        align-items: flex-start;
        flex-direction: column;
    }

    .refresh-button {
        width: 100%;
    }

    .summary-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .order-card-header {
        align-items: flex-start;
        flex-direction: column;
    }

    .order-card-body {
        gap: 1.25rem;
        padding: 1.1rem;
    }

    .order-card-footer {
        align-items: stretch;
        flex-direction: column;
        padding: 1.1rem;
    }

    .ship-button {
        width: 100%;
    }
}
</style>