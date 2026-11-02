<script setup>
import AppNavbar from './components/AppNavbar.vue';
import AppNotification from './components/AppNotification.vue';
</script>

<template>
  <div class="app-layout">
    <AppNavbar />
    <main>
      <AppNotification />
      <RouterView />
    </main>
  </div>
</template>