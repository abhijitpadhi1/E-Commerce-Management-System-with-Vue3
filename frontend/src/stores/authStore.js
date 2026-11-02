import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { login as loginRequest, getCurrentUser } from '@/services/authService';

export const useAuthStore = defineStore('auth', () => {
    // states
    const user = ref(null);
    const token = ref(localStorage.getItem('access_token') || '');
    const loading = ref(false);

    // getters
    const isAuthenticated = computed(() => Boolean(token.value && user.value));
    const isCustomer = computed(() => user.value?.role === 'CUSTOMER');
    const isAdmin = computed(() => user.value?.role === 'ADMIN');

    // actions
    async function login(credentials) {
        loading.value = true;
        try {
            const response = await loginRequest(credentials);
            if (!response.access_token) {
                throw new Error('Login response did not contain an access token.');
            }

            token.value = response.access_token;
            localStorage.setItem('access_token', token.value);

            const profileResponse = await getCurrentUser();
            user.value = profileResponse.user;

            return user.value;
        } catch (error) {
            logout();
            throw error;
        } finally {
            loading.value = false;
        }
    }

    async function fetchCurrentUser() {
        const savedToken = localStorage.getItem('access_token');
        if (!savedToken) {
            logout();
            return null;
        }

        token.value = savedToken;
        try {
            const response = await getCurrentUser();
            user.value = response.user;
            return user.value;
        } catch (error) {
            logout();
            return null;
        }
    }

    function logout() {
        user.value = null;
        token.value = '';
        localStorage.removeItem('access_token');
    }

    return {
        user, token, loading,
        isAuthenticated, isCustomer, isAdmin,
        login, fetchCurrentUser, logout,
    };
});