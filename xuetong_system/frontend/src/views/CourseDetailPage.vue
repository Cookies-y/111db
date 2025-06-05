<template>
  <div class="course-detail-container">
    <div v-if="courseStore.isLoadingCourseDetail && !courseStore.currentCourseDetail" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    <el-alert
      v-else-if="courseStore.fetchCourseDetailError && !courseStore.currentCourseDetail"
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
            <div class="header-actions">
              <el-tag :type="getStatusTagType(courseStore.currentCourseDetail.status)" size="large" style="margin-right: 10px;">
                {{ formatStatus(courseStore.currentCourseDetail.status) }}
              </el-tag>
              <router-link
                v-if="isCourseTeacher"
                :to="{ name: 'CreateAssignment', params: { course_id: courseId } }"
                style="margin-right: 10px;"
              >
                <el-button type="success" :icon="Plus" size="small">创建作业</el-button>
              </router-link>
              <router-link
                v-if="isCourseTeacher"
                :to="{ name: 'CreateExam', params: { course_id: courseId } }"
              >
                <el-button type="warning" :icon="Plus" size="small">创建考试</el-button>
              </router-link>
            </div>
          </div>
        </template>

        <el-row :gutter="20" class="course-meta-info">
          <el-col :span="courseStore.currentCourseDetail.cover_image ? 16 : 24">
            <p class="course-description">{{ courseStore.currentCourseDetail.description || '暂无详细描述。' }}</p>
            <p><strong><el-icon><User /></el-icon> 授课教师:</strong> {{ courseStore.currentCourseDetail.teacher?.real_name || 'N/A' }}</p>
            <p><strong><el-icon><Calendar /></el-icon> 课程日期:</strong> {{ formatDate(courseStore.currentCourseDetail.start_date) }} 至 {{ formatDate(courseStore.currentCourseDetail.end_date) }}</p>
            <p><small><strong><el-icon><Clock /></el-icon> 创建时间:</strong> {{ new Date(courseStore.currentCourseDetail.create_time).toLocaleString() }}</small></p>

            <!-- Student Progress Summary (Optional) -->
            <div v-if="isStudent && totalMaterials > 0" class="progress-summary">
                <p><strong>课程进度:</strong></p>
                <el-progress :percentage="courseCompletionPercentage" :stroke-width="10" />
                <p style="font-size:0.9em; color: #606266;">已完成 {{ completedMaterialsCount }} / {{ totalMaterials }} 个学习资料</p>
            </div>

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
              <li v-for="material in chapter.materials" :key="material.material_id" class="material-item" :class="{ 'completed-material': isStudent && progressStore.getCompletionStatusByMaterialId(material.material_id) }">
                <el-checkbox
                  v-if="isStudent"
                  :model-value="progressStore.getCompletionStatusByMaterialId(material.material_id)"
                  @change="(newStatus) => handleToggleMaterialCompletion(material.material_id, newStatus)"
                  :disabled="progressStore.isMaterialProgressUpdating(material.material_id)"
                  size="large"
                  style="margin-right: 10px;"
                />
                <el-icon class="material-icon"><component :is="getMaterialIcon(material.material_type)" /></el-icon>
                <el-link :href="material.url" target="_blank" type="primary" class="material-link">{{ material.title }}</el-link>
                <span v-if="material.material_type === 1 && material.duration" class="material-duration"> (时长: {{ formatDuration(material.duration) }})</span>
                <el-tag v-if="isStudent && progressStore.getCompletionStatusByMaterialId(material.material_id)" type="success" size="small" style="margin-left: auto;">已完成</el-tag>
              </li>
            </ul>
            <el-empty v-else description="本章节暂无学习资料" :image-size="50" class="empty-materials"></el-empty>
          </el-card>
        </div>
        <el-empty v-else description="该课程暂无章节信息。" class="empty-chapters"></el-empty>

        <el-divider content-position="left"><h2 class="section-title">课程作业</h2></el-divider>
        <div v-if="courseStore.isLoadingCourseAssignments" class="loading-section">
            <p>正在加载作业列表...</p><el-skeleton :rows="3" animated />
        </div>
        <el-alert v-else-if="courseStore.fetchCourseAssignmentsError" :title="courseStore.fetchCourseAssignmentsError" type="error" show-icon :closable="false" />
        <ul v-else-if="courseStore.currentCourseAssignments && courseStore.currentCourseAssignments.length" class="item-list">
            <li v-for="assignment in courseStore.currentCourseAssignments" :key="assignment.assignment_id" class="list-item">
                <router-link :to="`/assignments/${assignment.assignment_id}`">
                    <strong>{{ assignment.title }}</strong>
                </router-link>
                - 截止日期: {{ new Date(assignment.deadline).toLocaleDateString() }}
            </li>
        </ul>
        <el-empty v-else description="该课程暂无作业信息。" :image-size="60" class="empty-section"></el-empty>

        <el-divider content-position="left"><h2 class="section-title">课程考试</h2></el-divider>
        <div v-if="courseStore.isLoadingCourseExams" class="loading-section">
            <p>正在加载考试列表...</p><el-skeleton :rows="3" animated />
        </div>
        <el-alert v-else-if="courseStore.fetchCourseExamsError" :title="courseStore.fetchCourseExamsError" type="error" show-icon :closable="false" />
        <ul v-else-if="courseStore.currentCourseExams && courseStore.currentCourseExams.length" class="item-list">
            <li v-for="exam in courseStore.currentCourseExams" :key="exam.exam_id" class="list-item">
                <router-link :to="`/exams/${exam.exam_id}`">
                    <strong>{{ exam.exam_name }}</strong>
                </router-link>
                - 开始时间: {{ new Date(exam.start_time).toLocaleDateString() }}
            </li>
        </ul>
        <el-empty v-else description="该课程暂无考试信息。" :image-size="60" class="empty-section"></el-empty>

        <el-divider content-position="left"><h2 class="section-title">课程讨论区</h2></el-divider>
        <div class="discussion-toolbar">
            <router-link :to="{ name: 'CreateDiscussionTopic', params: { course_id: courseId } }" v-if="authStore.isAuthenticated">
                <el-button type="primary" :icon="ChatDotSquare">发起新讨论</el-button>
            </router-link>
        </div>
        <div v-if="courseStore.isLoadingCourseDiscussionTopics" class="loading-section">
            <p>正在加载讨论列表...</p><el-skeleton :rows="3" animated />
        </div>
        <el-alert v-else-if="courseStore.fetchCourseDiscussionTopicsError" :title="courseStore.fetchCourseDiscussionTopicsError" type="error" show-icon :closable="false" />
        <el-empty v-else-if="!courseStore.currentCourseDiscussionTopics || courseStore.currentCourseDiscussionTopics.length === 0" description="本课程暂无讨论话题，快来发起第一个吧！" :image-size="60" class="empty-section"></el-empty>
        <el-table :data="courseStore.currentCourseDiscussionTopics" style="width: 100%" v-else class="discussion-table">
            <el-table-column prop="title" label="话题">
                <template #default="scope">
                <router-link :to="{ name: 'DiscussionThread', params: { post_id: scope.row.post_id } }">
                    {{ scope.row.title }}
                </router-link>
                </template>
            </el-table-column>
            <el-table-column label="作者" width="180">
                <template #default="scope">{{ scope.row.author?.real_name || 'N/A' }}</template>
            </el-table-column>
            <el-table-column prop="reply_count" label="回复数" width="100" align="center" />
            <el-table-column label="发布时间" width="200">
                <template #default="scope">{{ new Date(scope.row.post_time).toLocaleString() }}</template>
            </el-table-column>
        </el-table>

      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useCourseStore } from '../../stores/courseStore';
import { useAuthStore } from '../../stores/authStore';
import { useProgressStore } from '../../stores/progressStore'; // Import progress store
import {
    ElCard, ElRow, ElCol, ElSkeleton, ElEmpty, ElTag, ElDivider,
    ElIcon, ElLink, ElBreadcrumb, ElBreadcrumbItem, ElAlert, ElImage,
    ElButton, ElTable, ElTableColumn, ElCheckbox, ElProgress // Added ElCheckbox, ElProgress
} from 'element-plus';
import { VideoCamera, Document, Link as LinkIcon, User, Calendar, Clock, ArrowRight, Plus, ChatDotSquare } from '@element-plus/icons-vue';

const route = useRoute();
const courseStore = useCourseStore();
const authStore = useAuthStore();
const progressStore = useProgressStore(); // Initialize progress store

const courseId = computed(() => parseInt(route.params.id, 10));
const isStudent = computed(() => authStore.isAuthenticated && authStore.user?.user_type === 1);

const fetchAllCourseData = async () => {
  if (courseId.value) {
    await courseStore.fetchCourseDetail(courseId.value);
    await courseStore.fetchAssignmentsForCourse(courseId.value);
    await courseStore.fetchExamsForCourse(courseId.value);
    await courseStore.fetchDiscussionTopicsForCourse(courseId.value);
    if (isStudent.value) { // Fetch progress only if user is a student
      await progressStore.fetchMaterialProgressForCourse(courseId.value);
    }
  }
};

onMounted(() => {
  fetchAllCourseData();
});

onUnmounted(() => {
  courseStore.clearCurrentCourseDetail();
  if(isStudent.value) { // Clear progress store if student was viewing
    progressStore.clearProgressForCourse();
  }
});

watch(() => route.params.id, (newIdStr, oldIdStr) => {
  const newId = newIdStr ? parseInt(newIdStr) : null;
  if (newId && newId !== (courseStore.currentCourseDetail?.course_id || null)) {
    fetchAllCourseData();
  } else if (!newId && courseStore.currentCourseDetail) { // Navigated away from a valid courseId
    courseStore.clearCurrentCourseDetail();
    if(isStudent.value) progressStore.clearProgressForCourse();
  }
}, { immediate: false });

const isCourseTeacher = computed(() => {
  if (!authStore.isAuthenticated || !courseStore.currentCourseDetail || !authStore.user) {
    return false;
  }
  return authStore.user.user_id === courseStore.currentCourseDetail.teacher?.user_id && authStore.user.user_type === 2;
});

const totalMaterials = computed(() => {
    if (!courseStore.currentCourseDetail || !courseStore.currentCourseDetail.chapters) return 0;
    return courseStore.currentCourseDetail.chapters.reduce((count, chapter) => count + (chapter.materials?.length || 0), 0);
});

const completedMaterialsCount = computed(() => {
    if (!isStudent.value || !progressStore.getMaterialProgressForCurrentCourse.length) return 0;
    return progressStore.getMaterialProgressForCurrentCourse.filter(p => p.is_completed).length;
});

const courseCompletionPercentage = computed(() => {
    if (totalMaterials.value === 0) return 0;
    return Math.round((completedMaterialsCount.value / totalMaterials.value) * 100);
});

async function handleToggleMaterialCompletion(materialId, newStatus) {
  // courseId.value is already available in the component's scope
  await progressStore.markMaterialProgress(materialId, newStatus);
  // The store action handles UI messages and optimistic updates.
  // If not optimistic, could re-fetch: await progressStore.fetchMaterialProgressForCourse(courseId.value);
}

const formatStatus = (status) => {
  const statuses = { 1: "未开始", 2: "进行中", 3: "已结束" };
  return statuses[status] || "未知";
};

const getStatusTagType = (status) => {
  const statusTypes = { 1: "info", 2: "success", 3: "warning" };
  return statusTypes[status] || "default";
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString();
};

const getMaterialIcon = (materialType) => {
  if (materialType === 1) return VideoCamera;
  if (materialType === 2) return Document;
  if (materialType === 3) return LinkIcon;
  return Document;
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
.course-detail-container { padding: 20px; background-color: #f9fafb; }
.loading-container, .empty-container, .loading-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100px;
    padding: 15px;
}
.error-alert { margin-bottom: 20px; }
.course-breadcrumb { margin-bottom: 20px; font-size: 0.9em; }
.course-main-card { border-radius: 8px; }
.course-main-header { display: flex; justify-content: space-between; align-items: center; }
.header-actions { display: flex; align-items: center; }
.header-actions .el-button { font-size: 0.9em; }
.course-title { font-size: 2em; font-weight: 600; color: #303133; margin: 0; }
.course-meta-info { margin-top: 10px; margin-bottom: 20px; }
.course-meta-info p { margin: 8px 0; color: #606266; font-size: 0.95em; display: flex; align-items: center; }
.course-meta-info .el-icon { margin-right: 6px; font-size: 1.1em; }
.course-description { color: #303133; line-height: 1.7; margin-bottom: 15px !important; }
.cover-image-col { display: flex; align-items: center; justify-content: center; }
.course-detail-cover-image { max-height: 250px; width: 100%; border-radius: 6px; object-fit: contain; }
.image-slot-detail { display: flex; justify-content: center; align-items: center; width: 100%; height: 100%; min-height: 150px; background: #f5f7fa; color: #c0c4cc; font-size: 0.9em; }
.section-title { font-size: 1.4em; font-weight: 600; color: #303133; margin: 0; }
.chapters-section, .assignment-list-section, .exam-list-section, .discussion-section { margin-top: 10px; }
.chapter-card { margin-bottom: 20px; border-left: 3px solid #409EFF; }
.chapter-header span { font-size: 1.2em; font-weight: 500; color: #303133; }
.chapter-description { font-size: 0.9em; color: #606266; margin-top: 5px; margin-bottom: 15px; white-space: pre-wrap; }
.material-list { list-style: none; padding-left: 0; }
.material-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}
.material-item:hover { background-color: #f0f4f8; }
.material-item.completed-material .material-link {
  text-decoration: line-through;
  color: #a9a9a9;
}
.material-icon { margin-right: 8px; font-size: 1.2em; color: #409EFF; }
.material-link { font-size: 1em; }
.material-duration { font-size: 0.85em; color: #909399; margin-left: 10px; }
.empty-materials, .empty-chapters, .empty-section { margin-top: 10px; }

.item-list { list-style: none; padding: 0; margin-top: 15px; }
.list-item { padding: 10px; margin-bottom: 10px; border: 1px solid #ebeef5; border-radius: 4px; background-color: #fff; transition: box-shadow 0.2s ease; }
.list-item:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.list-item strong { color: #409EFF; }
.discussion-toolbar { margin-bottom: 15px; text-align: right; }
.discussion-table { margin-top: 15px; }
.progress-summary { margin-top: 15px; padding-top:15px; border-top: 1px solid #eee;}
.progress-summary p { margin-bottom: 5px;}
</style>
