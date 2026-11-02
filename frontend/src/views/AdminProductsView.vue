<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { getAdminProducts, createProduct, deleteProduct } from '@/services/productService';
import { useNotification } from '@/composables/useNotifications';

const products = ref([]);
const loading = ref(false);
const saving = ref(false);
const deletingProductId = ref(null);
const showForm = ref(false);
const searchQuery = ref('');
const statusFilter = ref('ALL');

const { notify } = useNotification();

const emptyForm = () => ({
    name: '',
    description: '',
    price: '',
    stock: 0,
    category: '',
    image_url: '',
});

const form = reactive(emptyForm());

const totalProducts = computed(() => products.value.length);
const activeProducts = computed(() => products.value.filter((product) => product.is_active).length);
const inactiveProducts = computed(() => products.value.filter((product) => !product.is_active).length);

const filteredProducts = computed(() => {
    const query = searchQuery.value.trim().toLowerCase();

    return products.value.filter((product) => {
        const matchesSearch =
            !query ||
            product.name?.toLowerCase().includes(query) ||
            product.category?.toLowerCase().includes(query);

        const matchesStatus =
            statusFilter.value === 'ALL' ||
            (statusFilter.value === 'ACTIVE' && product.is_active) ||
            (statusFilter.value === 'INACTIVE' && !product.is_active);

        return matchesSearch && matchesStatus;
    });
});

onMounted(fetchProducts);

async function fetchProducts() {
    loading.value = true;

    try {
        products.value = await getAdminProducts();
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to load products.', 'danger');
    } finally {
        loading.value = false;
    }
}

function openCreateForm() {
    Object.assign(form, emptyForm());
    showForm.value = true;
}

function closeForm() {
    if (saving.value) return;
    showForm.value = false;
}

async function submitProduct() {
    const price = Number(form.price);
    const stock = Number(form.stock);

    if (!form.name.trim() || !form.category.trim()) {
        notify('Product name and category are required.', 'danger');
        return;
    }

    if (!Number.isFinite(price) || price < 0) {
        notify('Enter a valid non-negative price.', 'danger');
        return;
    }

    if (!Number.isInteger(stock) || stock < 0) {
        notify('Stock must be a non-negative whole number.', 'danger');
        return;
    }

    saving.value = true;

    try {
        const payload = {
            ...form,
            name: form.name.trim(),
            category: form.category.trim(),
            description: form.description.trim(),
            image_url: form.image_url.trim(),
            price,
            stock,
        };

        await createProduct(payload);

        notify('Product created successfully.', 'success');
        showForm.value = false;
        await fetchProducts();
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to create product.', 'danger');
    } finally {
        saving.value = false;
    }
}

async function removeProduct(product) {
    const confirmed = window.confirm(`Are you sure you want to remove "${product.name}" from the catalogue?`);
    if (!confirmed) return;
    
    deletingProductId.value = product.id;

    try {
        await deleteProduct(product.id);
        notify('Product removed from the catalogue.', 'success');
        await fetchProducts();
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to delete product.', 'danger');
    } finally {
        deletingProductId.value = null;
    }
}

function formatPrice(price) {
    return Number(price).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function stockStatus(stock) {
    if (stock <= 0) return 'Out of stock';
    if (stock <= 5) return 'Low stock';
    return 'In stock';
}

function stockClass(stock) {
    if (stock <= 0) return 'stock-out';
    if (stock <= 5) return 'stock-low';
    return 'stock-good';
}
</script>

<template>
    <main class="admin-products-page">
        <div class="products-container">
            <!-- Page heading -->
            <header class="page-header">
                <div>
                    <div class="eyebrow">CATALOGUE MANAGEMENT</div>
                    <h1>Manage Products</h1>
                    <p class="page-subtitle">Create, organize, and manage products in your store.</p>
                </div>

                <button v-if="!showForm" class="primary-button" @click="openCreateForm">
                    <span class="button-icon">＋</span>
                    Add Product
                </button>

                <button v-else class="secondary-button" :disabled="saving" @click="closeForm">
                    ← Back to Products
                </button>
            </header>

            <!-- Summary cards -->
            <section v-if="!showForm" class="summary-grid">
                <article class="summary-card">
                    <div class="summary-label">Total products</div>
                    <div class="summary-value">{{ totalProducts }}</div>
                    <div class="summary-note">Across all categories</div>
                </article>

                <article class="summary-card">
                    <div class="summary-label">Active products</div>
                    <div class="summary-value">{{ activeProducts }}</div>
                    <div class="summary-note">
                        <span class="status-dot dot-active"></span>
                        Available in catalogue
                    </div>
                </article>

                <article class="summary-card">
                    <div class="summary-label">Inactive products</div>
                    <div class="summary-value">{{ inactiveProducts }}</div>
                    <div class="summary-note">
                        Removed from customer view
                    </div>
                </article>
            </section>

            <!-- Create product form -->
            <section v-if="showForm" class="form-panel">
                <div class="panel-heading">
                    <div>
                        <div class="eyebrow">NEW LISTING</div>
                        <h2>Create a product</h2>
                        <p>Add product details to make it available in your store.</p>
                    </div>
                    <div class="form-icon">＋</div>
                </div>

                <form @submit.prevent="submitProduct">
                    <div class="form-section-title">Basic information</div>
                    <div class="form-grid">
                        <div class="form-field">
                            <label for="product-name">Product name *</label>
                            <input
                                id="product-name"
                                v-model.trim="form.name"
                                class="theme-input"
                                type="text"
                                placeholder="e.g. Wireless headphones"
                                maxlength="120"
                                required
                            />
                        </div>

                        <div class="form-field">
                            <label for="product-category">Category *</label>
                            <input
                                id="product-category"
                                v-model.trim="form.category"
                                class="theme-input"
                                type="text"
                                placeholder="e.g. Electronics"
                                maxlength="80"
                                required
                            />
                        </div>

                        <div class="form-field">
                            <label for="product-price">Price (₹) *</label>
                            <input
                                id="product-price"
                                v-model.number="form.price"
                                class="theme-input"
                                type="number"
                                min="0"
                                step="0.01"
                                placeholder="0.00"
                                required
                            />
                        </div>

                        <div class="form-field">
                            <label for="product-stock">Initial stock *</label>
                            <input
                                id="product-stock"
                                v-model.number="form.stock"
                                class="theme-input"
                                type="number"
                                min="0"
                                step="1"
                                required
                            />
                        </div>

                        <div class="form-field full-width">
                            <label for="product-image">Image URL</label>
                            <input
                                id="product-image"
                                v-model.trim="form.image_url"
                                class="theme-input"
                                type="url"
                                placeholder="https://example.com/product-image.jpg"
                            />
                            <small>Use a publicly accessible image URL.</small>
                        </div>

                        <div class="form-field full-width">
                            <label for="product-description">Description</label>
                            <textarea
                                id="product-description"
                                v-model.trim="form.description"
                                class="theme-input"
                                rows="4"
                                placeholder="Describe the product and its key features..."
                            ></textarea>
                        </div>
                    </div>

                    <div class="form-footer">
                        <span class="required-note">* Required fields</span>
                        <div class="form-actions">
                            <button
                                type="button"
                                class="secondary-button"
                                :disabled="saving"
                                @click="closeForm"
                            >
                                Cancel
                            </button>

                            <button type="submit" class="primary-button" :disabled="saving">
                                {{ saving ? 'Creating product…' : 'Create Product' }}
                            </button>
                        </div>
                    </div>
                </form>
            </section>

            <!-- Product list -->
            <section v-else class="products-panel">
                <div class="list-heading">
                    <div>
                        <h2>Product catalogue</h2>
                        <p>Review and manage your current product listings.</p>
                    </div>

                    <button
                        class="icon-button"
                        title="Refresh products"
                        :disabled="loading"
                        @click="fetchProducts"
                    >
                        ↻
                    </button>
                </div>

                <div class="toolbar">
                    <div class="search-box">
                        <span class="search-icon">⌕</span>
                        <input
                            v-model="searchQuery"
                            type="search"
                            placeholder="Search by product or category..."
                            aria-label="Search products"
                        />
                    </div>

                    <select v-model="statusFilter" class="filter-select" aria-label="Filter by status">
                        <option value="ALL">All products</option>
                        <option value="ACTIVE">Active</option>
                        <option value="INACTIVE">Inactive</option>
                    </select>
                </div>

                <div v-if="loading" class="state-message">
                    <div class="loading-spinner"></div>
                    <span>Loading products…</span>
                </div>

                <div v-else-if="filteredProducts.length === 0" class="empty-state">
                    <div class="empty-icon">▦</div>
                    <h3>{{ products.length ? 'No matching products' : 'No products yet' }}</h3>
                    <p>
                        {{
                            products.length
                                ? 'Try changing your search or filter.'
                                : 'Create your first product to start building your catalogue.'
                        }}
                    </p>

                    <button v-if="!products.length" class="primary-button" @click="openCreateForm">
                        ＋ Add your first product
                    </button>
                </div>

                <div v-else class="product-list">
                    <article v-for="product in filteredProducts" :key="product.id" class="product-row">
                        <div class="product-image">
                            <img
                                v-if="product.image_url"
                                :src="product.image_url"
                                :alt="product.name"
                                loading="lazy"
                            />
                            <span v-else class="image-placeholder">▧</span>
                        </div>

                        <div class="product-info">
                            <div class="product-name">{{ product.name }}</div>
                            <div class="product-category">{{ product.category }}</div>
                            <div class="product-id">Product ID: #{{ product.id }}</div>
                        </div>

                        <div class="product-price">
                            <span class="mobile-label">Price</span>
                            <strong>₹{{ formatPrice(product.price) }}</strong>
                        </div>

                        <div class="product-stock">
                            <span class="mobile-label">Stock</span>
                            <strong>{{ product.stock }}</strong>
                            <span class="stock-label" :class="stockClass(product.stock)">
                                {{ stockStatus(product.stock) }}
                            </span>
                        </div>

                        <div class="product-status">
                            <span
                                class="status-badge"
                                :class="product.is_active ? 'badge-active' : 'badge-inactive'"
                            >
                                <span class="status-dot"></span>
                                {{ product.is_active ? 'Active' : 'Inactive' }}
                            </span>
                        </div>

                        <div class="product-action">
                            <button
                                v-if="product.is_active"
                                class="delete-button"
                                :disabled="deletingProductId === product.id"
                                @click="removeProduct(product)"
                            >
                                {{ deletingProductId === product.id ? 'Removing...' : 'Remove' }}
                            </button>
                            <span v-else class="removed-label">Removed</span>
                        </div>
                    </article>
                </div>

                <div v-if="!loading && filteredProducts.length" class="list-footer">
                    Showing {{ filteredProducts.length }} of {{ products.length }} products
                </div>
            </section>
        </div>
    </main>
</template>

<style scoped>
.admin-products-page {
    min-height: 100vh;
    padding: 2.25rem 1.25rem 4rem;
    color: var(--text-primary);
}

.products-container {
    width: min(1180px, 100%);
    margin: 0 auto;
}

.page-header,
.panel-heading,
.list-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
}

.page-header {
    margin-bottom: 1.75rem;
}

.eyebrow {
    margin-bottom: 0.45rem;
    color: var(--brand);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.13em;
}

h1,
h2,
h3,
p {
    margin-top: 0;
}

h1 {
    margin-bottom: 0.4rem;
    font-size: clamp(1.8rem, 4vw, 2.35rem);
    font-weight: 750;
    letter-spacing: -0.04em;
}

h2 {
    margin-bottom: 0.35rem;
    font-size: 1.2rem;
    font-weight: 700;
}

.page-subtitle,
.panel-heading p,
.list-heading p {
    margin-bottom: 0;
    color: var(--text-secondary);
    font-size: 0.92rem;
}

.primary-button,
.secondary-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.55rem;
    min-height: 43px;
    padding: 0.7rem 1rem;
    border-radius: 11px;
    font-size: 0.88rem;
    font-weight: 700;
    transition: transform 0.18s ease, background 0.18s ease, border 0.18s ease;
}

.primary-button {
    border: 1px solid var(--brand);
    background: var(--brand);
    color: white;
}

.primary-button:hover:not(:disabled) {
    background: var(--brand-hover);
    transform: translateY(-1px);
}

.secondary-button {
    border: 1px solid var(--border);
    background: var(--surface, transparent);
    color: var(--text-primary);
}

.secondary-button:hover:not(:disabled) {
    border-color: var(--brand);
    background: var(--brand-soft);
}

button:disabled {
    cursor: not-allowed;
    opacity: 0.6;
}

.button-icon {
    font-size: 1.2rem;
    line-height: 1;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.summary-card,
.products-panel,
.form-panel {
    border: 1px solid var(--border);
    border-radius: var(--radius-lg, 16px);
    background: var(--surface, rgba(255, 255, 255, 0.04));
    box-shadow: var(--shadow-sm);
}

.summary-card {
    padding: 1.25rem 1.4rem;
}

.summary-label {
    color: var(--text-secondary);
    font-size: 0.82rem;
    font-weight: 600;
}

.summary-value {
    margin: 0.45rem 0;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.04em;
}

.summary-note {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    color: var(--text-secondary);
    font-size: 0.77rem;
}

.status-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: currentColor;
}

.dot-active {
    color: var(--success, #22c55e);
}

.products-panel,
.form-panel {
    overflow: hidden;
}

.list-heading {
    padding: 1.35rem 1.5rem;
    border-bottom: 1px solid var(--border);
}

.icon-button {
    width: 39px;
    height: 39px;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: transparent;
    color: var(--text-primary);
    font-size: 1.4rem;
}

.icon-button:hover:not(:disabled) {
    border-color: var(--brand);
    color: var(--brand);
}

.toolbar {
    display: flex;
    gap: 0.8rem;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border);
}

.search-box {
    display: flex;
    align-items: center;
    flex: 1;
    gap: 0.65rem;
    min-width: 0;
    padding: 0 0.85rem;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--input-bg, transparent);
}

.search-icon {
    color: var(--text-secondary);
    font-size: 1.35rem;
}

.search-box input {
    width: 100%;
    min-height: 42px;
    border: 0;
    outline: 0;
    background: transparent;
    color: var(--text-primary);
    font: inherit;
    font-size: 0.85rem;
}

.search-box input::placeholder {
    color: var(--text-secondary);
}

.filter-select {
    min-width: 145px;
    padding: 0.65rem 0.8rem;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--input-bg, transparent);
    color: var(--text-primary);
    font: inherit;
    font-size: 0.85rem;
}

.filter-select option {
    color: #222;
}

.product-row {
    display: grid;
    grid-template-columns: 58px minmax(160px, 1.6fr) minmax(95px, 0.7fr) minmax(105px, 0.8fr) minmax(95px, 0.7fr) auto;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border);
    transition: background 0.15s ease;
}

.product-row:last-child {
    border-bottom: 0;
}

.product-row:hover {
    background: var(--brand-soft);
}

.product-image {
    display: grid;
    width: 58px;
    height: 58px;
    overflow: hidden;
    place-items: center;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: var(--surface-raised, rgba(255, 255, 255, 0.05));
}

.product-image img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 0.25rem;
}

.image-placeholder {
    color: var(--text-secondary);
    font-size: 1.5rem;
}

.product-name {
    overflow: hidden;
    margin-bottom: 0.25rem;
    font-size: 0.9rem;
    font-weight: 700;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.product-category,
.product-id {
    color: var(--text-secondary);
    font-size: 0.75rem;
}

.product-id {
    margin-top: 0.2rem;
    opacity: 0.8;
}

.product-price strong,
.product-stock strong {
    font-size: 0.88rem;
    font-weight: 700;
}

.stock-label {
    display: block;
    margin-top: 0.2rem;
    font-size: 0.72rem;
    font-weight: 600;
}

.stock-good {
    color: var(--success, #22c55e);
}

.stock-low {
    color: var(--warning, #eab308);
}

.stock-out {
    color: var(--danger, #ef4444);
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.38rem 0.6rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    white-space: nowrap;
}

.badge-active {
    background: rgba(34, 197, 94, 0.12);
    color: var(--success, #22c55e);
}

.badge-inactive {
    background: rgba(148, 163, 184, 0.15);
    color: var(--text-secondary);
}

.delete-button {
    padding: 0.45rem 0.7rem;
    border: 1px solid rgba(239, 68, 68, 0.35);
    border-radius: 8px;
    background: transparent;
    color: var(--danger, #ef4444);
    font-size: 0.78rem;
    font-weight: 700;
}

.delete-button:hover:not(:disabled) {
    background: rgba(239, 68, 68, 0.1);
}

.removed-label {
    color: var(--text-secondary);
    font-size: 0.78rem;
}

.list-footer {
    padding: 0.9rem 1.5rem;
    border-top: 1px solid var(--border);
    color: var(--text-secondary);
    font-size: 0.77rem;
}

.state-message,
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3.5rem 1.5rem;
    color: var(--text-secondary);
    text-align: center;
}

.loading-spinner {
    width: 25px;
    height: 25px;
    margin-bottom: 0.8rem;
    border: 3px solid var(--border);
    border-top-color: var(--brand);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.empty-icon {
    display: grid;
    width: 58px;
    height: 58px;
    margin-bottom: 1rem;
    place-items: center;
    border-radius: 16px;
    background: var(--brand-soft);
    color: var(--brand);
    font-size: 1.8rem;
}

.empty-state h3 {
    margin-bottom: 0.4rem;
    color: var(--text-primary);
    font-size: 1.05rem;
}

.empty-state p {
    max-width: 390px;
    margin-bottom: 1.2rem;
    font-size: 0.85rem;
}

.form-panel {
    padding: 1.5rem;
}

.panel-heading {
    margin-bottom: 1.5rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid var(--border);
}

.form-icon {
    display: grid;
    width: 46px;
    height: 46px;
    flex: 0 0 auto;
    place-items: center;
    border-radius: 13px;
    background: var(--brand-soft);
    color: var(--brand);
    font-size: 1.7rem;
}

.form-section-title {
    margin-bottom: 1rem;
    color: var(--text-primary);
    font-size: 0.85rem;
    font-weight: 750;
}

.form-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1.2rem;
}

.form-field {
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
}

.form-field.full-width {
    grid-column: 1 / -1;
}

.form-field label {
    color: var(--text-primary);
    font-size: 0.82rem;
    font-weight: 650;
}

.theme-input {
    width: 100%;
    padding: 0.75rem 0.85rem;
    border: 1px solid var(--border);
    border-radius: 10px;
    outline: none;
    background: var(--input-bg, transparent);
    color: var(--text-primary);
    font: inherit;
    font-size: 0.87rem;
    transition: border 0.15s ease, box-shadow 0.15s ease;
}

.theme-input:focus {
    border-color: var(--brand);
    box-shadow: 0 0 0 3px var(--brand-soft);
}

.theme-input::placeholder {
    color: var(--text-secondary);
    opacity: 0.7;
}

.form-field small {
    color: var(--text-secondary);
    font-size: 0.74rem;
}

.form-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-top: 1.5rem;
    padding-top: 1.25rem;
    border-top: 1px solid var(--border);
}

.required-note {
    color: var(--text-secondary);
    font-size: 0.75rem;
}

.form-actions {
    display: flex;
    gap: 0.65rem;
}

.mobile-label {
    display: none;
}

@media (max-width: 950px) {
    .product-row {
        grid-template-columns: 52px minmax(140px, 1.5fr) minmax(80px, 0.7fr) minmax(90px, 0.8fr) auto;
    }

    .product-status {
        display: none;
    }
}

@media (max-width: 700px) {
    .admin-products-page {
        padding: 1.5rem 0.85rem 3rem;
    }

    .page-header {
        align-items: flex-start;
    }

    .page-header .primary-button,
    .page-header .secondary-button {
        flex-shrink: 0;
        padding: 0.65rem 0.75rem;
        font-size: 0.78rem;
    }

    .summary-grid {
        grid-template-columns: 1fr;
        gap: 0.7rem;
    }

    .summary-card {
        padding: 1rem 1.15rem;
    }

    .summary-value {
        font-size: 1.65rem;
    }

    .list-heading,
    .toolbar {
        padding-right: 1rem;
        padding-left: 1rem;
    }

    .toolbar {
        flex-direction: column;
    }

    .filter-select {
        width: 100%;
    }

    .product-row {
        grid-template-columns: 48px minmax(0, 1fr) auto;
        gap: 0.75rem;
        padding: 1rem;
    }

    .product-image {
        width: 48px;
        height: 48px;
    }

    .product-info {
        min-width: 0;
    }

    .product-price,
    .product-stock {
        grid-column: 2;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .product-price {
        grid-row: 2;
    }

    .product-stock {
        grid-row: 3;
    }

    .mobile-label {
        display: inline;
        color: var(--text-secondary);
        font-size: 0.72rem;
    }

    .stock-label {
        display: inline;
        margin-top: 0;
    }

    .product-action {
        grid-column: 3;
        grid-row: 1 / 4;
        align-self: center;
    }

    .product-id {
        font-size: 0.7rem;
    }

    .form-panel {
        padding: 1.1rem;
    }

    .form-grid {
        grid-template-columns: 1fr;
    }

    .form-field.full-width {
        grid-column: auto;
    }

    .form-footer {
        align-items: flex-start;
        flex-direction: column;
    }

    .form-actions {
        width: 100%;
    }

    .form-actions button {
        flex: 1;
    }
}

@media (max-width: 420px) {
    .page-header {
        flex-direction: column;
        align-items: stretch;
    }

    .page-header button {
        width: 100%;
    }

    .list-heading {
        gap: 0.7rem;
    }

    .product-row {
        grid-template-columns: 42px minmax(0, 1fr) auto;
        gap: 0.6rem;
    }

    .product-image {
        width: 42px;
        height: 42px;
    }

    .product-name {
        font-size: 0.82rem;
    }

    .delete-button {
        padding: 0.4rem 0.5rem;
        font-size: 0.72rem;
    }
}
</style>