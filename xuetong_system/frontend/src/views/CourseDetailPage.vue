<template>
  <div class="course-detail-container">
    <div v-if="courseStore.isLoadingCourseDetail" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    <el-alert
      v-else-if="courseStore.fetchCourseDetailError"
      :title="courseStore.fetchCourseDetailError"
      type="error"
      description="无法加载课程详情，请稍后再试或返回课程列表。"
      show-icon
      :closable="false"
      class="error-alert"
    />
    <div v-else-if="!courseStore.currentCourseDetail" class="empty-container">
      <el-empty description="未找到课程或课程信息为空。" />
      <router-link to="/dashboard"><el-button type="primary">返回仪表盘</el-button></router-link>
    </div>

    <div v-else class="course-content-wrapper">
      <el-breadcrumb separator-icon="ArrowRight" class="course-breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/dashboard' }">仪表盘</el-breadcrumb-item>
        <el-breadcrumb-item>{{ courseStore.currentCourseDetail.course_name }}</el-breadcrumb-item>
      </el-breadcrumb>

      <el-card class="course-main-card" shadow="never">
        <template #header>
          <div class="course-main-header">
            <h1 class="course-title">{{ courseStore.currentCourseDetail.course_name }}</h1>
            <el-tag :type="getStatusTagType(courseStore.currentCourseDetail.status)" size="large">
              {{ formatStatus(courseStore.currentCourseDetail.status) }}
            </el-tag>
          </div>
        </template>

        <el-row :gutter="20" class="course-meta-info">
          <el-col :span="16">
            <p class="course-description">{{ courseStore.currentCourseDetail.description || '暂无详细描述。' }}</p>
            <p><strong><el-icon><User /></el-icon> 授课教师:</strong> {{ courseStore.currentCourseDetail.teacher?.real_name || 'N/A' }}</p>
            <p><strong><el-icon><Calendar /></el-icon> 课程日期:</strong> {{ formatDate(courseStore.currentCourseDetail.start_date) }} 至 {{ formatDate(courseStore.currentCourseDetail.end_date) }}</p>
            <p><small><strong><el-icon><Clock /></el-icon> 创建时间:</strong> {{ new Date(courseStore.currentCourseDetail.create_time).toLocaleString() }}</small></p>
          </el-col>
          <el-col :span="8" v-if="courseStore.currentCourseDetail.cover_image" class="cover-image-col">
            <el-image
              :src="courseStore.currentCourseDetail.cover_image"
              :alt="courseStore.currentCourseDetail.course_name"
              fit="contain"
              class="course-detail-cover-image"
            >
              <template #error><div class="image-slot-detail">封面加载失败</div></template>
            </el-image>
          </el-col>
        </el-row>

        <el-divider content-position="left"><h2 class="section-title">课程章节</h2></el-divider>
        <div v-if="courseStore.currentCourseDetail.chapters && courseStore.currentCourseDetail.chapters.length" class="chapters-section">
          <el-card
            v-for="chapter in courseStore.currentCourseDetail.chapters"
            :key="chapter.chapter_id"
            shadow="sm"
            class="chapter-card"
          >
            <template #header>
              <div class="chapter-header">
                <span>第 {{ chapter.chapter_order }} 章: {{ chapter.chapter_name }}</span>
              </div>
            </template>
            <p v-if="chapter.description" class="chapter-description">{{ chapter.description }}</p>
            <ul v-if="chapter.materials && chapter.materials.length" class="material-list">
              <li v-for="material in chapter.materials" :key="material.material_id" class="material-item">
                <el-icon class="material-icon"><component :is="getMaterialIcon(material.material_type)" /></el-icon>
                <el-link :href="material.url" target="_blank" type="primary" class="material-link">{{ material.title }}</el-link>
                <span v-if="material.material_type === 1 && material.duration" class="material-duration"> (时长: {{ formatDuration(material.duration) }})</span>
              </li>
            </ul>
            <el-empty v-else description="本章节暂无学习资料" :image-size="50" class="empty-materials"></el-empty>
          </el-card>
        </div>
        <el-empty v-else description="该课程暂无章节信息。" class="empty-chapters"></el-empty>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useCourseStore } from '../../stores/courseStore';
import {
    ElCard, ElRow, ElCol, ElSkeleton, ElEmpty, ElTag, ElDivider,
    ElIcon, ElLink, ElBreadcrumb, ElBreadcrumbItem, ElAlert, ElImage
} from 'element-plus';
import { VideoCamera, Document, Link as LinkIcon, User, Calendar, Clock, ArrowRight } from '@element-plus/icons-vue';

const route = useRoute();
const courseStore = useCourseStore();

const courseId = computed(() => parseInt(route.params.id, 10));

const fetchDetails = () => {
  if (courseId.value) {
    courseStore.fetchCourseDetail(courseId.value);
  }
};

onMounted(() => {
  fetchDetails();
});

onUnmounted(() => {
  courseStore.clearCurrentCourseDetail();
});

// Watch for changes in route param id to re-fetch if navigating between course detail pages
watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    fetchDetails();
  }
});

const formatStatus = (status) => {
  const statuses = { 1: "未开始", 2: "进行中", 3: "已结束" };
  return statuses[status] || "未知";
};

const getStatusTagType = (status) => {
  const statusTypes = { 1: "info", 2: "success", 3: "warning" }; // Default for unknown
  return statusTypes[status] || "default";
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  // Assuming dateString is YYYY-MM-DD from backend (fields.Date)
  const date = new Date(dateString + 'T00:00:00'); // Add time part to avoid timezone issues if any
  return date.toLocaleDateString(); // Uses browser's locale
};

const getMaterialIcon = (materialType) => {
  if (materialType === 1) return VideoCamera; // Video
  if (materialType === 2) return Document;    // Document
  if (materialType === 3) return LinkIcon;    // Link
  return Document; // Default icon
};

const formatDuration = (seconds) => {
  if (seconds === null || seconds === undefined) return '';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) {
    return `${h}时${m}分${s}秒`;
  }
  if (m > 0) {
    return `${m}分${s}秒`;
  }
  return `${s}秒`;
};
</script>

<style scoped>
.course-detail-container {
  padding: 20px;
  background-color: #f9fafb; /* Light background */
}
.loading-container, .empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}
.error-alert {
  margin-bottom: 20px;
}
.course-breadcrumb {
  margin-bottom: 20px;
  font-size: 0.9em;
}
.course-main-card {
  border-radius: 8px;
}
.course-main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.course-title {
  font-size: 2em;
  font-weight: 600;
  color: #303133;
  margin: 0;
}
.course-meta-info {
  margin-top: 10px;
  margin-bottom: 20px;
}
.course-meta-info p {
  margin: 8px 0;
  color: #606266;
  font-size: 0.95em;
  display: flex;
  align-items: center;
}
.course-meta-info .el-icon {
  margin-right: 6px;
  font-size: 1.1em;
}
.course-description {
  color: #303133;
  line-height: 1.7;
  margin-bottom: 15px !important; /* Override p margin */
}
.cover-image-col {
  display: flex;
  align-items: center;
  justify-content: center;
}
.course-detail-cover-image {
  max-height: 250px;
  width: 100%;
  border-radius: 6px;
  object-fit: contain; /* Or 'cover' depending on desired effect */
}
.image-slot-detail {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  min-height: 150px; /* Ensure slot has some height */
  background: #f5f7fa;
  color: #c0c4cc;
  font-size: 0.9em;
}
.section-title {
  font-size: 1.4em;
  font-weight: 600;
  color: #303133;
  margin: 0; /* Reset margin if ElDivider adds its own */
}
.chapters-section {
  margin-top: 10px;
}
.chapter-card {
  margin-bottom: 20px;
  border-left: 3px solid #409EFF; /* Accent for chapters */
}
.chapter-header span {
  font-size: 1.2em;
  font-weight: 500;
  color: #303133;
}
.chapter-description {
  font-size: 0.9em;
  color: #606266;
  margin-top: 5px;
  margin-bottom: 15px;
  white-space: pre-wrap; /* Preserve formatting if any */
}
.material-list {
  list-style: none;
  padding-left: 0;
}
.material-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}
.material-item:hover {
  background-color: #f5f7fa;
}
.material-icon {
  margin-right: 8px;
  font-size: 1.2em;
  color: #409EFF;
}
.material-link {
  font-size: 1em;
}
.material-duration {
  font-size: 0.85em;
  color: #909399;
  margin-left: 10px;
}
.empty-materials, .empty-chapters {
  margin-top: 10px;
}
</style>
