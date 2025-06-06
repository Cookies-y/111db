<template>
  <div class="exam-create-container">
    <el-breadcrumb separator-icon="ArrowRight" class="page-breadcrumb">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: '/dashboard' }">仪表盘</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: `/courses/${courseId}` }">
        {{ courseStore.currentCourseDetail?.course_name || '课程详情' }}
      </el-breadcrumb-item>
      <el-breadcrumb-item>创建新考试</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card class="exam-create-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>为《{{ courseStore.currentCourseDetail?.course_name || '该课程' }}》创建新考试</span>
        </div>
      </template>

      <div v-if="isLoadingCourse" class="loading-initial">
        <p>正在加载课程信息...</p>
        <el-skeleton :rows="2" animated />
      </div>
      <el-alert v-else-if="!isTeacherOfCourse" title="权限不足" type="error" show-icon :closable="false">
        抱歉，只有该课程的教师才能创建考试。
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
        class="exam-create-form"
      >
        <el-alert
          v-if="courseStore.createExamError"
          :title="courseStore.createExamError"
          type="error"
          show-icon
          :closable="false"
          class="error-alert"
          @close="courseStore.clearCreateExamError()"
        />

        <el-form-item label="考试名称" prop="exam_name">
          <el-input v-model="form.exam_name" placeholder="请输入考试名称" clearable />
        </el-form-item>

        <el-form-item label="考试描述 (可选)" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入考试的详细描述"
            clearable
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="start_time">
              <el-date-picker
                v-model="form.start_time"
                type="datetime"
                placeholder="选择开始日期和时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DDTHH:mm:ssZ"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="end_time">
              <el-date-picker
                v-model="form.end_time"
                type="datetime"
                placeholder="选择结束日期和时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DDTHH:mm:ssZ"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="总分数" prop="total_score">
              <el-input-number v-model="form.total_score" :min="0" :max="1000" placeholder="请输入总分数" style="width: 100%;"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="考试时长 (分钟)" prop="duration">
              <el-input-number v-model="form.duration" :min="1" placeholder="请输入考试时长" style="width: 100%;"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="courseStore.isCreatingExam" class="submit-button">
            创建考试
          </el-button>
          <el-button @click="resetForm" :disabled="courseStore.isCreatingExam" class="reset-button">
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
import { ArrowRight } from '@element-plus/icons-vue'; // For breadcrumb

const courseStore = useCourseStore();
const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const formRef = ref(null);

const courseId = computed(() => parseInt(route.params.course_id, 10));
const isLoadingCourse = ref(true);

const form = reactive({
  exam_name: '',
  description: '',
  start_time: '',
  end_time: '',
  total_score: 100,
  duration: 60, // Default duration in minutes
});

const isTeacherOfCourse = computed(() => {
  if (!authStore.isAuthenticated || !courseStore.currentCourseDetail || !authStore.user) return false;
  return authStore.user.user_id === courseStore.currentCourseDetail.teacher?.user_id && authStore.user.user_type === 2;
});

onMounted(async () => {
  isLoadingCourse.value = true;
  await courseStore.fetchCourseDetail(courseId.value);
  isLoadingCourse.value = false;
  courseStore.clearCreateExamError(); // Clear previous errors when component mounts
});

onUnmounted(() => {
  courseStore.clearCreateExamError();
});

// Custom validator for end_time
const validateEndTime = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请选择结束时间'));
  } else if (form.start_time && new Date(value) <= new Date(form.start_time)) {
    callback(new Error('结束时间必须晚于开始时间'));
  } else {
    callback();
  }
};

const rules = reactive({
  exam_name: [{ required: true, message: '请输入考试名称', trigger: 'blur' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [
    { required: true, message: '请选择结束时间', trigger: 'change' },
    { validator: validateEndTime, trigger: 'change' }
  ],
  total_score: [
    { required: true, message: '请输入总分数', trigger: 'blur' },
    { type: 'number', message: '总分数必须是数字', trigger: 'blur' },
    { validator: (rule,value,cb) => { value >=0 ? cb() : cb(new Error('总分不能为负'))}, trigger: 'blur'}
  ],
  duration: [
    { required: true, message: '请输入考试时长', trigger: 'blur' },
    { type: 'number', message: '时长必须是数字', trigger: 'blur' },
    { validator: (rule,value,cb) => { value > 0 ? cb() : cb(new Error('时长必须大于0'))}, trigger: 'blur'}
  ]
});

async function submitForm() {
  if (!isTeacherOfCourse.value) {
    ElMessage.error('权限不足，只有课程教师才能创建考试。');
    return;
  }
  if (!formRef.value) return;

  courseStore.clearCreateExamError(); // Clear previous error

  await formRef.value.validate(async (valid) => {
    if (valid) {
      const examData = {
        exam_name: form.exam_name,
        description: form.description,
        start_time: form.start_time, // Ensure this is ISO 8601 string or compatible
        end_time: form.end_time,     // Ensure this is ISO 8601 string
        total_score: form.total_score,
        duration: form.duration,
      };

      const result = await courseStore.createExamForCourse(courseId.value, examData);

      if (result.success && result.data) {
        ElMessage.success('考试创建成功！');
        router.push({ name: 'CourseDetail', params: { id: courseId.value } });
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
  form.total_score = 100; // Reset non-prop fields
  form.duration = 60;
  courseStore.clearCreateExamError();
}
</script>

<style scoped>
.exam-create-container {
  padding: 20px;
  background-color: #f9fafb;
}
.page-breadcrumb {
  margin-bottom: 20px;
  font-size: 0.9em;
}
.exam-create-card {
  max-width: 800px;
  margin: 0 auto;
  border-radius: 8px;
}
.card-header {
  text-align: center;
  font-size: 1.6em; /* Slightly smaller than course create */
  font-weight: 600;
  color: #303133;
}
.loading-initial {
  text-align: center;
  padding: 20px;
}
.exam-create-form {
  margin-top: 10px;
}
.el-form-item {
  margin-bottom: 22px;
}
.el-date-picker, .el-select, .el-input-number { /* Ensure input number also takes full width if desired */
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
