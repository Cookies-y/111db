<template>
  <div class="dashboard-container">
    <el-card shadow="never" class="dashboard-card">
      <template #header>
        <div class="card-header">
          <span>仪表盘 - 课程列表</span>
          <div v-if="authStore.isAuthenticated && authStore.user?.user_type === 2" class="create-course-button-container">
            <router-link to="/create-course"> <!-- This route needs to be defined -->
                <el-button type="primary" :icon="Plus">创建新课程</el-button>
            </router-link>
          </div>
        </div>
      </template>

      <div v-if="authStore.isAuthenticated" class="content">
        <p class="welcome-message">
          欢迎回来, <strong>{{ authStore.user?.email || '用户' }}</strong>！
          <!-- (用户类型: {{ authStore.user?.user_type }}) -->
        </p>

        <div v-if="courseStore.isLoadingCourses" class="loading-container">
          <el-skeleton :rows="6" animated />
        </div>
        <el-alert
          v-else-if="courseStore.fetchCoursesError"
          :title="courseStore.fetchCoursesError"
          type="error"
          show-icon
          :closable="false"
          class="error-alert"
        />
        <el-empty
          v-else-if="!courseStore.allCourses || courseStore.allCourses.length === 0"
          description="暂无课程，教师可以创建新课程。"
          class="empty-courses"
        />
        <el-row :gutter="20" v-else class="course-list">
          <el-col
            :xs="24" :sm="12" :md="8"
            v-for="course in courseStore.allCourses"
            :key="course.course_id"
            class="course-col"
          >
            <el-card shadow="hover" class="course-card-item">
              <template #header>
                <div class="course-card-header">
                  <span>{{ course.course_name }}</span>
                </div>
              </template>
              <div class="course-cover-image-container">
                <el-image
                  v-if="course.cover_image"
                  :src="course.cover_image"
                  :alt="course.course_name"
                  fit="cover"
                  class="course-cover-image"
                >
                  <template #error><div class="image-slot">图片加载失败</div></template>
                </el-image>
                <div v-else class="course-cover-image-placeholder">暂无封面</div>
              </div>
              <div class="course-content-details">
                <p class="course-description" :title="course.description">
                  {{ course.description ? (course.description.length > 80 ? course.description.substring(0, 80) + '...' : course.description) : '暂无描述' }}
                </p>
                <p><strong>教师:</strong> {{ course.teacher?.real_name || 'N/A' }}</p>
                <p>
                  <strong>状态:</strong>
                  <el-tag :type="getStatusTagType(course.status)" size="small">{{ formatStatus(course.status) }}</el-tag>
                </p>
                <p><small>创建于: {{ new Date(course.create_time).toLocaleDateString() }}</small></p>
              </div>
              <template #footer>
                <div class="course-card-footer">
                  <router-link :to="`/courses/${course.course_id}`"> <!-- This route needs to be defined -->
                    <el-button type="primary" plain size="small">查看详情</el-button>
                  </router-link>
                </div>
              </template>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <div v-else class="content">
        <el-alert title="未授权访问" type="warning" description="您需要登录才能查看此页面。" show-icon :closable="false" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useAuthStore } from '../stores/authStore'; // Corrected path
import { useCourseStore } from '../stores/courseStore'; // Corrected path
import { ElCard, ElRow, ElCol, ElSkeleton, ElEmpty, ElButton, ElTag, ElAlert, ElImage } from 'element-plus';
import { Plus } from '@element-plus/icons-vue'; // For the create course button icon

const authStore = useAuthStore();
const courseStore = useCourseStore();

onMounted(() => {
  if (authStore.isAuthenticated) {
    courseStore.fetchCourses();
  }
});

const formatStatus = (status) => {
  const statuses = { 1: "未开始", 2: "进行中", 3: "已结束" };
  return statuses[status] || "未知状态";
};

const getStatusTagType = (status) => {
  const statusTypes = { 1: "info", 2: "success", 3: "warning" };
  return statusTypes[status] || "default";
};

// Placeholder for user_type in authStore.user.
// This computed property is an example of how it might be used if available.
// For now, the v-if for "Create Course" button directly checks authStore.user?.user_type === 2
const isTeacher = computed(() => {
  return authStore.isAuthenticated && authStore.user?.user_type === 2; // 2 for teacher
});

</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  background-color: #f9fafb;
}

.dashboard-card { /* This is the main outer card */
  max-width: 1200px; /* Allow wider content for course list */
  margin: 0 auto;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.5em;
  font-weight: 600;
  color: #303133;
}

.create-course-button-container {
  /* Styles for the container of the create course button if needed */
}

.content {
  padding-top: 10px;
}

.welcome-message {
  font-size: 1.1em;
  color: #333;
  margin-bottom: 20px;
}
.welcome-message strong {
  color: #409EFF;
}

.loading-container {
  padding: 20px;
}

.error-alert {
  margin-bottom: 20px;
}

.empty-courses {
  margin-top: 30px;
  margin-bottom: 30px;
}

.course-list {
  /* Styles for the row containing course cards */
}

.course-col {
  margin-bottom: 20px;
}

.course-card-item {
  height: 100%; /* Make cards in a row equal height if content varies */
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}
.course-card-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}


.course-card-header span {
  font-weight: bold;
  font-size: 1.1em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.course-cover-image-container {
  width: 100%;
  height: 150px; /* Fixed height for image container */
  background-color: #f5f7fa; /* Placeholder color */
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.course-cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover; /* Ensure image covers the area */
}
.course-cover-image-placeholder {
  color: #909399;
  font-size: 0.9em;
}
.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #c0c4cc;
}

.course-content-details {
  padding: 16px;
  flex-grow: 1; /* Allows this section to take available space */
}

.course-description {
  font-size: 0.9em;
  color: #606266;
  margin-bottom: 10px;
  height: 3.6em; /* Approx 2 lines with 1.8 line-height */
  line-height: 1.8;
  overflow: hidden;
  text-overflow: ellipsis;
  /* For multi-line ellipsis, more complex CSS might be needed or JS solution */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.course-content-details p {
  margin-bottom: 8px;
  font-size: 0.9em;
}
.course-content-details p strong {
  color: #303133;
}

.course-card-footer {
  padding: 10px 16px;
  border-top: 1px solid #ebeef5;
  text-align: right; /* Align button to the right */
}
</style>
