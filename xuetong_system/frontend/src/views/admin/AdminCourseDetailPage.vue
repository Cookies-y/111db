<template>
  <div class="admin-course-detail-page">
    <el-breadcrumb separator-icon="ArrowRight" class="page-breadcrumb">
      <el-breadcrumb-item :to="{ name: 'AdminDashboard' }">管理首页</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ name: 'AdminCourseList' }">课程管理</el-breadcrumb-item>
      <el-breadcrumb-item>课程详情: {{ courseDetail?.course_name || courseId }}</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="card-header">
          <span>课程详细信息 (管理)</span>
          <!-- Optional: Edit/Delete Course buttons here -->
        </div>
      </template>

      <div v-if="isLoading && !courseDetail" class="loading-container">
        <el-skeleton :rows="12" animated />
      </div>
      <el-alert
        v-else-if="error && !courseDetail"
        :title="`加载课程详情失败: ${error}`"
        type="error"
        show-icon
        :closable="false"
      />
      <div v-else-if="!courseDetail" class="empty-container">
         <el-empty description="未找到该课程信息或已被删除。" />
         <router-link :to="{ name: 'AdminCourseList' }">
            <el-button type="primary">返回课程列表</el-button>
        </router-link>
      </div>

      <div v-else>
        <el-descriptions :column="2" border class="course-main-details">
          <el-descriptions-item label="课程 ID">{{ courseDetail.course_id }}</el-descriptions-item>
          <el-descriptions-item label="课程名称">{{ courseDetail.course_name }}</el-descriptions-item>
          <el-descriptions-item label="授课教师">{{ courseDetail.teacher?.real_name || 'N/A' }} (ID: {{ courseDetail.teacher?.user_id || 'N/A' }})</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getCourseStatusTag(courseDetail.status)" disable-transitions>
              {{ formatCourseStatus(courseDetail.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ formatDateSimple(courseDetail.start_date) }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ formatDateSimple(courseDetail.end_date) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ formatDate(courseDetail.create_time) }}</el-descriptions-item>
          <el-descriptions-item label="课程描述" :span="2">{{ courseDetail.description || '暂无描述' }}</el-descriptions-item>
          <el-descriptions-item label="封面图片" :span="2" v-if="courseDetail.cover_image">
            <el-image
              :src="courseDetail.cover_image"
              :alt="courseDetail.course_name"
              fit="contain"
              style="max-height: 200px; width: auto;"
              preview-teleported
              :preview-src-list="[courseDetail.cover_image]"
            />
          </el-descriptions-item>
          <el-descriptions-item label="封面图片" :span="2" v-else>暂无封面</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left"><h3 class="section-title">课程章节与资料</h3></el-divider>
        <div v-if="courseDetail.chapters && courseDetail.chapters.length" class="chapters-section">
          <el-card
            v-for="chapter in courseDetail.chapters"
            :key="chapter.chapter_id"
            shadow="never"
            class="chapter-card-admin"
          >
            <template #header>
              <div class="chapter-header-admin">
                <span>第 {{ chapter.chapter_order }} 章: {{ chapter.chapter_name }}</span>
              </div>
            </template>
            <p v-if="chapter.description" class="chapter-description-admin">{{ chapter.description }}</p>
            <ul v-if="chapter.materials && chapter.materials.length" class="material-list-admin">
              <li v-for="material in chapter.materials" :key="material.material_id" class="material-item-admin">
                <el-icon class="material-icon-admin"><component :is="getMaterialIcon(material.material_type)" /></el-icon>
                <el-link :href="material.url" target="_blank" type="primary">{{ material.title }}</el-link>
                <span v-if="material.material_type === 1 && material.duration" class="material-duration-admin">
                  (时长: {{ formatDuration(material.duration) }})
                </span>
              </li>
            </ul>
            <el-empty v-else description="本章节暂无学习资料" :image-size="50" />
          </el-card>
        </div>
        <el-empty v-else description="该课程暂无章节信息" />

        <!-- Placeholder for listing enrollments, assignments, exams for this course from an admin perspective -->
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useAdminStore } from '../../../stores/adminStore'; // Adjusted path
import {
    ElCard, ElDescriptions, ElDescriptionsItem, ElTag, ElSkeleton,
    ElAlert, ElEmpty, ElBreadcrumb, ElBreadcrumbItem, ElButton,
    ElDivider, ElIcon, ElLink, ElImage
} from 'element-plus';
import { ArrowRight, VideoCamera, Document as DocIcon, Link as LinkIconElem } from '@element-plus/icons-vue'; // Renamed Link to LinkIconElem

const route = useRoute();
const adminStore = useAdminStore();

const courseId = ref(route.params.course_id ? parseInt(route.params.course_id) : null);

const courseDetail = computed(() => adminStore.getAdminCourseDetail);
const isLoading = computed(() => adminStore.isLoadingAdminCourseDetail);
const error = computed(() => adminStore.fetchAdminCourseDetailError);

const fetchData = async (id) => {
  if (id) {
    await adminStore.fetchCourseDetailForAdmin(id);
  }
};

onMounted(() => {
  fetchData(courseId.value);
});

onUnmounted(() => {
  adminStore.clearCourseDetailAdmin();
});

watch(() => route.params.course_id, (newIdStr) => {
  const newId = newIdStr ? parseInt(newIdStr) : null;
  if (newId && newId !== courseId.value) {
    courseId.value = newId;
    fetchData(newId);
  } else if (!newId && courseId.value) {
    courseId.value = null;
    adminStore.clearCourseDetailAdmin();
  }
});

// Helper functions (could be moved to a utils file)
function formatCourseStatus(status) {
  const statuses = { 1: '未开始', 2: '进行中', 3: '已结束' };
  return statuses[status] || '未知状态';
}

function getCourseStatusTag(status) {
  const tags = { 1: 'info', 2: 'success', 3: 'warning' };
  return tags[status] || 'default';
}

function formatDate(dateTimeString) {
  if (!dateTimeString) return 'N/A';
  return new Date(dateTimeString).toLocaleString('zh-CN', { dateStyle: 'medium', timeStyle: 'short' });
}

function formatDateSimple(dateString) {
  if (!dateString) return 'N/A';
  // Ensure dateString is treated as UTC if it's just YYYY-MM-DD to avoid timezone shift
  return new Date(dateString + 'T00:00:00Z').toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });
}

function getMaterialIcon(materialType) {
  if (materialType === 1) return VideoCamera;
  if (materialType === 2) return DocIcon;
  if (materialType === 3) return LinkIconElem;
  return DocIcon; // Default
}

function formatDuration(seconds) {
  if (seconds === null || seconds === undefined) return '';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}时${m}分${s}秒`;
  if (m > 0) return `${m}分${s}秒`;
  return `${s}秒`;
}
</script>

<style scoped>
.admin-course-detail-page {
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
.loading-container, .empty-container {
  padding: 20px;
  text-align: center;
}
.course-main-details {
  margin-top: 15px;
}
.el-descriptions-item__label {
  font-weight: bold !important;
}
.section-title {
  font-size: 1.2em;
  font-weight: 600;
  color: #303133;
  margin: 0;
}
.chapters-section {
  margin-top: 15px;
}
.chapter-card-admin {
  margin-bottom: 15px;
  border-left: 3px solid #67c23a; /* Different accent for admin view */
}
.chapter-header-admin span {
  font-size: 1.1em;
  font-weight: 500;
}
.chapter-description-admin {
  font-size: 0.9em;
  color: #555;
  margin-top: 5px;
  margin-bottom: 10px;
  white-space: pre-wrap;
}
.material-list-admin {
  list-style: none;
  padding-left: 0;
}
.material-item-admin {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  padding: 6px;
  border-radius: 4px;
}
.material-icon-admin {
  margin-right: 8px;
  color: #67c23a;
}
.material-duration-admin {
  font-size: 0.8em;
  color: #888;
  margin-left: 8px;
}
</style>
