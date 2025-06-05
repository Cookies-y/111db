import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://localhost:5001', // Backend API root
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    }
});

// Optional: Request Interceptor (Example for adding JWT token)
// We will uncomment and implement this properly when auth state (Pinia) is set up.
// apiClient.interceptors.request.use(config => {
//     // const authStore = useAuthStore(); // Assuming a Pinia store for auth
//     // const token = authStore.accessToken;
//     const token = localStorage.getItem('accessToken'); // Placeholder until Pinia store is ready
//     if (token) {
//         config.headers.Authorization = `Bearer ${token}`;
//     }
//     return config;
// }, error => {
//     return Promise.reject(error);
// });

// Optional: Response Interceptor (Example for handling 401 or token refresh)
// apiClient.interceptors.response.use(response => {
//     return response;
// }, error => {
//     if (error.response && error.response.status === 401) {
//         // const authStore = useAuthStore();
//         // authStore.logout(); // Or clear token and redirect
//         // router.push('/login'); // Requires router instance
//         console.error('Unauthorized, redirecting to login might be needed');
//     }
//     return Promise.reject(error);
// });

export default apiClient;
