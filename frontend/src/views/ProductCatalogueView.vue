<script setup>
import { computed, onMounted, ref } from 'vue';
import { getProducts } from '@/services/productService';
import { useCartStore } from '@/stores/cartStore';
import { useNotification } from '@/composables/useNotifications';
import { getStockStatus } from '@/utils/inventory';

const cartStore = useCartStore();
const { notify } = useNotification();

const products = ref([]);
const loading = ref(true);
const searchQuery = ref('');
const selectedCategory = ref('');
const sortOption = ref('featured');
const addingProductId = ref(null);

onMounted(async () => {
    try {
        products.value = await getProducts();

        if (products.value.length === 0) {
            notify('No products are currently available.', 'info');
        }
    } catch (error) {
        console.error('Failed to load products:', error);
        notify('Unable to load products. Please try again later.', 'danger');
    } finally {
        loading.value = false;
    }
});

const categories = computed(() => {
    return [...new Set(products.value.map(product => product.category).filter(Boolean))]
        .sort((a, b) => a.localeCompare(b));
});

const filteredProducts = computed(() => {
    const query = searchQuery.value.trim().toLowerCase();

    let result = products.value.filter(product => {
        const matchesSearch =
            !query ||
            product.name?.toLowerCase().includes(query) ||
            product.description?.toLowerCase().includes(query) ||
            product.category?.toLowerCase().includes(query);

        const matchesCategory =
            !selectedCategory.value ||
            product.category === selectedCategory.value;

        return matchesSearch && matchesCategory;
    });

    result = [...result];

    if (sortOption.value === 'price-low') {
        result.sort((a, b) => Number(a.price) - Number(b.price));
    } else if (sortOption.value === 'price-high') {
        result.sort((a, b) => Number(b.price) - Number(a.price));
    } else if (sortOption.value === 'name') {
        result.sort((a, b) => a.name.localeCompare(b.name));
    }

    return result;
});

async function handleAddToCart(product) {
    const token = localStorage.getItem('access_token');
    if (!token) {
        notify('Please log in to add products to your cart.', 'warning');
        return;
    }
    if (!product.is_active || product.stock <= 0) {
        notify('This product is currently unavailable.', 'info');
        return;
    }

    addingProductId.value = product.id;

    try {
        await cartStore.addItem(product.id, 1);
        notify(`${product.name} added to your cart.`);
    } catch (error) {
        notify(error.response?.data?.message || 'Unable to add this product to your cart.', 'danger');
    } finally {
        addingProductId.value = null;
    }
}

function formatPrice(price) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 2,
    }).format(Number(price));
}
</script>

<template>
    <main class="page-container catalogue-page">
        <!-- Page heading -->
        <section class="catalogue-heading">
            <div>
                <p class="page-eyebrow mb-2">Discover something great</p>
                <h1 class="catalogue-title">Product Catalogue</h1>
                <p class="page-description mb-0">Explore our collection and find the right products for you.</p>
            </div>

            <div class="catalogue-count">
                <span class="count-number">{{ filteredProducts.length }}</span>
                <span class="count-label">{{ filteredProducts.length === 1 ? 'Product' : 'Products' }}</span>
            </div>
        </section>

        <!-- Search and filters -->
        <section class="catalogue-toolbar">
            <div class="catalogue-search">
                <span class="search-icon" aria-hidden="true">⌕</span>
                <input
                    v-model="searchQuery"
                    type="search"
                    class="form-control"
                    placeholder="Search products, categories..."
                    aria-label="Search products"
                />
            </div>

            <select v-model="selectedCategory" class="form-select catalogue-filter" aria-label="Filter by category">
                <option value="">All categories</option>
                <option v-for="category in categories" :key="category" :value="category"> {{ category }} </option>
            </select>

            <select v-model="sortOption" class="form-select catalogue-filter" aria-label="Sort products">
                <option value="featured">Featured</option>
                <option value="price-low">Price: Low to high</option>
                <option value="price-high">Price: High to low</option>
                <option value="name">Name: A to Z</option>
            </select>
        </section>

        <!-- Loading state -->
        <div v-if="loading" class="catalogue-state">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading products...</span>
            </div>
            <p class="mt-3 mb-0">Finding products for you...</p>
        </div>

        <!-- Empty state -->
        <div v-else-if="filteredProducts.length === 0" class="catalogue-empty">
            <div class="empty-icon">⌕</div>
            <h2>No products found</h2>
            <p>Try changing your search or selecting another category.</p>

            <button
                class="btn btn-outline-primary"
                @click="searchQuery = ''; selectedCategory = ''; sortOption = 'featured'"
            >
                Clear filters
            </button>
        </div>

        <!-- Product grid -->
        <section v-else class="product-grid">
            <article v-for="product in filteredProducts" :key="product.id" class="product-card">
                <RouterLink
                    class="product-image-link"
                    :to="{ name: 'product-details', params: { id: product.id } }"
                    :aria-label="`View ${product.name}`"
                >
                    <div class="product-image-wrap">
                        <img
                            v-if="product.image_url"
                            :src="product.image_url"
                            :alt="product.name"
                            class="product-image"
                            loading="lazy"
                        />

                        <div v-else class="product-image-placeholder">
                            <span>No image</span>
                        </div>
                    </div>
                </RouterLink>

                <div class="product-card-body">
                    <p class="product-category">{{ product.category || 'General' }}</p>

                    <RouterLink
                        :to="{ name: 'product-details', params: { id: product.id } }"
                        class="product-name-link"
                    >
                        <h2 class="product-name">{{ product.name }}</h2>
                    </RouterLink>

                    <p class="product-description">{{ product.description }}</p>

                    <div class="product-card-footer">
                        <div class="product-price">{{ formatPrice(product.price) }}</div>

                        <p class="product-stock" :class="getStockStatus(product.stock).className">
                            <span class="stock-dot"></span> {{ getStockStatus(product.stock).label }}
                        </p>

                        <button
                            class="btn btn-primary product-add-button"
                            :disabled="product.stock <= 0 || addingProductId === product.id"
                            @click="handleAddToCart(product)"
                        >
                            <span v-if="addingProductId === product.id">Adding...</span>
                            <span v-else-if="product.stock <= 0">Out of Stock</span>
                            <span v-else>Add to Cart</span>
                        </button>
                    </div>
                </div>
            </article>
        </section>
    </main>
</template>

<style scoped>
.catalogue-page {
    position: relative;
}

/* Heading */
.catalogue-heading {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1.5rem;
    margin-bottom: 1.75rem;
}

.catalogue-title {
    margin-bottom: 0.5rem;
    font-size: clamp(1.8rem, 3vw, 2.5rem);
    font-weight: 750;
}

.catalogue-count {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    padding: 0.75rem 1rem;
    border: 1px solid var(--border);
    border-radius: 14px;
    background: rgba(248, 250, 252, 0.8);
}

.count-number {
    color: var(--brand);
    font-size: 1.5rem;
    font-weight: 750;
    line-height: 1.1;
}

.count-label {
    color: var(--text-secondary);
    font-size: 0.78rem;
}

/* Toolbar */
.catalogue-toolbar {
    display: grid;
    grid-template-columns: minmax(220px, 1fr) minmax(160px, 220px) minmax(170px, 220px);
    gap: 0.75rem;
    padding: 1rem;
    margin-bottom: 1.5rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: rgba(248, 250, 252, 0.88);
    box-shadow: var(--shadow-sm);
}

.catalogue-search {
    position: relative;
}

.catalogue-search .form-control {
    min-height: 44px;
    padding-left: 2.5rem;
}

.search-icon {
    position: absolute;
    top: 50%;
    left: 0.9rem;
    z-index: 1;
    color: var(--text-secondary);
    font-size: 1.35rem;
    line-height: 1;
    transform: translateY(-55%);
}

.catalogue-filter {
    min-height: 44px;
}

/* Product grid */
.product-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1.25rem;
}

.product-card {
    display: flex;
    min-width: 0;
    flex-direction: column;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: rgba(248, 250, 252, 0.96);
    box-shadow: var(--shadow-sm);
    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease,
        border-color 0.2s ease;
}

.product-card:hover {
    transform: translateY(-4px);
    border-color: #bdccff;
    box-shadow: var(--shadow-md);
}

.product-image-link {
    display: block;
    padding: 0.75rem 0.75rem 0;
    text-decoration: none;
}

.product-image-wrap {
    display: flex;
    height: 220px;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border-radius: 12px;
    background: #ffffff;
}

.product-image {
    width: 100%;
    height: 100%;
    padding: 1rem;
    object-fit: contain;
    transition: transform 0.25s ease;
}

.product-card:hover .product-image {
    transform: scale(1.04);
}

.product-image-placeholder {
    color: var(--text-secondary);
    font-size: 0.85rem;
}

/* Product details */
.product-card-body {
    display: flex;
    flex: 1;
    flex-direction: column;
    padding: 1rem;
}

.product-category {
    margin-bottom: 0.45rem;
    color: var(--brand);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.045em;
    text-transform: uppercase;
}

.product-name-link {
    color: var(--text-primary);
    text-decoration: none;
}

.product-name-link:hover {
    color: var(--brand);
}

.product-name {
    display: -webkit-box;
    min-height: 2.8em;
    overflow: hidden;
    margin-bottom: 0.6rem;
    font-size: 1rem;
    font-weight: 700;
    line-height: 1.4;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    line-clamp: 2;
}

.product-description {
    display: -webkit-box;
    overflow: hidden;
    margin-bottom: 1rem;
    color: var(--text-secondary);
    font-size: 0.82rem;
    line-height: 1.55;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
    line-clamp: 3;
}

/* Price, stock, action */
.product-card-footer {
    margin-top: auto;
    padding-top: 0.9rem;
    border-top: 1px solid var(--border);
}

.product-price {
    margin-bottom: 0.45rem;
    color: var(--text-primary);
    font-size: 1.15rem;
    font-weight: 800;
}

.product-stock {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 0.8rem;
    font-size: 0.78rem;
    font-weight: 600;
}

.stock-dot {
    width: 7px;
    height: 7px;
    flex: 0 0 7px;
    border-radius: 50%;
    background: currentColor;
}

.product-add-button {
    width: 100%;
    min-height: 42px;
}

/* Loading and empty states */
.catalogue-state,
.catalogue-empty {
    display: flex;
    min-height: 300px;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 1px dashed var(--border);
    border-radius: var(--radius-lg);
    background: rgba(248, 250, 252, 0.72);
    color: var(--text-secondary);
    text-align: center;
}

.catalogue-empty {
    padding: 2rem;
}

.catalogue-empty h2 {
    margin-bottom: 0.5rem;
    font-size: 1.4rem;
}

.empty-icon {
    display: grid;
    width: 56px;
    height: 56px;
    place-items: center;
    margin-bottom: 1rem;
    border-radius: 16px;
    background: var(--brand-soft);
    color: var(--brand);
    font-size: 2rem;
}

/* Responsive grid */
@media (max-width: 1199px) {
    .product-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }
}

@media (max-width: 767px) {
    .catalogue-heading {
        align-items: flex-start;
    }

    .catalogue-toolbar {
        grid-template-columns: 1fr 1fr;
    }

    .catalogue-search {
        grid-column: 1 / -1;
    }

    .product-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.85rem;
    }

    .product-image-wrap {
        height: 180px;
    }

    .product-card-body {
        padding: 0.8rem;
    }

    .product-description {
        font-size: 0.78rem;
    }
}

@media (max-width: 480px) {
    .catalogue-count {
        padding: 0.6rem 0.75rem;
    }

    .catalogue-toolbar {
        grid-template-columns: 1fr;
    }

    .catalogue-search {
        grid-column: auto;
    }

    .product-grid {
        gap: 0.65rem;
    }

    .product-image-link {
        padding: 0.5rem 0.5rem 0;
    }

    .product-image-wrap {
        height: 145px;
    }

    .product-name {
        font-size: 0.9rem;
    }

    .product-price {
        font-size: 1rem;
    }

    .product-add-button {
        padding-inline: 0.4rem;
        font-size: 0.82rem;
    }
}
</style>