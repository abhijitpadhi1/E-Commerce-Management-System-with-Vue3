import { createRouter, createWebHistory } from 'vue-router';

import { useAuthStore } from '@/stores/authStore';

import HomePage from '@/views/HomePage.vue';
import ProductCatalogueView from '@/views/ProductCatalogueView.vue';
import ProductDetails from '@/views/ProductDetails.vue';
import CartView from '@/views/CartView.vue';
import SignupView from '@/views/SignupView.vue';
import LoginView from '@/views/LoginView.vue';
import CheckoutView from '@/views/CheckoutView.vue';
import OrderConformationView from '@/views/OrderConformationView.vue';
import OrdersView from '@/views/OrdersView.vue';
import AdminOrderView from '@/views/AdminOrderView.vue';
import AdminInventryVue from '@/views/AdminInventryVue.vue';
import AdminDashboardView from '@/views/AdminDashboardView.vue';
import AdminProductsView from '@/views/AdminProductsView.vue';

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{ path: '/', name: 'home', component: HomePage },
		{ path: '/signup', name: 'signup', component: SignupView },
		{ path: '/login', name: 'login', component: LoginView },
		{ path: '/products', name: 'products', component: ProductCatalogueView },
		{ path: '/product/:id', name: 'product-details', component: ProductDetails },
		{
			path: '/cart',
			name: 'cart',
			component: CartView,
			meta: { requiresAuth: true, role: 'CUSTOMER' },
		},
		{
			path: '/orders',
			name: 'orders',
			component: OrdersView,
			meta: { requiresAuth: true, role: 'CUSTOMER' },
		},
		{
			path: '/orders/:orderId',
			name: 'order-confirmation',
			component: OrderConformationView,
			meta: { requiresAuth: true, role: 'CUSTOMER' },
		},
		{
			path: '/checkout',
			name: 'checkout',
			component: CheckoutView,
			meta: { requiresAuth: true, role: 'CUSTOMER' },
		},
		{
			path: '/admin',
			name: 'admin-dashboard',
			component: AdminDashboardView,
			meta: { requiresAuth: true, role: 'ADMIN' },
		},
		{
			path: '/admin/orders',
			name: 'admin-orders',
			component: AdminOrderView,
			meta: { requiresAuth: true, role: 'ADMIN' },
		},
		{
			path: '/admin/products',
			name: 'admin-products',
			component: AdminProductsView,
			meta: { requiresAuth: true, role: 'ADMIN' },
		},
		{
			path: '/admin/inventory',
			name: 'admin-inventory',
			component: AdminInventryVue,
			meta: { requiresAuth: true, role: 'ADMIN' },
		},
		{ path: '/:catchAll(.*)', redirect: '/' },
	],
});

router.beforeEach(async (to) => {
	const authStore = useAuthStore();

	// Restore the user from a saved token after page refresh
	if (localStorage.getItem('access_token') && !authStore.user) {
		await authStore.fetchCurrentUser();
	}

	if (to.meta.requiresAuth && !authStore.isAuthenticated) {
		return {
			name: 'login',
			query: { redirect: to.fullPath },
		};
	}

	if (to.meta.role && authStore.user?.role !== to.meta.role) {
		return { name: 'home' };
	}
});

export default router;
