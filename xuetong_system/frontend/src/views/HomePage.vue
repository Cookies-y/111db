<template>
  <div>
    <h1>首页</h1>
    <p v-if="isAuthenticated">欢迎回来！您的冒险从这里开始。</p>
    <p v-else>请先 <router-link to="/login">登录</router-link> 或 <router-link to="/register">注册</router-link>。</p>

    <nav>
      <router-link to="/dashboard" v-if="isAuthenticated">前往仪表盘</router-link>
    </nav>

    <h2>课程预览（占位）</h2>
    <ul>
      <li>课程1：Vue.js入门</li>
      <li>课程2：Pinia状态管理</li>
      <li>课程3：Element Plus实战</li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue';
// Simplified auth check for template logic.
// In a real app, this would come from a Pinia store.
const isAuthenticated = computed(() => {
  if (typeof window !== 'undefined') {
    return !!localStorage.getItem('accessToken');
  }
  return false;
});
</script>

<style scoped>
h1 {
  color: #42b983;
}
nav a {
  margin-right: 10px;
}
ul {
  list-style: none;
  padding: 0;
}
li {
  background-color: #f5f5f5;
  padding: 8px;
  margin-bottom: 5px;
  border-radius: 4px;
}
</style>
