import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/authStore'; // Import the Pinia auth store

// Import actual view components
import HomePage from '../views/HomePage.vue';
import LoginPage from '../views/LoginPage.vue';
import RegisterPage from '../views/RegisterPage.vue';
import DashboardPage from '../views/DashboardPage.vue';
// import NotFoundPage from '../views/NotFoundPage.vue'; // Example for a 404 page

const routes = [
    {
        path: '/',
        name: 'Home',
        component: HomePage
    },
    {
        path: '/login',
        name: 'Login',
        component: LoginPage,
        meta: { guestOnly: true }
    },
    {
        path: '/register',
        name: 'Register',
        component: RegisterPage,
        meta: { guestOnly: true }
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: DashboardPage,
        meta: { requiresAuth: true }
    }
    // { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFoundPage }
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
});

// Navigation Guards
router.beforeEach((to, from, next) => {
    // It's crucial that the Pinia instance has been installed on the app
    // before the router instance is used. This is handled in main.js by
    // app.use(createPinia()) before app.use(router).
    const authStore = useAuthStore();

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        // If route requires auth and user is not authenticated, store the intended URL and redirect to login
        authStore.setReturnUrl(to.fullPath);
        next({ name: 'Login' }); // Removed query param here, returnUrl in store handles it
    } else if (to.meta.guestOnly && authStore.isAuthenticated) {
        // If route is for guests only (login, register) and user is authenticated, redirect to dashboard
        next({ name: 'Dashboard' });
    } else {
        // Otherwise, proceed as normal
        next();
    }
});

export default router;
