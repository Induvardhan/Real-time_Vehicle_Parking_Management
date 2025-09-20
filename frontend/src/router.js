import { createRouter, createWebHistory } from 'vue-router';
import AdminLogin from './components/AdminLogin.vue';
import UserLogin from './components/UserLogin.vue';
import UserRegister from './components/UserRegister.vue';
import AdminDashboard from './components/AdminDashboard.vue';
import UserDashboard from './components/UserDashboard.vue';
import HomePage from './components/HomePage.vue';

const routes = [
  { path: '/admin', redirect: '/admin/login' },
  { path: '/admin/login', component: AdminLogin },
  { path: '/admin-login', component: AdminLogin },
  { path: '/admin/dashboard', component: AdminDashboard },
  { path: '/admin-dashboard', component: AdminDashboard }, // Add hyphenated route
  { path: '/user', redirect: '/user/login' },
  { path: '/user/login', component: UserLogin },
  { path: '/user-login', component: UserLogin }, // Add hyphenated route
  { path: '/user/register', component: UserRegister },
  { path: '/user/dashboard', component: UserDashboard },
  { path: '/user-dashboard', component: UserDashboard }, // Add hyphenated route
  { path: '/', name: 'HomePage', component: HomePage },
  {
    path: '/user-register',
    name: 'UserRegister',
    component: UserRegister,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
