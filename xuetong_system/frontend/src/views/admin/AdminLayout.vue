<template>
  <div class="admin-layout">
    <el-container style="height: 100vh;">
      <el-aside width="220px" class="admin-sidebar">
        <div class="admin-sidebar-header">
          <router-link to="/" class="admin-brand-link">
            <el-icon :size="24" style="margin-right: 8px;"><School /></el-icon>
            <span>学通后台管理</span>
          </router-link>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="admin-menu"
          router
          style="height: calc(100% - 60px);"
        >
          <el-menu-item index="/admin/dashboard">
            <el-icon><Platform /></el-icon>
            <span>管理首页</span>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><UserFilled /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/courses">
            <el-icon><Collection /></el-icon>
            <span>课程管理</span>
          </el-menu-item>
          <!-- Add more admin sections later, e.g., system settings, analytics -->
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="admin-main-header">
          <div>
            <!-- Breadcrumbs or other header content can go here -->
            <span style="font-weight: bold;">管理后台</span>
          </div>
          <div>
            <el-dropdown>
              <span class="el-dropdown-link">
                {{ authStore.user?.real_name || authStore.user?.username || '管理员' }}
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="goToHome">返回主站</el-dropdown-item>
                  <el-dropdown-item @click="handleLogout" divided>登出</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        <el-main class="admin-main-content">
          <router-view v-slot="{ Component, route }">
            <transition name="fade-admin" mode="out-in">
              <component :is="Component" :key="route.path" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter, RouterView } from 'vue-router'; // RouterView needs to be imported
import { useAuthStore } from '../../../stores/authStore'; // Adjusted path
import {
    ElContainer, ElAside, ElMenu, ElMenuItem, ElIcon, ElMain, ElHeader,
    ElDropdown, ElDropdownMenu, ElDropdownItem
} from 'element-plus';
import { Platform, UserFilled, Collection, School, ArrowDown } from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const activeMenu = computed(() => {
    // Ensure activeMenu highlights parent path if on a sub-route not directly in menu
    if (route.path.startsWith('/admin/users')) return '/admin/users';
    if (route.path.startsWith('/admin/courses')) return '/admin/courses';
    return route.path; // Default for /admin/dashboard etc.
});

function handleLogout() {
  authStore.logout(); // This will also navigate to /login
}

function goToHome() {
    router.push('/');
}
</script>

<style scoped>
.admin-layout {
  height: 100%;
  width: 100%;
}
.admin-sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #001529; /* Dark theme for sidebar header */
}
.admin-brand-link {
  color: white;
  text-decoration: none;
  font-size: 1.1em;
  display: flex;
  align-items: center;
}
.admin-sidebar {
  background-color: #001529; /* Dark theme for sidebar */
  color: #fff;
  border-right: none; /* Remove default border if using dark theme */
}
.admin-menu {
  border-right: none; /* Remove default border from ElMenu */
  background-color: #001529;
}
.admin-menu .el-menu-item {
  color: #a6adb4; /* Light text for menu items */
}
.admin-menu .el-menu-item:hover {
  background-color: #000c17; /* Darker hover for items */
}
.admin-menu .el-menu-item.is-active {
  color: #fff;
  background-color: #1890ff; /* Element Plus primary, or your admin theme color */
}
.admin-menu .el-icon {
  color: inherit; /* Icons inherit color from menu item */
}

.admin-main-header {
  background-color: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}
.el-dropdown-link {
  cursor: pointer;
  color: #333;
  display: flex;
  align-items: center;
}

.admin-main-content {
  padding: 20px;
  background-color: #f0f2f5; /* Light grey background for content area */
  height: calc(100vh - 60px); /* Full height minus header */
  overflow-y: auto;
}

/* Router transition */
.fade-admin-enter-active, .fade-admin-leave-active {
  transition: opacity 0.15s ease;
}
.fade-admin-enter-from, .fade-admin-leave-to {
  opacity: 0;
}
</style>
