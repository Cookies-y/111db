<template>
  <div class="admin-course-list-page">
    <el-breadcrumb separator-icon="ArrowRight" class="page-breadcrumb">
      <el-breadcrumb-item :to="{ name: 'AdminDashboard' }">管理首页</el-breadcrumb-item>
      <el-breadcrumb-item>课程管理</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="card-header">
          <span>系统课程列表</span>
          <!-- Optional: Global Create Course button for Admin if functionality differs from teacher's -->
        </div>
      </template>

      <div v-if="isLoading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      <el-alert
        v-else-if="error"
        :title="`加载课程列表失败: ${error}`"
        type="error"
        show-icon
        :closable="false"
      />
      <el-table v-else :data="courses" stripe style="width: 100%" class="courses-table">
        <el-table-column prop="course_id" label="ID" sortable width="80" />
        <el-table-column prop="course_name" label="课程名称" sortable />
        <el-table-column label="授课教师" width="180" sortable prop="teacher.real_name">
           <template #default="scope">{{ scope.row.teacher?.real_name || 'N/A' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="scope">
            <el-tag :type="getCourseStatusTag(scope.row.status)" disable-transitions>
              {{ formatCourseStatus(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" sortable width="200">
          <template #default="scope">{{ formatDate(scope.row.create_time) }}</template>
        </el-table-column>
         <el-table-column prop="start_date" label="开始日期" sortable width="150">
          <template #default="scope">{{ formatDateSimple(scope.row.start_date) }}</template>
        </el-table-column>
        <el-table-column prop="end_date" label="结束日期" sortable width="150">
          <template #default="scope">{{ formatDateSimple(scope.row.end_date) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="120" align="center">
          <template #default="scope">
            <router-link :to="{ name: 'AdminCourseDetail', params: { course_id: scope.row.course_id } }">
              <el-button size="small" type="primary" :icon="View">查看详情</el-button>
            </router-link>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!isLoading && !error && (!courses || courses.length === 0)" description="暂无课程数据" />
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useAdminStore } from '../../../stores/adminStore'; // Adjusted path
import { ElTable, ElTableColumn, ElButton, ElTag, ElCard, ElSkeleton, ElAlert, ElEmpty, ElBreadcrumb, ElBreadcrumbItem, ElIcon } from 'element-plus';
import { View, ArrowRight } from '@element-plus/icons-vue';

const adminStore = useAdminStore();

const courses = computed(() => adminStore.allAdminCourses);
const isLoading = computed(() => adminStore.isLoadingAdminCourses);
const error = computed(() => adminStore.fetchAdminCoursesError);

onMounted(() => {
  adminStore.fetchAllAdminCourses();
});

function formatCourseStatus(status) {
  const statuses = { 1: '未开始', 2: '进行中', 3: '已结束' };
  return statuses[status] || '未知状态';
}

function getCourseStatusTag(status) {
  const tags = { 1: 'info', 2: 'success', 3: 'warning' }; // Warning for 'Ended' might be better than 'danger'
  return tags[status] || 'default';
}

function formatDate(dateTimeString) {
  if (!dateTimeString) return 'N/A';
  return new Date(dateTimeString).toLocaleString('zh-CN', { dateStyle: 'medium', timeStyle: 'short' });
}
function formatDateSimple(dateString) {
  if (!dateString) return 'N/A';
  return new Date(dateString + 'T00:00:00').toLocaleDateString('zh-CN', { dateStyle: 'medium' });
}
</script>

<style scoped>
.admin-course-list-page {
  padding: 0;
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
.courses-table {
  margin-top: 15px;
}
.el-table th.el-table__cell {
  background-color: #f5f7fa !important;
}
</style>
