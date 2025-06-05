import { defineStore } from 'pinia';
import apiClient from '../services/apiClient';
// import router from '../router'; // Only if actions directly navigate

export const useAssignmentStore = defineStore('assignment', {
    state: () => ({
        currentAssignmentDetail: null, // Holds details of the fetched assignment
        submissionsForCurrentAssignment: [], // Holds submissions if fetched separately or as part of detail

        isLoadingAssignmentDetail: false,
        fetchAssignmentDetailError: null,

        isLoadingSubmissions: false, // Specifically for submissions list if fetched separately
        fetchSubmissionsError: null,

        isSubmitting: false, // For student submitting work
        submitError: null,

        isGrading: false, // For teacher grading a submission
        gradeError: null,
    }),
    getters: {
        getAssignmentDetails: (state) => state.currentAssignmentDetail,
        // If submissions are part of currentAssignmentDetail from backend:
        // getSubmissions: (state) => state.currentAssignmentDetail?.submissions || [],
        // If submissions are fetched separately into submissionsForCurrentAssignment:
        getSubmissions: (state) => state.submissionsForCurrentAssignment,
    },
    actions: {
        async fetchAssignmentDetail(assignmentId) {
            this.isLoadingAssignmentDetail = true;
            this.fetchAssignmentDetailError = null;
            this.currentAssignmentDetail = null; // Clear previous
            // Also clear submissions if they are tied to this assignment detail view
            this.submissionsForCurrentAssignment = [];
            this.fetchSubmissionsError = null;

            try {
                const response = await apiClient.get(`/assignments/${assignmentId}`);
                this.currentAssignmentDetail = response.data;
                // If backend for GET /assignments/:id includes submissions for teacher, this is enough.
                // Otherwise, teacher might need to call fetchSubmissionsForAssignment separately.
                // For now, assume it does NOT include submissions.
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch assignment details.';
                this.fetchAssignmentDetailError = message;
                console.error(`Error fetching assignment detail for ID ${assignmentId}:`, message);
            } finally {
                this.isLoadingAssignmentDetail = false;
            }
        },

        async fetchSubmissionsForAssignment(assignmentId) {
            // This action is primarily for teachers to view all submissions for an assignment.
            // Students would typically only see their own submission, perhaps via a different mechanism or filtered list.
            this.isLoadingSubmissions = true;
            this.fetchSubmissionsError = null;
            this.submissionsForCurrentAssignment = [];
            try {
                const response = await apiClient.get(`/assignments/${assignmentId}/submissions`);
                this.submissionsForCurrentAssignment = response.data;
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch submissions.';
                this.fetchSubmissionsError = message;
                console.error(`Error fetching submissions for assignment ID ${assignmentId}:`, message);
            } finally {
                this.isLoadingSubmissions = false;
            }
        },

        async submitToAssignment(assignmentId, submissionData) {
            this.isSubmitting = true;
            this.submitError = null;
            try {
                const response = await apiClient.post(`/assignments/${assignmentId}/submissions`, submissionData);
                // After successful submission, the student might be redirected or the UI updated.
                // For now, just return success. The component can decide to re-fetch or navigate.
                // Optionally, if the response contains the created submission, add it to a local list of "my submissions".
                return { success: true, data: response.data };
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to submit assignment.';
                this.submitError = message;
                console.error(`Error submitting to assignment ID ${assignmentId}:`, message);
                return { success: false, error: message };
            } finally {
                this.isSubmitting = false;
            }
        },

        async gradeSubmission(submissionId, gradeData) {
            this.isGrading = true;
            this.gradeError = null;
            try {
                const response = await apiClient.put(`/submissions/${submissionId}/grade`, gradeData);
                // Update the specific submission in the local state if it's being displayed.
                // This often requires finding and updating the item in submissionsForCurrentAssignment array.
                const updatedSubmission = response.data;
                const index = this.submissionsForCurrentAssignment.findIndex(sub => sub.submission_id === submissionId);
                if (index !== -1) {
                    this.submissionsForCurrentAssignment.splice(index, 1, updatedSubmission);
                }
                // If viewing a single submission that was graded, update currentAssignmentDetail if it holds that.
                // This part depends on how submission details are structured and displayed.
                return { success: true, data: updatedSubmission };
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to grade submission.';
                this.gradeError = message;
                console.error(`Error grading submission ID ${submissionId}:`, message);
                return { success: false, error: message };
            } finally {
                this.isGrading = false;
            }
        },

        clearAssignmentDetail() {
            this.currentAssignmentDetail = null;
            this.fetchAssignmentDetailError = null;
            this.submissionsForCurrentAssignment = [];
            this.fetchSubmissionsError = null;
        },

        clearSubmitError() {
            this.submitError = null;
        },

        clearGradeError() {
            this.gradeError = null;
        }
    },
});
