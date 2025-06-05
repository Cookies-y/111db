import { defineStore } from 'pinia';
import apiClient from '../services/apiClient';
// import router from '../router'; // Optional: if actions directly cause navigation

export const useExamStore = defineStore('exam', {
    state: () => ({
        currentExamDetail: null, // Includes exam info. For teachers, might include all results. For students, might include their own result.
        examResultsForTeacher: [], // Specifically for teacher viewing all results for currentExamDetail if not nested or for refresh
        studentOwnResult: null, // Specifically for student's own result for currentExamDetail

        isLoadingExamDetail: false,
        fetchExamDetailError: null,

        isLoadingExamResults: false, // For teacher fetching all results
        fetchExamResultsError: null,

        isSubmittingExamResult: false,
        submitExamResultError: null,

        isUpdatingExamResult: false, // For teacher grading/updating a specific result
        updateExamResultError: null,
    }),
    getters: {
        getExamDetails: (state) => state.currentExamDetail,
        getExamResultsForTeacher: (state) => state.examResultsForTeacher,
        // Getter for student's own result if it's stored separately
        // getStudentOwnResult: (state) => state.studentOwnResult,
        // Or, if currentExamDetail contains student's result under a specific key:
        getStudentOwnResultFromDetail: (state) => state.currentExamDetail?.my_result || null,
    },
    actions: {
        async fetchExamDetail(examId) {
            this.isLoadingExamDetail = true;
            this.fetchExamDetailError = null;
            this.currentExamDetail = null;
            this.examResultsForTeacher = []; // Clear associated results
            this.studentOwnResult = null;    // Clear student's specific result

            try {
                const response = await apiClient.get(`/exams/${examId}`);
                this.currentExamDetail = response.data;
                // Backend logic for GET /exams/:exam_id determines what's in response.data:
                // - For Teachers: it might include all `results` already.
                // - For Students: it might include their `my_result` or just exam info.
                // This store action just stores what it gets.
                // If backend nests results for teacher in currentExamDetail.results:
                if (this.currentExamDetail && this.currentExamDetail.results) {
                    this.examResultsForTeacher = this.currentExamDetail.results;
                }
                // If backend nests student's own result:
                if (this.currentExamDetail && this.currentExamDetail.my_result) {
                    this.studentOwnResult = this.currentExamDetail.my_result;
                }

            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch exam details.';
                this.fetchExamDetailError = message;
                console.error(`Error fetching exam detail for ID ${examId}:`, message);
            } finally {
                this.isLoadingExamDetail = false;
            }
        },

        async fetchResultsForExam(examId) { // Primarily for teacher to explicitly fetch/refresh all results
            this.isLoadingExamResults = true;
            this.fetchExamResultsError = null;
            try {
                const response = await apiClient.get(`/exams/${examId}/results`);
                this.examResultsForTeacher = response.data;
                // If currentExamDetail is for the same exam, update its results too
                if (this.currentExamDetail && this.currentExamDetail.exam_id === parseInt(examId)) {
                    this.currentExamDetail.results = response.data;
                }
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch exam results.';
                this.fetchExamResultsError = message;
                console.error(`Error fetching results for exam ID ${examId}:`, message);
            } finally {
                this.isLoadingExamResults = false;
            }
        },

        async submitExamResult(examId, resultData) { // For students
            this.isSubmittingExamResult = true;
            this.submitExamResultError = null;
            try {
                const response = await apiClient.post(`/exams/${examId}/submit`, resultData);
                // After successful submission, update student's own result view.
                this.studentOwnResult = response.data;
                // If currentExamDetail is for the same exam, update its 'my_result' field if present
                if (this.currentExamDetail && this.currentExamDetail.exam_id === parseInt(examId)) {
                     this.currentExamDetail.my_result = response.data; // Or a similar structure
                }
                return { success: true, data: response.data };
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to submit exam result.';
                this.submitExamResultError = message;
                console.error(`Error submitting result for exam ID ${examId}:`, message);
                return { success: false, error: message };
            } finally {
                this.isSubmittingExamResult = false;
            }
        },

        async updateExamResult(resultId, resultData) { // For teachers to update/override
            this.isUpdatingExamResult = true;
            this.updateExamResultError = null;
            try {
                const response = await apiClient.put(`/exam-results/${resultId}`, resultData);
                const updatedResult = response.data;
                // Update this result in the teacher's list of results
                const index = this.examResultsForTeacher.findIndex(res => res.result_id === resultId);
                if (index !== -1) {
                    this.examResultsForTeacher.splice(index, 1, updatedResult);
                }
                // If this result is also the studentOwnResult (e.g. if student is also a teacher on another course, unlikely scenario)
                if (this.studentOwnResult && this.studentOwnResult.result_id === resultId) {
                    this.studentOwnResult = updatedResult;
                }
                // If this result is part of currentExamDetail.results (teacher view)
                if (this.currentExamDetail && this.currentExamDetail.results) {
                     const detailIndex = this.currentExamDetail.results.findIndex(res => res.result_id === resultId);
                     if (detailIndex !== -1) {
                         this.currentExamDetail.results.splice(detailIndex, 1, updatedResult);
                     }
                }
                return { success: true, data: updatedResult };
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to update exam result.';
                this.updateExamResultError = message;
                console.error(`Error updating exam result ID ${resultId}:`, message);
                return { success: false, error: message };
            } finally {
                this.isUpdatingExamResult = false;
            }
        },

        clearExamDetail() {
            this.currentExamDetail = null;
            this.fetchExamDetailError = null;
            this.examResultsForTeacher = [];
            this.fetchExamResultsError = null;
            this.studentOwnResult = null;
        },
        clearSubmitExamResultError() {
            this.submitExamResultError = null;
        },
        clearUpdateExamResultError() {
            this.updateExamResultError = null;
        }
    },
});
