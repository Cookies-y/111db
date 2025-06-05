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
        isCreatingAssignment: false,
        createAssignmentError: null,

        currentCourseExams: [],
        isLoadingCourseExams: false,
        fetchCourseExamsError: null,
        isCreatingExam: false,
        createExamError: null,

        // New state for discussion topics within a course context
        currentCourseDiscussionTopics: [],
        isLoadingCourseDiscussionTopics: false,
        fetchCourseDiscussionTopicsError: null,
        isCreatingDiscussionTopic: false,
        createDiscussionTopicError: null,
    }),
    getters: {
        allCourses: (state) => state.courses,
        getCourseDetails: (state) => state.currentCourseDetail,
        getCourseAssignments: (state) => state.currentCourseAssignments,
        getCourseExams: (state) => state.currentCourseExams,
        getCourseDiscussionTopics: (state) => state.currentCourseDiscussionTopics, // New getter
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

            // Clear all related sub-data for the course
            this.clearCourseAssignments();
            this.clearCourseExams();
            this.clearCourseDiscussionData(); // New call

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
            this.clearCourseAssignments();
            this.clearCourseExams();
            this.clearCourseDiscussionData(); // New call
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

        async createAssignmentForCourse(courseId, assignmentData) {
            this.isCreatingAssignment = true;
            this.createAssignmentError = null;
            try {
                const response = await apiClient.post(`/courses/${courseId}/assignments`, assignmentData);
                if (response.data && this.currentCourseDetail?.course_id === parseInt(courseId)) {
                    this.currentCourseAssignments.push(response.data);
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
        },

        async fetchExamsForCourse(courseId) {
            this.isLoadingCourseExams = true;
            this.fetchCourseExamsError = null;
            this.currentCourseExams = [];
            try {
                const response = await apiClient.get(`/courses/${courseId}/exams`);
                this.currentCourseExams = response.data;
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch exams for course.';
                this.fetchCourseExamsError = message;
                console.error(`Error fetching exams for course ID ${courseId}:`, message);
            } finally {
                this.isLoadingCourseExams = false;
            }
        },

        async createExamForCourse(courseId, examData) {
            this.isCreatingExam = true;
            this.createExamError = null;
            try {
                const response = await apiClient.post(`/courses/${courseId}/exams`, examData);
                if (response.data && this.currentCourseDetail?.course_id === parseInt(courseId)) {
                    this.currentCourseExams.push(response.data);
                }
                return { success: true, data: response.data };
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to create exam.';
                this.createExamError = message;
                console.error(`Error creating exam for course ID ${courseId}:`, message);
                return { success: false, error: message };
            } finally {
                this.isCreatingExam = false;
            }
        },

        clearCourseExams() {
            this.currentCourseExams = [];
            this.fetchCourseExamsError = null;
        },

        clearCreateExamError() {
            this.createExamError = null;
        },

        // New actions for course discussion topics
        async fetchDiscussionTopicsForCourse(courseId) {
            this.isLoadingCourseDiscussionTopics = true;
            this.fetchCourseDiscussionTopicsError = null;
            this.currentCourseDiscussionTopics = [];
            try {
                const response = await apiClient.get(`/courses/${courseId}/discussions`);
                this.currentCourseDiscussionTopics = response.data;
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch discussion topics for course.';
                this.fetchCourseDiscussionTopicsError = message;
                console.error(`Error fetching discussion topics for course ID ${courseId}:`, message);
            } finally {
                this.isLoadingCourseDiscussionTopics = false;
            }
        },

        async createDiscussionTopic(courseId, topicData) {
            this.isCreatingDiscussionTopic = true;
            this.createDiscussionTopicError = null;
            try {
                const response = await apiClient.post(`/courses/${courseId}/discussions`, topicData);
                if (response.data && this.currentCourseDetail?.course_id === parseInt(courseId)) {
                    this.currentCourseDiscussionTopics.unshift(response.data); // Add to top
                }
                return { success: true, data: response.data };
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to create discussion topic.';
                this.createDiscussionTopicError = message;
                console.error(`Error creating discussion topic for course ID ${courseId}:`, message);
                return { success: false, error: message };
            } finally {
                this.isCreatingDiscussionTopic = false;
            }
        },

        clearCourseDiscussionData() {
            this.currentCourseDiscussionTopics = [];
            this.fetchCourseDiscussionTopicsError = null;
            this.createDiscussionTopicError = null; // Also clear creation error
        },
        // No clearCreateDiscussionTopicError needed if cleared in clearCourseDiscussionData
    },
});
