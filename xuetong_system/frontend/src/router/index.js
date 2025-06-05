import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/authStore';
// import { ElMessage } from 'element-plus'; // Removed: Better not to use UI components directly in router guards

// Eagerly load core layout/public pages
import HomePage from '../views/HomePage.vue';
import LoginPage from '../views/LoginPage.vue';
import RegisterPage from '../views/RegisterPage.vue';

// Admin Layout
import AdminLayout from '../views/admin/AdminLayout.vue';

const routes = [
    // Public routes
    { path: '/', name: 'Home', component: HomePage },
    { path: '/login', name: 'Login', component: LoginPage, meta: { guestOnly: true } },
    { path: '/register', name: 'Register', component: RegisterPage, meta: { guestOnly: true } },

    // Authenticated user routes (non-admin)
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
        path: '/exams/:id',
        name: 'ExamDetail',
        component: () => import('../views/ExamDetailPage.vue'),
        props: true,
        meta: { requiresAuth: true }
    },
    {
        path: '/courses/:course_id/discussions/new',
        name: 'CreateDiscussionTopic',
        component: () => import('../views/DiscussionCreateTopicPage.vue'),
        props: true,
        meta: { requiresAuth: true }
    },
    {
        path: '/discussions/:post_id',
        name: 'DiscussionThread',
        component: () => import('../views/DiscussionThreadPage.vue'),
        props: true,
        meta: { requiresAuth: true }
    },

    // Admin Routes
    {
        path: '/admin',
        component: AdminLayout,
        meta: { requiresAuth: true, requiresAdmin: true },
        children: [
            {
                path: '',
                redirect: { name: 'AdminDashboard' }
            },
            {
                path: 'dashboard',
                name: 'AdminDashboard',
                component: () => import('../views/admin/AdminDashboardPage.vue'),
            },
            {
                path: 'users',
                name: 'AdminUserList',
                component: () => import('../views/admin/AdminUserListPage.vue'),
            },
            {
                path: 'users/:user_id',
                name: 'AdminUserDetail',
                component: () => import('../views/admin/AdminUserDetailPage.vue'),
                props: true
            },
            {
                path: 'courses',
                name: 'AdminCourseList',
                component: () => import('../views/admin/AdminCourseListPage.vue'),
            },
            {
                path: 'courses/:course_id',
                name: 'AdminCourseDetail',
                component: () => import('../views/admin/AdminCourseDetailPage.vue'),
                props: true
            }
        ]
    }
    // {
    //     path: '/:pathMatch(.*)*',
    //     name: 'NotFound',
    //     component: () => import('../views/NotFoundPage.vue')
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

    if (to.matched.some(record => record.meta.requiresAdmin)) {
        if (!authStore.isAuthenticated) {
            authStore.setReturnUrl(to.fullPath);
            next({ name: 'Login' });
        } else if (!authStore.isAdmin) {
            console.warn('Unauthorized access attempt to admin route by non-admin user.'); // Log warning
            next({ name: 'Dashboard' }); // Redirect non-admins to their regular dashboard
        } else {
            next();
        }
    } else if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        authStore.setReturnUrl(to.fullPath);
        next({ name: 'Login' });
    } else if (to.meta.guestOnly && authStore.isAuthenticated) {
        next({ name: authStore.isAdmin ? 'AdminDashboard' : 'Dashboard' });
    } else {
        next();
    }
});

export default router;
