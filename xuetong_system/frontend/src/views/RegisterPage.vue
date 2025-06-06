<template>
  <div class="register-container">
    <el-card class="register-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>用户注册</span>
        </div>
      </template>
      <el-form
        @submit.prevent="submitForm"
        :model="form"
        :rules="rules"
        ref="formRef"
        label-position="top"
        class="register-form"
      >
        <el-alert
          v-if="authStore.registrationError"
          :title="authStore.registrationError"
          type="error"
          show-icon
          :closable="false"
          class="error-alert"
        />
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" clearable prefix-icon="User" />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入真实姓名" clearable prefix-icon="Document" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" type="email" placeholder="请输入邮箱地址" clearable prefix-icon="Message" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password clearable prefix-icon="Lock" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="form.confirm_password" type="password" placeholder="请再次输入密码" show-password clearable prefix-icon="Lock" />
        </el-form-item>
        <el-form-item label="账户类型" prop="user_type">
          <el-select v-model="form.user_type" placeholder="请选择账户类型" style="width: 100%;">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="isLoading" class="register-button">
            注册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="form-footer">
        <router-link to="/login">已有账户？点此登录！</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue';
import { useAuthStore } from '../stores/authStore'; // Corrected path
// import { ElMessage } from 'element-plus'; // Optional for success/error notifications

const authStore = useAuthStore();
const formRef = ref(null); // To access Element Plus form instance for validation

const form = reactive({
  username: '',
  email: '',
  real_name: '',
  password: '',
  confirm_password: '',
  user_type: 'student', // Default value
});

const isLoading = ref(false);

// Custom validator for confirm_password
const validatePassConfirm = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致!'));
  } else {
    callback();
  }
};

const rules = reactive({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePassConfirm, trigger: 'blur' }
  ],
  user_type: [{ required: true, message: '请选择账户类型', trigger: 'change' }]
});

async function submitForm() {
  if (!formRef.value) return;
  // Clear previous errors from store before new validation attempt
  if (authStore.registrationError) {
      authStore.registrationError = null;
  }

  await formRef.value.validate(async (valid) => {
    if (valid) {
      isLoading.value = true;
      const success = await authStore.register({
        username: form.username,
        email: form.email,
        real_name: form.real_name,
        password: form.password,
        user_type: form.user_type,
      });
      isLoading.value = false;

      // Navigation is handled by the store action on success (to login page)
      // If registration fails, authStore.registrationError will be set and displayed by ElAlert
      // if (success) {
      //   ElMessage.success('注册成功！请登录。'); // Optional success message
      // }
    } else {
      console.log('Form validation failed. Please check the inputs.');
      // ElMessage.error('请检查您输入的信息。'); // Optional generic validation error message
      return false;
    }
  });
}

// Clear registration error when component is unmounted
onUnmounted(() => {
  if (authStore.registrationError) {
    authStore.registrationError = null;
  }
});
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px); /* Adjust based on potential header/footer */
  background-color: #f0f2f5;
  padding: 20px;
  box-sizing: border-box;
}

.register-card {
  width: 100%;
  max-width: 450px; /* Slightly wider for more fields */
  border-radius: 8px;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  animation: fadeInCard 0.5s ease-out; /* From login page */
}

.register-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-header {
  text-align: center;
  font-size: 1.8em;
  font-weight: bold;
  color: #333;
}

.register-form {
  margin-top: 10px;
}

.el-form-item {
  margin-bottom: 18px; /* Adjusted for more fields */
}

.el-input :deep(input), .el-select :deep(input) {
  height: 40px;
  line-height: 40px;
}

.register-button {
  width: 100%;
  height: 40px;
  font-size: 1em;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.register-button:hover {
  background-color: #3a8ee6;
}

.register-button:active {
  transform: scale(0.98);
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 0.9em;
}

.form-footer a {
  color: #409EFF;
  text-decoration: none;
  transition: color 0.2s ease;
}

.form-footer a:hover {
  color: #3a8ee6;
  text-decoration: underline;
}

.error-alert {
  margin-bottom: 18px;
  transition: opacity 0.3s ease;
}

@keyframes fadeInCard { /* From login page */
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
