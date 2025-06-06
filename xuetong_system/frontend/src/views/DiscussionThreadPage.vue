<template>
  <div class="discussion-thread-container">
    <!-- Loading State -->
    <div v-if="discussionStore.isLoadingThread && !thread" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    <!-- Error State -->
    <el-alert
      v-else-if="discussionStore.fetchThreadError && !thread"
      :title="discussionStore.fetchThreadError"
      type="error"
      description="无法加载讨论串，请稍后再试或返回。"
      show-icon
      :closable="false"
      class="error-alert"
    />
    <!-- Empty State (Thread Not Found) -->
    <div v-else-if="!thread" class="empty-container">
      <el-empty description="未找到该讨论串或已被删除。" />
      <router-link :to="authStore.isAuthenticated ? '/dashboard' : '/'">
        <el-button type="primary">返回仪表盘</el-button>
      </router-link>
    </div>

    <!-- Discussion Thread Content -->
    <div v-else class="thread-content-wrapper">
      <el-breadcrumb separator-icon="ArrowRight" class="page-breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/dashboard' }">仪表盘</el-breadcrumb-item>
        <el-breadcrumb-item v-if="thread.course_id" :to="{ path: `/courses/${thread.course_id}` }">
          课程 {{ thread.course_id }} <!-- TODO: Display actual course name -->
        </el-breadcrumb-item>
        <el-breadcrumb-item>讨论串</el-breadcrumb-item>
      </el-breadcrumb>

      <!-- Main Topic Post -->
      <el-card class="main-post-card" shadow="never">
        <template #header>
          <div class="post-header">
            <h1 class="post-title">{{ thread.title || '无标题讨论' }}</h1>
            <div class="author-info">
              <el-icon><User /></el-icon>
              <span>{{ thread.author?.real_name || thread.author?.username || '匿名用户' }}</span>
              <span class="post-time">发布于: {{ formatDate(thread.post_time) }}</span>
            </div>
          </div>
        </template>
        <div class="post-content" v-html="thread.content?.replace(/\n/g, '<br>')"></div>
      </el-card>

      <!-- Replies Section -->
      <el-divider content-position="left"><h2 class="section-title">回复列表 ({{ thread.reply_count || 0 }})</h2></el-divider>
      <div v-if="thread.replies && thread.replies.length > 0" class="replies-list">
        <el-card v-for="reply in thread.replies" :key="reply.post_id" class="reply-card" shadow="sm">
          <template #header>
            <div class="reply-header author-info">
              <el-icon><User /></el-icon>
              <span>{{ reply.author?.real_name || reply.author?.username || '匿名用户' }}</span>
              <span class="post-time">回复于: {{ formatDate(reply.post_time) }}</span>
            </div>
          </template>
          <div class="post-content" v-html="reply.content?.replace(/\n/g, '<br>')"></div>
          <!-- TODO: Add reply-to-reply button/logic if deeper nesting is desired in future -->
        </el-card>
      </div>
      <el-empty v-else description="暂无回复，快来发表第一个回复吧！" :image-size="80" class="empty-replies"></el-empty>

      <!-- Reply Form -->
      <el-divider />
      <div v-if="authStore.isAuthenticated" class="reply-form-section">
        <h3>发表您的回复</h3>
        <el-form @submit.prevent="handlePostReply" :model="newReply" :rules="replyRules" ref="replyFormRef" label-position="top">
          <el-alert v-if="discussionStore.postReplyError" :title="discussionStore.postReplyError" type="error" show-icon :closable="false" @close="discussionStore.clearPostReplyError()" class="error-alert" />
          <el-form-item label="回复内容" prop="content">
            <el-input v-model="newReply.content" type="textarea" :rows="4" placeholder="请输入您的回复..." />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handlePostReply" :loading="discussionStore.isPostingReply" :icon="ChatLineRound">
              发表回复
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      <div v-else>
        <el-alert title="请先登录以发表回复。" type="info" show-icon :closable="false">
          <router-link :to="{name: 'Login', query: {redirect: route.fullPath}}"><el-button type="primary" plain>前往登录</el-button></router-link>
        </el-alert>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore'; // Corrected path
import { useDiscussionStore } from '../stores/discussionStore'; // Corrected path
import { ElMessage } from 'element-plus';
import { ArrowRight, User, ChatLineRound } from '@element-plus/icons-vue'; // Import necessary icons

const route = useRoute();
const router = useRouter(); // If needed for navigation
const authStore = useAuthStore();
const discussionStore = useDiscussionStore();

const postId = computed(() => parseInt(route.params.post_id)); // Assuming route is /discussions/:post_id
const thread = computed(() => discussionStore.getThread);

const newReply = reactive({ content: '' });
const replyFormRef = ref(null);

const replyRules = reactive({
  content: [
    { required: true, message: '回复内容不能为空', trigger: 'blur' },
    { min: 1, message: '回复内容不能为空', trigger: 'blur' } // Min length 1 ensures not just whitespace
  ],
});

const fetchData = async () => {
  if (postId.value) {
    await discussionStore.fetchDiscussionThread(postId.value);
  }
};

onMounted(() => {
  fetchData();
});

onUnmounted(() => {
  discussionStore.clearDiscussionThread();
});

watch(() => route.params.post_id, (newIdStr) => {
  const newId = newIdStr ? parseInt(newIdStr) : null;
  if (newId && newId !== postId.value) {
    fetchData();
  } else if (!newId && postId.value) { // Navigated away from a valid postId
    discussionStore.clearDiscussionThread();
  }
}, { immediate: false });


const formatDate = (dateString) => dateString ? new Date(dateString).toLocaleString('zh-CN', { dateStyle: 'medium', timeStyle: 'short' }) : 'N/A';

async function handlePostReply() {
  if (!replyFormRef.value) return;
  await replyFormRef.value.validate(async (valid) => {
    if (valid) {
      if (!thread.value) { // Should not happen if form is visible
        ElMessage.error('无法找到当前讨论主题。');
        return;
      }
      const result = await discussionStore.postReply(thread.value.post_id, { content: newReply.content });
      if (result.success) {
        ElMessage.success('回复成功！');
        newReply.content = ''; // Clear form
        // The store action fetchDiscussionThread is called on success to refresh the thread
      }
      // Error is displayed by ElAlert via reactive store property if set up, or ElMessage.error
      else if (discussionStore.postReplyError) {
        // ElMessage.error(discussionStore.postReplyError); // Already shown by ElAlert
      } else {
        ElMessage.error('回复失败，请稍后再试。');
      }
    } else {
      ElMessage.error('请检查您输入的回复内容。');
      return false;
    }
  });
}
</script>

<style scoped>
.discussion-thread-container { padding: 20px; background-color: #f9fafb; }
.loading-container, .empty-container { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 200px; }
.error-alert { margin-bottom: 20px; }
.page-breadcrumb { margin-bottom: 20px; font-size: 0.9em; }

.main-post-card { border-radius: 8px; margin-bottom: 25px; }
.post-header { /* For main post and replies */ }
.post-title { font-size: 1.8em; font-weight: 600; color: #303133; margin: 0 0 10px 0; }
.author-info { display: flex; align-items: center; color: #606266; font-size: 0.9em; margin-bottom: 10px; }
.author-info .el-icon { margin-right: 5px; }
.post-time { margin-left: auto; /* Pushes time to the right */ font-style: italic; }
.post-content { white-space: pre-wrap; color: #333; line-height: 1.7; font-size: 1em; padding: 10px 0; }

.section-title { font-size: 1.4em; font-weight: 600; color: #303133; margin-top: 0; }
.replies-list .reply-card { margin-bottom: 15px; background-color: #fff; border-left: 3px solid #a0cfff; } /* Slightly different for replies */
.reply-header { font-size: 1em; } /* Slightly smaller for reply authors */
.empty-replies { margin-top: 15px; }

.reply-form-section { margin-top: 25px; }
.reply-form-section h3 { font-size: 1.2em; margin-bottom: 15px; }
.el-form-item { margin-bottom: 20px; }
</style>
