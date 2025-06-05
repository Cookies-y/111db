<template>
  <div class="assignment-create-container">
    <el-breadcrumb separator-icon="ArrowRight" class="page-breadcrumb">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: '/dashboard' }">仪表盘</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: `/courses/${courseId}` }">
        {{ courseStore.currentCourseDetail?.course_name || '课程详情' }}
      </el-breadcrumb-item>
      <el-breadcrumb-item>创建新作业</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card class="assignment-create-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>为《{{ courseStore.currentCourseDetail?.course_name || '该课程' }}》创建新作业</span>
        </div>
      </template>

      <div v-if="isLoadingCourse" class="loading-initial">
        <p>正在加载课程信息...</p>
        <el-skeleton :rows="2" animated />
      </div>
      <el-alert v-else-if="!isTeacherOfCourse" title="权限不足" type="error" show-icon :closable="false">
        抱歉，只有该课程的教师才能创建作业。
        <div style="margin-top: 10px;">
          <router-link :to="`/courses/${courseId}`"><el-button size="small">返回课程详情</el-button></router-link>
        </div>
      </el-alert>

      <el-form
        v-else
        @submit.prevent="submitForm"
        :model="form"
        :rules="rules"
        ref="formRef"
        label-position="top"
        class="assignment-create-form"
      >
        <el-alert
          v-if="courseStore.createAssignmentError"
          :title="courseStore.createAssignmentError"
          type="error"
          show-icon
          :closable="false"
          class="error-alert"
          @close="courseStore.clearCreateAssignmentError()"
        />

        <el-form-item label="作业标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入作业标题" clearable />
        </el-form-item>

        <el-form-item label="作业描述 (可选)" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="5"
            placeholder="请输入作业的详细描述和要求"
            clearable
          />
        </el-form-item>

        <el-form-item label="截止日期" prop="deadline">
          <el-date-picker
            v-model="form.deadline"
            type="datetime"
            placeholder="选择截止日期和时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ssZ"
            style="width: 100%;"
          />
        </el-form-item>

        <el-form-item label="总分数 (可选, 默认100)" prop="total_score">
          <el-input-number v-model="form.total_score" :min="0" :max="1000" placeholder="请输入总分数" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="courseStore.isCreatingAssignment" class="submit-button">
            创建作业
          </el-button>
          <el-button @click="resetForm" :disabled="courseStore.isCreatingAssignment" class="reset-button">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
import { useCourseStore } from '../../stores/courseStore';
import { useAuthStore } from '../../stores/authStore';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { ArrowRight } from '@element-plus/icons-vue'; // For breadcrumb

const courseStore = useCourseStore();
const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const formRef = ref(null);

const courseId = computed(() => parseInt(route.params.course_id, 10));
const isLoadingCourse = ref(true); // For initial course detail loading

const form = reactive({
  title: '',
  description: '',
  deadline: '',
  total_score: 100,
});

// Role check based on fetched course details
const isTeacherOfCourse = computed(() => {
  if (!authStore.isAuthenticated || !courseStore.currentCourseDetail) return false;
  return authStore.user?.user_id === courseStore.currentCourseDetail.teacher?.user_id && authStore.user?.user_type === 2;
});

onMounted(async () => {
  isLoadingCourse.value = true;
  await courseStore.fetchCourseDetail(courseId.value); // Fetch course details to get name and verify teacher
  isLoadingCourse.value = false;
  // Clear any previous assignment creation errors when component mounts
  courseStore.clearCreateAssignmentError();
});

onUnmounted(() => {
  courseStore.clearCreateAssignmentError();
});

const rules = reactive({
  title: [{ required: true, message: '请输入作业标题', trigger: 'blur' }],
  deadline: [
    { required: true, message: '请选择截止日期和时间', trigger: 'change' },
    { validator: (rule, value, callback) => {
        if (value && new Date(value) < new Date()) {
          callback(new Error('截止日期不能早于当前时间'));
        } else {
          callback();
        }
      }, trigger: 'change'
    }
  ],
  total_score: [
    { type: 'number', message: '总分数必须是数字', trigger: 'blur' },
    { validator: (rule, value, callback) => {
        if (value < 0) {
          callback(new Error('总分数不能为负'));
        } else {
          callback();
        }
      }, trigger: 'blur'
    }
  ]
});

async function submitForm() {
  if (!isTeacherOfCourse.value) {
    ElMessage.error('权限不足，只有课程教师才能创建作业。');
    return;
  }
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (valid) {
      const assignmentData = {
        title: form.title,
        description: form.description,
        deadline: form.deadline, // Ensure this is ISO 8601 string or compatible with backend
        total_score: form.total_score,
      };

      const result = await courseStore.createAssignmentForCourse(courseId.value, assignmentData);

      if (result.success && result.data) {
        ElMessage.success('作业创建成功！');
        // Navigate to the course detail page to see the new assignment
        router.push({ name: 'CourseDetail', params: { id: courseId.value } });
      } else {
        // Error is already set in store and displayed by ElAlert
        // ElMessage.error(courseStore.createAssignmentError || '作业创建失败，请检查输入。');
      }
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
  form.total_score = 100; // Reset non-prop fields if form.resetFields doesn't catch them
  courseStore.clearCreateAssignmentError();
}
</script>

<style scoped>
.assignment-create-container {
  padding: 20px;
  background-color: #f9fafb;
}
.page-breadcrumb {
  margin-bottom: 20px;
  font-size: 0.9em;
}
.assignment-create-card {
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
.assignment-create-form {
  margin-top: 10px;
}
.el-form-item {
  margin-bottom: 22px;
}
.el-date-picker, .el-select {
  width: 100%;
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
