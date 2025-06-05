<template>
  <div class="dashboard-container">
    <el-card shadow="never" class="dashboard-card">
      <template #header>
        <div class="card-header">
          <span>仪表盘</span>
        </div>
      </template>

      <div v-if="authStore.isAuthenticated && authStore.user" class="content">
        <p class="welcome-message">
          欢迎回来, <strong>{{ authStore.user.email || '用户' }}</strong>！
        </p>
        <p>
          您的用户ID (来自JWT): <strong>{{ decodedUserId || '无法解析或未登录' }}</strong>
        </p>
        <!--
          Note: authStore.user currently only stores { email: credentials.email } upon login.
          To display user_type or real_name here, the authStore.login action would need to:
          1. Decode the JWT to get claims (if they are included in the token by the backend).
          2. OR, make a separate API call to a '/users/me' endpoint to fetch full user details.
          For now, we'll keep it simple and rely on email and what can be decoded from token.
        -->
        <p>这里是您的仪表盘。后续将在此处展示课程管理、学习进度等内容。</p>

        <div class="quick-actions">
          <h3>快速操作 (占位符)</h3>
          <ul>
            <li><router-link to="/courses-overview">所有课程概览</router-link></li>
            <!-- Example for teacher-specific link -->
            <!-- <li v-if="authStore.user?.user_type_from_token === 'teacher'"><router-link :to="{ name: 'CreateCourse' }">创建新课程</router-link></li> -->
            <li><router-link to="/my-profile">我的资料</router-link></li>
          </ul>
        </div>
      </div>

      <div v-else class="content">
        <!-- This part should ideally not be reached if route guards are working correctly -->
        <el-alert
          title="未授权访问"
          type="warning"
          description="您需要登录才能查看此页面。正在重定向到登录页..."
          show-icon
          :closable="false"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useAuthStore } from '../../stores/authStore';
import { useRouter } // To redirect if needed, though guard should handle it.

const authStore = useAuthStore();
const router = useRouter();

// Attempt to decode user_id from the token for display purposes
const decodedUserId = computed(() => {
  if (authStore.accessToken) {
    try {
      const payloadBase64 = authStore.accessToken.split('.')[1];
      const decodedPayload = JSON.parse(atob(payloadBase64));
      return payloadBase64.sub || 'N/A'; // 'sub' is the standard claim for subject (user ID)
    } catch (e) {
      console.error("Error decoding JWT for display:", e);
      return '解码错误';
    }
  }
  return null;
});

onMounted(() => {
  if (!authStore.isAuthenticated) {
    // This is a fallback, router guard should ideally handle this.
    // router.push({ name: 'Login', query: { redirect: router.currentRoute.value.fullPath } });
    console.warn("Dashboard accessed by unauthenticated user - router guard might need review or this is direct access attempt.");
  }
  // Example: If you wanted to fetch dashboard-specific data
  // fetchDashboardData();
});

// function fetchDashboardData() {
//   console.log("Fetching dashboard data for user:", authStore.user?.email);
//   // apiClient.get('/dashboard-data').then(...)
// }
</script>

<style scoped>
.dashboard-container {
  padding: 2rem;
  background-color: #f9fafb; /* Lighter background for contrast with card */
  flex-grow: 1;
}

.dashboard-card {
  max-width: 900px;
  margin: 0 auto;
  border: none; /* Remove card border if background provides enough contrast */
  border-radius: 8px;
}

.card-header {
  border-bottom: 1px solid #ebeef5; /* Element Plus card header border color */
  padding-bottom: 10px; /* Ensure space for border */
}

.card-header span {
  font-size: 1.6em; /* Larger title */
  font-weight: 600; /* Bolder */
  color: #303133; /* Element Plus primary text color */
}

.content {
  padding: 1rem 0; /* Padding inside card body */
}

.welcome-message {
  font-size: 1.2em;
  color: #333;
  margin-bottom: 1rem;
}

.welcome-message strong {
  color: #409EFF; /* Highlight user email */
}

p {
  line-height: 1.7;
  color: #606266; /* Element Plus secondary text color */
  margin-bottom: 0.8rem;
}

.quick-actions {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e4e7ed;
}

.quick-actions h3 {
  font-size: 1.1em;
  color: #303133;
  margin-bottom: 1rem;
}

.quick-actions ul {
  list-style: none;
  padding: 0;
}

.quick-actions li {
  margin-bottom: 0.5rem;
}

.quick-actions a {
  color: #409EFF;
  text-decoration: none;
  transition: color 0.2s ease;
}

.quick-actions a:hover {
  color: #66b1ff; /* Lighter blue on hover */
  text-decoration: underline;
}

.el-alert {
  margin-top: 1rem;
}
</style>
