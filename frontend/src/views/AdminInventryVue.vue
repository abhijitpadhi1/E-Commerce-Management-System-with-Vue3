<script setup>
import { onMounted, ref, computed } from 'vue';
import { getAdminProducts, updateProduct } from '@/services/productService';
import { useNotification } from '@/composables/useNotifications';

const products = ref([]);
const loading = ref(false);
const savingProductId = ref(null);
const searchQuery = ref('');
const selectedFilter = ref('ALL');

const { notify } = useNotification();

onMounted(fetchProducts);

async function fetchProducts() {
    loading.value = true;
    try {
        products.value = await getAdminProducts();
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to load inventory.', 'danger');
    } finally {
        loading.value = false;
    }
}

async function saveStock(product) {
    const stock = Number(product.stock);
    if (!Number.isInteger(stock) || stock < 0) {
        notify('Stock must be a non-negative whole number.', 'danger');
        return;
    }

    savingProductId.value = product.id;

    try {
        const updatedProduct = await updateProduct(product.id, { stock });

        const index = products.value.findIndex((item) => item.id === updatedProduct.id);

        if (index !== -1) {
            products.value[index] = updatedProduct;
        }

        notify(`Stock updated for ${product.name}.`, 'success');
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to update stock.', 'danger');
        await fetchProducts();
    } finally {
        savingProductId.value = null;
    }
}

function stockStatus(stock) {
    if (stock <= 0) return 'Out of Stock';
    if (stock <= 5) return 'Low Stock';
    return 'In Stock';
}

function stockClass(stock) {
    if (stock <= 0) return 'stock-out';
    if (stock <= 5) return 'stock-low';
    return 'stock-available';
}

const stockCounts = computed(() => ({
    ALL: products.value.length,
    IN_STOCK: products.value.filter((product) => product.stock > 5).length,
    LOW_STOCK: products.value.filter((product) => product.stock > 0 && product.stock <= 5).length,
    OUT_OF_STOCK: products.value.filter((product) => product.stock <= 0).length,
}));

const filteredProducts = computed(() => {
    const query = searchQuery.value.trim().toLowerCase();

    return products.value.filter((product) => {
        const matchesSearch =
            !query ||
            product.name?.toLowerCase().includes(query) ||
            product.category?.toLowerCase().includes(query);

        const matchesFilter =
            selectedFilter.value === 'ALL' ||
            (selectedFilter.value === 'IN_STOCK' && product.stock > 5) ||
            (selectedFilter.value === 'LOW_STOCK' && product.stock > 0 && product.stock <= 5) ||
            (selectedFilter.value === 'OUT_OF_STOCK' && product.stock <= 0);

        return matchesSearch && matchesFilter;
    });
});
</script>

<template>
    <main class="admin-inventory-page container py-5">
        <!-- Header -->
        <header class="page-header">
            <div>
                <p class="eyebrow">Store management</p>
                <h1>Inventory Management</h1>
                <p class="page-description">
                    Monitor product availability and keep stock levels up to date.
                </p>
            </div>

            <button class="btn btn-outline-primary refresh-button" :disabled="loading" @click="fetchProducts">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                {{ loading ? 'Refreshing...' : '↻ Refresh Inventory' }}
            </button>
        </header>

        <!-- Summary cards -->
        <section v-if="!loading && products.length" class="summary-grid">
            <article class="summary-card">
                <span class="summary-label">Total Products</span>
                <strong>{{ stockCounts.ALL }}</strong>
                <span class="summary-description">In the catalogue</span>
            </article>

            <article class="summary-card summary-available">
                <span class="summary-label">In Stock</span>
                <strong>{{ stockCounts.IN_STOCK }}</strong>
                <span class="summary-description">More than 5 units</span>
            </article>

            <article class="summary-card summary-low">
                <span class="summary-label">Low Stock</span>
                <strong>{{ stockCounts.LOW_STOCK }}</strong>
                <span class="summary-description">1–5 units remaining</span>
            </article>

            <article class="summary-card summary-out">
                <span class="summary-label">Out of Stock</span>
                <strong>{{ stockCounts.OUT_OF_STOCK }}</strong>
                <span class="summary-description">Unavailable for purchase</span>
            </article>
        </section>

        <!-- Search and filters -->
        <section v-if="!loading && products.length" class="inventory-controls">
            <div class="search-wrapper">
                <span class="search-icon">⌕</span>
                <input
                    v-model="searchQuery"
                    type="search"
                    class="form-control search-input"
                    placeholder="Search by product name or category..."
                    aria-label="Search inventory"
                />
            </div>

            <div class="filter-tabs">
                <button
                    v-for="filter in [
                        { value: 'ALL', label: 'All', count: stockCounts.ALL },
                        { value: 'IN_STOCK', label: 'In Stock', count: stockCounts.IN_STOCK },
                        { value: 'LOW_STOCK', label: 'Low Stock', count: stockCounts.LOW_STOCK },
                        { value: 'OUT_OF_STOCK', label: 'Out of Stock', count: stockCounts.OUT_OF_STOCK },
                    ]"
                    :key="filter.value"
                    class="filter-tab"
                    :class="{ active: selectedFilter === filter.value }"
                    @click="selectedFilter = filter.value"
                >
                    {{ filter.label }}
                    <span>{{ filter.count }}</span>
                </button>
            </div>
        </section>

        <!-- Loading -->
        <section v-if="loading" class="state-card">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading inventory</span>
            </div>
            <p class="mt-3 mb-0">Loading product inventory...</p>
        </section>

        <!-- Empty inventory -->
        <section v-else-if="products.length === 0" class="state-card">
            <div class="empty-icon">▦</div>
            <h2>No products found</h2>
            <p>Products will appear here once they are added to your catalogue.</p>
        </section>

        <!-- No filter/search matches -->
        <section v-else-if="filteredProducts.length === 0" class="state-card">
            <div class="empty-icon">⌕</div>
            <h2>No matching products</h2>
            <p>Try changing your search term or stock filter.</p>
            <button class="btn btn-outline-primary" @click="searchQuery = ''; selectedFilter = 'ALL'">
                Clear Filters
            </button>
        </section>

        <!-- Product inventory -->
        <section v-else class="inventory-list">
            <div class="list-heading">
                <h2>Product Stock</h2>
                <span>{{ filteredProducts.length }} product(s)</span>
            </div>

            <article
                v-for="product in filteredProducts"
                :key="product.id"
                class="inventory-card"
                :class="{ 'is-out-of-stock': product.stock <= 0 }"
            >
                <div class="product-info">
                    <div class="product-avatar">
                        {{ product.name?.charAt(0)?.toUpperCase() || '?' }}
                    </div>

                    <div class="product-text">
                        <h3>{{ product.name }}</h3>
                        <span class="product-category">{{ product.category }}</span>
                        <span class="product-id">Product #{{ product.id }}</span>
                    </div>
                </div>

                <div class="stock-info">
                    <span class="field-label">Current stock</span>
                    <strong class="stock-number" :class="stockClass(product.stock)">
                        {{ product.stock }}
                    </strong>

                    <span class="stock-badge" :class="stockClass(product.stock)">
                        {{ stockStatus(product.stock) }}
                    </span>
                </div>

                <div class="stock-editor">
                    <label :for="`stock-${product.id}`" class="field-label">
                        Update quantity
                    </label>

                    <div class="stock-input-group">
                        <input
                            :id="`stock-${product.id}`"
                            v-model.number="product.stock"
                            type="number"
                            min="0"
                            step="1"
                            class="form-control stock-input"
                            :disabled="savingProductId === product.id"
                        />

                        <button
                            class="btn btn-primary save-button"
                            :disabled="savingProductId === product.id"
                            @click="saveStock(product)"
                        >
                            <span
                                v-if="savingProductId === product.id"
                                class="spinner-border spinner-border-sm me-2"
                                role="status"
                            ></span>
                            {{ savingProductId === product.id ? 'Saving...' : 'Save Stock' }}
                        </button>
                    </div>

                    <span class="editor-hint">Enter a whole number greater than or equal to 0.</span>
                </div>
            </article>
        </section>
    </main>
</template>

<style scoped>
.admin-inventory-page {
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
    min-height: 42px;
    flex-shrink: 0;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.summary-card {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    padding: 1.2rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface, rgba(255, 255, 255, 0.72));
    box-shadow: var(--shadow-sm);
}

.summary-label {
    color: var(--text-secondary);
    font-size: 0.82rem;
    font-weight: 650;
}

.summary-card strong {
    font-size: 1.8rem;
    font-weight: 800;
}

.summary-description {
    color: var(--text-secondary);
    font-size: 0.75rem;
}

.summary-available strong {
    color: var(--success, #198754);
}

.summary-low strong {
    color: #a87900;
}

.summary-out strong {
    color: var(--danger, #dc3545);
}

.inventory-controls {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.search-wrapper {
    position: relative;
    max-width: 520px;
}

.search-icon {
    position: absolute;
    top: 50%;
    left: 0.9rem;
    transform: translateY(-50%);
    color: var(--text-secondary);
    font-size: 1.25rem;
    pointer-events: none;
}

.search-input {
    min-height: 44px;
    padding-left: 2.5rem;
    border-color: var(--border);
    border-radius: 12px;
    background: var(--surface, rgba(255, 255, 255, 0.72));
    color: var(--text-primary);
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
    gap: 0.5rem;
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

.list-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
}

.list-heading h2 {
    margin: 0;
    font-size: 1.15rem;
    font-weight: 750;
}

.list-heading span {
    color: var(--text-secondary);
    font-size: 0.82rem;
}

.inventory-card,
.state-card {
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface, rgba(255, 255, 255, 0.72));
    box-shadow: var(--shadow-sm);
}

.inventory-card {
    display: grid;
    grid-template-columns: minmax(0, 1.5fr) minmax(110px, 0.6fr) minmax(250px, 1fr);
    align-items: center;
    gap: 1.5rem;
    padding: 1.25rem;
    margin-bottom: 0.85rem;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.inventory-card:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

.inventory-card.is-out-of-stock {
    border-left: 3px solid var(--danger, #dc3545);
}

.product-info {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    min-width: 0;
}

.product-avatar {
    display: grid;
    width: 46px;
    height: 46px;
    flex-shrink: 0;
    place-items: center;
    border-radius: 14px;
    background: var(--brand-soft);
    color: var(--brand);
    font-size: 1.2rem;
    font-weight: 800;
}

.product-text {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    min-width: 0;
}

.product-text h3 {
    margin: 0;
    font-size: 0.95rem;
    font-weight: 750;
    overflow-wrap: anywhere;
}

.product-category,
.product-id {
    color: var(--text-secondary);
    font-size: 0.75rem;
}

.stock-info {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.35rem;
}

.field-label {
    color: var(--text-secondary);
    font-size: 0.75rem;
    font-weight: 650;
}

.stock-number {
    font-size: 1.5rem;
    font-weight: 800;
}

.stock-available {
    color: var(--success, #198754);
}

.stock-low {
    color: #a87900;
}

.stock-out {
    color: var(--danger, #dc3545);
}

.stock-badge {
    display: inline-flex;
    padding: 0.25rem 0.55rem;
    border-radius: 999px;
    font-size: 0.68rem;
    font-weight: 750;
    white-space: nowrap;
}

.stock-badge.stock-available {
    background: rgba(25, 135, 84, 0.12);
}

.stock-badge.stock-low {
    background: rgba(255, 193, 7, 0.18);
}

.stock-badge.stock-out {
    background: rgba(220, 53, 69, 0.12);
}

.stock-editor {
    min-width: 0;
}

.stock-input-group {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.4rem;
}

.stock-input {
    min-width: 0;
    max-width: 100px;
    border-color: var(--border);
    background: var(--surface, rgba(255, 255, 255, 0.72));
    color: var(--text-primary);
}

.save-button {
    flex-shrink: 0;
    min-height: 38px;
}

.editor-hint {
    display: block;
    margin-top: 0.4rem;
    color: var(--text-secondary);
    font-size: 0.68rem;
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
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .inventory-card {
        grid-template-columns: minmax(0, 1fr) minmax(110px, 0.5fr);
    }

    .stock-editor {
        grid-column: 1 / -1;
        padding-top: 1rem;
        border-top: 1px solid var(--border);
    }
}

@media (max-width: 576px) {
    .page-header {
        align-items: flex-start;
        flex-direction: column;
    }

    .refresh-button {
        width: 100%;
    }

    .summary-grid {
        gap: 0.75rem;
    }

    .summary-card {
        padding: 1rem;
    }

    .summary-card strong {
        font-size: 1.5rem;
    }

    .inventory-card {
        grid-template-columns: minmax(0, 1fr);
        gap: 1rem;
        padding: 1rem;
    }

    .stock-info {
        display: grid;
        grid-template-columns: 1fr auto;
        align-items: center;
    }

    .stock-info .field-label {
        grid-column: 1 / -1;
    }

    .stock-editor {
        grid-column: auto;
    }

    .stock-input-group {
        display: grid;
        grid-template-columns: 100px minmax(0, 1fr);
    }

    .save-button {
        width: 100%;
    }
}
</style>