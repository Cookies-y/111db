import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/authStore'; // Import the Pinia auth store

// Import view components
import HomePage from '../views/HomePage.vue';
import LoginPage from '../views/LoginPage.vue';
import RegisterPage from '../views/RegisterPage.vue';
import DashboardPage from '../views/DashboardPage.vue'; // This is the main course listing page currently
import CourseDetailPage from '../views/CourseDetailPage.vue';
import CourseCreatePage from '../views/CourseCreatePage.vue'; // Import the new page
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
        path: '/dashboard', // Currently serves as the course listing page
        name: 'Dashboard',
        component: DashboardPage,
        meta: { requiresAuth: true }
    },
    {
        path: '/courses/:id', // Route for individual course details
        name: 'CourseDetail',
        component: CourseDetailPage,
        props: true, // Passes route.params (like :id) as props to the component
        meta: { requiresAuth: true } // Protected route
    },
    {
        path: '/create-course',
        name: 'CreateCourse',
        component: CourseCreatePage,
        meta: { requiresAuth: true } // Protected route, component will check for teacher role
    }
    // Example for a 404 page - good practice to add
    // {
    //     path: '/:pathMatch(.*)*',
    //     name: 'NotFound',
    //     component: () => import('../views/NotFoundPage.vue') // Lazy load 404
    // }
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
    scrollBehavior(to, from, savedPosition) {
        // Always scroll to top when navigating to a new page
        if (savedPosition) {
            return savedPosition;
        } else {
            return { top: 0 };
        }
    }
});

// Navigation Guards
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        authStore.setReturnUrl(to.fullPath);
        next({ name: 'Login' });
    } else if (to.meta.guestOnly && authStore.isAuthenticated) {
        next({ name: 'Dashboard' });
    } else {
        // Add role check here if desired for routes with meta.requiresRole
        // For example:
        // if (to.meta.requiresRole && to.meta.requiresRole !== authStore.user?.role_name_or_id) {
        //    next({ name: 'AccessDenied' }); // Or redirect to dashboard with error
        // } else {
        //    next();
        // }
        next();
    }
});

export default router;
