import { defineStore } from 'pinia';
import apiClient from '../services/apiClient';
import { ElMessage } from 'element-plus';

export const useAdminStore = defineStore('admin', {
    state: () => ({
        users: [],
        courses: [],

        currentUserDetail: null, // For viewing/editing a specific user by admin
        currentCourseDetail: null, // For viewing/editing a specific course by admin (different from courseStore's user-facing one)

        isLoadingUsers: false,
        fetchUsersError: null,

        isLoadingUserDetail: false,
        fetchUserDetailError: null,

        isLoadingAdminCourses: false, // Renamed to avoid conflict if this store is used alongside courseStore
        fetchAdminCoursesError: null,

        isLoadingAdminCourseDetail: false, // Renamed
        fetchAdminCourseDetailError: null,
    }),
    getters: {
        allUsers: (state) => state.users,
        getUserDetail: (state) => state.currentUserDetail,
        allAdminCourses: (state) => state.courses,
        getAdminCourseDetail: (state) => state.currentCourseDetail,
    },
    actions: {
        async fetchAllUsers() {
            this.isLoadingUsers = true;
            this.fetchUsersError = null;
            try {
                // Assumes apiClient is configured to send JWT from authStore
                const response = await apiClient.get('/admin/users');
                this.users = response.data;
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch users.';
                this.fetchUsersError = message;
                this.users = [];
                console.error('Error fetching users (admin):', message);
                ElMessage.error(message);
            } finally {
                this.isLoadingUsers = false;
            }
        },

        async fetchUserDetail(userId) {
            this.isLoadingUserDetail = true;
            this.fetchUserDetailError = null;
            this.currentUserDetail = null;
            try {
                const response = await apiClient.get(`/admin/users/${userId}`);
                this.currentUserDetail = response.data;
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch user details.';
                this.fetchUserDetailError = message;
                console.error(`Error fetching user detail for ID ${userId} (admin):`, message);
                ElMessage.error(message);
            } finally {
                this.isLoadingUserDetail = false;
            }
        },

        async fetchAllAdminCourses() {
            this.isLoadingAdminCourses = true;
            this.fetchAdminCoursesError = null;
            try {
                const response = await apiClient.get('/admin/courses');
                this.courses = response.data;
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch courses (admin).';
                this.fetchAdminCoursesError = message;
                this.courses = [];
                console.error('Error fetching courses (admin):', message);
                ElMessage.error(message);
            } finally {
                this.isLoadingAdminCourses = false;
            }
        },

        async fetchCourseDetailForAdmin(courseId) {
            this.isLoadingAdminCourseDetail = true;
            this.fetchAdminCourseDetailError = null;
            this.currentCourseDetail = null;
            try {
                const response = await apiClient.get(`/admin/courses/${courseId}`);
                this.currentCourseDetail = response.data;
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch course details (admin).';
                this.fetchAdminCourseDetailError = message;
                console.error(`Error fetching course detail for ID ${courseId} (admin):`, message);
                ElMessage.error(message);
            } finally {
                this.isLoadingAdminCourseDetail = false;
            }
        },

        clearAdminData() {
            this.users = [];
            this.courses = [];
            this.currentUserDetail = null;
            this.currentCourseDetail = null;

            this.fetchUsersError = null;
            this.fetchUserDetailError = null;
            this.fetchAdminCoursesError = null;
            this.fetchAdminCourseDetailError = null;

            this.isLoadingUsers = false;
            this.isLoadingUserDetail = false;
            this.isLoadingAdminCourses = false;
            this.isLoadingAdminCourseDetail = false;
        },

        clearUserDetail() {
            this.currentUserDetail = null;
            this.fetchUserDetailError = null;
        },

        clearCourseDetailAdmin() { // Renamed to avoid conflict if used with courseStore
            this.currentCourseDetail = null;
            this.fetchAdminCourseDetailError = null;
        }
    },
});
