<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue';
import { getMyOrders, confirmOrderDelivery } from '@/services/orderService';
import { requestOrderHistoryExport, getOrderHistoryExportStatus } from '@/services/exportService';
import { useNotification } from '@/composables/useNotifications';

const { notify } = useNotification();

const orders = ref([]);
const loading = ref(true);
const updatingOrderId = ref(null);

const exportFormat = ref('csv');
const exporting = ref(false);
const exportStatus = ref('');

let exportPollingTimer = null;

onMounted(async () => {
    try {
        orders.value = await getMyOrders();
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to load your orders.', 'danger');
    } finally {
        loading.value = false;
    }
});

onBeforeUnmount(() => {
    if (exportPollingTimer) {
        clearTimeout(exportPollingTimer);
    }
});

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

async function confirmDelivery(orderId) {
    if (updatingOrderId.value !== null) return;
    updatingOrderId.value = orderId;

    try {
        const updatedOrder = await confirmOrderDelivery(orderId);
        const index = orders.value.findIndex((order) => order.id === updatedOrder.id);
        if (index !== -1) {
            orders.value[index] = {
                ...orders.value[index],
                ...updatedOrder,
            };
        }
        notify(`Receipt of order #${orderId} confirmed.`, 'success');
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to confirm delivery.', 'danger');
    } finally {
        updatingOrderId.value = null;
    }
}


async function requestExport() {
    if (exporting.value) return;

    exporting.value = true;
    exportStatus.value = 'Your export is being queued...';

    try {
        const result = await requestOrderHistoryExport(exportFormat.value);

        exportStatus.value = 'Export queued. Preparing your file...';
        notify('Your order history export has been queued.', 'info');

        pollExportStatus(result.task_id);
    } catch (error) {
        exporting.value = false;
        exportStatus.value = '';
        notify(error.response?.data?.error || 'Unable to request your export.', 'danger');
    }
}

function pollExportStatus(taskId) {
    exportPollingTimer = setTimeout(async () => {
        try {
            const result = await getOrderHistoryExportStatus(taskId);
            if (result.status === 'SUCCESS') {
                exporting.value = false;
                exportStatus.value = 'Your export has been emailed successfully.';
                notify('Your order history export has been sent to your email.', 'success');
                return;
            }
            if (result.status === 'FAILURE') {
                exporting.value = false;
                exportStatus.value = 'Export failed. Please try again.';
                notify('Export generation failed. Please try again.', 'danger');
                return;
            }
            exportStatus.value = 'Preparing your export...';
            pollExportStatus(taskId);
        } catch (error) {
            exporting.value = false;
            exportStatus.value = '';
            notify('Unable to check export status.', 'danger');
        }
    }, 2000);
}
</script>

<template>
    <main class="my-orders-page container py-5">
        <!-- Header -->
        <header class="page-header">
            <div>
                <p class="eyebrow">Your account</p>
                <h1>My Orders</h1>
                <p class="page-description">
                    Track your purchases, check payment status, and confirm deliveries.
                </p>
            </div>

            <RouterLink :to="{ name: 'products' }" class="btn btn-primary browse-button">
                Continue Shopping
            </RouterLink>
        </header>

        <!-- Exporting -->
        <section class="export-card mb-4">
            <div class="export-card-content">
                <div>
                    <h2 class="export-title">Export Order History</h2>
                    <p class="export-description">
                        Receive a copy of your order history by email.
                    </p>
                </div>

                <div class="export-controls">
                    <label for="export-format" class="form-label mb-0">File format</label>
                    <select id="export-format" v-model="exportFormat" class="form-select" :disabled="exporting">
                        <option value="csv">CSV (.csv)</option>
                        <option value="xlsx">Excel (.xlsx)</option>
                    </select>

                    <button 
                        class="btn btn-primary" 
                        :disabled="exporting || orders.length === 0" 
                        @click="requestExport"
                    >
                        <span v-if="exporting" class="spinner-border spinner-border-sm me-2" role="status"></span>
                        {{ exporting ? 'Preparing...' : 'Email My Export' }}
                    </button>
                </div>
            </div>

            <p v-if="exportStatus" class="export-status mb-0" role="status">{{ exportStatus }}</p>
        </section>

        <!-- Loading -->
        <section v-if="loading" class="state-card">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading orders</span>
            </div>
            <p class="mt-3 mb-0">Loading your orders...</p>
        </section>

        <!-- Empty state -->
        <section v-else-if="orders.length === 0" class="state-card empty-state">
            <div class="empty-icon">🛍</div>
            <h2>No orders yet</h2>
            <p>Your purchases will appear here once you place your first order.</p>

            <RouterLink :to="{ name: 'products' }" class="btn btn-primary">
                Browse Products
            </RouterLink>
        </section>

        <!-- Orders -->
        <section v-else class="orders-list">
            <div class="orders-summary">
                <span>{{ orders.length }} order{{ orders.length === 1 ? '' : 's' }}</span>
                <span>Most recent orders first</span>
            </div>

            <article v-for="order in orders" :key="order.id" class="order-card">
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
                    <div class="order-info">
                        <span class="info-label">Order total</span>
                        <strong class="order-total">
                            ₹{{ Number(order.total_amount).toFixed(2) }}
                        </strong>
                    </div>

                    <div class="order-info">
                        <span class="info-label">Payment status</span>
                        <span
                            class="payment-badge"
                            :class="order.payment_status === 'PAID' ? 'payment-paid' : 'payment-pending'"
                        >
                            {{ order.payment_status.replaceAll('_', ' ') }}
                        </span>
                    </div>
                </div>

                <div class="order-card-footer">
                    <div class="delivery-message">
                        <template v-if="order.status === 'PENDING_PAYMENT'">
                            Payment is required to begin processing.
                        </template>
                        <template v-else-if="order.status === 'PROCESSING'">
                            Your order is being prepared.
                        </template>
                        <template v-else-if="order.status === 'SHIPPED'">
                            Your order has shipped. Confirm once it arrives.
                        </template>
                        <template v-else-if="order.status === 'DELIVERED'">
                            Delivery confirmed. Thank you for shopping with us!
                        </template>
                        <template v-else-if="order.status === 'CANCELLED'">
                            This order has been cancelled.
                        </template>
                        <template v-else>
                            Check the order details for more information.
                        </template>
                    </div>

                    <div class="order-actions">
                        <RouterLink
                            :to="{ name: 'order-confirmation', params: { orderId: order.id } }"
                            class="btn btn-outline-primary"
                        >
                            View Details
                        </RouterLink>

                        <button
                            v-if="order.status === 'SHIPPED'"
                            class="btn btn-success"
                            :disabled="updatingOrderId === order.id"
                            @click="confirmDelivery(order.id)"
                        >
                            <span
                                v-if="updatingOrderId === order.id"
                                class="spinner-border spinner-border-sm me-2"
                                role="status"
                            ></span>
                            {{ updatingOrderId === order.id ? 'Confirming...' : 'Confirm Receipt' }}
                        </button>
                    </div>
                </div>
            </article>
        </section>
    </main>
</template>

<style scoped>
.my-orders-page {
    max-width: 1000px;
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

.browse-button {
    flex-shrink: 0;
}

.orders-summary {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
    color: var(--text-secondary);
    font-size: 0.85rem;
}

.export-card {
    padding: 1.25rem 1.35rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface, rgba(255, 255, 255, 0.72));
    box-shadow: var(--shadow-sm);
}

.export-card-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
}

.export-title {
    margin-bottom: 0.35rem;
    font-size: 1.05rem;
    font-weight: 750;
}

.export-description {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.85rem;
}

.export-controls {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.export-controls .form-select {
    min-width: 140px;
}

.export-status {
    margin-top: 0.9rem;
    color: var(--text-secondary);
    font-size: 0.85rem;
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
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
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
    color: #856404;
    background: rgba(255, 193, 7, 0.18);
}

.status-processing {
    color: #084298;
    background: rgba(13, 110, 253, 0.12);
}

.status-shipped {
    color: #055160;
    background: rgba(13, 202, 240, 0.15);
}

.status-delivered,
.payment-paid {
    color: #146c43;
    background: rgba(25, 135, 84, 0.13);
}

.status-cancelled {
    color: #842029;
    background: rgba(220, 53, 69, 0.12);
}

.status-default {
    color: var(--text-secondary);
    background: var(--surface-muted, rgba(128, 128, 128, 0.1));
}

.order-card-body {
    display: flex;
    flex-wrap: wrap;
    gap: 2.5rem;
    padding: 1.35rem;
}

.order-info {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
}

.info-label {
    color: var(--text-secondary);
    font-size: 0.8rem;
}

.order-total {
    font-size: 1.35rem;
}

.order-card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.25rem;
    padding: 1rem 1.35rem;
    border-top: 1px solid var(--border);
}

.delivery-message {
    color: var(--text-secondary);
    font-size: 0.85rem;
    line-height: 1.5;
}

.order-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.65rem;
    flex-shrink: 0;
}

.order-actions .btn {
    min-height: 40px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
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
    font-size: 2.5rem;
}

.empty-state h2 {
    font-size: 1.35rem;
    font-weight: 700;
}

@media (max-width: 650px) {
    .export-card-content {
        align-items: stretch;
        flex-direction: column;
    }

    .export-controls {
        align-items: stretch;
        flex-direction: column;
    }

    .export-controls .form-select {
        width: 100%;
    }
}

@media (max-width: 650px) {
    .page-header {
        align-items: flex-start;
        flex-direction: column;
    }

    .browse-button {
        width: 100%;
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

    .order-actions {
        flex-direction: column;
    }

    .order-actions .btn {
        width: 100%;
    }

    .orders-summary {
        flex-direction: column;
        gap: 0.25rem;
    }
}
</style>