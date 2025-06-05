<template>
  <div id="app-layout">
    <header class="app-header">
      <nav class="main-nav">
        <div class="nav-left">
          <router-link to="/" class="nav-brand">学通系统</router-link>
          <router-link to="/" class="nav-item">首页</router-link>
          <router-link v-if="authStore.isAuthenticated && !authStore.isAdmin" to="/dashboard" class="nav-item">仪表盘</router-link>
          <!-- Admin link -->
          <router-link v-if="authStore.isAdmin" to="/admin/dashboard" class="nav-item admin-link">
            <el-icon style="vertical-align: middle; margin-right: 4px;"><Setting /></el-icon>管理后台
          </router-link>
        </div>
        <div class="nav-right">
          <span v-if="authStore.isAuthenticated" class="auth-links">
            <span class="user-greeting">
              欢迎, {{ authStore.user?.real_name || authStore.user?.email || authStore.user?.username || '用户' }}
              <el-tag size="small" type="info" style="margin-left: 5px;">{{ userRoleDisplay }}</el-tag>
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
import { computed } from 'vue'; // Import computed
import { RouterView, useRouter } from 'vue-router';
import { useAuthStore } from './stores/authStore';
import { ElTag, ElIcon } from 'element-plus'; // Import ElTag and ElIcon
import { Setting } from '@element-plus/icons-vue'; // Import Setting icon

const authStore = useAuthStore();
const router = useRouter();

const userRoleDisplay = computed(() => {
  if (!authStore.user || authStore.user.user_type === null || authStore.user.user_type === undefined) return '未知';
  switch (authStore.user.user_type) {
    case 1: return '学生';
    case 2: return '教师';
    case 3: return '管理员';
    default: return '未知角色';
  }
});

function handleLogout() {
  authStore.logout();
}
</script>

<style>
/* Global reset and base styles */
body {
  margin: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  background-color: #f4f7f6;
}

#app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background-color: #ffffff;
  color: #333;
  padding: 0 2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  height: 60px;
  display: flex;
  align-items: center;
  position: sticky; /* Make header sticky */
  top: 0;
  z-index: 1000; /* Ensure header is above other content */
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
  color: #409EFF;
  text-decoration: none;
}

.nav-item {
  color: #333;
  margin: 0 0.75rem;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 0;
  border-bottom: 2px solid transparent;
  transition: color 0.2s ease, border-color 0.2s ease;
  display: inline-flex; /* For icon alignment */
  align-items: center;
}
.admin-link .el-icon {
  margin-right: 4px;
}

.nav-item:hover,
.nav-item.router-link-exact-active {
  color: #409EFF;
  border-bottom-color: #409EFF;
}

.logout-link {
  cursor: pointer;
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
  display: flex; /* For ElTag alignment */
  align-items: center;
}

.app-main {
  flex-grow: 1;
  padding: 1.5rem;
}

.app-footer {
  text-align: center;
  padding: 1rem;
  background-color: #303133;
  color: #ccc;
  font-size: 0.85rem;
  border-top: 1px solid #e0e0e0;
}

/* Router transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
