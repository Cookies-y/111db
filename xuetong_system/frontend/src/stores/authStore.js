import { defineStore } from 'pinia';
import apiClient from '../services/apiClient';
import router from '../router'; // Import router for navigation

export const useAuthStore = defineStore('auth', {
    state: () => ({
        accessToken: localStorage.getItem('accessToken') || null,
        // Storing the whole user object can be useful, but ensure sensitive data is not kept if not needed.
        // For now, a simple placeholder or just email might be stored after login.
        user: JSON.parse(localStorage.getItem('user')) || null,
        returnUrl: null, // For redirecting after login from a protected route attempt
        loginError: null, // To store login error messages
        registrationError: null, // To store registration error messages
    }),
    getters: {
        isAuthenticated: (state) => !!state.accessToken,
        // Example: To get user role or other details if stored in `state.user`
        // getUser: (state) => state.user,
        // getUserRole: (state) => state.user?.user_type, // Assuming user object has user_type
    },
    actions: {
        async login(credentials) {
            this.loginError = null; // Clear previous errors
            try {
                const response = await apiClient.post('/auth/login', credentials);
                this.accessToken = response.data.access_token;
                localStorage.setItem('accessToken', this.accessToken);

                // Placeholder for user data - ideally fetch from a /me endpoint after login
                // For now, we'll just store the email as part of user info, or a decoded part of token if safe
                this.user = { email: credentials.email }; // Example
                localStorage.setItem('user', JSON.stringify(this.user));

                const redirectPath = this.returnUrl || '/dashboard';
                this.returnUrl = null;
                router.push(redirectPath);
                return true;
            } catch (error) {
                const message = error.response?.data?.message || 'Login failed. Please check your credentials.';
                console.error('Login failed:', message);
                this.loginError = message;
                this.clearAuthData(); // Clear any partial auth data
                return false;
            }
        },
        async register(userInfo) {
            this.registrationError = null; // Clear previous errors
            try {
                // Backend expects: username, password, real_name, email, user_type (string 'student'/'teacher')
                await apiClient.post('/auth/register', userInfo);
                // After successful registration, redirect to login or show a success message
                router.push('/login');
                // Optionally, you could set a success message to be displayed on the login page
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
        // Helper to clear auth data from state and localStorage
        clearAuthData() {
            this.accessToken = null;
            this.user = null;
            localStorage.removeItem('accessToken');
            localStorage.removeItem('user');
        }
    },
});
