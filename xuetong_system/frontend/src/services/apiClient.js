import axios from 'axios';

// Vite exposes environment variables on import.meta.env
// Variables prefixed with VITE_ are exposed to client-side code.
const VITE_API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const apiClient = axios.create({
    baseURL: VITE_API_BASE_URL || 'http://localhost:5001', // Fallback for safety or non-Vite contexts
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    }
});

// Request Interceptor: Adds JWT token to Authorization header
apiClient.interceptors.request.use(config => {
    // In a real app, token would come from a Pinia store getter or a dedicated auth service
    // const authStore = useAuthStore(); // This can't be used here directly as this is not a setup function
    // const token = authStore.accessToken;

    // For now, retrieve directly from localStorage. This should be synchronized with Pinia state.
    const token = localStorage.getItem('accessToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, error => {
    return Promise.reject(error);
});

// Response Interceptor: Handles 401 errors (e.g., token expired)
// apiClient.interceptors.response.use(response => {
//     return response;
// }, error => {
//     if (error.response && error.response.status === 401) {
//         // const authStore = useAuthStore(); // Need to get store instance properly if used here
//         // authStore.logout(); // This action includes router.push('/login')
//         // For simplicity, directly clear localStorage and redirect if this interceptor is active
//         console.error('API request Unauthorized (401):', error.config.url);
//         localStorage.removeItem('accessToken');
//         localStorage.removeItem('user');
//         // Potentially emit an event or use a navigator service if router instance is not available here
//         // window.location.href = '/login'; // Hard redirect
//     }
//     return Promise.reject(error);
// });

export default apiClient;
