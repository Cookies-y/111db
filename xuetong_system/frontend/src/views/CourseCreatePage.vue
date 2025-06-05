<template>
  <div class="course-create-container">
    <el-card class="course-create-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>创建新课程</span>
        </div>
      </template>

      <div v-if="!isTeacher">
        <el-alert
          title="权限不足"
          type="error"
          description="抱歉，只有教师才能创建新课程。"
          show-icon
          :closable="false"
        />
        <div style="margin-top: 20px; text-align: center;">
          <router-link to="/dashboard">
            <el-button type="primary">返回仪表盘</el-button>
          </router-link>
        </div>
      </div>

      <el-form
        v-else
        @submit.prevent="submitForm"
        :model="form"
        :rules="rules"
        ref="formRef"
        label-position="top"
        class="course-create-form"
      >
        <el-alert
          v-if="courseStore.createCourseError"
          :title="courseStore.createCourseError"
          type="error"
          show-icon
          :closable="false"
          class="error-alert"
          @close="courseStore.clearCreateCourseError()"
        />

        <el-form-item label="课程名称" prop="course_name">
          <el-input v-model="form.course_name" placeholder="请输入课程名称" clearable />
        </el-form-item>

        <el-form-item label="课程描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入课程描述"
            clearable
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker
                v-model="form.start_date"
                type="date"
                placeholder="选择开始日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="end_date">
              <el-date-picker
                v-model="form.end_date"
                type="date"
                placeholder="选择结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="课程状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择课程状态" style="width: 100%;">
            <el-option label="未开始" :value="1" />
            <el-option label="进行中" :value="2" />
            <el-option label="已结束" :value="3" />
          </el-select>
        </el-form-item>

        <el-form-item label="封面图片URL (可选)" prop="cover_image">
          <el-input v-model="form.cover_image" placeholder="请输入封面图片的URL" clearable />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="isLoading" class="create-button">
            提交创建
          </el-button>
          <el-button @click="resetForm" :disabled="isLoading" class="reset-button">
            重置表单
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted, computed } from 'vue';
import { useCourseStore } from '../../stores/courseStore';
import { useAuthStore } from '../../stores/authStore';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus'; // For success/error notifications

const courseStore = useCourseStore();
const authStore = useAuthStore();
const router = useRouter();
const formRef = ref(null);

const form = reactive({
  course_name: '',
  description: '',
  start_date: '',
  end_date: '',
  status: 1, // Default to "Not Started"
  cover_image: '',
});

const isLoading = ref(false);

// Role check
const isTeacher = computed(() => authStore.isAuthenticated && authStore.user?.user_type === 2);
// IMPORTANT: authStore.user.user_type needs to be populated correctly after login.
// Currently, authStore.user only has { email: ... }. This check will fail until user profile is fully loaded.
// For testing, one might temporarily hardcode isTeacher or ensure user_type is in JWT and decoded into store.

// Custom validator for end_date
const validateEndDate = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请选择结束日期'));
  } else if (form.start_date && new Date(value) < new Date(form.start_date)) {
    callback(new Error('结束日期不能早于开始日期'));
  } else {
    callback();
  }
};

const rules = reactive({
  course_name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  description: [{ required: false }], // Optional
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'change' },
    { validator: validateEndDate, trigger: 'change' }
  ],
  status: [{ required: true, message: '请选择课程状态', trigger: 'change' }],
  cover_image: [{ type: 'url', message: '请输入有效的URL', trigger: ['blur', 'change'] }, {required: false}]
});

async function submitForm() {
  if (!isTeacher.value) {
    ElMessage.error('只有教师才能创建课程。');
    return;
  }
  if (!formRef.value) return;

  // Clear previous errors
  courseStore.clearCreateCourseError();

  await formRef.value.validate(async (valid) => {
    if (valid) {
      isLoading.value = true;
      const result = await courseStore.createCourse({ ...form });
      isLoading.value = false;

      if (result.success && result.data) {
        ElMessage.success('课程创建成功！');
        // Navigate to the dashboard or the new course's detail page
        router.push({ name: 'Dashboard' }); // Or router.push({ name: 'CourseDetail', params: { id: result.data.course_id } });
      } else {
        // Error message is already set in store and displayed by ElAlert
        // ElMessage.error(courseStore.createCourseError || '课程创建失败，请检查输入。');
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
  courseStore.clearCreateCourseError(); // Clear any previous error messages
  form.cover_image = ''; // Explicitly clear non-prop fields if needed
}

onUnmounted(() => {
  courseStore.clearCreateCourseError(); // Clear error when leaving page
});
</script>

<style scoped>
.course-create-container {
  display: flex;
  justify-content: center;
  align-items: flex-start; /* Align to top for longer forms */
  min-height: calc(100vh - 120px);
  background-color: #f0f2f5;
  padding: 20px;
  box-sizing: border-box;
}

.course-create-card {
  width: 100%;
  max-width: 700px; /* Wider card for forms */
  border-radius: 8px;
  animation: fadeInCard 0.5s ease-out;
}

.card-header {
  text-align: center;
  font-size: 1.8em;
  font-weight: bold;
  color: #333;
}

.course-create-form {
  margin-top: 10px;
}

.el-form-item {
  margin-bottom: 22px;
}

.el-date-picker, .el-select {
  width: 100%;
}

.create-button, .reset-button {
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

@keyframes fadeInCard {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
