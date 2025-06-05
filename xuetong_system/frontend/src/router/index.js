import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/authStore';

// Eagerly load core layout/public pages for faster initial interaction
import HomePage from '../views/HomePage.vue';
import LoginPage from '../views/LoginPage.vue';
import RegisterPage from '../views/RegisterPage.vue';

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
        component: () => import('../views/DashboardPage.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/courses/:id',
        name: 'CourseDetail',
        component: () => import('../views/CourseDetailPage.vue'),
        props: true,
        meta: { requiresAuth: true }
    },
    {
        path: '/create-course',
        name: 'CreateCourse',
        component: () => import('../views/CourseCreatePage.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/courses/:course_id/create-assignment',
        name: 'CreateAssignment',
        component: () => import('../views/AssignmentCreatePage.vue'),
        props: true,
        meta: { requiresAuth: true }
    },
    {
        path: '/assignments/:id',
        name: 'AssignmentDetail',
        component: () => import('../views/AssignmentDetailPage.vue'),
        props: true,
        meta: { requiresAuth: true }
    },
    {
        path: '/courses/:course_id/create-exam',
        name: 'CreateExam',
        component: () => import('../views/ExamCreatePage.vue'),
        props: true,
        meta: { requiresAuth: true }
    },
    {
        path: '/exams/:id', // New route for Exam Detail
        name: 'ExamDetail',
        component: () => import('../views/ExamDetailPage.vue'), // Lazy load
        props: true,
        meta: { requiresAuth: true }
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
        next();
    }
});

export default router;
