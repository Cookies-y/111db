<template>
  <div id="app-layout">
    <header class="app-header">
      <nav class="main-nav">
        <div class="nav-left">
          <router-link to="/" class="nav-brand">学通系统</router-link>
          <router-link to="/" class="nav-item">首页</router-link>
          <router-link v-if="authStore.isAuthenticated" to="/dashboard" class="nav-item">仪表盘</router-link>
          <!-- Add other common links like /courses if needed -->
        </div>
        <div class="nav-right">
          <span v-if="authStore.isAuthenticated" class="auth-links">
            <span class="user-greeting">
              欢迎, {{ authStore.user?.email || authStore.user?.username || '用户' }}
            </span>
            <a @click="handleLogout" href="#" class="nav-item logout-link">登出</a>
          </span>
          <span v-else class="auth-links">
            <router-link to="/login" class="nav-item">登录</router-link>
            <router-link to="/register" class="nav-item">注册</router-link>
          </span>
        </div>
      </nav>
    </header>

    <main class="app-main">
      <router-view v-slot="{ Component, route }">
        <transition name="fade" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>

    <footer class="app-footer">
      <p>&copy; {{ new Date().getFullYear() }} 学通系统 (XueTong System) MVP. 版权所有.</p>
    </footer>
  </div>
</template>

<script setup>
import { RouterView, useRouter } from 'vue-router';
import { useAuthStore } from './stores/authStore';

const authStore = useAuthStore();
const router = useRouter(); // Get router instance

function handleLogout() {
  authStore.logout();
  // The authStore.logout() action already navigates to '/login'
}
</script>

<style>
/* Global reset and base styles (consider moving to a separate global CSS file if it grows) */
body {
  margin: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  background-color: #f4f7f6; /* Light background for the whole page */
}

#app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background-color: #ffffff; /* Cleaner white header */
  color: #333;
  padding: 0 2rem; /* Use rem for spacing */
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  height: 60px; /* Fixed header height */
  display: flex;
  align-items: center;
}

.main-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: bold;
  color: #409EFF; /* Element Plus primary color for brand */
  text-decoration: none;
}

.nav-item {
  color: #333; /* Darker text for better contrast on white */
  margin: 0 0.75rem;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 0;
  border-bottom: 2px solid transparent;
  transition: color 0.2s ease, border-color 0.2s ease;
}

.nav-item:hover,
.nav-item.router-link-exact-active {
  color: #409EFF;
  border-bottom-color: #409EFF;
}

.logout-link {
  cursor: pointer; /* Indicate it's clickable */
}

.nav-left, .nav-right {
  display: flex;
  align-items: center;
}

.auth-links .nav-item {
  margin-left: 0.75rem;
}
.user-greeting {
  margin-right: 1rem;
  color: #555;
  font-size: 0.9rem;
}

.app-main {
  flex-grow: 1;
  padding: 1.5rem; /* Consistent padding */
  /* background-color: #fff; /* Optional: if content area should be white */
}

.app-footer {
  text-align: center;
  padding: 1rem;
  background-color: #303133; /* Darker footer */
  color: #ccc;
  font-size: 0.85rem;
  border-top: 1px solid #e0e0e0;
}

/* Router transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease; /* Faster transition */
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
