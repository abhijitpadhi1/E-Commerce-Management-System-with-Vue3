<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

const authStore = useAuthStore();
const router = useRouter();

const isMenuOpen = ref(false);

function closeMenu() {
    isMenuOpen.value = false;
}

function handleLogout() {
    authStore.logout();
    closeMenu();
    router.push('/');
}
</script>

<template>
    <!-- <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom shadow-sm"></nav> -->
    <nav class="navbar navbar-expand-lg navbar-light app-navbar sticky-top">
        <div class="container">
            <RouterLink :to="{ name: 'home' }" class="navbar-brand fw-bold text-primary" @click="closeMenu">
                Ecom
            </RouterLink>

            <button 
                class="navbar-toggler" 
                type="button"
                aria-label="Toggle navigation"
                :aria-expanded="isMenuOpen"
                @click="isMenuOpen = !isMenuOpen"
            >
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" :class="{ show: isMenuOpen }">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <RouterLink :to="{ name: 'home' }" class="nav-link" @click="closeMenu">
                            Home
                        </RouterLink>
                    </li>

                    <li v-if="authStore.isCustomer" class="nav-item">
                        <RouterLink :to="{ name: 'products' }" class="nav-link" @click="closeMenu">
                            Products
                        </RouterLink>
                    </li>
                    <li v-if="authStore.isAdmin" class="nav-item">
                        <RouterLink :to="{ name: 'admin-products' }" class="nav-link" @click="closeMenu">
                            Products
                        </RouterLink>
                    </li>

                    <!-- Customer-only navigation -->
                    <li v-if="authStore.isCustomer" class="nav-item">
                        <RouterLink :to="{ name: 'cart' }" class="nav-link" @click="closeMenu">
                            Cart
                        </RouterLink>
                    </li>
                    <li v-if="authStore.isCustomer" class="nav-item">
                        <RouterLink :to="{ name: 'orders' }" class="nav-link" @click="closeMenu">
                            Orders
                        </RouterLink>
                    </li>

                    <!-- Admin-only navigation; destinations will be implemented later -->
                    <li v-if="authStore.isAdmin" class="nav-item">
                        <RouterLink :to="{ name: 'admin-dashboard' }" class="nav-link" @click="closeMenu">
                            Dashboard
                        </RouterLink>
                    </li>
                    <li v-if="authStore.isAdmin" class="nav-item">
                        <RouterLink :to="{ name: 'admin-orders' }" class="nav-link" @click="closeMenu">
                            Manage Orders
                        </RouterLink>
                    </li>
                    <li v-if="authStore.isAdmin" class="nav-item">
                        <RouterLink :to="{ name: 'admin-inventory' }" class="nav-link" @click="closeMenu">
                            Inventory
                        </RouterLink>
                    </li>
                </ul>

                <div class="d-flex align-items-center gap-2">
                    <!-- Logged-out actions -->
                    <template v-if="!authStore.isAuthenticated">
                        <RouterLink :to="{ name: 'login' }" class="btn btn-outline-primary" @click="closeMenu">
                            Login
                        </RouterLink>

                        <RouterLink :to="{ name: 'signup' }" class="btn btn-primary" @click="closeMenu">
                            Sign Up
                        </RouterLink>
                    </template>

                    <!-- Logged-in actions -->
                    <template v-else>
                        <span class="text-secondary small">{{ authStore.user?.name }}</span>
                        <button class="btn btn-outline-danger" type="button" @click="handleLogout">
                            Logout
                        </button>
                    </template>
                </div>
            </div>
        </div>
    </nav>
</template>