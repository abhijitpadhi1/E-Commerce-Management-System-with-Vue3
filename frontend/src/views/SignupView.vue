<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { signup } from '@/services/authService';
import { useNotification } from '@/composables/useNotifications';

const router = useRouter();
const { notify } = useNotification();

const form = reactive({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
});

const loading = ref(false);

async function handleSignup() {
    if (!form.name.trim() || !form.email.trim() || !form.password || !form.confirmPassword) {
        notify('Please fill in all fields.', 'warning');
        return;
    }
    if (form.password.length < 8) {
        notify('Password must contain at least 8 characters.', 'warning');
        return;
    }
    if (form.password !== form.confirmPassword) {
        notify('Passwords do not match.', 'warning');
        return;
    }

    loading.value = true;
    try {
        await signup({
            name: form.name.trim(),
            email: form.email.trim().toLowerCase(),
            password: form.password,
        });
        notify('Account created successfully. Redirecting to login...', 'success');
        setTimeout(() => {
            router.push('/login');
        }, 1200);
    } catch (error) {
        notify('Unable to create your account.Please try again.', 'danger');
    } finally {
        loading.value = false;
    }
}
</script>

<template>
    <section class="signup-page py-5">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-12 col-sm-10 col-md-7 col-lg-5">
                    <div class="card border-0 shadow-sm">
                        <div class="card-body p-4 p-md-5">
                            <div class="text-center mb-4">
                                <h1 class="h3 fw-bold">Create your account</h1>
                                <p class="text-secondary mb-0">Join us and start exploring products.</p>
                            </div>

                            <form @submit.prevent="handleSignup">
                                <div class="mb-3">
                                    <label for="name" class="form-label">Full name</label>
                                    <input
                                        id="name"
                                        v-model="form.name"
                                        type="text"
                                        class="form-control"
                                        placeholder="Enter your name"
                                        autocomplete="name"
                                        required
                                    />
                                </div>

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

                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <input
                                        id="password"
                                        v-model="form.password"
                                        type="password"
                                        class="form-control"
                                        placeholder="At least 8 characters"
                                        autocomplete="new-password"
                                        minlength="8"
                                        required
                                    />
                                </div>

                                <div class="mb-4">
                                    <label for="confirmPassword" class="form-label">Confirm password</label>
                                    <input
                                        id="confirmPassword"
                                        v-model="form.confirmPassword"
                                        type="password"
                                        class="form-control"
                                        placeholder="Enter your password again"
                                        autocomplete="new-password"
                                        required
                                    />
                                </div>

                                <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                                    <span v-if="loading" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
                                    {{ loading ? 'Creating account...' : 'Create account' }}
                                </button>
                            </form>

                            <p class="text-center text-secondary mt-4 mb-0">
                                Already have an account?
                                <RouterLink :to="{ name: 'login' }" class="text-decoration-none fw-semibold">
                                    Login
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
.signup-page {
  min-height: 75vh;
  background: #f8f9fa;
}
</style>