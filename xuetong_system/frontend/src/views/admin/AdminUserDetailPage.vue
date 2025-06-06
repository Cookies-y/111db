<template>
  <div class="admin-user-detail-page">
    <el-breadcrumb separator-icon="ArrowRight" class="page-breadcrumb">
      <el-breadcrumb-item :to="{ name: 'AdminDashboard' }">管理首页</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ name: 'AdminUserList' }">用户管理</el-breadcrumb-item>
      <el-breadcrumb-item>用户详情: {{ userDetail?.username || userId }}</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="card-header">
          <span>用户详细信息</span>
          <!-- Optional: Edit User button here if functionality is added later -->
        </div>
      </template>

      <div v-if="isLoading && !userDetail" class="loading-container">
        <el-skeleton :rows="8" animated />
      </div>
      <el-alert
        v-else-if="error && !userDetail"
        :title="`加载用户详情失败: ${error}`"
        type="error"
        show-icon
        :closable="false"
      />
      <div v-else-if="!userDetail" class="empty-container">
        <el-empty description="未找到该用户信息或已被删除。" />
        <router-link :to="{ name: 'AdminUserList' }">
            <el-button type="primary">返回用户列表</el-button>
        </router-link>
      </div>

      <el-descriptions v-else :column="2" border class="user-details-descriptions">
        <el-descriptions-item label="用户 ID">{{ userDetail.user_id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ userDetail.username }}</el-descriptions-item>
        <el-descriptions-item label="真实姓名">{{ userDetail.real_name }}</el-descriptions-item>
        <el-descriptions-item label="邮箱地址">{{ userDetail.email }}</el-descriptions-item>
        <el-descriptions-item label="电话号码">{{ userDetail.phone || '未提供' }}</el-descriptions-item>
        <el-descriptions-item label="用户类型">
          <el-tag :type="getUserTypeTag(userDetail.user_type)" disable-transitions>
            {{ formatUserType(userDetail.user_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ formatDate(userDetail.register_time) }}</el-descriptions-item>
        <el-descriptions-item label="最后登录">{{ userDetail.last_login ? formatDate(userDetail.last_login) : '从未登录' }}</el-descriptions-item>
      </el-descriptions>

      <!-- Future sections for user's courses, activity, etc. -->

    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useAdminStore } from '../../stores/adminStore'; // Corrected path
import {
    ElCard, ElDescriptions, ElDescriptionsItem, ElTag, ElSkeleton,
    ElAlert, ElEmpty, ElBreadcrumb, ElBreadcrumbItem, ElButton, ElIcon
} from 'element-plus';
import { ArrowRight } from '@element-plus/icons-vue';

const route = useRoute();
const adminStore = useAdminStore();

// Using ref for userId to ensure reactivity if route changes in a way that keeps component alive (though less common here)
const userId = ref(route.params.user_id ? parseInt(route.params.user_id) : null);

const userDetail = computed(() => adminStore.getUserDetail);
const isLoading = computed(() => adminStore.isLoadingUserDetail);
const error = computed(() => adminStore.fetchUserDetailError);

const fetchData = async (id) => {
  if (id) {
    await adminStore.fetchUserDetail(id);
  }
};

onMounted(() => {
  fetchData(userId.value);
});

onUnmounted(() => {
  adminStore.clearUserDetail(); // Clear specific user detail when leaving page
});

// Watch for route parameter changes
watch(() => route.params.user_id, (newIdStr) => {
  const newId = newIdStr ? parseInt(newIdStr) : null;
  if (newId && newId !== userId.value) {
    userId.value = newId;
    fetchData(newId);
  } else if (!newId && userId.value) { // Navigated away or param removed
    userId.value = null;
    adminStore.clearUserDetail();
  }
});

function formatUserType(type) {
  const types = { 1: '学生', 2: '教师', 3: '管理员' };
  return types[type] || '未知类型';
}

function getUserTypeTag(type) {
  const tags = { 1: 'info', 2: 'success', 3: 'warning' }; // Using 'warning' for Admin
  return tags[type] || 'default';
}

function formatDate(dateTimeString) {
  if (!dateTimeString) return 'N/A';
  return new Date(dateTimeString).toLocaleString('zh-CN', { dateStyle: 'medium', timeStyle: 'short' });
}
</script>

<style scoped>
.admin-user-detail-page {
  padding: 0; /* Let card handle padding */
}
.page-breadcrumb {
  margin-bottom: 20px;
}
.page-card {
  border-radius: 8px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header span {
  font-size: 1.2em;
  font-weight: bold;
}
.loading-container, .empty-container {
  padding: 20px;
  text-align: center;
}
.user-details-descriptions {
  margin-top: 15px;
}
.el-descriptions-item__label {
  font-weight: bold !important; /* Make labels in description bold */
}
</style>
