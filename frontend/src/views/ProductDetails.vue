<script setup>
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { getProductById } from '@/services/productService';
import { useCartStore } from '@/stores/cartStore';
import { useNotification } from '@/composables/useNotifications';

const route = useRoute();
const cartStore = useCartStore();
const { notify } = useNotification();

const product = ref(null);
const loading = ref(true);
const addingToCart = ref(false);

onMounted(async () => {
    try {
        product.value = await getProductById(route.params.id);
    } catch (error) {
        console.error('Failed to load product:', error);

        if (error.response?.status === 404) {
            notify('Product not found.', 'warning');
        } else {
            notify('Unable to load this product. Please try again later.', 'danger');
        }
    } finally {
        loading.value = false;
    }
});

async function handleAddToCart() {
    const token = localStorage.getItem('access_token');

    if (!token) {
        notify('Please log in to add products to your cart.', 'warning');
        return;
    }

    if (!product.value || !product.value.is_active || product.value.stock <= 0) {
        notify('This product is currently unavailable.', 'warning');
        return;
    }

    addingToCart.value = true;

    try {
        await cartStore.addItem(product.value.id, 1);
        notify(`${product.value.name} added to your cart.`, 'success');
    } catch (error) {
        console.error('Failed to add product to cart:', error);
        notify('Unable to add this product to your cart.', 'danger');
    } finally {
        addingToCart.value = false;
    }
}

function formatPrice(price) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(Number(price));
}
</script>

<template>
    <main class="page-container product-details-page">
        <!-- Loading -->
        <div v-if="loading" class="product-details-state">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading product...</span>
            </div>
            <p class="mt-3 mb-0">Loading product details...</p>
        </div>

        <!-- Product not found -->
        <div v-else-if="!product" class="product-details-state">
            <div class="details-state-icon">!</div>
            <h1>Product unavailable</h1>
            <p>We couldn't find this product. It may have been removed.</p>

            <RouterLink :to="{ name: 'products' }" class="btn btn-primary">
                Browse Products
            </RouterLink>
        </div>

        <!-- Product details -->
        <template v-else>
            <nav class="product-breadcrumb" aria-label="Breadcrumb">
                <RouterLink :to="{ name: 'products' }">Products</RouterLink>
                <span aria-hidden="true">/</span>
                <span>{{ product.category || 'General' }}</span>
            </nav>

            <section class="product-details-layout">
                <!-- Image panel -->
                <div class="product-gallery">
                    <div class="product-gallery-image">
                        <img v-if="product.image_url" :src="product.image_url" :alt="product.name" />
                        <div v-else class="product-gallery-placeholder">
                            <span>No image available</span>
                        </div>
                    </div>

                    <div class="gallery-caption">
                        <span class="gallery-caption-dot"></span>
                        Product image
                    </div>
                </div>

                <!-- Information panel -->
                <div class="product-information">
                    <p class="product-detail-category">{{ product.category || 'General' }}</p>
                    <h1 class="product-detail-title">{{ product.name }}</h1>

                    <div class="product-detail-price">{{ formatPrice(product.price) }}</div>

                    <div class="product-availability" :class="product.stock > 0 ? 'is-available' : 'is-unavailable'">
                        <span class="availability-dot"></span>
                        <div>
                            <strong v-if="product.stock > 0" class="mb-0">
                                {{ product.stock > 0 ? 'In Stock' : 'Out of Stock' }}
                            </strong>
                            <p v-else class="mb-0">
                                This product is currently unavailable.
                            </p>
                        </div>
                    </div>

                    <div class="product-detail-description">
                        <h2>About this product</h2>
                        <p>{{ product.description || 'No description is available for this product.' }}</p>
                    </div>

                    <div class="product-detail-actions">
                        <button
                            class="btn btn-primary btn-lg product-detail-add-button"
                            :disabled="product.stock <= 0 || addingToCart || !product.is_active"
                            @click="handleAddToCart"
                        >
                            <span v-if="addingToCart">Adding to Cart...</span>
                            <span v-else-if="product.stock <= 0">Out of Stock</span>
                            <span v-else>Add to Cart</span>
                        </button>

                        <RouterLink
                            :to="{ name: 'products' }"
                            class="btn btn-outline-secondary product-detail-back-button"
                        >
                            Back to Products
                        </RouterLink>
                    </div>

                    <div class="product-detail-note">
                        <span aria-hidden="true">✓</span>
                        Secure checkout and order tracking
                    </div>
                </div>
            </section>
        </template>
    </main>
</template>

<style scoped>
.product-details-page {
    max-width: 1320px;
}

/* Breadcrumb */
.product-breadcrumb {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin-bottom: 1.5rem;
    color: var(--text-secondary);
    font-size: 0.85rem;
}

.product-breadcrumb a {
    color: var(--brand);
    font-weight: 600;
    text-decoration: none;
}

.product-breadcrumb a:hover {
    text-decoration: underline;
}

/* Main layout */
.product-details-layout {
    display: grid;
    grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
    gap: clamp(1.5rem, 4vw, 3.5rem);
    align-items: start;
}

/* Image gallery */
.product-gallery {
    padding: 1rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: rgba(248, 250, 252, 0.94);
    box-shadow: var(--shadow-sm);
}

.product-gallery-image {
    display: flex;
    min-height: 460px;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border-radius: 14px;
    background: #ffffff;
}

.product-gallery-image img {
    width: 100%;
    height: 460px;
    padding: 2rem;
    object-fit: contain;
}

.product-gallery-placeholder {
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.gallery-caption {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.9rem 0.25rem 0.1rem;
    color: var(--text-secondary);
    font-size: 0.78rem;
}

.gallery-caption-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--brand);
}

/* Product information */
.product-information {
    padding-block: 0.5rem;
}

.product-detail-category {
    margin-bottom: 0.75rem;
    color: var(--brand);
    font-size: 0.78rem;
    font-weight: 750;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.product-detail-title {
    margin-bottom: 1.25rem;
    font-size: clamp(1.8rem, 3.2vw, 2.7rem);
    font-weight: 800;
    line-height: 1.2;
}

.product-detail-price {
    margin-bottom: 1.5rem;
    color: var(--text-primary);
    font-size: clamp(1.7rem, 3vw, 2.2rem);
    font-weight: 800;
    letter-spacing: -0.04em;
}

/* Availability panel */
.product-availability {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 1rem;
    margin-bottom: 1.75rem;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: rgba(248, 250, 252, 0.8);
}

.availability-dot {
    width: 9px;
    height: 9px;
    flex: 0 0 9px;
    margin-top: 0.35rem;
    border-radius: 50%;
    background: currentColor;
}

.product-availability strong {
    display: block;
    margin-bottom: 0.15rem;
    font-size: 0.9rem;
}

.product-availability p {
    color: var(--text-secondary);
    font-size: 0.82rem;
}

.is-available {
    color: var(--success);
    background: rgba(22, 132, 91, 0.06);
    border-color: rgba(22, 132, 91, 0.2);
}

.is-unavailable {
    color: var(--danger);
    background: rgba(194, 65, 75, 0.06);
    border-color: rgba(194, 65, 75, 0.2);
}

/* Description */
.product-detail-description {
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}

.product-detail-description h2 {
    margin-bottom: 0.65rem;
    font-size: 1rem;
    font-weight: 750;
}

.product-detail-description p {
    margin-bottom: 0;
    color: var(--text-secondary);
    font-size: 0.92rem;
    line-height: 1.75;
}

/* Actions */
.product-detail-actions {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 0.75rem;
    margin-top: 1.5rem;
}

.product-detail-add-button {
    min-height: 52px;
    padding-inline: 1.5rem;
}

.product-detail-back-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 52px;
    border-color: var(--border);
    background: rgba(248, 250, 252, 0.7);
}

.product-detail-note {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 1rem;
    color: var(--text-secondary);
    font-size: 0.8rem;
}

.product-detail-note span {
    color: var(--success);
    font-weight: 800;
}

/* Loading and empty states */
.product-details-state {
    display: flex;
    min-height: 380px;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    border: 1px dashed var(--border);
    border-radius: var(--radius-lg);
    background: rgba(248, 250, 252, 0.72);
    color: var(--text-secondary);
    text-align: center;
}

.product-details-state h1 {
    margin-bottom: 0.5rem;
    font-size: 1.5rem;
}

.product-details-state p {
    margin-bottom: 1.25rem;
}

.details-state-icon {
    display: grid;
    width: 54px;
    height: 54px;
    place-items: center;
    margin-bottom: 1rem;
    border-radius: 16px;
    background: var(--brand-soft);
    color: var(--brand);
    font-size: 1.7rem;
    font-weight: 800;
}

/* Responsive */
@media (max-width: 767px) {
    .product-details-layout {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }

    .product-gallery-image {
        min-height: 300px;
    }

    .product-gallery-image img {
        height: 300px;
        padding: 1.5rem;
    }

    .product-detail-title {
        font-size: 1.8rem;
    }
}

@media (max-width: 480px) {
    .product-detail-actions {
        grid-template-columns: 1fr;
    }

    .product-detail-back-button {
        width: 100%;
    }
}
</style>