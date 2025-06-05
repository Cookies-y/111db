import { defineStore } from 'pinia';
import apiClient from '../services/apiClient';
import router from '../router'; // Import router for navigation

export const useAuthStore = defineStore('auth', {
    state: () => ({
        accessToken: localStorage.getItem('accessToken') || null,
        // User object. IMPORTANT: For isAdmin to work, this 'user' object MUST be populated
        // with 'user_type' (e.g., from JWT claims decoding or a /me API call after login).
        // Current login action only stores { email: ... }. This needs enhancement.
        user: JSON.parse(localStorage.getItem('user')) || null,
        returnUrl: null,
        loginError: null,
        registrationError: null,
    }),
    getters: {
        isAuthenticated: (state) => !!state.accessToken,
        getUser: (state) => state.user,
        // Assumes user object in state has a 'user_type' property (e.g., 1:student, 2:teacher, 3:admin)
        isAdmin: (state) => !!state.accessToken && state.user?.user_type === 3,
        isTeacher: (state) => !!state.accessToken && state.user?.user_type === 2,
        isStudent: (state) => !!state.accessToken && state.user?.user_type === 1,
    },
    actions: {
        async login(credentials) {
            this.loginError = null;
            try {
                const response = await apiClient.post('/auth/login', credentials);
                this.accessToken = response.data.access_token;
                localStorage.setItem('accessToken', this.accessToken);

                // TODO: CRITICAL - Enhance this part to get full user details including user_type.
                // This could be done by:
                // 1. Decoding the JWT if it contains user_type, user_id, real_name etc.
                // 2. Making a follow-up API call to a '/auth/me' endpoint to fetch user details.
                // For now, continuing with the assumption that 'user' might get populated more fully.
                // A temporary measure if JWT contains claims:
                try {
                    const tokenPayload = JSON.parse(atob(this.accessToken.split('.')[1]));
                    this.user = {
                        email: credentials.email, // from form
                        user_id: tokenPayload.sub, // 'sub' is standard for user ID
                        user_type: tokenPayload.user_type, // Assuming 'user_type' claim exists
                        // real_name: tokenPayload.real_name, // Assuming 'real_name' claim exists
                        // username: tokenPayload.username // Assuming 'username' claim exists
                    };
                } catch (e) {
                    console.error("Error decoding token or token doesn't have expected claims:", e);
                    // Fallback to minimal user info if token doesn't have claims or decoding fails
                    this.user = { email: credentials.email, user_id: null, user_type: null };
                }
                localStorage.setItem('user', JSON.stringify(this.user));

                const redirectPath = this.returnUrl || (this.user?.user_type === 3 ? '/admin/dashboard' : '/dashboard'); // Example admin redirect
                this.returnUrl = null;
                router.push(redirectPath);
                return true;
            } catch (error) {
                const message = error.response?.data?.message || 'Login failed. Please check your credentials.';
                console.error('Login failed:', message);
                this.loginError = message;
                this.clearAuthData();
                return false;
            }
        },
        async register(userInfo) {
            this.registrationError = null;
            try {
                await apiClient.post('/auth/register', userInfo);
                router.push('/login');
                return true;
            } catch (error) {
                const message = error.response?.data?.message || 'Registration failed. Please try again.';
                console.error('Registration failed:', message);
                this.registrationError = message;
                return false;
            }
        },
        logout() {
            this.clearAuthData();
            router.push('/login');
        },
        setReturnUrl(url) {
            this.returnUrl = url;
        },
        clearAuthData() {
            this.accessToken = null;
            this.user = null;
            localStorage.removeItem('accessToken');
            localStorage.removeItem('user');
        },
        // Action to potentially refresh user data from a /me endpoint
        async fetchCurrentUser() {
            if (!this.accessToken) return; // No token, no fetch
            // This action would call an API endpoint like /auth/me
            // For now, it's a placeholder. If implemented, it would update this.user
            // try {
            //   const response = await apiClient.get('/auth/me');
            //   this.user = response.data;
            //   localStorage.setItem('user', JSON.stringify(this.user));
            // } catch (error) {
            //   console.error("Failed to fetch current user details:", error);
            //   // Potentially handle token invalidation here if /me fails with 401
            //   if (error.response && error.response.status === 401) {
            //     this.logout(); // Example: logout if /me fails due to bad token
            //   }
            // }
        }
    },
});
