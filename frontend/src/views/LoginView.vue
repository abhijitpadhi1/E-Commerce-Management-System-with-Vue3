<script setup>
import { reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useNotification } from '@/composables/useNotifications';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { notify } = useNotification();

const form = reactive({
    email: '',
    password: '',
});

const loading = ref(false);

async function handleLogin() {
    if (!form.email.trim() || !form.password) {
        notify('Please enter your email and password.', 'warning');
        return;
    }
    loading.value = true;
    try {
        const user = await authStore.login({
            email: form.email.trim().toLowerCase(),
            password: form.password,
        });

        const requestedRedirect = route.query.redirect;
        if (typeof requestedRedirect === 'string' && requestedRedirect.startsWith('/')) {
            router.push(requestedRedirect);
        } else if (user.role === 'ADMIN') {
            router.push('/admin');
        } else {
            router.push('/products');
        }
    } catch (error) {
        const errorMsg = error.response?.data?.message || error.message || 'Login failed. Please check your credentials and try again.';
        notify(errorMsg, 'danger');
    } finally {
        loading.value = false;
    }
}
</script>

<template>
    <section class="login-page py-5">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-12 col-sm-10 col-md-7 col-lg-5">
                    <div class="card border-0 shadow-sm">
                        <div class="card-body p-4 p-md-5">
                            <div class="text-center mb-4">
                                <h1 class="h3 fw-bold">Welcome back</h1>
                                <p class="text-secondary mb-0">Login to continue shopping.</p>
                            </div>

                            <form @submit.prevent="handleLogin">
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email address</label>
                                    <input
                                        id="email"
                                        v-model="form.email"
                                        type="email"
                                        class="form-control"
                                        placeholder="you@example.com"
                                        autocomplete="email"
                                        required
                                    />
                                </div>

                                <div class="mb-4">
                                    <label for="password" class="form-label">Password</label>
                                    <input
                                        id="password"
                                        v-model="form.password"
                                        type="password"
                                        class="form-control"
                                        placeholder="Enter your password"
                                        autocomplete="current-password"
                                        required
                                    />
                                </div>

                                <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                                    <span v-if="loading" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
                                    {{ loading ? 'Logging in...' : 'Login' }}
                                </button>
                            </form>

                            <p class="text-center text-secondary mt-4 mb-0">
                                Don't have an account?
                                <RouterLink :to="{ name: 'signup' }" class="text-decoration-none fw-semibold">
                                    Sign up
                                </RouterLink>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
.login-page {
    min-height: 75vh;
    background: #f8f9fa;
}
</style>