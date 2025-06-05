<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>用户登录</span>
        </div>
      </template>
      <el-form @submit.prevent="performLogin" :model="form" ref="loginFormRef" label-position="top" class="login-form">
        <el-alert
          v-if="authStore.loginError"
          :title="authStore.loginError"
          type="error"
          show-icon
          :closable="false"
          class="error-alert"
        />
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="form.email"
            placeholder="请输入邮箱地址"
            clearable
            prefix-icon="Message"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
            clearable
            prefix-icon="Lock"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            @click="performLogin"
            :loading="isLoading"
            class="login-button"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="form-footer">
        <router-link to="/register">新用户？点此注册！</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue';
import { useAuthStore } from '../../stores/authStore';
// import { ElMessage } from 'element-plus'; // Can be used for alternative error display

const authStore = useAuthStore();
const form = reactive({
  email: '',
  password: '',
});
const isLoading = ref(false);
// const loginFormRef = ref(null); // For Element Plus form validation rules if needed

// Clear login error when component is unmounted or before a new login attempt
onUnmounted(() => {
  if (authStore.loginError) {
    authStore.loginError = null;
  }
});

async function performLogin() {
  isLoading.value = true;
  // Clear previous error directly in store or action can do it.
  // authStore.loginError = null; // Store action now handles this.

  const success = await authStore.login({ email: form.email, password: form.password });
  isLoading.value = false;

  // The authStore.login action handles navigation on success.
  // If login fails, authStore.loginError will be set and displayed by ElAlert.
  // No need for ElMessage here if ElAlert is used for persistent error display until next attempt.
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px); /* Adjust based on potential header/footer */
  background-color: #f0f2f5;
  padding: 20px;
  box-sizing: border-box;
}

.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 8px; /* Softer edges */
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.login-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); /* Enhanced shadow on hover */
}

.card-header {
  text-align: center;
  font-size: 1.8em; /* Larger header text */
  font-weight: bold;
  color: #333;
}

.login-form {
  margin-top: 10px; /* Space between header and form */
}

.el-form-item {
  margin-bottom: 22px; /* Consistent spacing */
}

.el-input :deep(input) { /* Style input fields */
  height: 40px;
  line-height: 40px;
}

.login-button {
  width: 100%;
  height: 40px;
  font-size: 1em;
  transition: background-color 0.2s ease, transform 0.1s ease; /* Added transform transition */
}

.login-button:hover {
  background-color: #3a8ee6; /* Darker shade for primary */
}

.login-button:active {
  transform: scale(0.98); /* Click effect */
}

.form-footer {
  text-align: center;
  margin-top: 25px;
  font-size: 0.9em;
}

.form-footer a {
  color: #409EFF; /* Element Plus primary color for links */
  text-decoration: none;
  transition: color 0.2s ease;
}

.form-footer a:hover {
  color: #3a8ee6;
  text-decoration: underline;
}

.error-alert {
  margin-bottom: 22px;
  transition: opacity 0.3s ease; /* Animation for error alert */
}

/* Animation for the card appearing (optional) */
.login-card {
  animation: fadeInCard 0.5s ease-out;
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
