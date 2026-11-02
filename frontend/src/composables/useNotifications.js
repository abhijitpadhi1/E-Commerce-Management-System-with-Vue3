import { ref } from 'vue';

// Shared state: one notification for the whole application
const message = ref('');
const type = ref('success');

let timer = null;

export function useNotification() {
    function notify(newMessage, newType = 'success', duration = 5000) {
        message.value = newMessage;
        type.value = newType;
        clearTimeout(timer);
        timer = setTimeout(() => {
            message.value = '';
        }, duration);
    }

    function clearNotification() {
        clearTimeout(timer);
        message.value = '';
    }

    return { message, type, notify, clearNotification };
}