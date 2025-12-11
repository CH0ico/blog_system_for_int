import { createApp } from "vue";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";

// 磁带未来主义样式
import "@/styles/cassette-futurism.scss";
import "@/styles/global.scss";

import App from "./App.vue";
import router from "./router";
import { useAuthStore } from "./stores/auth";
import { useSocketStore } from "./stores/socket";

const app = createApp(App);
const pinia = createPinia();

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

// Toast配置
const toastOptions = {
  position: "top-right",
  timeout: 3000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: "button",
  icon: true,
  rtl: false,
};

app.use(pinia);
app.use(router);
app.use(ElementPlus);
app.use(Toast, toastOptions);

// 初始化认证状态和Socket连接
const authStore = useAuthStore();
const socketStore = useSocketStore();

// 应用启动时检查认证状态
authStore.checkAuthStatus();

// 如果用户已登录，初始化Socket连接
if (authStore.isAuthenticated) {
  socketStore.initializeSocket();
}

app.mount("#app");
