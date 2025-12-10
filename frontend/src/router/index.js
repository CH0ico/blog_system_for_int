import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

// 路由配置
const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("@/views/Home.vue"),
    meta: {
      title: "首页",
    },
  },
  {
    path: "/posts",
    name: "Posts",
    component: () => import("@/views/Posts.vue"),
    meta: {
      title: "文章列表",
    },
  },
  {
    path: "/post/:id",
    name: "PostDetail",
    component: () => import("@/views/PostDetail.vue"),
    meta: {
      title: "文章详情",
    },
  },
  {
    path: "/write",
    name: "WritePost",
    component: () => import("@/views/WritePost.vue"),
    meta: {
      title: "写文章",
      requiresAuth: true,
      requiresPermission: "create_posts",
    },
  },
  {
    path: "/edit/:id",
    name: "EditPost",
    component: () => import("@/views/WritePost.vue"),
    meta: {
      title: "编辑文章",
      requiresAuth: true,
      requiresPermission: "edit_own_posts",
    },
  },
  {
    path: "/archives",
    name: "Archives",
    component: () => import("@/views/Archives.vue"),
    meta: {
      title: "文章归档",
    },
  },
  {
    path: "/tags",
    name: "Tags",
    component: () => import("@/views/Tags.vue"),
    meta: {
      title: "标签",
    },
  },
  {
    path: "/tags/:slug",
    name: "TagDetail",
    component: () => import("@/views/TagDetail.vue"),
    meta: {
      title: "标签",
    },
  },
  {
    path: "/categories",
    name: "Categories",
    component: () => import("@/views/Categories.vue"),
    meta: {
      title: "分类",
    },
  },
  {
    path: "/categories/:slug",
    name: "CategoryDetail",
    component: () => import("@/views/CategoryDetail.vue"),
    meta: {
      title: "分类详情",
    },
  },
  {
    path: "/about",
    name: "About",
    component: () => import("@/views/About.vue"),
    meta: {
      title: "关于",
    },
  },
  {
    path: "/profile",
    name: "Profile",
    component: () => import("@/views/Profile.vue"),
    meta: {
      title: "个人中心",
      requiresAuth: true,
    },
  },
  {
    path: "/notifications",
    name: "Notifications",
    component: () => import("@/views/Notifications.vue"),
    meta: {
      title: "通知中心",
      requiresAuth: true,
    },
  },
  {
    path: "/users/:username",
    name: "UserProfile",
    component: () => import("@/views/UserProfile.vue"),
    meta: {
      title: "用户主页",
    },
  },
  {
    path: "/search",
    name: "Search",
    component: () => import("@/views/Search.vue"),
    meta: {
      title: "搜索",
    },
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/auth/Login.vue"),
    meta: {
      title: "登录",
      guestOnly: true,
    },
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("@/views/auth/Register.vue"),
    meta: {
      title: "注册",
      guestOnly: true,
    },
  },
  {
    path: "/forgot-password",
    name: "ForgotPassword",
    component: () => import("@/views/auth/ForgotPassword.vue"),
    meta: {
      title: "忘记密码",
      guestOnly: true,
    },
  },
  {
    path: "/reset-password",
    name: "ResetPassword",
    component: () => import("@/views/auth/ResetPassword.vue"),
    meta: {
      title: "重置密码",
      guestOnly: true,
    },
  },
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: () => import("@/views/NotFound.vue"),
    meta: {
      title: "页面未找到",
    },
  },
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 如果存在保存的位置，则滚动到该位置
    if (savedPosition) {
      return savedPosition;
    }

    // 否则滚动到页面顶部
    return { top: 0 };
  },
});

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 博客系统` : "博客系统";

  // 检查是否需要认证
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 保存当前路径，登录后重定向
    next({
      name: "Login",
      query: { redirect: to.fullPath },
    });
    return;
  }

  // 检查权限
  if (
    to.meta.requiresPermission &&
    !authStore.hasPermission(to.meta.requiresPermission)
  ) {
    next({
      name: "Home",
      query: { error: "no_permission" },
    });
    return;
  }

  // 检查是否仅限访客
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    next({ name: "Home" });
    return;
  }

  // 如果需要认证但没有用户信息，先获取用户信息
  if (to.meta.requiresAuth && authStore.isAuthenticated && !authStore.user) {
    try {
      await authStore.fetchUser();
    } catch (error) {
      console.error("Failed to fetch user:", error);
      next({ name: "Login" });
      return;
    }
  }

  next();
});

// 路由后置守卫
router.afterEach((to, from) => {
  // 可以在这里添加页面访问统计等逻辑
  console.log(`Navigated from ${from.path} to ${to.path}`);
});

export default router;
