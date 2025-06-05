import { defineStore } from 'pinia';
import apiClient from '../services/apiClient';

export const useCourseStore = defineStore('course', {
    state: () => ({
        courses: [],
        currentCourseDetail: null,

        isLoadingCourses: false,
        isLoadingCourseDetail: false,
        isCreatingCourse: false,

        fetchCoursesError: null,
        fetchCourseDetailError: null,
        createCourseError: null,

        currentCourseAssignments: [],
        isLoadingCourseAssignments: false,
        fetchCourseAssignmentsError: null,

        // New state for creating assignments
        isCreatingAssignment: false,
        createAssignmentError: null,
    }),
    getters: {
        allCourses: (state) => state.courses,
        getCourseDetails: (state) => state.currentCourseDetail,
        getCourseAssignments: (state) => state.currentCourseAssignments,
    },
    actions: {
        async fetchCourses() {
            this.isLoadingCourses = true;
            this.fetchCoursesError = null;
            try {
                const response = await apiClient.get('/courses');
                this.courses = response.data;
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch courses.';
                this.fetchCoursesError = message;
                this.courses = [];
                console.error('Error fetching courses:', message);
            } finally {
                this.isLoadingCourses = false;
            }
        },

        async fetchCourseDetail(courseId) {
            this.isLoadingCourseDetail = true;
            this.fetchCourseDetailError = null;
            this.currentCourseDetail = null;
            // Also clear assignments when fetching new course detail, as they belong to the previous course
            this.currentCourseAssignments = [];
            this.fetchCourseAssignmentsError = null;
            try {
                const response = await apiClient.get(`/courses/${courseId}`);
                this.currentCourseDetail = response.data;
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch course details.';
                this.fetchCourseDetailError = message;
                console.error(`Error fetching course detail for ID ${courseId}:`, message);
            } finally {
                this.isLoadingCourseDetail = false;
            }
        },

        async createCourse(courseData) {
            this.isCreatingCourse = true;
            this.createCourseError = null;
            try {
                const response = await apiClient.post('/courses', courseData);
                if (response.data) {
                    this.courses.unshift(response.data);
                }
                return { success: true, data: response.data };
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to create course.';
                this.createCourseError = message;
                console.error('Error creating course:', message);
                return { success: false, error: message };
            } finally {
                this.isCreatingCourse = false;
            }
        },

        clearCurrentCourseDetail() {
            this.currentCourseDetail = null;
            this.fetchCourseDetailError = null;
            this.currentCourseAssignments = []; // Also clear assignments
            this.fetchCourseAssignmentsError = null;
        },

        clearCreateCourseError() {
            this.createCourseError = null;
        },

        async fetchAssignmentsForCourse(courseId) {
            this.isLoadingCourseAssignments = true;
            this.fetchCourseAssignmentsError = null;
            this.currentCourseAssignments = [];
            try {
                const response = await apiClient.get(`/courses/${courseId}/assignments`);
                this.currentCourseAssignments = response.data;
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch assignments for course.';
                this.fetchCourseAssignmentsError = message;
                console.error(`Error fetching assignments for course ID ${courseId}:`, message);
            } finally {
                this.isLoadingCourseAssignments = false;
            }
        },

        clearCourseAssignments() {
            this.currentCourseAssignments = [];
            this.fetchCourseAssignmentsError = null;
        },

        // New action for creating an assignment for a course
        async createAssignmentForCourse(courseId, assignmentData) {
            this.isCreatingAssignment = true;
            this.createAssignmentError = null;
            try {
                // Assumes apiClient is configured to send JWT (handled by request interceptor in apiClient.js)
                const response = await apiClient.post(`/courses/${courseId}/assignments`, assignmentData);
                // After creating, add to the current list of assignments for this course
                if (response.data && this.currentCourseDetail?.course_id === courseId) {
                    this.currentCourseAssignments.push(response.data);
                    // Or sort by deadline/id if desired.
                } else if (response.data) {
                    // If we are not on the course detail page that matches this courseId,
                    // we might not need to update currentCourseAssignments, or we could fetch them again.
                    // For now, just adding if it matches the currently viewed course context.
                    // Alternatively, always re-fetch: this.fetchAssignmentsForCourse(courseId);
                }
                return { success: true, data: response.data };
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to create assignment.';
                this.createAssignmentError = message;
                console.error(`Error creating assignment for course ID ${courseId}:`, message);
                return { success: false, error: message };
            } finally {
                this.isCreatingAssignment = false;
            }
        },

        clearCreateAssignmentError() {
            this.createAssignmentError = null;
        }
    },
});
