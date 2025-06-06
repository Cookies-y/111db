<template>
  <div class="admin-user-list-page">
    <el-breadcrumb separator-icon="ArrowRight" class="page-breadcrumb">
      <el-breadcrumb-item :to="{ name: 'AdminDashboard' }">管理首页</el-breadcrumb-item>
      <el-breadcrumb-item>用户管理</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="card-header">
          <span>系统用户列表</span>
          <!-- Optional: Add New User button here if functionality is added later -->
        </div>
      </template>

      <div v-if="isLoading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      <el-alert
        v-else-if="error"
        :title="`加载用户列表失败: ${error}`"
        type="error"
        show-icon
        :closable="false"
      />
      <el-table v-else :data="users" stripe style="width: 100%" class="users-table">
        <el-table-column prop="user_id" label="ID" sortable width="80" />
        <el-table-column prop="username" label="用户名" sortable width="180" />
        <el-table-column prop="real_name" label="真实姓名" sortable width="180" />
        <el-table-column prop="email" label="邮箱" sortable />
        <el-table-column prop="user_type" label="用户类型" width="120" align="center">
          <template #default="scope">
            <el-tag :type="getUserTypeTag(scope.row.user_type)" disable-transitions>
              {{ formatUserType(scope.row.user_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="register_time" label="注册时间" sortable width="200">
          <template #default="scope">{{ formatDate(scope.row.register_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="120" align="center">
          <template #default="scope">
            <router-link :to="{ name: 'AdminUserDetail', params: { user_id: scope.row.user_id } }">
              <el-button size="small" type="primary" :icon="View">查看详情</el-button>
            </router-link>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!isLoading && !error && (!users || users.length === 0)" description="暂无用户数据" />
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useAdminStore } from '../../stores/adminStore'; // Corrected path
import { ElTable, ElTableColumn, ElButton, ElTag, ElCard, ElSkeleton, ElAlert, ElEmpty, ElBreadcrumb, ElBreadcrumbItem, ElIcon } from 'element-plus';
import { View, ArrowRight } from '@element-plus/icons-vue';

const adminStore = useAdminStore();

const users = computed(() => adminStore.allUsers);
const isLoading = computed(() => adminStore.isLoadingUsers);
const error = computed(() => adminStore.fetchUsersError);

onMounted(() => {
  adminStore.fetchAllUsers();
});

function formatUserType(type) {
  const types = { 1: '学生', 2: '教师', 3: '管理员' };
  return types[type] || '未知类型';
}

function getUserTypeTag(type) {
  const tags = { 1: 'info', 2: 'success', 3: 'warning' };
  return tags[type] || 'default';
}

function formatDate(dateTimeString) {
  if (!dateTimeString) return 'N/A';
  return new Date(dateTimeString).toLocaleString('zh-CN', { dateStyle: 'medium', timeStyle: 'short' });
}
</script>

<style scoped>
.admin-user-list-page {
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
.loading-container {
  padding: 20px;
}
.users-table {
  margin-top: 15px;
}
.el-table th.el-table__cell {
  background-color: #f5f7fa !important; /* Element Plus specific for header */
}
</style>
