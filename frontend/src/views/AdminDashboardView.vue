<script setup>
import { onMounted, ref } from 'vue';
import { getAdminDashboard } from '@/services/dashboardService';
import { useNotification } from '@/composables/useNotifications';

const { notify } = useNotification();

const dashboard = ref(null);
const loading = ref(false);

onMounted(fetchDashboard);

async function fetchDashboard() {
    loading.value = true;

    try {
        dashboard.value = await getAdminDashboard();
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to load dashboard.', 'danger');
    } finally {
        loading.value = false;
    }
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 2,
    }).format(Number(value || 0));
}

const inventoryMetrics = [
    {
        key: 'total_products',
        label: 'Total Products',
        description: 'Products in your catalogue',
        icon: '▦',
        tone: 'neutral',
    },
    {
        key: 'active_products',
        label: 'Active Products',
        description: 'Visible to customers',
        icon: '✓',
        tone: 'success',
    },
    {
        key: 'low_stock_products',
        label: 'Low Stock',
        description: 'Only 1–5 units remaining',
        icon: '!',
        tone: 'warning',
    },
    {
        key: 'out_of_stock_products',
        label: 'Out of Stock',
        description: 'Currently unavailable',
        icon: '×',
        tone: 'danger',
    },
];

const orderMetrics = [
    {
        key: 'total_orders',
        label: 'Total Orders',
        description: 'All orders placed',
        icon: '▤',
        tone: 'neutral',
    },
    {
        key: 'pending_payment_orders',
        label: 'Pending Payment',
        description: 'Awaiting payment',
        icon: '◷',
        tone: 'warning',
    },
    {
        key: 'processing_orders',
        label: 'Processing',
        description: 'Paid orders being prepared',
        icon: '↻',
        tone: 'primary',
    },
    {
        key: 'shipped_orders',
        label: 'Shipped',
        description: 'Orders in transit',
        icon: '➜',
        tone: 'info',
    },
    {
        key: 'delivered_orders',
        label: 'Delivered',
        description: 'Orders received by customers',
        icon: '✓',
        tone: 'success',
    },
];
</script>

<template>
    <main class="admin-dashboard container py-5">
        <!-- Page heading -->
        <header class="dashboard-header">
            <div>
                <p class="eyebrow">Store management</p>
                <h1>Admin Dashboard</h1>
                <p class="page-description">
                    Monitor your catalogue, inventory, orders, and paid sales.
                </p>
            </div>

            <button lass="btn btn-outline-primary refresh-button" :disabled="loading"@click="fetchDashboard">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                {{ loading ? 'Refreshing...' : '↻ Refresh' }}
            </button>
        </header>

        <!-- Initial loading -->
        <section v-if="loading && !dashboard" class="state-card">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading dashboard</span>
            </div>
            <p class="mt-3 mb-0">Loading store overview...</p>
        </section>

        <!-- Dashboard content -->
        <template v-else-if="dashboard">
            <!-- Paid sales highlight -->
            <section class="sales-highlight">
                <div>
                    <p class="sales-label">Total Paid Sales</p>
                    <h2>{{ formatCurrency(dashboard.total_sales) }}</h2>
                    <p class="sales-description">
                        Total value of orders with successful payment
                    </p>
                </div>

                <div class="sales-icon">₹</div>
            </section>

            <!-- Inventory -->
            <section class="dashboard-section">
                <div class="section-heading">
                    <div>
                        <h2>Products & Inventory</h2>
                        <p>Catalogue health and stock availability</p>
                    </div>

                    <RouterLink :to="{ name: 'admin-inventory' }" class="section-link">
                        Manage Inventory <span>→</span>
                    </RouterLink>
                </div>

                <div class="metric-grid">
                    <article
                        v-for="metric in inventoryMetrics"
                        :key="metric.key"
                        class="metric-card"
                        :class="`tone-${metric.tone}`"
                    >
                        <div class="metric-top">
                            <span class="metric-icon">{{ metric.icon }}</span>
                            <span class="metric-label">{{ metric.label }}</span>
                        </div>

                        <strong class="metric-value">
                            {{ dashboard[metric.key] }}
                        </strong>

                        <p class="metric-description">{{ metric.description }}</p>
                    </article>
                </div>
            </section>

            <!-- Orders -->
            <section class="dashboard-section">
                <div class="section-heading">
                    <div>
                        <h2>Order Activity</h2>
                        <p>Track orders across the fulfilment lifecycle</p>
                    </div>

                    <RouterLink :to="{ name: 'admin-orders' }" class="section-link">
                        Manage Orders <span>→</span>
                    </RouterLink>
                </div>

                <div class="metric-grid">
                    <article
                        v-for="metric in orderMetrics"
                        :key="metric.key"
                        class="metric-card"
                        :class="`tone-${metric.tone}`"
                    >
                        <div class="metric-top">
                            <span class="metric-icon">{{ metric.icon }}</span>
                            <span class="metric-label">{{ metric.label }}</span>
                        </div>

                        <strong class="metric-value">
                            {{ dashboard[metric.key] }}
                        </strong>

                        <p class="metric-description">{{ metric.description }}</p>
                    </article>
                </div>
            </section>

            <!-- Inventory attention panel -->
            <section class="attention-panel">
                <div class="attention-heading">
                    <span class="attention-icon">!</span>
                    <div>
                        <h2>Inventory Attention</h2>
                        <p>Products that may need restocking</p>
                    </div>
                </div>

                <div class="attention-stats">
                    <div>
                        <span class="attention-number warning-number">
                            {{ dashboard.low_stock_products }}
                        </span>
                        <span>Low stock</span>
                    </div>

                    <div>
                        <span class="attention-number danger-number">
                            {{ dashboard.out_of_stock_products }}
                        </span>
                        <span>Out of stock</span>
                    </div>
                </div>

                <RouterLink :to="{ name: 'admin-inventory' }" class="btn btn-outline-primary">
                    Review Inventory
                </RouterLink>
            </section>
        </template>

        <!-- Failed load -->
        <section v-else class="state-card">
            <div class="error-icon">!</div>
            <h2>Dashboard unavailable</h2>
            <p>We couldn’t retrieve the store metrics. Try refreshing.</p>

            <button class="btn btn-primary" :disabled="loading" @click="fetchDashboard">
                Try Again
            </button>
        </section>
    </main>
</template>

<style scoped>
.admin-dashboard {
    max-width: 1200px;
    color: var(--text-primary);
}

.dashboard-header {
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

.dashboard-header h1 {
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

.sales-highlight {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    padding: 1.75rem 2rem;
    margin-bottom: 2.5rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background:
        linear-gradient(120deg, var(--brand-soft), transparent 75%),
        var(--surface, rgba(255, 255, 255, 0.72));
    box-shadow: var(--shadow-sm);
}

.sales-label {
    margin-bottom: 0.5rem;
    color: var(--text-secondary);
    font-size: 0.9rem;
    font-weight: 600;
}

.sales-highlight h2 {
    margin-bottom: 0.4rem;
    font-size: clamp(1.8rem, 5vw, 2.6rem);
    font-weight: 800;
    letter-spacing: -0.03em;
}

.sales-description {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.85rem;
}

.sales-icon {
    display: grid;
    width: 64px;
    height: 64px;
    flex-shrink: 0;
    place-items: center;
    border-radius: 18px;
    background: var(--brand);
    color: white;
    font-size: 1.8rem;
    font-weight: 750;
    box-shadow: var(--shadow-sm);
}

.dashboard-section {
    margin-bottom: 2.5rem;
}

.section-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1.25rem;
}

.section-heading h2 {
    margin-bottom: 0.35rem;
    font-size: 1.2rem;
    font-weight: 750;
}

.section-heading p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.85rem;
}

.section-link {
    color: var(--brand);
    font-size: 0.85rem;
    font-weight: 700;
    text-decoration: none;
    white-space: nowrap;
}

.section-link:hover {
    color: var(--brand-hover);
}

.section-link span {
    margin-left: 0.25rem;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
}

.metric-card {
    min-width: 0;
    padding: 1.25rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface, rgba(255, 255, 255, 0.72));
    box-shadow: var(--shadow-sm);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.metric-top {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin-bottom: 1rem;
}

.metric-icon {
    display: grid;
    width: 32px;
    height: 32px;
    flex-shrink: 0;
    place-items: center;
    border-radius: 10px;
    background: var(--metric-soft, var(--brand-soft));
    color: var(--metric-color, var(--brand));
    font-weight: 800;
}

.metric-label {
    color: var(--text-secondary);
    font-size: 0.82rem;
    font-weight: 600;
}

.metric-value {
    display: block;
    margin-bottom: 0.4rem;
    font-size: clamp(1.6rem, 3vw, 2rem);
    font-weight: 800;
    line-height: 1.15;
}

.metric-description {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.78rem;
    line-height: 1.5;
}

.tone-neutral {
    --metric-color: var(--brand);
    --metric-soft: var(--brand-soft);
}

.tone-primary {
    --metric-color: #0d6efd;
    --metric-soft: rgba(13, 110, 253, 0.12);
}

.tone-success {
    --metric-color: #198754;
    --metric-soft: rgba(25, 135, 84, 0.12);
}

.tone-warning {
    --metric-color: #a87900;
    --metric-soft: rgba(255, 193, 7, 0.18);
}

.tone-danger {
    --metric-color: #dc3545;
    --metric-soft: rgba(220, 53, 69, 0.12);
}

.tone-info {
    --metric-color: #087990;
    --metric-soft: rgba(13, 202, 240, 0.15);
}

.attention-panel {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    padding: 1.4rem 1.5rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface-muted, rgba(128, 128, 128, 0.05));
}

.attention-heading {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}

.attention-icon {
    display: grid;
    width: 38px;
    height: 38px;
    flex-shrink: 0;
    place-items: center;
    border-radius: 12px;
    background: rgba(255, 193, 7, 0.18);
    color: #a87900;
    font-weight: 800;
}

.attention-heading h2 {
    margin-bottom: 0.25rem;
    font-size: 0.95rem;
    font-weight: 750;
}

.attention-heading p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.8rem;
}

.attention-stats {
    display: flex;
    gap: 1.5rem;
}

.attention-stats > div {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    color: var(--text-secondary);
    font-size: 0.75rem;
}

.attention-number {
    font-size: 1.25rem;
    font-weight: 800;
}

.warning-number {
    color: #a87900;
}

.danger-number {
    color: #dc3545;
}

.state-card {
    padding: 3rem 1.5rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface, rgba(255, 255, 255, 0.72));
    text-align: center;
    box-shadow: var(--shadow-sm);
}

.state-card p {
    max-width: 450px;
    margin: 0.75rem auto 1.5rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

.error-icon {
    display: grid;
    width: 48px;
    height: 48px;
    margin: 0 auto 1rem;
    place-items: center;
    border-radius: 50%;
    background: rgba(220, 53, 69, 0.12);
    color: #dc3545;
    font-size: 1.5rem;
    font-weight: 800;
}

@media (max-width: 900px) {
    .metric-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .attention-panel {
        align-items: flex-start;
        flex-direction: column;
    }
}

@media (max-width: 576px) {
    .dashboard-header {
        align-items: flex-start;
        flex-direction: column;
    }

    .refresh-button {
        width: 100%;
    }

    .sales-highlight {
        padding: 1.25rem;
    }

    .sales-icon {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        font-size: 1.4rem;
    }

    .section-heading {
        align-items: flex-start;
        flex-direction: column;
    }

    .metric-grid {
        gap: 0.75rem;
    }

    .metric-card {
        padding: 1rem;
    }

    .metric-top {
        align-items: flex-start;
        flex-direction: column;
        gap: 0.5rem;
    }

    .metric-value {
        font-size: 1.6rem;
    }

    .attention-stats {
        width: 100%;
        justify-content: space-between;
    }

    .attention-panel > .btn {
        width: 100%;
    }
}
</style>