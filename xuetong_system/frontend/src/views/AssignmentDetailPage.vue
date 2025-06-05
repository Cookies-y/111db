<template>
  <div class="assignment-detail-container">
    <!-- Loading State for Assignment Detail -->
    <div v-if="assignmentStore.isLoadingAssignmentDetail" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    <!-- Error State for Assignment Detail -->
    <el-alert
      v-else-if="assignmentStore.fetchAssignmentDetailError"
      :title="assignmentStore.fetchAssignmentDetailError"
      type="error"
      description="无法加载作业详情，请稍后再试或返回。"
      show-icon
      :closable="false"
      class="error-alert"
    />
    <!-- Empty State for Assignment Detail -->
    <div v-else-if="!assignment" class="empty-container">
      <el-empty description="未找到作业信息。" />
      <router-link :to="authStore.isAuthenticated ? '/dashboard' : '/'">
        <el-button type="primary">返回</el-button>
      </router-link>
    </div>

    <!-- Assignment Detail Content -->
    <div v-else class="assignment-content-wrapper">
      <el-breadcrumb separator-icon="ArrowRight" class="page-breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/dashboard' }">仪表盘</el-breadcrumb-item>
        <el-breadcrumb-item v-if="assignment.course_id" :to="{ path: `/courses/${assignment.course_id}` }">
          课程 {{ assignment.course_id }}
        </el-breadcrumb-item>
        <el-breadcrumb-item>{{ assignment.title }}</el-breadcrumb-item>
      </el-breadcrumb>

      <el-card class="assignment-main-card" shadow="never">
        <template #header>
          <div class="assignment-main-header">
            <h1 class="assignment-title">{{ assignment.title }}</h1>
            <el-tag size="large">总分: {{ assignment.total_score }}</el-tag>
          </div>
        </template>
        <p class="assignment-description" v-html="assignment.description?.replace(/\n/g, '<br>') || '暂无描述。'"></p>
        <p><strong>截止日期:</strong> {{ formatDate(assignment.deadline) }}</p>
        <p><strong>创建时间:</strong> {{ formatDate(assignment.create_time) }}</p>
      </el-card>

      <el-divider />

      <!-- Student View: Submission Form or Existing Submission -->
      <div v-if="!isTeacher" class="student-view">
        <el-card shadow="sm" class="submission-card">
          <template #header><h3>我的提交</h3></template>
          <div v-if="studentSubmission">
            <h4>您已提交作业:</h4>
            <p><strong>提交时间:</strong> {{ formatDate(studentSubmission.submit_time) }}</p>
            <p><strong>内容:</strong></p>
            <div class="submission-content" v-html="studentSubmission.content?.replace(/\n/g, '<br>')"></div>
            <p v-if="studentSubmission.attachment_url">
              <strong>附件:</strong> <el-link :href="studentSubmission.attachment_url" target="_blank" type="primary">{{ studentSubmission.attachment_url }}</el-link>
            </p>
            <div v-if="studentSubmission.score !== null" class="grade-info">
              <el-divider content-position="left">评分结果</el-divider>
              <p><strong>分数:</strong> {{ studentSubmission.score }} / {{ assignment.total_score }}</p>
              <p><strong>教师评语:</strong></p>
              <div class="feedback-content" v-html="studentSubmission.feedback?.replace(/\n/g, '<br>') || '暂无评语。'"></div>
            </div>
            <el-alert v-else title="您的作业尚未评分。" type="info" show-icon :closable="false" style="margin-top:15px;" />
          </div>
          <div v-else-if="isPastDeadline">
             <el-alert title="已过截止日期" description="抱歉，该作业的提交截止日期已过。" type="warning" show-icon :closable="false" />
          </div>
          <div v-else>
            <h4>提交您的作业:</h4>
            <el-form @submit.prevent="handleStudentSubmit" :model="submissionForm" :rules="submissionRules" ref="submissionFormRef" label-position="top">
              <el-alert v-if="assignmentStore.submitError" :title="assignmentStore.submitError" type="error" show-icon :closable="false" @close="assignmentStore.clearSubmitError()" />
              <el-form-item label="提交内容" prop="content">
                <el-input v-model="submissionForm.content" type="textarea" :rows="5" placeholder="请输入作业内容" />
              </el-form-item>
              <el-form-item label="附件链接 (可选)" prop="attachment_url">
                <el-input v-model="submissionForm.attachment_url" placeholder="请输入附件URL" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleStudentSubmit" :loading="assignmentStore.isSubmitting">提交作业</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </div>

      <!-- Teacher View: List of Submissions -->
      <div v-if="isTeacher" class="teacher-view">
        <el-card shadow="sm">
          <template #header><h3>学生提交列表</h3></template>
          <div v-if="assignmentStore.isLoadingSubmissions" class="loading-container">
            <el-skeleton :rows="3" animated />
          </div>
          <el-alert v-else-if="assignmentStore.fetchSubmissionsError" :title="assignmentStore.fetchSubmissionsError" type="error" show-icon />
          <el-empty v-else-if="!submissions || submissions.length === 0" description="暂无学生提交此作业。" />
          <el-table v-else :data="submissions" stripe style="width: 100%">
            <el-table-column prop="student.real_name" label="学生姓名" sortable width="150" />
            <el-table-column prop="student.username" label="用户名" sortable width="150" />
            <el-table-column prop="submit_time" label="提交时间" sortable :formatter="row => formatDate(row.submit_time)" width="180" />
            <el-table-column prop="score" label="得分" sortable width="100">
              <template #default="scope">
                {{ scope.row.score === null ? '未评分' : scope.row.score }}
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="120">
              <template #default="scope">
                <el-button size="small" type="primary" @click="openGradingModal(scope.row)">查看/评分</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>

    <!-- Grading Modal -->
    <el-dialog v-model="gradingModalVisible" title="批改作业" width="60%" :before-close="handleCloseGradingModal">
      <div v-if="selectedSubmission" class="grading-modal-content">
        <el-descriptions title="提交详情" :column="1" border>
          <el-descriptions-item label="学生姓名">{{ selectedSubmission.student?.real_name }} ({{ selectedSubmission.student?.username }})</el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ formatDate(selectedSubmission.submit_time) }}</el-descriptions-item>
          <el-descriptions-item label="提交内容">
            <div class="submission-content-modal" v-html="selectedSubmission.content?.replace(/\n/g, '<br>')"></div>
          </el-descriptions-item>
          <el-descriptions-item label="附件" v-if="selectedSubmission.attachment_url">
            <el-link :href="selectedSubmission.attachment_url" target="_blank" type="primary">{{ selectedSubmission.attachment_url }}</el-link>
          </el-descriptions-item>
          <el-descriptions-item label="附件" v-else>无</el-descriptions-item>
        </el-descriptions>

        <el-divider />
        <h3>评分</h3>
        <el-form :model="gradeForm" :rules="gradeRules" ref="gradeFormRef" label-position="top">
          <el-form-item label="分数" prop="score">
            <el-input-number v-model="gradeForm.score" :min="0" :max="assignment?.total_score || 100" /> / {{ assignment?.total_score || 100 }}
          </el-form-item>
          <el-form-item label="评语 (可选)" prop="feedback">
            <el-input v-model="gradeForm.feedback" type="textarea" :rows="4" placeholder="请输入评语..." />
          </el-form-item>
        </el-form>
        <el-alert v-if="assignmentStore.gradeError" :title="assignmentStore.gradeError" type="error" show-icon style="margin-top:10px;" @close="assignmentStore.clearGradeError()" />
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="gradingModalVisible = false">取消</el-button>
          <el-button type="primary" @click="handleGradeSubmit" :loading="assignmentStore.isGrading">提交评分</el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';
import { useAssignmentStore } from '../../stores/assignmentStore';
import { ElMessage, ElMessageBox } from 'element-plus'; // ElMessageBox for confirm dialog
import { ArrowRight, User, Calendar, Clock, Document as DocIcon, VideoCamera, Link as LinkIconElem } from '@element-plus/icons-vue'; // Renamed Link to LinkIconElem

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const assignmentStore = useAssignmentStore();

const assignmentId = computed(() => parseInt(route.params.id, 10));
const assignment = computed(() => assignmentStore.getAssignmentDetails);
const submissions = computed(() => assignmentStore.getSubmissions);

const submissionFormRef = ref(null);
const submissionForm = reactive({ content: '', attachment_url: '' });

const gradingModalVisible = ref(false);
const selectedSubmission = ref(null);
const gradeFormRef = ref(null);
const gradeForm = reactive({ score: null, feedback: '' });

const isTeacher = computed(() => authStore.isAuthenticated && authStore.user?.user_type === 2);

const studentSubmission = computed(() => {
  if (!authStore.isAuthenticated || !authStore.user || !submissions.value || submissions.value.length === 0) {
    // If submissions are only fetched for teachers, a student needs another way to see their submission.
    // This assumes `submissions` might contain the student's own submission if fetched.
    // A dedicated `mySubmissionForAssignment` state in store might be better.
    // For now, if student has submitted, we expect the API to have returned it somehow or form is hidden.
    // The current logic in `fetchData` doesn't populate `submissions` for students.
    // This computed will likely be null for students unless `fetchSubmissionsForAssignment` is called for them too (and returns only their submission).
    // Let's assume for now, if a submission was made, the page reloaded and `fetchData` got it.
    // Or, after student submits, we store the result in a different reactive variable.
    // For simplicity here: if a student has just submitted successfully, the page re-fetches.
    // If API for GET /assignments/:id/submissions was made accessible to students for *their own* submission, this would work.
    // Given current backend, student only sees submission if they know its ID and go to /submissions/:submission_id.
    // This page is /assignments/:id. So student view of *existing* submission needs a dedicated fetch.
    // For now, this will show the form if no submission is found via the teacher-centric submission list.
    // This means a student might not see their submission here after submitting unless there's a page refresh AND
    // `fetchSubmissionsForAssignment` is modified to be callable by students for their own items.
    // For now, the UI will show the form again after submission unless the `fetchData` after submit somehow populates `studentSubmission`.
    // The `submitToAssignment` action should probably update a `currentStudentSubmission` state.
    return assignmentStore.submissionsForCurrentAssignment.find(sub => sub.student.user_id === authStore.user?.user_id);
  }
  return null; // Fallback
});


const isPastDeadline = computed(() => {
    if (!assignment.value || !assignment.value.deadline) return false;
    return new Date() > new Date(assignment.value.deadline);
});

const submissionRules = reactive({
  content: [{ required: true, message: '请输入提交内容', trigger: 'blur' }],
  attachment_url: [{ type: 'url', message: '请输入有效的URL', trigger: 'blur' }],
});

const gradeRules = reactive({
  score: [
    { required: true, message: '请输入分数', trigger: 'blur' },
    { type: 'number', message: '分数必须是数字', trigger: 'blur' },
    { validator: (rule, value, callback) => {
        if (value < 0) callback(new Error('分数不能为负'));
        else if (assignment.value && value > assignment.value.total_score) callback(new Error(`分数不能超过总分 ${assignment.value.total_score}`));
        else callback();
      }, trigger: 'blur'
    }
  ],
  feedback: [{ required: false }]
});

const fetchData = async () => {
  if (assignmentId.value) {
    await assignmentStore.fetchAssignmentDetail(assignmentId.value);
    if (isTeacher.value && assignmentStore.currentAssignmentDetail) {
      await assignmentStore.fetchSubmissionsForAssignment(assignmentId.value);
    }
    // Student specific fetch for their submission if needed for this page:
    // if (!isTeacher.value && authStore.isAuthenticated && assignmentStore.currentAssignmentDetail) {
    //   // This would require a new store action and API endpoint like /assignments/:id/my-submission
    //   // await assignmentStore.fetchMySubmissionForAssignment(assignmentId.value);
    //   // For now, studentSubmission relies on submissions list or what happens after they submit.
    // }
  }
};

onMounted(() => { fetchData(); });
onUnmounted(() => { assignmentStore.clearAssignmentDetail(); assignmentStore.clearSubmitError(); assignmentStore.clearGradeError(); });
watch(() => route.params.id, (newId) => { if (newId && parseInt(newId, 10) !== assignmentId.value) fetchData(); }, { immediate: true });

const formatDate = (dateString) => dateString ? new Date(dateString).toLocaleString() : 'N/A';

async function handleStudentSubmit() {
  if (!submissionFormRef.value) return;
  await submissionFormRef.value.validate(async (valid) => {
    if (valid) {
      const result = await assignmentStore.submitToAssignment(assignmentId.value, { ...submissionForm });
      if (result.success) {
        ElMessage.success('作业提交成功！');
        submissionForm.content = ''; // Clear form
        submissionForm.attachment_url = '';
        await fetchData(); // Re-fetch to show their submission (assuming student can see their own via modified logic or endpoint)
      }
    } else { ElMessage.error('请检查您输入的信息。'); }
  });
}

function openGradingModal(submission) {
  selectedSubmission.value = { ...submission }; // Clone to avoid direct mutation if not intended
  gradeForm.score = submission.score !== null ? submission.score : null;
  gradeForm.feedback = submission.feedback || '';
  assignmentStore.clearGradeError(); // Clear previous errors
  gradingModalVisible.value = true;
}

function handleCloseGradingModal() {
    gradingModalVisible.value = false;
    // Optionally reset form if not submitted:
    // if (gradeFormRef.value) gradeFormRef.value.resetFields();
    // selectedSubmission.value = null; // Already cleared/reset by closing
}

async function handleGradeSubmit() {
  if (!gradeFormRef.value) return;
  await gradeFormRef.value.validate(async (valid) => {
    if (valid) {
      const result = await assignmentStore.gradeSubmission(selectedSubmission.value.submission_id, { ...gradeForm });
      if (result.success) {
        ElMessage.success('评分成功！');
        gradingModalVisible.value = false;
        // The store action already updates the submission in the list, so UI should reflect.
        // If not, uncomment: await assignmentStore.fetchSubmissionsForAssignment(assignmentId.value);
      }
    } else { ElMessage.error('请检查评分信息。'); }
  });
}

// Icons for material types (not used in this component directly, but kept if expanding)
// const getMaterialIcon = (materialType) => {
//   if (materialType === 1) return VideoCamera;
//   if (materialType === 2) return DocIcon;
//   if (materialType === 3) return LinkIconElem;
//   return DocIcon;
// };
</script>

<style scoped>
.assignment-detail-container { padding: 20px; background-color: #f9fafb; }
.loading-container, .empty-container { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 200px; }
.error-alert { margin-bottom: 20px; }
.page-breadcrumb { margin-bottom: 20px; font-size: 0.9em; }
.assignment-main-card { border-radius: 8px; margin-bottom: 20px; }
.assignment-main-header { display: flex; justify-content: space-between; align-items: center; }
.assignment-title { font-size: 1.8em; font-weight: 600; color: #303133; margin: 0; }
.assignment-description { white-space: pre-wrap; margin: 15px 0; color: #333; line-height: 1.7; }
.submission-card, .teacher-view .el-card { margin-top: 20px; }
.submission-content, .feedback-content, .submission-content-modal {
  white-space: pre-wrap;
  background-color: #fdfdfd;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-top: 5px;
  max-height: 200px; /* For modal content */
  overflow-y: auto;
}
.grade-info { margin-top: 15px; }
.el-table th { background-color: #f5f7fa !important; } /* Ensure this works or use :header-cell-style */
.grading-modal-content .el-descriptions { margin-bottom: 20px; }
.grading-modal-content h3 { margin-top: 0; margin-bottom: 15px; font-size: 1.2em; }
</style>
