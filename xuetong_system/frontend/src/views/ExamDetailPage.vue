<template>
  <div class="exam-detail-container">
    <!-- Loading State for Exam Detail -->
    <div v-if="examStore.isLoadingExamDetail && !exam" class="loading-container">
      <el-skeleton :rows="12" animated />
    </div>
    <!-- Error State for Exam Detail -->
    <el-alert
      v-else-if="examStore.fetchExamDetailError && !exam"
      :title="examStore.fetchExamDetailError"
      type="error"
      description="无法加载考试详情，请检查网络或稍后再试。"
      show-icon
      :closable="false"
      class="error-alert"
    />
    <!-- Empty State (Exam Not Found) -->
    <div v-else-if="!exam" class="empty-container">
      <el-empty description="未找到该考试信息或已被删除。" />
      <router-link :to="authStore.isAuthenticated ? '/dashboard' : '/'">
        <el-button type="primary">返回仪表盘</el-button>
      </router-link>
    </div>

    <!-- Exam Detail Content -->
    <div v-else class="exam-content-wrapper">
      <el-breadcrumb separator-icon="ArrowRight" class="page-breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/dashboard' }">仪表盘</el-breadcrumb-item>
        <el-breadcrumb-item v-if="exam.course_id" :to="{ path: `/courses/${exam.course_id}` }">
          课程 {{ exam.course_id }} <!-- TODO: Display course name -->
        </el-breadcrumb-item>
        <el-breadcrumb-item>{{ exam.exam_name }}</el-breadcrumb-item>
      </el-breadcrumb>

      <el-card class="exam-main-card" shadow="never">
        <template #header>
          <div class="exam-main-header">
            <h1 class="exam-title">{{ exam.exam_name }}</h1>
            <el-tag :type="currentExamStatus.tagType" size="large">{{ currentExamStatus.text }}</el-tag>
          </div>
        </template>
        <div class="exam-description" v-html="exam.description?.replace(/\n/g, '<br>') || '暂无详细描述。'"></div>
        <el-row :gutter="20" class="exam-meta-info">
          <el-col :xs="24" :sm="12">
            <p><strong><el-icon><Calendar /></el-icon> 开始时间:</strong> {{ formatDate(exam.start_time) }}</p>
            <p><strong><el-icon><Calendar /></el-icon> 结束时间:</strong> {{ formatDate(exam.end_time) }}</p>
          </el-col>
          <el-col :xs="24" :sm="12">
            <p><strong><el-icon><Clock /></el-icon> 考试时长:</strong> {{ exam.duration }} 分钟</p>
            <p><strong><el-icon><StarFilled /></el-icon> 总分:</strong> {{ exam.total_score }}</p>
          </el-col>
        </el-row>
      </el-card>

      <el-divider />

      <!-- Student View -->
      <div v-if="!isTeacher" class="student-view">
        <el-card shadow="sm" class="submission-card">
          <template #header><h3>我的考试状态</h3></template>
          <div v-if="hasStudentSubmitted">
            <h4>您已完成本次考试:</h4>
            <el-descriptions :column="1" border class="submission-details">
              <el-descriptions-item label="提交时间">{{ formatDate(studentOwnResult.submit_time) }}</el-descriptions-item>
              <el-descriptions-item label="您的得分">
                <el-tag :type="studentOwnResult.score >= (exam.total_score * 0.6) ? 'success' : 'warning'">
                  {{ studentOwnResult.score }} / {{ exam.total_score }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
          <div v-else-if="!isExamActive && !isExamUpcoming">
             <el-alert title="考试已结束" description="抱歉，本次考试已结束，您未提交成绩。" type="warning" show-icon :closable="false" />
          </div>
           <div v-else-if="isExamUpcoming">
             <el-alert title="考试未开始" :description="`本次考试将于 ${formatDate(exam.start_time)} 开始。`" type="info" show-icon :closable="false" />
          </div>
          <div v-else-if="isExamActive && !hasStudentSubmitted">
            <h4>提交您的考试成绩 (MVP):</h4>
            <el-form @submit.prevent="handleStudentSubmitScore" :model="studentScoreForm" :rules="studentScoreRules" ref="studentScoreFormRef" label-position="top">
              <el-alert v-if="examStore.submitExamResultError" :title="examStore.submitExamResultError" type="error" show-icon :closable="false" @close="examStore.clearSubmitExamResultError()" class="error-alert"/>
              <el-form-item label="您的得分" prop="score">
                <el-input-number v-model="studentScoreForm.score" :min="0" :max="exam.total_score" placeholder="输入您的得分" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleStudentSubmitScore" :loading="examStore.isSubmittingExamResult">确认提交成绩</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </div>

      <!-- Teacher View -->
      <div v-if="isTeacher" class="teacher-view">
        <el-card shadow="sm">
          <template #header><h3>学生作答情况</h3></template>
          <div v-if="examStore.isLoadingExamResults || (examStore.isLoadingExamDetail && !resultsForTeacher.length)" class="loading-container">
            <el-skeleton :rows="3" animated />
          </div>
          <el-alert v-else-if="examStore.fetchExamResultsError" :title="examStore.fetchExamResultsError" type="error" show-icon :closable="false" />
          <el-empty v-else-if="!resultsForTeacher || resultsForTeacher.length === 0" description="暂无学生提交考试结果。" />
          <el-table v-else :data="resultsForTeacher" stripe style="width: 100%" class="results-table">
            <el-table-column prop="student.real_name" label="学生姓名" sortable />
            <el-table-column prop="student.username" label="用户名" sortable />
            <el-table-column prop="submit_time" label="提交时间" sortable :formatter="row => formatDate(row.submit_time)" />
            <el-table-column prop="score" label="得分" sortable />
            <el-table-column label="操作" fixed="right" width="120">
              <template #default="scope">
                <el-button size="small" type="primary" :icon="EditPen" @click="openGradingModal(scope.row)">批改</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>

    <!-- Grading Modal for Teacher -->
    <el-dialog v-model="gradingModalVisible" title="批改考试成绩" width="500px" :before-close="handleCloseGradingModal">
      <div v-if="selectedResultForGrading">
        <el-descriptions :column="1" border class="submission-details">
            <el-descriptions-item label="学生">{{ selectedResultForGrading.student?.real_name }} ({{selectedResultForGrading.student?.username }})</el-descriptions-item>
            <el-descriptions-item label="当前得分">{{ selectedResultForGrading.score === null ? '未评分' : selectedResultForGrading.score }} / {{ exam?.total_score }}</el-descriptions-item>
        </el-descriptions>
        <el-divider/>
        <el-form :model="gradeForm" :rules="gradingRules" ref="gradeFormRef" label-position="top">
          <el-form-item label="新分数" prop="score">
            <el-input-number v-model="gradeForm.score" :min="0" :max="exam?.total_score || 100" />
          </el-form-item>
          <!-- Add feedback field if backend supports it for exam results -->
        </el-form>
        <el-alert v-if="examStore.updateExamResultError" :title="examStore.updateExamResultError" type="error" show-icon style="margin-top:10px;" @close="examStore.clearUpdateExamResultError()" />
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="gradingModalVisible = false">取消</el-button>
          <el-button type="primary" @click="handleGradeSubmit" :loading="examStore.isUpdatingExamResult">提交评分</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';
import { useExamStore } from '../../stores/examStore';
import { ElMessage, ElDialog, ElDescriptions, ElDescriptionsItem } from 'element-plus'; // Added ElDialog, ElDescriptions, ElDescriptionsItem
import { ArrowRight, User, Calendar, Clock, StarFilled, EditPen } from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const examStore = useExamStore();

const examId = computed(() => parseInt(route.params.id));
const exam = computed(() => examStore.currentExamDetail);
const resultsForTeacher = computed(() => examStore.examResultsForTeacher);
const studentOwnResult = computed(() => examStore.studentOwnResult);

const studentScoreFormRef = ref(null);
const studentScoreForm = reactive({ score: null });

// Grading Modal State
const gradingModalVisible = ref(false);
const selectedResultForGrading = ref(null);
const gradeFormRef = ref(null);
const gradeForm = reactive({ score: null });


const isTeacher = computed(() => {
  return authStore.isAuthenticated && authStore.user?.user_type === 2;
});

const now = ref(new Date());
let timer = null;

const currentExamStatus = computed(() => {
  if (!exam.value || !exam.value.start_time || !exam.value.end_time) {
    return { text: '状态未知', tagType: 'info' };
  }
  const startTime = new Date(exam.value.start_time);
  const endTime = new Date(exam.value.end_time);
  const currentTime = now.value;
  if (currentTime < startTime) return { text: '未开始', tagType: 'info' };
  if (currentTime > endTime) return { text: '已结束', tagType: 'danger' };
  return { text: '进行中', tagType: 'success' };
});

const isExamActive = computed(() => currentExamStatus.value.text === '进行中');
const isExamUpcoming = computed(() => currentExamStatus.value.text === '未开始');
const hasStudentSubmitted = computed(() => !!studentOwnResult.value && studentOwnResult.value.exam_id === examId.value);

const studentScoreRules = computed(() => ({
  score: [
    { required: true, message: '请输入您的得分', trigger: 'blur' },
    { type: 'number', message: '得分必须是数字', trigger: 'blur' },
    { validator: (rule, value, callback) => {
        if (value === null || value === undefined) callback(new Error('请输入分数'));
        else if (value < 0) callback(new Error('分数不能为负'));
        else if (exam.value && value > exam.value.total_score) callback(new Error(`分数不能超过总分 ${exam.value.total_score}`));
        else callback();
      }, trigger: 'blur'
    }
  ],
}));

const gradingRules = computed(() => ({ // Computed to access exam.value.total_score
    score: [
        { required: true, message: '请输入分数', trigger: 'blur' },
        { type: 'number', message: '分数必须是数字', trigger: 'blur' },
        { validator: (rule, value, callback) => {
            if (value === null || value === undefined) callback(new Error('请输入分数'));
            else if (value < 0) callback(new Error('分数不能为负'));
            else if (exam.value && value > exam.value.total_score) callback(new Error(`分数不能超过总分 ${exam.value.total_score}`));
            else callback();
          }, trigger: 'blur'
        }
    ]
}));


const fetchData = async () => {
  if (examId.value) {
    await examStore.fetchExamDetail(examId.value);
    if (isTeacher.value && examStore.currentExamDetail) {
      // Assuming fetchExamDetail for teacher might already include results.
      // If not, or to refresh results explicitly:
      await examStore.fetchResultsForExam(examId.value);
    }
  }
};

onMounted(() => {
  fetchData();
  timer = setInterval(() => { now.value = new Date(); }, 1000);
});

onUnmounted(() => {
  examStore.clearExamDetail();
  examStore.clearSubmitExamResultError();
  examStore.clearUpdateExamResultError();
  if (timer) clearInterval(timer);
});

watch(() => route.params.id, (newIdStr) => {
  const newId = newIdStr ? parseInt(newIdStr) : null;
  if (newId && newId !== examId.value) {
    fetchData();
  } else if (!newId && examId.value) {
    examStore.clearExamDetail();
  }
}, { immediate: false });


const formatDate = (dateString) => dateString ? new Date(dateString).toLocaleString('zh-CN', {dateStyle: 'medium', timeStyle: 'short'}) : 'N/A';

async function handleStudentSubmitScore() {
  if (!studentScoreFormRef.value) return;
  await studentScoreFormRef.value.validate(async (valid) => {
    if (valid) {
      const result = await examStore.submitExamResult(examId.value, { score: studentScoreForm.score });
      if (result.success) {
        ElMessage.success('考试成绩提交成功！');
        await examStore.fetchExamDetail(examId.value);
      }
    } else { ElMessage.error('请检查您输入的成绩。'); }
  });
}

function openGradingModal(result) {
  selectedResultForGrading.value = { ...result };
  gradeForm.score = result.score !== null ? result.score : null;
  examStore.clearUpdateExamResultError(); // Clear previous errors
  gradingModalVisible.value = true;
}

function handleCloseGradingModal() {
    gradingModalVisible.value = false;
    selectedResultForGrading.value = null; // Clear selection
    if (gradeFormRef.value) gradeFormRef.value.resetFields(); // Reset validation
    gradeForm.score = null; // Reset form data
}

async function handleGradeSubmit() {
  if (!gradeFormRef.value) return;
  await gradeFormRef.value.validate(async (valid) => {
    if (valid) {
      const result = await examStore.updateExamResult(selectedResultForGrading.value.result_id, { score: gradeForm.score });
      if (result.success) {
        ElMessage.success('评分更新成功！');
        gradingModalVisible.value = false;
        // The store action should update the list reactively.
        // If not, explicitly call: await examStore.fetchResultsForExam(examId.value);
      }
      // Error is displayed by ElAlert in modal via reactive store property
    } else { ElMessage.error('请检查评分信息。'); }
  });
}
</script>

<style scoped>
.exam-detail-container { padding: 20px; background-color: #f9fafb; }
.loading-container, .empty-container { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 200px; }
.error-alert { margin-bottom: 20px; }
.page-breadcrumb { margin-bottom: 20px; font-size: 0.9em; }
.exam-main-card { border-radius: 8px; margin-bottom: 20px; }
.exam-main-header { display: flex; justify-content: space-between; align-items: center; }
.exam-title { font-size: 1.8em; font-weight: 600; color: #303133; margin: 0; }
.exam-description { white-space: pre-wrap; margin: 15px 0; color: #555; line-height: 1.7; font-size: 1em; }
.exam-meta-info p { margin: 8px 0; color: #606266; font-size: 0.95em; display: flex; align-items: center; }
.exam-meta-info .el-icon { margin-right: 8px; font-size: 1.1em; }
.submission-card, .teacher-view .el-card { margin-top: 20px; }
.submission-details .el-descriptions-item__label { font-weight: bold; }
.submission-details .el-descriptions-item__content { color: #333; }
.results-table { margin-top: 15px; }
.el-table th.el-table__cell { background-color: #f5f7fa !important; }
.grading-modal-content .el-descriptions { margin-bottom: 20px; }
.grading-modal-content h3 { margin-top: 0; margin-bottom: 15px; font-size: 1.2em; }
</style>
