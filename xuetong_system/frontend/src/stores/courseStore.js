import { defineStore } from 'pinia';
import apiClient from '../services/apiClient';

export const useCourseStore = defineStore('course', {
    state: () => ({
        courses: [], // For the list of all courses
        currentCourseDetail: null, // For the details of a single selected course

        isLoadingCourses: false,
        isLoadingCourseDetail: false,
        isCreatingCourse: false, // For create course loading state

        fetchCoursesError: null,
        fetchCourseDetailError: null,
        createCourseError: null,
    }),
    getters: {
        allCourses: (state) => state.courses,
        getCourseDetails: (state) => state.currentCourseDetail,
        // Example: a getter to find a course from the list if needed
        // getCourseByIdFromList: (state) => (id) => state.courses.find(course => course.course_id === id),
    },
    actions: {
        async fetchCourses() {
            this.isLoadingCourses = true;
            this.fetchCoursesError = null;
            try {
                const response = await apiClient.get('/courses'); // Endpoint for listing courses
                this.courses = response.data;
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch courses.';
                this.fetchCoursesError = message;
                this.courses = []; // Clear courses on error
                console.error('Error fetching courses:', message);
                // Optionally re-throw or return error status for component to handle
                // throw new Error(message);
            } finally {
                this.isLoadingCourses = false;
            }
        },

        async fetchCourseDetail(courseId) {
            this.isLoadingCourseDetail = true;
            this.fetchCourseDetailError = null;
            this.currentCourseDetail = null; // Clear previous detail
            try {
                const response = await apiClient.get(`/courses/${courseId}`);
                this.currentCourseDetail = response.data;
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch course details.';
                this.fetchCourseDetailError = message;
                console.error(`Error fetching course detail for ID ${courseId}:`, message);
                // throw new Error(message);
            } finally {
                this.isLoadingCourseDetail = false;
            }
        },

        async createCourse(courseData) {
            this.isCreatingCourse = true;
            this.createCourseError = null;
            try {
                // Assumes apiClient is configured to send JWT from authStore (via interceptor)
                const response = await apiClient.post('/courses', courseData); // Endpoint for creating a course
                // Add the new course to the local 'courses' list (or re-fetch)
                // Prepending it to the list can provide immediate UI update.
                if (response.data) { // Assuming backend returns the created course object
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
        },

        // Action to clear specific errors if needed, e.g., when a form is re-attempted
        clearCreateCourseError() {
            this.createCourseError = null;
        }
    },
});
