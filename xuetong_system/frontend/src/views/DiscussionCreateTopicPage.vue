<template>
  <div class="discussion-create-container">
    <el-breadcrumb separator-icon="ArrowRight" class="page-breadcrumb">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: '/dashboard' }">仪表盘</el-breadcrumb-item>
      <el-breadcrumb-item v-if="courseId" :to="{ path: `/courses/${courseId}` }">
        {{ courseStore.currentCourseDetail?.course_name || `课程 ${courseId}` }}
      </el-breadcrumb-item>
      <el-breadcrumb-item>发起新讨论</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card class="discussion-create-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>在《{{ courseStore.currentCourseDetail?.course_name || `课程 ${courseId}` }}》中发起新讨论</span>
        </div>
      </template>

      <div v-if="isLoadingCourseInfo" class="loading-initial">
        <p>正在加载课程信息...</p>
        <el-skeleton :rows="1" animated />
      </div>
      <el-alert
        v-else-if="courseStore.fetchCourseDetailError && !courseStore.currentCourseDetail"
        title="无法加载课程信息"
        type="error"
        :description="courseStore.fetchCourseDetailError"
        show-icon
        :closable="false"
      />
      <!-- Form is shown even if course detail fails, as courseId is primary from route. Backend will validate user's right to post. -->
      <el-form
        @submit.prevent="submitForm"
        :model="form"
        :rules="rules"
        ref="formRef"
        label-position="top"
        class="discussion-create-form"
      >
        <el-alert
          v-if="courseStore.createDiscussionTopicError"
          :title="courseStore.createDiscussionTopicError"
          type="error"
          show-icon
          :closable="false"
          class="error-alert"
          @close="courseStore.clearCreateDiscussionTopicError()"
        />

        <el-form-item label="讨论标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入讨论标题" clearable />
        </el-form-item>

        <el-form-item label="讨论内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="8"
            placeholder="请输入详细的讨论内容..."
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="courseStore.isCreatingDiscussionTopic" class="submit-button">
            发布话题
          </el-button>
          <el-button @click="resetForm" :disabled="courseStore.isCreatingDiscussionTopic" class="reset-button">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
import { useCourseStore } from '../stores/courseStore'; // Corrected path
import { useAuthStore } from '../stores/authStore'; // Corrected path
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { ArrowRight } from '@element-plus/icons-vue';

const courseStore = useCourseStore();
const authStore = useAuthStore(); // Though actual posting auth is by backend via JWT
const router = useRouter();
const route = useRoute();
const formRef = ref(null);

const courseId = computed(() => parseInt(route.params.course_id, 10));
const isLoadingCourseInfo = ref(false); // For fetching course name for breadcrumb/title

const form = reactive({
  title: '',
  content: '',
});

const rules = reactive({
  title: [
    { required: true, message: '请输入讨论标题', trigger: 'blur' },
    { min: 3, message: '标题长度至少为3个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入讨论内容', trigger: 'blur' },
    { min: 10, message: '内容长度至少为10个字符', trigger: 'blur' }
  ],
});

onMounted(async () => {
  // Fetch course details minimally for course name if not already available or if it's a different course
  if (courseId.value && courseStore.currentCourseDetail?.course_id !== courseId.value) {
    isLoadingCourseInfo.value = true;
    await courseStore.fetchCourseDetail(courseId.value); // To get course name for display
    isLoadingCourseInfo.value = false;
  }
  courseStore.clearCreateDiscussionTopicError(); // Clear previous errors
});

onUnmounted(() => {
  courseStore.clearCreateDiscussionTopicError();
});

async function submitForm() {
  if (!authStore.isAuthenticated) {
      ElMessage.error('请先登录后再发起讨论。');
      router.push({ name: 'Login', query: { redirect: route.fullPath } });
      return;
  }
  if (!formRef.value) return;

  courseStore.clearCreateDiscussionTopicError();

  await formRef.value.validate(async (valid) => {
    if (valid) {
      const topicData = {
        title: form.title,
        content: form.content,
      };

      const result = await courseStore.createDiscussionTopic(courseId.value, topicData);

      if (result.success && result.data) {
        ElMessage.success('新讨论话题已发布！');
        // Navigate to the newly created discussion thread page
        // Assumes backend returns the created topic object including its post_id
        router.push({ name: 'DiscussionThread', params: { post_id: result.data.post_id } });
      }
      // Error is displayed by ElAlert via reactive store property
    } else {
      ElMessage.error('表单验证失败，请检查您输入的信息。');
      return false;
    }
  });
}

function resetForm() {
  if (formRef.value) {
    formRef.value.resetFields();
  }
  courseStore.clearCreateDiscussionTopicError();
}
</script>

<style scoped>
.discussion-create-container {
  padding: 20px;
  background-color: #f9fafb;
}
.page-breadcrumb {
  margin-bottom: 20px;
  font-size: 0.9em;
}
.discussion-create-card {
  max-width: 800px;
  margin: 0 auto;
  border-radius: 8px;
}
.card-header {
  text-align: center;
  font-size: 1.6em;
  font-weight: 600;
  color: #303133;
}
.loading-initial {
  text-align: center;
  padding: 20px;
}
.discussion-create-form {
  margin-top: 10px;
}
.el-form-item {
  margin-bottom: 22px;
}
.submit-button, .reset-button {
  min-width: 120px;
  height: 40px;
  font-size: 1em;
}
.reset-button {
  margin-left: 10px;
}
.error-alert {
  margin-bottom: 22px;
}
</style>
