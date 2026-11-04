<script setup>
import { useNotification } from '@/composables/useNotifications';

const { message, type, clearNotification } = useNotification();

const notificationClass = {
    success: 'notification-success',
    danger: 'notification-danger',
    warning: 'notification-warning',
    info: 'notification-info',
};

const notificationIcon = {
    success: '✓',
    danger: '!',
    warning: '⚠',
    info: 'i',
};
</script>

<template>
    <Transition name="toast">
        <div
            v-if="message"
            class="notification-toast"
            :class="notificationClass[type] || 'notification-info'"
            role="alert"
            aria-live="polite"
        >
            <div class="notification-icon" aria-hidden="true">
                {{ notificationIcon[type] || 'i' }}
            </div>

            <div class="notification-content">
                <div class="notification-title">
                    {{
                        type === 'success'
                            ? 'Success'
                            : type === 'danger'
                              ? 'Something went wrong'
                              : type === 'warning'
                                ? 'Attention'
                                : 'Notice'
                    }}
                </div>

                <p class="notification-message">{{ message }}</p>
            </div>

            <button
                type="button"
                class="notification-close"
                aria-label="Dismiss notification"
                @click="clearNotification"
            >
                ×
            </button>
        </div>
    </Transition>
</template>

<style scoped>
.notification-toast {
    position: fixed;
    top: 82px;
    right: 24px;
    z-index: 1100;

    display: flex;
    align-items: flex-start;
    gap: 0.85rem;

    width: min(420px, calc(100vw - 32px));
    padding: 1rem 1rem 1rem 1.05rem;

    border: 1px solid var(--border);
    border-radius: 14px;

    background: var(--surface, rgba(30, 35, 45, 0.96));
    color: var(--text-primary);

    box-shadow: var(--shadow-md, 0 12px 35px rgba(0, 0, 0, 0.18));
    backdrop-filter: blur(14px);
}

.notification-icon {
    display: grid;
    flex: 0 0 30px;
    width: 30px;
    height: 30px;
    place-items: center;

    border-radius: 9px;
    font-size: 0.9rem;
    font-weight: 800;
}

.notification-content {
    flex: 1;
    min-width: 0;
    padding-top: 0.05rem;
}

.notification-title {
    margin-bottom: 0.2rem;
    font-size: 0.82rem;
    font-weight: 750;
}

.notification-message {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.82rem;
    line-height: 1.5;
    overflow-wrap: anywhere;
}

.notification-close {
    display: grid;
    flex: 0 0 26px;
    width: 26px;
    height: 26px;
    place-items: center;

    border: 0;
    border-radius: 7px;
    background: transparent;
    color: var(--text-secondary);

    font-size: 1.35rem;
    line-height: 1;
    cursor: pointer;
}

.notification-close:hover {
    background: var(--brand-soft);
    color: var(--text-primary);
}

/* Success */
.notification-success {
    border-left: 3px solid var(--success, #22c55e);
}

.notification-success .notification-icon {
    background: rgba(34, 197, 94, 0.13);
    color: var(--success, #22c55e);
}

/* Error */
.notification-danger {
    border-left: 3px solid var(--danger, #ef4444);
}

.notification-danger .notification-icon {
    background: rgba(239, 68, 68, 0.13);
    color: var(--danger, #ef4444);
}

/* Warning */
.notification-warning {
    border-left: 3px solid var(--warning, #eab308);
}

.notification-warning .notification-icon {
    background: rgba(234, 179, 8, 0.13);
    color: var(--warning, #eab308);
}

/* Information */
.notification-info {
    border-left: 3px solid var(--brand);
}

.notification-info .notification-icon {
    background: var(--brand-soft);
    color: var(--brand);
}

/* Enter and leave animation */
.toast-enter-active,
.toast-leave-active {
    transition:
        opacity 0.25s ease,
        transform 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
    opacity: 0;
    transform: translateX(24px);
}

@media (max-width: 480px) {
    .notification-toast {
        top: 72px;
        right: 16px;
        width: calc(100vw - 32px);
        padding: 0.85rem;
    }
}
</style>