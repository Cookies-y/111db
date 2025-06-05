<template>
  <div class="admin-dashboard-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>管理后台首页</span>
        </div>
      </template>
      <p>欢迎来到管理员控制面板。</p>
      <p>您可以在这里管理系统的各个方面，例如用户、课程、以及其他设置。</p>
      <p>请使用左侧的导航菜单开始操作。</p>
    </el-card>
  </div>
</template>

<script setup>
// No specific script logic needed for this placeholder
</script>

<style scoped>
.admin-dashboard-page {
  padding: 10px; /* Minimal padding as content is in card */
}
.card-header span {
  font-size: 1.2em;
  font-weight: bold;
}
p {
  line-height: 1.6;
  margin-bottom: 10px;
}
</style>
