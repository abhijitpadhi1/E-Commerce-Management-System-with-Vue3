<script setup></script>

<template>
    <div>
        <!-- Hero Section -->
        <section class="bg-light">
            <div class="container py-5">
                <div class="row align-items-center py-lg-5">
                    <div class="col-lg-6">
                        <span class="badge bg-primary-subtle text-primary mb-3">
                            Welcome to Ecom
                        </span>

                        <h1 class="display-4 fw-bold mb-3">
                            Everything you need,
                            <span class="text-primary">all in one place.</span>
                        </h1>

                        <p class="lead text-secondary mb-4">
                            Discover quality products, enjoy a simple shopping experience, and keep track of your orders with ease.
                        </p>

                        <div class="d-flex flex-wrap gap-3">
                            <RouterLink :to="{ name: 'products' }" class="btn btn-primary btn-lg">
                                Browse Products
                            </RouterLink>

                            <RouterLink :to="{ name: 'signup' }" class="btn btn-outline-primary btn-lg">
                                Create Account
                            </RouterLink>
                        </div>
                    </div>

                    <div class="col-lg-6 mt-5 mt-lg-0">
                        <div class="hero-visual rounded-4 d-flex align-items-center justify-content-center">
                            <div class="text-center text-white p-4">
                                <div class="display-1 mb-3">🛍️</div>
                                <h2 class="h3 fw-semibold">Your next favourite find</h2>
                                <p class="mb-0"> A simple and convenient way to shop. </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Features Section -->
        <section class="container py-5">
            <div class="text-center mb-5">
                <h2 class="fw-bold">A better way to shop</h2>
                <p class="text-secondary"> Designed to make your shopping experience simple and convenient. </p>
            </div>

            <div class="row g-4">
                <div class="col-md-4">
                    <div class="card h-100 border-0 shadow-sm">
                        <div class="card-body text-center p-4">
                            <div class="feature-icon mb-3">🔎</div>
                            <h3 class="h5 fw-semibold">Explore Products</h3>
                            <p class="text-secondary mb-0">
                                Browse our catalogue and discover products that match your needs.
                            </p>
                        </div>
                    </div>
                </div>

                <div class="col-md-4">
                    <div class="card h-100 border-0 shadow-sm">
                        <div class="card-body text-center p-4">
                            <div class="feature-icon mb-3">🛒</div>
                            <h3 class="h5 fw-semibold">Easy Shopping</h3>
                            <p class="text-secondary mb-0">
                                Add products to your cart and manage your selections in one place.
                            </p>
                        </div>
                    </div>
                </div>

                <div class="col-md-4">
                    <div class="card h-100 border-0 shadow-sm">
                        <div class="card-body text-center p-4">
                            <div class="feature-icon mb-3">📦</div>
                            <h3 class="h5 fw-semibold">Track Your Orders</h3>
                            <p class="text-secondary mb-0">
                                Keep track of your purchases and follow their progress.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Call to Action -->
        <section class="bg-primary text-white">
            <div class="container py-5 text-center">
                <h2 class="fw-bold mb-3">Ready to start shopping?</h2>
                <p class="lead mb-4"> Explore the catalogue and find something you'll love. </p>
                <RouterLink :to="{ name: 'products' }" class="btn btn-light btn-lg">
                    Explore Products
                </RouterLink>
            </div>
        </section>
    </div>
</template>

<style scoped>
.hero-visual {
    min-height: 350px;
    background: linear-gradient(135deg, #0d6efd, #6610f2);
}

.feature-icon {
    font-size: 2.5rem;
}
</style>